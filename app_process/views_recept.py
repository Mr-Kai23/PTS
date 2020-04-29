import json, time
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import View

from app_process.forms import WorkflowForm, RecipientForm
from app_process.models import Segment, OrderInfo, Project, UnitType
from system.models import UserInfo
from system.mixin import LoginRequiredMixin
from system.models import Menu


class ReceptView(LoginRequiredMixin, View):
    """
    接收工单视图
    """
    def get(self, request):
        res = dict()

        # 專案
        res['projects'] = Project.objects.all()
        # 機種
        res['unit_types'] = UnitType.objects.all()
        # 段别
        segments = Segment.objects.all()
        res['segments'] = segments

        menu = Menu.get_menu_by_request_url(url=self.request.path_info)
        if menu is not None:
            res.update(menu)

        return render(request, 'process/Recipient/Recipient_List.html', res)


class ReceptListView(LoginRequiredMixin, View):
    """
    接收工单显示视图
    """
    def get(self, request):

        fields = ['id', 'project', 'build', 'order', 'publish_dept', 'publisher', 'publish_status',
                  'publish_time', 'subject', 'key_content', 'segment', 'receive_status', 'status',
                  'withdraw_time', 'unit_type']

        searchfields = ['segment', 'status', 'receive_status', 'unit_type']

        filters = {i + '__contains': request.GET.get(i, '') for i in searchfields if request.GET.get(i, '')}

        # 获取接收者是用户或者用户DRI的未接收工单
        if request.user.superior:
            workflows = list(OrderInfo.objects.filter(receiver=request.user.superior.name, receive_status=0, **filters).values(*fields).order_by('-id'))
        else:
            workflows = list(
                OrderInfo.objects.filter(receiver=request.user.name, receive_status=0, **filters).values(
                    *fields).order_by('-id'))

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



