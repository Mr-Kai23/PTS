from django.core.serializers import json
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from app_process.models import Segment, OrderInfo
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

        # 执行状况
        statuses, restatuses = tuple(OrderInfo.objects.values_list('status', 'receive_status'))

        res = {
            'statues': statuses,
            'restatues': restatuses
        }

        menu = Menu.get_menu_by_request_url(url=self.request.path_info)
        if menu is not None:
            res.update(menu)

        return render(request, 'process/WorkFlow/WorkFlow_List.html', res)


class WorkFlowListView(LoginRequiredMixin, View):
    """
    工单显示视图
    """
    def get(self, request):

        fields = ['project', 'build', 'order', 'publish_dept', 'publisher', 'publish_status',
                  'publish_time', 'subject', 'key_content', 'segment', 'receiver', 'receive_status',
                  'status', 'withdraw_time', 'unit_type']

        searchfields = ['segment', 'status', 'receive_status', 'unit_type']

        filters = {i + '__contains': request.GET.get(i, '') for i in searchfields if request.GET.get(i, '')}

        # 获取工单
        workflows = list(OrderInfo.objects.filter(**filters).values(*fields).order_by('-id'))

        res = dict(data=workflows)

        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')


