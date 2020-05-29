import json
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder

from custom import BreadcrumbMixin
from app_process.forms import ProjectCreateForm, SegmentCreateForm, UnitTypeCreateForm
from app_process.models import Project, Build, Segment,UnitType
from system.mixin import LoginRequiredMixin
from system.models import Structure, Menu


class UnitTypeView(LoginRequiredMixin, View):
    """
    机种
    """
    def get(self, request):
        res = dict()

        # 專案
        unit_types = UnitType.objects.all()
        res['unit_types'] = unit_types

        menu = Menu.get_menu_by_request_url(url=self.request.path_info)
        if menu is not None:
            res.update(menu)

        return render(request, 'system/unit_type/unit_type_list.html', res)


class UnitTypeListView(LoginRequiredMixin, View):
    """
    机种详情
    """
    def get(self, request):

        fields = ['id', 'project', 'unit_type']
        searchFields = ['project', 'unit_type', ]  # 与数据库字段一致

        # 此处的if语句有很大作用，如remark中数据为None,可通过if request.GET.get('')将传入为''的不将条件放入进去
        filters = {i + '__icontains': request.GET.get(i, '') for i in searchFields if request.GET.get(i, '')}

        res = dict(data=list(UnitType.objects.filter(**filters).values(*fields)))

        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')


class UnitTypeUpdateView(LoginRequiredMixin, View):
    """
    新增 和 修改
    """
    # 注意：编辑页面中type=hidden隐藏的id，目的就是为了标识是编辑/增加操作
    def get(self, request):
        res = dict()
        if 'id' in request.GET and request.GET['id']:
            unit_type = get_object_or_404(UnitType, pk=request.GET.get('id'))
            res['unit_type'] = unit_type
        else:
            unit_type = UnitType.objects.all()
            res['unit_type'] = unit_type

        # 獲取所有專案
        projects = Project.objects.all()
        res['projects'] = projects

        return render(request, 'system/unit_type/unit_type_Update.html', res)

    def post(self, request):
        res = dict(result=False)
        if 'id' in request.POST and request.POST['id']:  # id的存在，就是为了说明是新增数据还是编辑数据
            unit_type = get_object_or_404(UnitType, pk=request.POST.get('id'))
        else:
            unit_type = UnitType()

        unit_type_create_form = UnitTypeCreateForm(request.POST, instance=unit_type)

        if unit_type_create_form.is_valid():
            unit_type_create_form.save()
            res['result'] = True

        return HttpResponse(json.dumps(res), content_type='application/json')


class UnitTypeDeleteView(LoginRequiredMixin, View):
    """
    删除视图
    """
    def post(self, request):
        res = dict(result=False)
        id = list(map(int, request.POST.get('id').split(',')))[0]

        if 'id' in request.POST and request.POST['id']:
            id_list = map(int, request.POST.get('id').split(','))
            UnitType.objects.filter(id__in=id_list).delete()
            res['result'] = True

        return HttpResponse(json.dumps(res), content_type='application/json')


