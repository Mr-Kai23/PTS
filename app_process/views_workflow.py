
# ======================================================
# @Author  :   Daniel                 
# @Time    :   2020-03
# @Desc    :   工單處理視圖
# ======================================================

import json, time, datetime, re
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.decorators.cache import cache_page

from app_process.forms import WorkflowForm
from app_process.models import Segment, OrderInfo, Project, UnitType
from system.models import UserInfo
from system.mixin import LoginRequiredMixin
from system.models import Menu
from message import send_email, send_message
from django.conf import settings


class WorkFlowView(LoginRequiredMixin, View):
    """
    工单视图
    """
    def get(self, request):
        res = dict()

        # 專案
        res['projects'] = Project.objects.all()
        # 段别
        segments = Segment.objects.all()
        res['segments'] = segments

        menu = Menu.get_menu_by_request_url(url=self.request.path_info)
        if menu is not None:
            res.update(menu)

        return render(request, 'process/WorkFlow/WorkFlow_List.html', res)


class WorkFlowListView(LoginRequiredMixin, View):
    """
    工单显示视图
    """

    def get(self, request):

        fields = ['id', 'project', 'build', 'order', 'publish_dept', 'publisher', 'publish_status',
                  'publish_time', 'subject', 'key_content', 'segment', 'receiver', 'receive_status',
                  'status', 'withdraw_time', 'unit_type']

        searchfields = ['segment', 'status', 'receive_status', 'unit_type']

        filters = {i + '__contains': request.GET.get(i, '') for i in searchfields if request.GET.get(i, '')}

        # 获取工单
        workflows = OrderInfo.objects.filter(**filters).values(*fields).order_by('-id')

        for workflow in workflows:
            order = OrderInfo.objects.get(id=workflow['id'])
            # workflow['status'] = order.get_status_display()
            workflow['receive_status'] = order.get_receive_status_display()

        res = dict(data=list(workflows))

        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')


class WorkFlowCreateView(LoginRequiredMixin, View):
    """
    工單創建视图
    """
    def get(self, request):
        res = dict(msg='')
        if 'id' in request.GET and request.GET['id']:
            workflow = get_object_or_404(OrderInfo, pk=request.GET.get('id'))

            # 用于编辑时，前端的显示
            res['workflow'] = workflow

            # 获取工单发布时间
            res['time'] = workflow.publish_time.strftime('%Y-%m-%d %H:%M')

            # 获取工单的接收者，由于没用外键，所以以字符串形式拼接存储
            res['receivers'] = workflow.receiver.split(';')
        else:
            # workflow = OrderInfo.objects.all()
            # res['workflow'] = workflow
            # 新建的时候，获取当前的时间为工单创建时间
            t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            res['time'] = t

        # 获取所有接收者DRI
        dris = UserInfo.objects.filter(account_type=1, is_admin=True)
        res['dris'] = dris

        return render(request, 'process/WorkFlow/WorkFlow_Create.html', res)

    def post(self, request):
        res = dict(result=False)
        email = False
        message = False
        emails = []  # 用于存放接收者邮箱
        mobiles = []  # 用于存放接受者电话

        # 手选编辑工单状态保存
        if 'ids' in request.POST and request.POST['ids']:
            # 獲取出工單
            order = OrderInfo.objects.get(id=request.POST['ids'])

            # 判斷工單是否接收，0:未接收 1:已接收
            if order.receive_status == 0:
                res['msg'] = '工單未接收！！'
            else:
                order.status = int(request.POST['data'])
                order.save()
                res['result'] = True

            return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')

        # 工单信息发布或编辑修改
        # 存在 ID 是为编辑已存在工单，否则为创建新的工单
        if 'id' in request.POST and request.POST['id']:
            workflow = get_object_or_404(OrderInfo, id=int(request.POST['id']))

            workflow_form = WorkflowForm(request.POST, instance=workflow)

            # 判断表单是否有效
            if workflow_form.is_valid():
                workflow.save()
                res['result'] = True

        else:
            # 新建时发送邮件和短信的标签
            email = True
            message = True

            # 判断工单接收DRI,以字符串的形式存储
            if 'All' not in request.POST.getlist('receiver'):
                # 获取接收前端选中的接收者
                receiver_list = request.POST.getlist('receiver')

                # 所有接收者DRI
                users = UserInfo.objects.filter(name__in=receiver_list)
                # 获取接收DRI姓名和段别
                receivers = list(users.values_list('name', 'project', 'segment'))

                # 获取出所有接收的DRI
                for user in users:
                    emails.append(user.email)
                    mobiles.append(user.mobile)

                    # 若果用户存在下属员工
                    if user.userinfo_set.all():
                        # 获取DRI下面的员工邮箱和电话
                        for email, mobile in tuple(user.userinfo_set.values_list('email', 'mobile')):
                            emails.append(email)
                            mobiles.append(mobile)

            else:
                # 如果选择了 All
                # 获取所有接收者信息
                users = UserInfo.objects.filter(account_type=1).all()
                # 获取所有接收DRI姓名和段别
                receivers = list(users.filter(is_admin=True).values_list('name', 'project', 'segment'))

                # 获取所有用户的邮箱和电话
                for email, mobile in tuple(users.values_list('email', 'mobile')):
                    emails.append(email)
                    mobiles.append(mobile)

            # 为每个接收者创建工单数据
            for receiver, project, segment in receivers:
                # 实例一个新工单
                workflow = OrderInfo()
                workflow_form = WorkflowForm(request.POST, instance=workflow)

                if workflow_form.is_valid():
                    # 工單接收者和段别
                    workflow.receiver = receiver
                    workflow.project = project
                    workflow.segment = segment
                    workflow.save()
                    res['result'] = True

            # 新建时发送邮件和短信
            if email and message:

                # 邮件和短息发送
                # 工单信息
                subject = request.POST['subject']
                date = re.split(r'[-, :, \s]\s*', request.POST['publish_time'])
                year = date[0]
                month = date[1]
                day = date[2]
                hour = date[3]
                minute = date[4]

                # 发布者信息
                name = request.user.name
                department = request.user.department.name
                project = request.user.project

                # # 發送郵件
                # send_email(subject,
                #            request.POST.get('key_content'),
                #            settings.DEFAULT_FROM_EMAIL,
                #            emails)
                # # 發送短信
                # send_message(mobiles,
                #              [project+"專案"+department+"部門"+name, year, month, day, hour, minute, subject],
                #              '6311', '7')

        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')


class WorkFlowDeleteView(LoginRequiredMixin, View):
    """
    工單刪除視圖
    """
    def post(self, request):
        res = dict(result=False)

        # 判断获取前端传过来的要删除的id
        if 'id' in request.POST and request.POST.get('id'):
            ids = map(int, request.POST.get('id').split(','))

            OrderInfo.objects.filter(id__in=ids).delete()

            res['result'] = True

        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')


class WorkFlowDetailView(LoginRequiredMixin, View):
    """
    工單详情視圖
    """
    def get(self, request):
        res = dict()

        id = request.GET.get('workflowId')

        workflow = OrderInfo.objects.get(id=id)

        res['workflow'] = workflow

        return render(request, 'process/WorkFlow/WorkFlow_Detail.html', res)



