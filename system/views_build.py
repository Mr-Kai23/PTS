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
from app_process.forms import BuildCreateForm
from app_process.models import Build, Project
from system.mixin import LoginRequiredMixin
from system.models import Structure, Menu


class BuildView(LoginRequiredMixin, View):
    """
    阶段界面
    """
    def get(self, request):
        res = dict(data=Build.objects.all())

        # 專案
        projects = Project.objects.all()
        res['projects'] = projects

        # 階段
        builds = Build.objects.all()
        res['builds'] = builds

        menu = Menu.get_menu_by_request_url(url=self.request.path_info)
        if menu is not None:
            res.update(menu)
        return render(request, 'system/Build/Build_List.html', res)


class BuildListView(LoginRequiredMixin, View):
    """
    阶段详情列表
    """
    def get(self, request):

        fields = ['id', 'project', 'build']
        searchFields = ['project', 'build']  # 与数据库字段一致
        filters = {i + '__icontains': request.GET.get(i, '') for i in searchFields if request.GET.get(i, '')}  # 此处的if语句有很大作用，如remark中数据为None,可通过if request.GET.get('')将传入为''的不将条件放入进去

        res = dict(data=list(Build.objects.filter(**filters).values(*fields)))

        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')


class BuildUpdateView(LoginRequiredMixin, View):
    """
    專案 新增 和 修改
    """
    # 注意：编辑页面中type=hidden隐藏的id，目的就是为了标识是编辑/增加操作
    def get(self, request):
        res = dict()
        if 'id' in request.GET and request.GET['id']:
            build = get_object_or_404(Build, pk=request.GET.get('id'))
            res['build'] = build
        else:
            builds = Build.objects.all()
            res['builds'] = builds

        # 專案
        projects = Project.objects.all()
        res['projects'] = projects

        return render(request, 'system/Build/Build_Update.html', res)

    def post(self, request):
        res = dict(result=False)
        if 'id' in request.POST and request.POST['id']:  #id的存在，就是为了说明是新增数据还是编辑数据
            build = get_object_or_404(Build, pk=request.POST.get('id'))
        else:
            build = Build()

        build_create_form = BuildCreateForm(request.POST, instance=build)

        if build_create_form.is_valid():
            build_create_form.save()
            res['result'] = True

        return HttpResponse(json.dumps(res), content_type='application/json')


class BuildDeleteView(LoginRequiredMixin, View):
    """
    阶段删除
    """
    def post(self, request):
        res = dict(result=False)
        id = list(map(int, request.POST.get('id').split(',')))[0]

        if 'id' in request.POST and request.POST['id']:
            id_list = map(int, request.POST.get('id').split(','))
            Build.objects.filter(id__in=id_list).delete()
            res['result'] = True

        return HttpResponse(json.dumps(res), content_type='application/json')


class ProjectAndBuildLinkageView(LoginRequiredMixin, View):
    """
    专案 和 阶段 联动
    """
    def post(self, request):

        res = dict()

        if request.POST.get('project'):
            builds = Build.objects.filter(project=request.POST.get('project')).values(*['id', 'build'])
            res['builds'] = list(builds)

        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')