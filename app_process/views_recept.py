import json, time, re
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from app_process.models import Segment, OrderInfo, Project, UnitType, Stations, Subject

from system.mixin import LoginRequiredMixin
from system.models import Menu


class ReceptView(LoginRequiredMixin, View):
    """
    接收工单视图
    """
    def get(self, request, receive_id):
        res = dict()

        # 用戶專案
        projects = re.split(r'[/|，|, |\n]\s*', request.user.project)
        res['projects'] = projects
        # 所有主旨
        res['subjects'] = Subject.objects.all()
        # 機種
        res['unit_types'] = UnitType.objects.filter(project__in=projects)
        # 工站
        res['stations'] = Stations.objects.all()
        # 段别
        segments = Segment.objects.all()
        res['segments'] = segments

        res['receive_id'] = receive_id

        menu = Menu.get_menu_by_request_url(url=self.request.path_info)
        if menu is not None:
            res.update(menu)

        return render(request, 'process/Recipient/Recipient_List.html', res)


class ReceptListView(LoginRequiredMixin, View):
    """
    接收流程显示视图
    """
    def get(self, request):

        # 用戶專案、用戶名、用戶部門
        projects = re.split(r'[/|，|, |\n]\s*', request.user.project)
        username = request.user.name
        department = request.user.department.name

        fields = ['id', 'project', 'build', 'order', 'publish_dept', 'publisher', 'publish_status',
                  'publish_time', 'subject', 'key_content', 'segment', 'receiver', 'receive_status', 'status',
                  'receive_time', 'unit_type', 'station']

        searchfields = ['segment', 'status', 'receive_status', 'unit_type', 'station', 'order']

        filters = {i + '__icontains': request.GET.get(i, '') for i in searchfields if request.GET.get(i, '')}

        # 本部門所有未接收工單
        # 子流程、未被刪除的
        if request.GET['receive_id'] == '1':
            # 接收者
            if request.user.account_type == 1:
                workflows = list(OrderInfo.objects.filter(project__in=projects, receive_dept=department,
                                                          receive_status=0, is_parent=False, deleted=False,
                                                          **filters).values(*fields).order_by('-id'))
            else:
                # 發佈者
                workflows = list(OrderInfo.objects.filter(project__in=projects, publisher=username, receive_status=0,
                                                          is_parent=False, deleted=False,
                                                          **filters).values(*fields).order_by('-id'))

        # 我的待辦工單
        # 未刪除的、接收用戶自能拿到子流程，不用加 is_parent=False
        elif request.GET['receive_id'] == '2':
            workflows = list(OrderInfo.objects.filter(project__in=projects, receiver=username, receive_status=0,
                                                      deleted=False, **filters).values(*fields).order_by('-id'))

        for workflow in workflows:
            order = OrderInfo.objects.get(id=workflow['id'])
            workflow['status'] = order.get_status_display()
            workflow['receive_status'] = order.get_receive_status_display()

        res = dict(data=workflows)

        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')


class WorkFlowReceiveView(LoginRequiredMixin, View):
    """
    工单接收视图
    """
    def post(self, request):
        res = dict(result=False)

        if 'id' in request.POST and request.POST['id']:
            ids = map(int, request.POST['id'].split(','))

            # 将工单接收状态更新为已接收
            OrderInfo.objects.filter(id__in=ids).update(receive_status=1)

            res['result'] = True

        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')


class ReceptDetailView(LoginRequiredMixin, View):
    """
    工單详情視圖
    """
    def get(self, request):
        res = dict()

        id = request.GET.get('workflowId')

        workflow = OrderInfo.objects.get(id=id)

        res['workflow'] = workflow

        return render(request, 'process/Recipient/Recipient_Detail.html', res)


class MessageView(View):
    """
    消息显示提醒
    """
    def get(self, request):
        res = dict(count=0)

        # 用戶專案
        projects = re.split(r'[/|，|, |\n]\s*', request.user.project)

        username = request.user.name

        # 本人的未接收流程數量，子流程，未被刪除的
        count = OrderInfo.objects.filter(project__in=projects, receiver=username, is_parent=False, deleted=False,
                                         receive_status=0).count()

        res['count'] = count

        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')


