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
from app_process.forms import SubjectForm
from app_process.models import Project, Build, Segment, UnitType, Subject
from system.mixin import LoginRequiredMixin
from system.models import Structure, Menu


class SubjectView(LoginRequiredMixin, View):
    """
    机种
    """
    def get(self, request):
        res = dict()

        menu = Menu.get_menu_by_request_url(url=self.request.path_info)
        if menu is not None:
            res.update(menu)

        return render(request, 'system/Subject/Subject_List.html', res)


class SubjectListView(LoginRequiredMixin, View):
    """
    工站详情
    """
    def get(self, request):

        fields = ['id', 'subject']
        searchFields = ['subject']  # 与数据库字段一致

        # 此处的if语句有很大作用，如remark中数据为None,可通过if request.GET.get('')将传入为''的不将条件放入进去
        filters = {i + '__icontains': request.GET.get(i, '') for i in searchFields if request.GET.get(i, '')}

        res = dict(data=list(Subject.objects.filter(**filters).values(*fields)))

        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')


class SubjectUpdateView(LoginRequiredMixin, View):
    """
    新增 和 修改
    """
    # 注意：编辑页面中type=hidden隐藏的id，目的就是为了标识是编辑/增加操作
    def get(self, request):
        res = dict()
        if 'id' in request.GET and request.GET['id']:
            subject = get_object_or_404(Subject, pk=request.GET.get('id'))
            res['subject'] = subject
        else:
            subject = Subject.objects.all()
            res['subject'] = subject

        return render(request, 'system/Subject/Subject_Update.html', res)

    def post(self, request):
        res = dict(result=False)
        if 'id' in request.POST and request.POST['id']:  # id的存在，就是为了说明是新增数据还是编辑数据
            subject = get_object_or_404(Subject, pk=request.POST.get('id'))
        else:
            subject = Subject()

        subject_create_form = SubjectForm(request.POST, instance=subject)

        if subject_create_form.is_valid():
            subject_create_form.save()
            res['result'] = True

        return HttpResponse(json.dumps(res), content_type='application/json')


class SubjectDeleteView(LoginRequiredMixin, View):
    """
    删除视图
    """
    def post(self, request):
        res = dict(result=False)
        id = list(map(int, request.POST.get('id').split(',')))[0]

        if 'id' in request.POST and request.POST['id']:
            id_list = map(int, request.POST.get('id').split(','))
            Subject.objects.filter(id__in=id_list).delete()
            res['result'] = True

        return HttpResponse(json.dumps(res), content_type='application/json')


