# @Time   : 2018/10/16 23:11
# @Author : RobbieHan
# @File   : views_user.py

import re
import json

from django.shortcuts import render, HttpResponse
from django.views.generic.base import View, TemplateView
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404

from .forms import LoginForm, UserCreateForm, UserUpdateForm, PasswordChangeForm
from .mixin import LoginRequiredMixin
from .models import Structure, Role
from custom import BreadcrumbMixin
from django import forms
from django.contrib.auth import get_user_model
from system.models import Structure, Menu
from app_process.models import OrderInfo, Project, Segment
from datetime import datetime
from django.db.models import Count, Q
User = get_user_model()


class IndexView(LoginRequiredMixin, View):

    def get(self, request):

        res = {
            'created': OrderInfo.objects.all().count(),
            'receive': OrderInfo.objects.filter(receive_status=0).count(),
            'finished': OrderInfo.objects.filter(receive_status=1, status=1).count()
        }

        return render(request, 'process/order_index.html', res)


class LoginView(View):

    def get(self, request):
        if not request.user.is_authenticated:
            return render(request, 'system/users/login.html')
        else:
            return HttpResponseRedirect('/')

    def post(self, request):
        redirect_to = request.GET.get('next', '/')
        login_form = LoginForm(request.POST)
        ret = dict(login_form=login_form)
        if login_form.is_valid():
            user_name = request.POST['username']
            pass_word = request.POST['password']
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(redirect_to)
                else:
                    ret['msg'] = '用户未激活！'
            else:
                ret['msg'] = '用户名或密码错误！'
        else:
            ret['msg'] = '用户和密码不能为空！'
        return render(request, 'system/users/login.html', ret)


class LogoutView(View):

    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('login'))


class UserView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
    template_name = 'system/users/user.html'


class UserListView(LoginRequiredMixin, View):
    def get(self, request):
        fields = ['id', 'work_num', 'name', 'mobile', 'email', 'department__name', 'project', 'segment', 'account_type',
                  'is_admin', 'remark']
        filters = dict()
        if 'select' in request.GET and request.GET['select']:
            filters['is_active'] = request.GET['select']

        users = list(User.objects.filter(**filters).values(*fields))

        # 更新前端显示为choice文字显示
        for user in users:
            user['account_type'] = User.objects.get(id=user['id']).get_account_type_display()

        ret = dict(data=users)
        return HttpResponse(json.dumps(ret), content_type='application/json')


class UserCreateView(LoginRequiredMixin, View):
    """
    添加用户
    """

    def get(self, request):
        users = User.objects.exclude(username='admin')
        structures = Structure.objects.values()
        projects = Project.objects.values()
        segments = Segment.objects.values()
        roles = Role.objects.values()

        ret = {
            'users': users,
            'structures': structures,
            'projects': projects,
            'segments': segments,
            'roles': roles,
        }
        return render(request, 'system/users/user_create.html', ret)

    def post(self, request):
        user_create_form = UserCreateForm(request.POST)
        if user_create_form.is_valid():
            new_user = user_create_form.save(commit=False)
            new_user.password = make_password(user_create_form.cleaned_data['password'])
            new_user.save()
            user_create_form.save_m2m()
            ret = {'status': 'success'}
        else:
            pattern = '<li>.*?<ul class=.*?><li>(.*?)</li>'
            errors = str(user_create_form.errors)
            user_create_form_errors = re.findall(pattern, errors)
            ret = {
                'status': 'fail',
                'user_create_form_errors': user_create_form_errors[0]
            }
        return HttpResponse(json.dumps(ret), content_type='application/json')


class UserDetailView(LoginRequiredMixin, View):

    def get(self, request):
        user = get_object_or_404(User, pk=int(request.GET['id']))
        users = User.objects.exclude(Q(id=int(request.GET['id'])) | Q(username='admin'))
        structures = Structure.objects.values()
        segments = Segment.objects.values()
        projects = Project.objects.values()
        roles = Role.objects.values()
        user_roles = user.roles.values()
        ret = {
            'user': user,
            'structures': structures,
            'projects': projects,
            'segments': segments,
            'users': users,
            'roles': roles,
            'user_roles': user_roles
        }
        return render(request, 'system/users/user_detail.html', ret)


class UserInfoView(LoginRequiredMixin, View):

    """
    个人中心：个人信息查看修改和修改
    """

    def get(self, request):

        return render(request, 'system/user_info/user_info.html')

    def post(self, request):

        ret = dict(status="fail")
        user = User.objects.get(id=request.POST['id'])
        user_update_form = UserUpdateForm(request.POST, instance=user)
        if user_update_form.is_valid():
            user_update_form.save()
            ret = {"status": "success"}
        return HttpResponse(json.dumps(ret), content_type='application/json')


class PasswdChangeView(LoginRequiredMixin, View):
    """
    登陆用户修改个人密码
    """

    def get(self, request):
        ret = dict()
        user = get_object_or_404(User, pk=int(request.user.id))
        ret['user'] = user
        return render(request, 'system/user_info/passwd-change.html', ret)

    def post(self, request):

        user = get_object_or_404(User, pk=int(request.user.id))
        form = AdminPasswdChangeForm(request.POST)
        if form.is_valid():
            new_password = request.POST.get('password')
            user.set_password(new_password)
            user.save()
            ret = {'status': 'success'}
        else:
            pattern = '<li>.*?<ul class=.*?><li>(.*?)</li>'
            errors = str(form.errors)
            admin_passwd_change_form_errors = re.findall(pattern, errors)
            ret = {
                'status': 'fail',
                'admin_passwd_change_form_errors': admin_passwd_change_form_errors[0]
            }
        return HttpResponse(json.dumps(ret), content_type='application/json')


class AdminPasswdChangeForm(forms.Form):
    """
    管理员用户修改用户列表中的用户密码
    """
    # def __init__(self, *args, **kwargs):
    #     super(AdminPasswdChangeForm, self).__init__(*args, **kwargs)

    password = forms.CharField(
        required=True,
        min_length=6,
        max_length=20,
        error_messages={
            "required": u"密码不能为空"
        })

    confirm_password = forms.CharField(
        required=True,
        min_length=6,
        max_length=20,
        error_messages={
            "required": u"确认密码不能为空"
        })

    def clean(self):
        cleaned_data = super(AdminPasswdChangeForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("两次密码输入不一致")


class UserUpdateView(LoginRequiredMixin, View):

    def post(self, request):
        if 'id' in request.POST and request.POST['id']:
            user = get_object_or_404(User, pk=int(request.POST['id']))

        else:
            user = get_object_or_404(User, pk=int(request.user.id))
        user_update_form = UserUpdateForm(request.POST, instance=user)
        if user_update_form.is_valid():
            user_update_form.save()
            ret = {"status": "success"}
        else:
            ret = {"status": "fail", "message": user_update_form.errors}
        return HttpResponse(json.dumps(ret), content_type="application/json")


class PasswordChangeView(LoginRequiredMixin, View):

    def get(self, request):
        ret = dict()
        if 'id' in request.GET and request.GET['id']:
            user = get_object_or_404(User, pk=int(request.GET.get('id')))
            ret['user'] = user
        return render(request, 'system/users/passwd_change.html', ret)

    def post(self, request):
        if 'id' in request.POST and request.POST['id']:
            user = get_object_or_404(User, pk=int(request.POST['id']))
            form = PasswordChangeForm(request.POST)
            if form.is_valid():
                new_password = request.POST['password']
                user.set_password(new_password)
                user.save()
                ret = {'status': 'success'}
            else:
                pattern = '<li>.*?<ul class=.*?><li>(.*?)</li>'
                errors = str(form.errors)
                password_change_form_errors = re.findall(pattern, errors)
                ret = {
                    'status': 'fail',
                    'password_change_form_errors': password_change_form_errors[0]
                }
        return HttpResponse(json.dumps(ret), content_type='application/json')


class UserDeleteView(LoginRequiredMixin, View):
    """
    删除数据：支持删除单条记录和批量删除
    """

    def post(self, request):
        ret = dict(result=False)
        if 'id' in request.POST and request.POST['id']:
            id_list = map(int, request.POST['id'].split(','))
            User.objects.filter(id__in=id_list).delete()
            ret['result'] = True
        return HttpResponse(json.dumps(ret), content_type='application/json')


class UserEnableView(LoginRequiredMixin, View):
    """
    启用用户：单个或批量启用
    """

    def post(self, request):
        if 'id' in request.POST and request.POST['id']:
            id_nums = request.POST.get('id')
            queryset = User.objects.extra(where=["id IN(" + id_nums + ")"])
            queryset.filter(is_active=False).update(is_active=True)
            ret = {'result': 'True'}
        return HttpResponse(json.dumps(ret), content_type='application/json')


class UserDisableView(LoginRequiredMixin, View):
    """
    启用用户：单个或批量启用
    """

    def post(self, request):
        if 'id' in request.POST and request.POST['id']:
            id_nums = request.POST.get('id')
            queryset = User.objects.extra(where=["id IN(" + id_nums + ")"])
            queryset.filter(is_active=True).update(is_active=False)
            ret = {'result': 'True'}
        return HttpResponse(json.dumps(ret), content_type='application/json')