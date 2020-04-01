import json, time
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, QueryDict
from django.shortcuts import render, get_object_or_404
from django.views import View

from app_process.forms import WorkflowForm
from app_process.models import Segment, OrderInfo
from system.models import UserInfo
from system.mixin import LoginRequiredMixin
from system.models import Menu


class WorkFlowView(LoginRequiredMixin, View):
    """
    工单视图
    """
    def get(self, request):
        res = dict()

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
        workflows = list(OrderInfo.objects.filter(**filters).values(*fields).order_by('-id'))

        res = dict(data=workflows)

        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')


class WorkFlowCreateView(LoginRequiredMixin, View):
    """
    工單創建视图
    """
    def get(self, request):
        res = dict()
        if 'id' in request.GET and request.GET['id']:
            workflow = get_object_or_404(OrderInfo, pk=request.GET.get('id'))
            # 用于编辑时，前端的显示
            res['workflow'] = workflow
            # 获取工单发布时间
            res['time'] = workflow.publish_time.strftime("%Y-%m-%d %H:%M")
            # 获取工单的接收者，由于没用外键，所以以字符串形式拼接存储
            res['receivers'] = workflow.receiver.split(';')
        else:
            # workflow = OrderInfo.objects.all()
            # res['workflow'] = workflow
            # 新建的时候，获取当前的时间为工单创建时间
            t = time.strftime("%Y-%m-%d %H:%M", time.localtime())
            res['time'] = t

        dris = UserInfo.objects.filter(is_admin=True)
        res['dris'] = dris

        return render(request, 'process/WorkFlow/WorkFlow_Create.html', res)

    def post(self, request):
        res = dict(result=False)
        if 'id' in request.POST and request.POST['id']:
            workflow = get_object_or_404(OrderInfo, id=int(request.POST['id']))

        else:
            workflow = OrderInfo()

        request.POST.getlist('receiver')

        workflow_form = WorkflowForm(request.POST, instance=workflow)

        # 判断工单接收DRI,以字符串的形式存储
        if 'All' not in request.POST.getlist('receiver'):
            receiver = ';'.join(request.POST.getlist('receiver'))
        else:
            # 如果选择了 All,则接受者为 All
            receiver = request.POST.getlist('receiver')[0]

        workflow.receiver = receiver

        # 判断表单是否有效
        if workflow_form.is_valid():
            workflow.save()
            res['result'] = True
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
    pass

