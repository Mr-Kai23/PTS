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
from app_process.forms import ProjectCreateForm
from app_process.models import Project, UnitType
from system.mixin import LoginRequiredMixin
from system.models import Structure,Menu


# 专案界面
class ProjectView(LoginRequiredMixin, View):
    def get(self, request):
        res = dict(data=Project.objects.all())

        # 專案
        projects = Project.objects.all()
        res['projects'] = projects

        menu = Menu.get_menu_by_request_url(url=self.request.path_info)
        if menu is not None:
            res.update(menu)
        return render(request, 'system/Project/Project_List.html', res)


# 申请详情列表
class ProjectListView(LoginRequiredMixin, View):
    def get(self, request):

        fields = ['id', 'project']
        searchFields = ['project', ]  # 与数据库字段一致
        filters = {i + '__icontains': request.GET.get(i, '') for i in searchFields if request.GET.get(i, '') }  #此处的if语句有很大作用，如remark中数据为None,可通过if request.GET.get('')将传入为''的不将条件放入进去

        res = dict(data=list(Project.objects.filter(**filters).values(*fields)))

        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')


# 專案 新增 和 修改
class ProjectUpdateView(LoginRequiredMixin, View):
    # 注意：编辑页面中type=hidden隐藏的id，目的就是为了标识是编辑/增加操作
    def get(self, request):
        res = dict()
        if 'id' in request.GET and request.GET['id']:
            project = get_object_or_404(Project, pk=request.GET.get('id'))
            res['project'] = project
        else:
            projects = Project.objects.all()
            res['projects'] = projects

        return render(request, 'system/Project/Project_Update.html', res)

    def post(self, request):
        res = dict(result=False)
        if 'id' in request.POST and request.POST['id']:  # id的存在，就是为了说明是新增数据还是编辑数据
            project = get_object_or_404(Project, pk=request.POST.get('id'))
        else:
            project = Project()

        project_create_form = ProjectCreateForm(request.POST, instance=project)

        if project_create_form.is_valid():
            project_create_form.save()
            res['result'] = True

        return HttpResponse(json.dumps(res), content_type='application/json')


# 库存删除
class ProjectDeleteView(LoginRequiredMixin, View):
    def post(self, request):
        res = dict(result=False)
        id = list(map(int, request.POST.get('id').split(',')))[0]

        if 'id' in request.POST and request.POST['id']:
            id_list = map(int, request.POST.get('id').split(','))
            Project.objects.filter(id__in=id_list).delete()
            res['result'] = True

        return HttpResponse(json.dumps(res), content_type='application/json')


# 专案 和 机种 联动
class ProjectAndUnitTypeLinkView(View):
    def post(self, request):
        res = dict()

        if request.POST.get('project'):
            unit_types = UnitType.objects.filter(project=request.POST.get('project')).values(*['unit_type'])
            res['unit_types'] = list(unit_types)

        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')


