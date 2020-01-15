# @Time   : 2018/10/18 23:04
# @Author : RobbieHan
# @File   : views_structure.py

import json

from django.views.generic.base import TemplateView
from django.views.generic.base import View
from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from .mixin import LoginRequiredMixin
from .models import Structure
from .forms import StructureForm
from custom import BreadcrumbMixin

User = get_user_model()


class StructureView(LoginRequiredMixin,  BreadcrumbMixin, TemplateView):

    template_name = 'system/structure/structure.html'


class StructureListView(LoginRequiredMixin, View):

    def get(self, request):
        fields = ['id', 'name', 'type', 'parent__name', 'resetTime']

        # 通过*fields将需要查询字段列表传递给QuerySet的values
        ret = dict(data=list(Structure.objects.values(*fields)))

        return HttpResponse(json.dumps(ret), content_type='application/json')


class StructureCreateView(LoginRequiredMixin, View):

    def get(self, request):
        ret = dict(structure_all=Structure.objects.all())
        # 判断如果request.GET中包含id,则返回该条数据信息
        if 'id' in request.GET and request.GET['id']:
            structure = get_object_or_404(Structure, pk=request.GET['id'])
            ret['structure'] = structure
        return render(request, 'system/structure/structure_create.html', ret)

    def post(self, request):
        res = dict(result=False)
        # 如果 request.POST中包含id则查找该实例，并传递给ModelForm关键字参数instance，通过调用save()方法，将修改信息保存到该实例
        if 'id' in request.POST and request.POST['id']:
            structure = get_object_or_404(Structure, pk=request.POST['id'])

        # 如果request.POST中ID值不存在，则使用空的模型作为instance关键参数，调用save()方法，保存新建的数据
        else:
            structure = Structure()
        structure_form = StructureForm(request.POST, instance=structure)  # request.POST 获取表单数据
        if structure_form.is_valid():
            structure_form.save()
            res['result'] = True
        return HttpResponse(json.dumps(res), content_type='application/json')


class StructureDeleteView(LoginRequiredMixin, View):

    def post(self, request):
        ret = dict(result=False)
        if 'id' in request.POST and request.POST['id']:
            id_list = map(int, request.POST['id'].split(','))
            Structure.objects.filter(id__in=id_list).delete()
            ret['result'] = True
        return HttpResponse(json.dumps(ret), content_type='application/json')


class Structure2UserView(LoginRequiredMixin, View):

    def get(self, request):
        if 'id' in request.GET and request.GET['id']:
            structure = get_object_or_404(Structure, pk=int(request.GET['id']))
            added_users = structure.userinfo_set.all()
            all_users = User.objects.all()
            un_add_users = set(all_users).difference(added_users)
            ret = dict(structure=structure, added_users=added_users, un_add_users=list(un_add_users))
        return render(request, 'system/structure/structure_user.html', ret)

    def post(self, request):
        res = dict(result=False)
        id_list = None
        structure = get_object_or_404(Structure, pk=int(request.POST['id']))
        if 'to' in request.POST and request.POST.getlist('to', []):
            id_list = map(int, request.POST.getlist('to', []))
        structure.userinfo_set.clear()
        if id_list:
            for user in User.objects.filter(id__in=id_list):
                structure.userinfo_set.add(user)
        res['result'] = True
        return HttpResponse(json.dumps(res), content_type='application/json')