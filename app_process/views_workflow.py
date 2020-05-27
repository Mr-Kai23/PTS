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
from app_process.models import Segment, OrderInfo, Project, UnitType, Stations, Subject
from system.models import UserInfo
from system.mixin import LoginRequiredMixin
from system.models import Menu
import pandas as pd
from .views import create_workflow, send_email_message
from django.core.cache import cache


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
        # 機種
        res['unit_types'] = UnitType.objects.filter(project=request.user.project)
        # 工站
        res['stations'] = Stations.objects.all()
        # 所有主旨
        res['subjects'] = Subject.objects.all()

        menu = Menu.get_menu_by_request_url(url=self.request.path_info)
        if menu is not None:
            res.update(menu)

        return render(request, 'process/WorkFlow/WorkFlow_List.html', res)

    """
    @Author  :   Daniel                
    @Time    :   2020-5-20 Update
    @Desc    :   工单导入
    """

    def post(self, request):

        """
        工單導入
        :param request:
        :return: 返回渲染上传信息页面
        """
        msg = ''

        correct_workflow = []  # 上傳成功的工單
        error_department = []  # 部門錯誤的工單
        error_project = []  # 專案錯誤的工單
        error_publisher = []  # 段別錯誤的工單

        file = request.FILES['file']

        if file.name.endswith(".xlsx") or file.name.endswith(".xls"):  # 判断上传文件是否为表格
            df = pd.read_excel(file, keep_default_na=False)

            column_list = ['專案', '發佈者部門', '發佈者姓名', '主旨', '工單', '工站', '流程內容', '接收段別']

            if list(df.columns) == column_list:

                # 用户部门、專案
                department = request.user.department.name
                project = request.user.project

                # 工單發佈時間、發佈者
                publisher = request.user.name

                # 讀取工單數據
                for i in range(len(df)):
                    if project == df.loc[i, '專案']:
                        if department == df.loc[i, '發佈者部門']:
                            if publisher == df.loc[i, '發佈者姓名']:

                                # 上傳成功的工單，将工单信息放入缓存中
                                # 到上传信息页面查看是否信息有误
                                correct_workflow.append(df.loc[i].tolist())
                                cache.set('workflow_cache', correct_workflow, 60*60)

                            else:
                                msg = '工單發佈者與當前用戶不匹配！！'
                                error_publisher.append(df.loc[i].tolist())
                                break

                        else:
                            msg = '請勿發佈其他部門工單！！'
                            error_department.append(df.loc[i].tolist())
                            break
                    else:
                        msg = '用戶無該專案工單發佈權限！！'
                        error_project.append(df.loc[i].tolist())
                        break

                if not error_project and not error_department:
                    msg = '工單上傳！！'

            else:
                msg = '請選擇正確的文件！！'

        return render(request, 'process/WorkFlow/WorkFlow_upload_info.html',
                      {"msg": msg, "correct_workflow": correct_workflow, "error_department": error_department,
                       "error_project": error_project, "error_publisher": error_publisher})


class WorkFlowListView(LoginRequiredMixin, View):
    """
    工单显示视图
    """

    def get(self, request):
        # 用戶專案、部門
        project = request.user.project
        department = request.user.department.name
        name = request.user.name

        # 前端要显示的属性
        fields = ['id', 'project', 'build', 'order', 'publish_dept', 'publisher', 'publish_status',
                  'publish_time', 'subject', 'key_content', 'segment', 'receiver', 'receive_status',
                  'status', 'withdraw_time', 'unit_type', 'station']

        searchfields = ['subject', 'segment', 'status', 'receive_status', 'station', 'order']

        filters = {i + '__icontains': request.GET.get(i, '') for i in searchfields if request.GET.get(i, '')}

        # 接收者工單顯示
        if request.user.account_type == 1:

            if request.user.user_type == 0:
                # 接收者只能看接收人是自己的子工單
                workflows = OrderInfo.objects.filter(project=project, receive_dept=department, receiver=name,
                                                     deleted=False, is_parent=False,
                                                     **filters).values(*fields).order_by('-id')

            else:
                # 获取当先用户的下级
                juniors = [junior for junior in request.user.userinfo_set.all()]
                juniors_name = [junior.name for junior in juniors]

                # 线长
                if request.user.user_type == 1:
                    # 下级 副线长
                    workflows = OrderInfo.objects.filter(project=project, receive_dept=department, is_parent=False,
                                                         deleted=False, receiver__in=juniors_name,
                                                         **filters).values(*fields).order_by('-id')
                # 专案主管
                elif request.user.user_type == 2:
                    lower_juniors = []
                    # 下级 线长
                    for junior in juniors:
                        # 线长 下级 副线长
                        for lower_junior in junior.userinfo_set.all():
                            lower_juniors.append(lower_junior.name)

                    workflows = OrderInfo.objects.filter(project=project, receive_dept=department, is_parent=False,
                                                         receiver__in=lower_juniors, deleted=False,
                                                         **filters).values(*fields).order_by('-id')

        else:
            # 發佈者工單
            # 發佈者只能看自己發佈的工單，所有父工單
            workflows = OrderInfo.objects.filter(project=project, publish_dept=department, publisher=name,
                                                 is_parent=True, deleted=False,
                                                 **filters).values(*fields).order_by('-id')

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

            # # 获取工单的接收者，由于没用外键，所以以字符串形式拼接存储
            # res['receiver_segments'] = workflow.segment.split(';')
        else:
            # workflow = OrderInfo.objects.all()
            # res['workflow'] = workflow
            # 新建的时候，获取当前的时间为工单创建时间
            t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            res['time'] = t

        # 获取段别
        segments = Segment.objects.all()
        res['segments'] = segments
        # 获取主旨
        res['subjects'] = Subject.objects.all()

        return render(request, 'process/WorkFlow/WorkFlow_Create.html', res)

    def post(self, request):
        res = dict(result=False)

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

        # 上传信息页面，点击发布时执行
        if request.POST['publish']:

            # 从缓存中拿导入的工单数据
            workflows = cache.get('workflow_cache', None)

            if workflows:
                # 发布时间
                publish_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                pattern = re.compile(r'[/|;|\n]\s*')

                for workflow in workflows:
                    project = workflow[0]  # 专案
                    department = workflow[1]  # 部门
                    publisher = workflow[2]  # 发布者
                    subject = workflow[3]  # 主旨
                    order = workflow[4]  # 工单
                    order_type = workflow[5]  # 工单类型
                    work_station = workflow[6]  # 工站
                    key_content = workflow[7]  # 工单内容
                    segments = workflow[8]  # 接收段别

                    # 工單
                    order = pattern.split(order)

                    # 工单属性
                    fields = {
                        'project': project, 'publish_dept': department, 'publisher': publisher,
                        'publish_time': publish_time, 'subject': subject, 'order': order, 'key_content': key_content,
                    }

                    segment_list = pattern.split(segments)

                    # 父工單中段別將所有段別合併顯示
                    segment = '/'.join(segment_list)
                    # 創建父工單
                    father_order = OrderInfo.objects.create(**fields, is_parent=True, segment=segment)

                    mobiles, emails = create_workflow(father_order, fields, segment_list)

                    # 郵件和信息發送
                    # send_email_message(fields, mobiles, emails)

                res['result'] = True

            return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')

        # 工单信息发布或编辑修改
        # 存在 ID 是为编辑已存在工单，否则为创建新的工单
        # 更新工單
        if 'id' in request.POST and request.POST['id']:
            workflow = get_object_or_404(OrderInfo, id=int(request.POST['id']))

            workflow_form = WorkflowForm(request.POST, instance=workflow)

            # 判断表单是否有效
            if workflow_form.is_valid():
                workflow.save()
                OrderInfo.objects.filter(parent=workflow).update(subject=workflow.subject, order=workflow.order,
                                                                 key_content=workflow.key_content)
                res['result'] = True

        # 發佈新工單
        else:
            # 用户专案、發佈者
            project = request.user.project
            publisher = request.POST['publisher']

            # 工单信息主旨和發佈時間
            subject = request.POST['subject']
            publish_time = request.POST['publish_time']

            # 工单属性
            fields = {
                'project': project, 'publish_dept': request.POST['publish_dept'], 'publisher': publisher,
                'publish_time': publish_time, 'subject': subject, 'order': request.POST['order'],
                'key_content': request.POST['key_content']
            }

            # 判断工单接收DRI,以字符串的形式存储
            if 'All' not in request.POST.getlist('segment'):
                # 获取接收前端选中的接收者
                segment_list = request.POST.getlist('segment')

                # 父工單中段別將所有段別合併顯示
                segment = '/'.join(segment_list)
                # 創建父工單
                parent_order = OrderInfo.objects.create(**fields, is_parent=True, segment=segment)

                # 創建工單
                mobiles, emails = create_workflow(parent_order, fields, segment_list)

            else:
                # 創建父工單，發佈者顯示父工單
                parent_order = OrderInfo.objects.create(**fields, is_parent=True, segment='All')
                # 創建工單,
                mobiles, emails = create_workflow(parent_order, fields)

            res['result'] = True

            # 郵件和信息發送需要的數據
            # send_email_message(fields, mobiles, emails)

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

            OrderInfo.objects.filter(id__in=ids).update(deleted=True)

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
