import re
from django import forms
from django.contrib.auth import get_user_model
from .models import Structure, Menu

User = get_user_model()


class LoginForm(forms.Form):
    username = forms.CharField(required=True, error_messages={"requeired": "請填寫用戶名"})
    password = forms.CharField(required=True, error_messages={"requeired": "請填寫密碼"})


class StructureForm(forms.ModelForm):
    class Meta:
        model = Structure
        fields = ['type', 'name', 'parent']


class UserCreateForm(forms.ModelForm):
    password = forms.CharField(
        required=True,
        min_length=6,
        max_length=20,
        error_messages={
            "required": "密碼不能為空",
            "min_length": "密碼長度至少6位數",
        }
    )

    confirm_password = forms.CharField(
        required=True,
        min_length=6,
        max_length=20,
        error_messages={
            "required": "确认密码不能为空",
            "min_length": "密码长度最少6位数",
        }
    )

    class Meta:
        model = User
        fields = [
            'name', 'work_num', 'username', 'department', 'superior', 'project', 'mobile', 'email',
            'segment', 'account_type', 'user_type', 'is_admin', 'roles', 'password', 'remark'
        ]

        error_messages = {
            "name": {"required": "姓名不能為空"},
            "username": {"required": "用戶名不能為空"},
            "email": {"required": "郵箱不能為空"},
            "mobile": {
                "required": "手機號碼不能為空",
                "max_length": "輸入有效的手機號碼",
                "min_length": "輸入有效的手機號碼"
            }
         }

    def clean(self):
        cleaned_data = super(UserCreateForm, self).clean()
        username = cleaned_data.get("username")
        work_num = cleaned_data.get('work_num')
        # mobile = cleaned_data.get("mobile", "")
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if User.objects.filter(username=username).count():
            raise forms.ValidationError('用戶名：{}已存在'.format(username))

        if User.objects.filter(work_num=work_num).count():
            raise forms.ValidationError('工號：{}已存在'.format(work_num))

        if password != confirm_password:
            raise forms.ValidationError("兩次密碼輸入不一致")

        # if User.objects.filter(mobile=mobile).count():
        #     raise forms.ValidationError('手機號碼：{}已存在'.format(mobile))

        # REGEX_MOBILE = "^1[3578]\d{9}$|^147\d{8}$|^176\d{8}$"
        # if not re.match(REGEX_MOBILE, mobile):
        #     raise forms.ValidationError("請輸入正確的手機號碼")

        # if User.objects.filter(email=email).count():
        #     raise forms.ValidationError('邮箱：{}已存在'.format(email))


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'name', 'work_num', 'username', 'department', 'project', 'superior', 'mobile', 'email',
            'segment', 'account_type', 'user_type', 'is_admin', 'roles', 'remark'
        ]


class PasswordChangeForm(forms.Form):

    password = forms.CharField(
        required=True,
        min_length=6,
        max_length=20,
        error_messages={
            "required": u"密碼不能為空"
        })

    confirm_password = forms.CharField(
        required=True,
        min_length=6,
        max_length=20,
        error_messages={
            "required": u"確認密碼不能為空"
        })

    def clean(self):
        cleaned_data = super(PasswordChangeForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("兩次密碼輸入不一致")


class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = '__all__'
