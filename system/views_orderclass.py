from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from app_process.forms import OrderclassForm
from app_process.models import Orderclass
from system.mixin import LoginRequiredMixin
from django.views.generic.base import View
from system.models import Structure, Menu
import json


class OrderclassView(LoginRequiredMixin, View):
    '''工单种类视图'''
    def get(self, request):
        ret = dict()
        orderclass = Orderclass.objects.all()
        ret['orderclasses'] = orderclass

        menu = Menu.get_menu_by_request_url(url=self.request.path_info)
        if menu is not None:
            ret.update(menu)

        return render(request, 'system/order_class/orderclasslist.html', ret)

class OrderclassListView(LoginRequiredMixin, View):

    def get(self, request):

        fields = ['id', 'orderclass']
        searchFields = ['orderclass', ]  # 与数据库字段一致
        filters = {i + '__icontains': request.GET.get(i, '') for i in searchFields if
                   request.GET.get(i, '')}  # 此处的if语句有很大作用，如remark中数据为None,可通过if request.GET.get('')将传入为''的不将条件放入进去

        res = dict(data=list(Orderclass.objects.filter(**filters).values(*fields)))
        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')

class OrderclassUpdate(LoginRequiredMixin, View):

    def get(self, request):
        res = dict()
        if 'id' in request.GET and request.GET['id']:
            orderclass = get_object_or_404(Orderclass, pk=request.GET.get('id'))
            res['orderclass'] = orderclass
        else:
            orderclass = Orderclass.objects.all()
            res['orderclass'] = orderclass

        return render(request, 'system/order_class/orderclassupdate.html', res)

    def post(self, request):
        res = dict(result=False)
        if 'id' in request.POST and request.POST['id']:  # id的存在，就是为了说明是新增数据还是编辑数据
            orderclass = get_object_or_404(Orderclass, pk=request.POST.get('id'))
        else:
            orderclass = Orderclass()

        orderclass_create_form = OrderclassForm(request.POST, instance=orderclass)

        if orderclass_create_form.is_valid():
            orderclass_create_form.save()
            res['result'] = True

        return HttpResponse(json.dumps(res), content_type='application/json')

class OrderclassDelete(LoginRequiredMixin, View):
    def post(self, request):
        res = dict(result=False)
        id = list(map(int, request.POST.get('id').split(',')))[0]

        if 'id' in request.POST and request.POST['id']:
            id_list = map(int, request.POST.get('id').split(','))
            Orderclass.objects.filter(id__in=id_list).delete()
            res['result'] = True

        return HttpResponse(json.dumps(res), content_type='application/json')