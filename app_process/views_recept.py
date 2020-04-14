import json, time
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import View

from app_process.forms import WorkflowForm, RecipientForm
from app_process.models import Segment, OrderInfo
from system.models import UserInfo
from system.mixin import LoginRequiredMixin
from system.models import Menu


class ReceptView(LoginRequiredMixin, View):
    """
    接收工单视图
    """
    def get(self, request):
        res = dict()

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
                  'publish_time', 'subject', 'key_content', 'segment', 'receive_status','status',
                  'withdraw_time', 'unit_type']

        searchfields = ['segment', 'status', 'receive_status', 'unit_type']


        filters = {i + '__contains': request.GET.get(i, '') for i in searchfields if request.GET.get(i, '')}

        # 获取工单
        workflows = list(OrderInfo.objects.filter(**filters, receive_status=0).values(*fields).order_by('-id'))

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


class ReceptCreateView(LoginRequiredMixin, View):
    """
    接收工單創建视图
    """
    def get(self, request):
        res = dict()
        user = request.user.name
        t = time.strftime("%Y/%m/%d %H:%M", time.localtime())
        dris = UserInfo.objects.filter(is_admin=True)
        res = {
            'time': t,
            'dris': dris
        }

        return render(request, 'process/Recipient/Recipient_Create.html', res)

    def post(self, request):
        res = dict(result=False)
        if 'id' in request.POST and request.POST['id']:
            workflow = get_object_or_404(OrderInfo, id=request.POST['id'])
        else:
            workflow = OrderInfo()

        recipientform = RecipientForm(request.POST, instance=workflow)

        if recipientform.is_valid():
            workflow.save()
            res['result'] = True
        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')


class ReceptDeleteView(LoginRequiredMixin, View):
    """
    接收工單刪除視圖
    """
    def post(self, request):
        res = dict(result=False)
        if 'id' in request.POST and request.POST.get('id'):
            ids = map(int, request.POST.get('id').split(','))
            OrderInfo.objects.filter(id__in=ids).delete()

            res['result'] = True

        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')


