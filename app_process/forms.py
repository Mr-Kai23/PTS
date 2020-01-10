# @Time   : 2018/10/17 23:13
# @Author : RobbieHan
# @File   : forms.py

import re
from django import forms
from django.contrib.auth import get_user_model
from .models import Project, Build


class ProjectCreateForm(forms.ModelForm):
    """
    专案表
    """
    class Meta:
        model = Project
        fields = '__all__'


class BuildCreateForm(forms.ModelForm):
    """
    階段表
    """
    class Meta:
        model = Build
        fields = '__all__'
