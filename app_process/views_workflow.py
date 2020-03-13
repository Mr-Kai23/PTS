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


class WorkFlowCreateView(LoginRequiredMixin, View):
    """
    工單創建视图
    """
    pass


class WorkFlowDeleteView(LoginRequiredMixin, View):
    """
    工單刪除視圖
    """
    def post(self, request):
        res = dict(result=False)
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

