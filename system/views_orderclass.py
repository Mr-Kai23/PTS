from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from app_process.forms import OrderclassForm
from app_process.models import Orderclass
from system.mixin import LoginRequiredMixin
from django.views.generic.base import View
from system.models import Structure, Menu


class OrderclassView(LoginRequiredMixin, View):
    '''工单种类视图'''
    def get(self,request):
        ret = dict()
        orderclass = Orderclass.objects.all()
        ret['orderclasses'] = orderclass

        menu = Menu.get_menu_by_request_url(url=self.request.path_info)
        if menu is not None:
            ret.update(menu)

        return render(request, 'system/order_class/orderclasslist.html', ret)

class OrderclassListView(LoginRequiredMixin, View):

    def get(self,request):

        ret = dict()
        orderclasslist = Orderclass.objects.all()
        ret['orderclasslist'] = orderclasslist

        menu = Menu.get_menu_by_request_url(url=self.request.path_info)
        if menu is not None:
            ret.update(menu)

        return render(request,'system/order_class/orderclasslist.html', ret)

class OrderclassUpdate(LoginRequiredMixin, View):
    def post(self, requst):
        pass