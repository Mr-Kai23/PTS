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
from app_process.models import OrderInfo, Project, Segment, Attachment
from datetime import datetime
from django.db.models import Count, Q
User = get_user_model()


class IndexView(LoginRequiredMixin, View):

    def get(self, request):
        """
        流程主頁面數據展示
        :param request:
        :return: 渲染主頁面
        """
        # 接收者
        user = request.user.name
        orders = OrderInfo.objects.all()

        # 圖片
        attachments = Attachment.objects.filter(workflow__isnull=True)

        if attachments:
            attachment = attachments.last().attachment
        else:
            attachment = ''

        res = {
            'created': orders.filter(publisher=user, is_parent=True).count(),
            'commission': orders.filter(receiver=user, receive_status=0).count(),  # 待辦事項
            'finished': orders.filter(receiver=user, receive_status=1, status=1).count(),
            'image': attachment
        }
        return render(request, 'process/order_index.html', res)

    # def get(self, request):
    #     """
    #     用于渲染看板页面
    #     :param request:
    #     :return:
    #     """
    #
    #     # 用于存放每个段别下的工单
    #     segment_orders = []
    #     # 用存放每个段别下每种执行状态下的工单
    #     un_accept_list = []
    #     un_product_list = []
    #     Ongoing_list = []
    #     Closed_list = []
    #
    #     # 只看未被刪除的子流程
    #     # 父流程只是給發佈者看，方便修改
    #     orders = OrderInfo.objects.filter(is_parent=False, deleted=False)
    #
    #     # 獲取所有专案
    #     projects = Project.objects.all()
    #
    #     # 获取所有段别下的工单数量
    #     segments = Segment.objects.exclude(segment__icontains='all').order_by('id')
    #
    #     for segment in segments:
    #         # 获取每个段别下的工单
    #         segment_orders.append(orders.filter(segment=segment).all())
    #         # 获取每个段别下的未接收的工单
    #         un_accept_list.append(orders.filter(receive_status=0, segment=segment).count())
    #         # 获取每个段别下的未投产的工单
    #         un_product_list.append(orders.filter(status=0, segment=segment).count())
    #         # 获取每个段别下的Ongoing的工单
    #         Ongoing_list.append(orders.filter(status=1, segment=segment).count())
    #         # 获取每个段别下的Closed的工单
    #         Closed_list.append(orders.filter(status=2, segment=segment).count())
    #
    #     # 用于echarts显示
    #     res = {
    #         'un_receive': orders.filter(receive_status=0).count(),  # 待接收工单数量
    #         'un_product': orders.filter(status=0).count(),  # 未投产工单数量
    #         'ongoing': orders.filter(status=1).count(),  # 进行中
    #         'closed': orders.filter(status=2).count(),  # 已完成
    #         'segments': segments,
    #         'projects': projects,
    #         'segment_orders': segment_orders,
    #         'un_accept_list': un_accept_list,
    #         'un_product_list': un_product_list,
    #         'Ongoing_list': Ongoing_list,
    #         'Closed_list': Closed_list,
    #     }
    #
    #     return render(request, 'process/Index.html', res)


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
        """
        用户批量上传
        :param request:
        :return: 返回渲染上传信息页面
        """
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

            column_list = ['姓名', '工號', '用戶名', '郵箱', '手機', '部門', '上級', '專案', '段別', '備註', '賬號類型',
                           '用戶類型', '所屬角色组']
            if list(df.columns) == column_list:
                # 循環df讀取數據
                for i in range(len(df)):
                    """
                    @Author  :   Daniel                
                    @Time    :   2020-5-15 Update
                    @Desc    :   用户上传信息核验，部门、专案和段别是否有效
                    """
                    if str(df.loc[i, '部門']) in departments:
                        if set(re.split(r'[/|，|, |\n]\s*', str(df.loc[i, '專案']))).issubset(projects):
                            if not str(df.loc[i, '段別']) or str(df.loc[i, '段別']) in segments or str(df.loc[i, '段別']).lower() == 'all':

                                # 判断是否存在该用户
                                if User.objects.filter(work_num=str(df.loc[i, '工號'])):
                                    user = get_object_or_404(User, work_num=str(df.loc[i, '工號']))
                                else:
                                    user = User()
                                    user.password = 123456

                                    user.name = str(df.loc[i, '姓名'])
                                    user.username = str(df.loc[i, '工號'])
                                    user.work_num = str(df.loc[i, '工號'])

                                user.mobile = str(df.loc[i, '手機'])
                                user.email = str(df.loc[i, '郵箱'])
                                user.project = str(df.loc[i, '專案'])
                                user.segment = None if pd.isnull(str(df.loc[i, '段別'])) or str(df.loc[i, '段別']) == 'All' else str(df.loc[i, '段別'])
                                user.remark = str(df.loc[i, '備註'])
                                user.department = Structure.objects.get(name=str(df.loc[i, '部門']))
                                user.account_type = 1 if str(df.loc[i, '賬號類型']) == '接收者' else 0

                                # 如果用户没有上级，则为空
                                user.superior_id = None if str(df.loc[i, '上級']) == '' else User.objects.get(name=str(df.loc[i, '上級'])).id

                                # 用戶類型
                                if str(df.loc[i, '用戶類型']) == '副線長':
                                    user.user_type = 0
                                elif str(df.loc[i, '用戶類型']) == '線長':
                                    user.user_type = 1
                                elif str(df.loc[i, '用戶類型']) == '專案主管':
                                    user.user_type = 2
                                else:
                                    user.user_type = None

                                # 如果用戶是發佈者，沒有上級時為 admin；用戶為接收者，線長和專案主管為 admin
                                if (str(df.loc[i, '賬號類型']) == '發佈者' and pd.isnull(str(df.loc[i, '上級']))) \
                                        or (str(df.loc[i, '賬號類型']) == '接收者' and (str(df.loc[i, '用戶類型']) == '線長' or str(df.loc[i, '用戶類型']) == '專案主管')):
                                    user.is_admin = True

                                user.save()
                                # 多對多字段添加關聯，用户权限添加
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
        if 'name' in request.GET and request.GET['name']:
            filters['name__icontains'] = request.GET['name']

        # 用户部门
        department = request.user.department

        users = User.objects.filter(**filters, department=department).values(*fields).order_by('id')

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
        # 获取本部门的所有 admin 用户
        superiors = User.objects.filter(department=request.user.department, is_admin=True).values()
        structures = Structure.objects.values()
        projects = Project.objects.values()
        segments = Segment.objects.values()
        roles = Role.objects.values()

        ret = {
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
            # 如果用户为专案主管或线长，则 is_admin True
            if user_create_form.cleaned_data['user_type'] == 1 or user_create_form.cleaned_data['user_type'] == 2:
                new_user.is_admin = True
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
        # users = User.objects.exclude(Q(id=int(request.GET['id'])) | Q(username='admin'))

        # 获取被修改用户部门的 admin 用户
        users = User.objects.filter(department=user.department, account_type=user.account_type, is_admin=True)
        if user.user_type == 0:
            # 获取被修改用户部门的 admin 用户
            superiors = users.filter(user_type=1)
        else:
            superiors = users.filter(user_type=2)

        structures = Structure.objects.values()
        segments = Segment.objects.values()
        projects = Project.objects.values()
        roles = Role.objects.values()
        user_roles = user.roles.values()
        ret = {
            'user': user,
            'superiors': superiors,
            'structures': structures,
            'projects': projects,
            'segments': segments,
            # 'users': users,
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
            # 当用户为接收者时，用户 段别、类型 为空
            if user_update_form.cleaned_data['account_type'] == 0:
                user.segment = ''
                user.user_type = None
                user_update_form.cleaned_data['user_type'] = ''
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