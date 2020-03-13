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
from app_process.forms import ProjectCreateForm, SegmentCreateForm
from app_process.models import Project, Build, Segment
from system.mixin import LoginRequiredMixin
from system.models import Structure, Menu


class SegmentView(LoginRequiredMixin, View):
    """
    段别
    """
    def get(self, request):
        res = dict()

        # 專案
        segments = Segment.objects.all()
        res['segments'] = segments

        menu = Menu.get_menu_by_request_url(url=self.request.path_info)
        if menu is not None:
            res.update(menu)

        return render(request, 'system/segment/segment_list.html', res)


class SegmentListView(LoginRequiredMixin, View):
    """
    段别详情
    """
    def get(self, request):

        fields = ['id', 'segment']
        searchFields = ['segment', ]  # 与数据库字段一致
        filters = {i + '__icontains': request.GET.get(i, '') for i in searchFields if request.GET.get(i, '')}  # 此处的if语句有很大作用，如remark中数据为None,可通过if request.GET.get('')将传入为''的不将条件放入进去

        res = dict(data=list(Segment.objects.filter(**filters).values(*fields)))

        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')


class SegmentUpdateView(LoginRequiredMixin, View):
    """
    新增 和 修改
    """
    # 注意：编辑页面中type=hidden隐藏的id，目的就是为了标识是编辑/增加操作
    def get(self, request):
        res = dict()
        if 'id' in request.GET and request.GET['id']:
            segment = get_object_or_404(Segment, pk=request.GET.get('id'))
            res['segment'] = segment
        else:
            segmrnts = Segment.objects.all()
            res['segmrnts'] = segmrnts

        return render(request, 'system/segment/segment_Update.html', res)

    def post(self, request):
        res = dict(result=False)
        if 'id' in request.POST and request.POST['id']:  # id的存在，就是为了说明是新增数据还是编辑数据
            segment = get_object_or_404(Segment, pk=request.POST.get('id'))
        else:
            segment = Segment()

        segment_create_form = SegmentCreateForm(request.POST, instance=segment)

        if segment_create_form.is_valid():
            segment_create_form.save()
            res['result'] = True

        return HttpResponse(json.dumps(res), content_type='application/json')


class SegmentDeleteView(LoginRequiredMixin, View):
    """
    删除视图
    """
    def post(self, request):
        res = dict(result=False)
        id = list(map(int, request.POST.get('id').split(',')))[0]

        if 'id' in request.POST and request.POST['id']:
            id_list = map(int, request.POST.get('id').split(','))
            Segment.objects.filter(id__in=id_list).delete()
            res['result'] = True

        return HttpResponse(json.dumps(res), content_type='application/json')


