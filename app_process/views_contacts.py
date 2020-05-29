import json, time, re
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import View

from app_process.forms import ContactForm
from app_process.models import Segment, OrderInfo, Project, ExceptionContact
from system.models import UserInfo, Structure
from system.mixin import LoginRequiredMixin
from system.models import Menu


class ContactView(LoginRequiredMixin, View):
    """
    联系人页面渲染视图
    """
    def get(self, request):
        res = dict()

        # 專案
        # res['projects'] = re.split(r'[/|，|, |\n]\s*', request.user.project)
        res['projects'] = Project.objects.all()

        # 段别
        segments = Segment.objects.all()
        res['segments'] = segments

        # 部门
        departments = Structure.objects.all()
        res['departments'] = departments

        menu = Menu.get_menu_by_request_url(url=self.request.path_info)
        if menu is not None:
            res.update(menu)

        return render(request, 'process/Contact/Contact_List.html', res)


class ContactListView(LoginRequiredMixin, View):
    """
    联系人显示视图
    """
    def get(self, request):

        # 用户专案
        projects = re.split(r'[/|，|, |\n]\s*', request.user.project)

        fields = ['id', 'project', 'department', 'segment', 'contact', 'phone']

        searchfields = ['project', 'department', 'segment']

        filters = {i + '__icontains': request.GET.get(i, '') for i in searchfields if request.GET.get(i, '')}

        contacts = list(ExceptionContact.objects.filter(project__in=projects, **filters).values(*fields).order_by('-id'))

        res = dict(data=contacts)

        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')


class ContactCreateView(LoginRequiredMixin, View):
    """
    联系人创建视图
    """
    def get(self, request):
        res = dict()

        # 用户专案
        # projects = re.split(r'[/|，|, |\n]\s*', request.user.project)
        res['projects'] = Project.objects.all()

        # 部门
        departments = Structure.objects.all()
        res['departments'] = departments

        return render(request, 'process/Contact/Contact_Create.html', res)

    def post(self, request):
        res = dict(result=False)

        if 'id' in request.POST and request.POST.get('id'):
            contact = get_object_or_404(ExceptionContact, id=request.POST['id'])
            res['contact'] = contact
        else:
            contact = ExceptionContact()

        contact_create_form = ContactForm(request.POST, instance=contact)

        if contact_create_form.is_valid():
            contact_create_form.save()
            res['result'] = True

        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')


class ContactDeleteView(LoginRequiredMixin, View):
    """
    联系人删除視圖
    """
    def post(self, request):
        res = dict(result=False)

        if 'id' in request.POST and request.POST['id']:
            ids = map(int, request.POST.get('id').split(','))

            ExceptionContact.objects.filter(id__in=ids).delete()

            res['result'] = True

        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')





