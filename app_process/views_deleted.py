import json, time, re
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import View

from app_process.forms import WorkflowForm, RecipientForm
from app_process.models import Segment, OrderInfo, Project, UnitType, Stations, Subject
from system.models import UserInfo
from system.mixin import LoginRequiredMixin
from system.models import Menu


class DeletedView(LoginRequiredMixin, View):
    """
    接收工单视图
    """
    def get(self, request):
        res = dict()

        # 專案
        res['projects'] = re.split(r'[/|，|, |\n]\s*', request.user.project)
        # 所有主旨
        res['subjects'] = Subject.objects.all()
        # 機種
        res['unit_types'] = UnitType.objects.filter(project=request.user.project)
        # 工站
        res['stations'] = Stations.objects.all()
        # 段别
        segments = Segment.objects.all()
        res['segments'] = segments

        menu = Menu.get_menu_by_request_url(url=self.request.path_info)
        if menu is not None:
            res.update(menu)

        return render(request, 'process/Deleted/Deleted_List.html', res)


class DeletedListView(LoginRequiredMixin, View):
    """
    接收工单显示视图
    """
    def get(self, request):
        # 用戶名
        username = request.user.name

        fields = ['id', 'project', 'build', 'order', 'publish_dept', 'publisher', 'publish_status',
                  'publish_time', 'subject', 'key_content', 'segment', 'receive_status', 'status',
                  'withdraw_time', 'unit_type', 'station']

        searchfields = ['project', 'segment', 'status', 'receive_status', 'unit_type', 'station', 'order']

        filters = {i + '__icontains': request.GET.get(i, '') for i in searchfields if request.GET.get(i, '')}

        # 用戶只能看自己刪除的流程
        # 发布者 删除了的工单
        if request.user.account_type == 0:
            workflows = list(OrderInfo.objects.filter(publisher=username, is_parent=True, deleted=True,
                                                      **filters).values(*fields).order_by('-id'))

        # 接收者
        # 删除了的工单
        elif request.user.account_type == 1:
            workflows = list(OrderInfo.objects.filter(receiver=username, deleted=True, is_parent=False,
                                                      **filters).values(*fields).order_by('-id'))

        for workflow in workflows:
            order = OrderInfo.objects.get(id=workflow['id'])
            workflow['status'] = order.get_status_display()
            workflow['receive_status'] = order.get_receive_status_display()

        res = dict(data=workflows)

        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')


class DeletedDetailView(LoginRequiredMixin, View):
    """
    流程详情視圖
    """
    def get(self, request):
        res = dict()

        id = request.GET.get('workflowId')

        workflow = OrderInfo.objects.get(id=id)

        res['workflow'] = workflow

        return render(request, 'process/Deleted/Deleted_Detail.html', res)


class DeletedWithdrawView(LoginRequiredMixin, View):
    """
    刪除流程撤回視圖
    """
    def post(self, request):
        res = dict(result=False)

        if 'id' in request.POST and request.POST['id']:
            # 獲取id
            ids = map(int, request.POST['id'].split(','))

            OrderInfo.objects.filter(id__in=ids).update(deleted=False)

            res['result'] = True

        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')



