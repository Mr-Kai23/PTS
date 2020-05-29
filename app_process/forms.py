# @Time   : 2018/10/17 23:13
# @Author : RobbieHan
# @File   : forms.py

import re
from django import forms
from django.contrib.auth import get_user_model
from .models import Project, Build, Segment, UnitType, OrderInfo, Stations, Subject, ExceptionContact


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


class SegmentCreateForm(forms.ModelForm):
    """
    段别表
    """
    class Meta:
        model = Segment
        fields = '__all__'


class UnitTypeCreateForm(forms.ModelForm):
    """
    机种表
    """
    class Meta:
        model = UnitType
        fields = '__all__'


class WorkflowForm(forms.ModelForm):
    """
    工单表
    """
    class Meta:
        model = OrderInfo
        fields = '__all__'


class RecipientForm(forms.ModelForm):
    """
    待接收工单表
    """
    class Meta:
        model = OrderInfo
        fields = '__all__'


class StationsForm(forms.ModelForm):
    """
    工单表
    """
    class Meta:
        model = Stations
        fields = '__all__'


class SubjectForm(forms.ModelForm):
    """
    工单表
    """
    class Meta:
        model = Subject
        fields = '__all__'


class ContactForm(forms.ModelForm):
    """
    联系人表
    """
    class Meta:
        model = ExceptionContact
        fields = '__all__'