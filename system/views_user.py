# @Time   : 2018/10/16 23:11
# @Author : RobbieHan
# @File   : views_user.py

import re
import json
import pandas as pd

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
from django.core.serializers.json import DjangoJSONEncoder
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
            user1 = User.objects.filter(username=user_name, password=pass_word)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(redirect_to)
                else:
                    ret['msg'] = '用户未激活！'
            elif user1 is not None:
                if user1[0].is_active:
                    login(request, user1[0])
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
        return HttpResponseRedirect('/board')


class UserView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
    template_name = 'system/users/user.html'

    def post(self, request):
        msg = ''

        correct_user = []  # 上傳成功的用戶
        error_department = []  # 部門錯誤的用戶
        error_project = []  # 專案錯誤的用戶
        error_segment = []  # 段別錯誤的用戶

        file = request.FILES['file']

        # 獲取所有部門、專案和段別
        projects = set(Project.objects.values_list('project', flat=True))
        departments = list(Structure.objects.values_list('name', flat=True))
        segments = list(Segment.objects.values_list('segment', flat=True))

        if file.name.endswith(".xlsx") or file.name.endswith(".xls"):  # 判断上传文件是否为表格
            df = pd.read_excel(file, keep_default_na=False)

            column_list = ['姓名', '工號', '用戶名', '郵箱', '手機', '部門', '上級DRI', '專案', '段別', '備註', '賬號類型', 'DRI', '所屬角色组']
            if list(df.columns) == column_list:
                # 循環df讀取數據
                for i in range(len(df)):

                    # try:
                        # 如果存在部門和專案
                        # assert str(df.loc[i, '部門']) in departments, '第' + str(i+1) + '行 部門 信息不存在！！'
                        # assert set(str(df.loc[i, '專案']).split('/')).issubset(projects), '第' + str(i+1) + '行'+str(df.loc[i, '專案'])+'專案 信息不存在！！'
                        # assert not str(df.loc[i, '段別']) or str(df.loc[i, '段別']) in segments or str(df.loc[i, '段別']).lower() == 'all', '第' + str(i+1) + '行 段別 信息不存在！！'

                        # defaults = {
                        #     'name': str(df.loc[i, '姓名']), 'mobile': str(df.loc[i, '手機']),
                        #     'email': str(df.loc[i, '郵箱']), 'username': str(df.loc[i, '工號']),
                        #     'password': 123456, 'remark': str(df.loc[i, '備註']),
                        #     'department': Structure.objects.get(name=str(df.loc[i, '部門'])),
                        #     'project': str(df.loc[i, '專案']), 'segment': str(df.loc[i, '段別']),
                        #     'account_type': 1 if str(df.loc[i, '賬號類型']) == '接收者' else 0,
                        #     'superior_id': '' if str(df.loc[i, '上級DRI']) == '' else User.objects.get(name=str(df.loc[i, '上級DRI'])),
                        #     'is_admin': True if str(df.loc[i, 'DRI']) == '是' else False,
                        #     'roles': Role.objects.get(name=str(df.loc[i, '所屬角色组']))
                        # }
                        #
                        # User.objects.update_or_create(work_num=str(df.loc[i, '工號']), defaults=defaults)

                    if str(df.loc[i, '部門']) in departments:
                        if set(str(df.loc[i, '專案']).split('/')).issubset(projects):
                            if not str(df.loc[i, '段別']) or str(df.loc[i, '段別']) in segments or str(df.loc[i, '段別']).lower() == 'all':

                                # 判断是否存在该用户
                                if User.objects.filter(work_num=str(df.loc[i, '工號'])):
                                    user = get_object_or_404(User, work_num=str(df.loc[i, '工號']))
                                else:
                                    user = User()

                                user.name = str(df.loc[i, '姓名'])
                                user.username = str(df.loc[i, '工號'])
                                user.work_num = str(df.loc[i, '工號'])
                                user.mobile = str(df.loc[i, '手機'])
                                user.email = str(df.loc[i, '郵箱'])
                                user.project = str(df.loc[i, '專案'])
                                user.segment = str(df.loc[i, '段別'])
                                user.password = 123456
                                user.remark = str(df.loc[i, '備註'])
                                user.department = Structure.objects.get(name=str(df.loc[i, '部門']))
                                user.account_type = 1 if str(df.loc[i, '賬號類型']) == '接收者' else 0
                                user.superior_id = '' if str(df.loc[i, '上級DRI']) == '' else User.objects.get(name=str(df.loc[i, '上級DRI'])).id
                                user.is_admin = True if str(df.loc[i, 'DRI']) == '是' else False
                                user.save()
                                # 多對多字段添加關聯
                                user.roles.add(Role.objects.get(name=str(df.loc[i, '所屬角色组'])))

                                correct_user.append(df.loc[i].tolist())


                            else:
                                msg = '用戶信息有誤！！'
                                error_department.append(df.loc[i].tolist())
                                break
                        else:
                            msg = '用戶信息有誤！！'
                            error_project.append(df.loc[i].tolist())
                            break

                # except Exception as e:
                #     msg = str(e)
                #     return render(request, 'system/users/User_upload_info.html', {'msg': msg})
                    else:
                        msg = '用戶信息有誤！！'
                        error_segment.append(df.loc[i].tolist())
                        break

            if not error_department and not error_project and not error_segment:
                msg = '上傳成功！！'

        else:
            msg = '請選擇正確的文件！！'

        return render(request, 'system/users/User_upload_info.html',
                      {"msg": msg, "correct_user": correct_user, "error_department": error_department, "error_project": error_project, "error_segment": error_segment})


class UserListView(LoginRequiredMixin, View):
    def get(self, request):
        fields = ['id', 'work_num', 'name', 'mobile', 'email', 'department__name', 'project', 'segment', 'account_type',
                  'is_admin', 'remark']
        filters = dict()
        if 'select' in request.GET and request.GET['select']:
            filters['is_active'] = request.GET['select']

        users = User.objects.filter(**filters).values(*fields).order_by('id')

        # 更新前端显示为choice文字显示
        for user in users:
            user['account_type'] = User.objects.get(id=user['id']).get_account_type_display()

        ret = dict(data=list(users))
        return HttpResponse(json.dumps(ret), content_type='application/json')


class UserCreateView(LoginRequiredMixin, View):
    """
    添加用户
    """

    def get(self, request):
        users = User.objects.exclude(username='admin')
        superiors = User.objects.filter(is_admin=True).values()
        structures = Structure.objects.values()
        projects = Project.objects.values()
        segments = Segment.objects.values()
        roles = Role.objects.values()

        ret = {
            'users': users,
            'superiors': superiors,
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
        superiors = User.objects.filter(is_admin=True).values()
        structures = Structure.objects.exclude(name=user.department.name).values()
        segments = Segment.objects.exclude(segment=user.segment).values()
        projects = Project.objects.exclude(project=user.project).values()
        roles = Role.objects.values()
        user_roles = user.roles.values()
        ret = {
            'user': user,
            'superiors': superiors,
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