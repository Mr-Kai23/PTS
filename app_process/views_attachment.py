# ======================================================
# @Author  :   Daniel                 
# @Time    :   2020-03
# @Desc    :   工單處理視圖
# ======================================================

import json, time, datetime, re

from django.core.files import File
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, FileResponse
from django.shortcuts import render, get_object_or_404
from django.utils.http import urlquote
from django.views import View
from django.views.decorators.cache import cache_page

from app_process.forms import WorkflowForm
from app_process.models import Segment, OrderInfo, Project, UnitType, Stations, Subject, Attachment
from system.models import UserInfo
from system.mixin import LoginRequiredMixin
from system.models import Menu
import pandas as pd
from .views import create_workflow, send_email_message
from django.core.cache import cache


class AttachmentView(LoginRequiredMixin, View):
    """
    附件视图
    """

    def get(self, request):
        res = dict()

        menu = Menu.get_menu_by_request_url(url=self.request.path_info)
        if menu is not None:
            res.update(menu)

        # 流程ID
        res['workflow_id'] = request.GET['id']

        return render(request, 'process/Attachment/Attachment_List.html', res)


class AttachmentListView(LoginRequiredMixin, View):
    """
    附件显示视图
    """
    def get(self, request):

        # 前端要显示的属性
        fields = ['id', 'attachment']

        # 接收者
        if request.user.account_type == 1:
            # 獲取父流程的id,拿到對應的附件
            parent_id = OrderInfo.objects.get(pk=int(request.GET['id'])).parent_id
            # 對用流程的附件
            attachments = Attachment.objects.filter(workflow=parent_id).values(*fields).order_by('-id')
        else:
            # 對用流程的附件
            attachments = Attachment.objects.filter(workflow=int(request.GET['id'])).values(*fields).order_by('-id')

        # 只顯示文件名部分
        for attachment in attachments:
            attachment['path'] = '/'.join(attachment['attachment'].split('/')[:4])
            attachment['attachment'] = attachment['attachment'].split('/')[-1]

        res = dict(data=list(attachments))

        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')


class AttachmentCreateView(LoginRequiredMixin, View):
    """
    附件創建视图
    """

    def get(self, request):
        """
        創建和更新頁面渲染數據
        :param request: 请求对象
        :return: 渲染创建页面
        """
        res = dict()

        # 流程ID
        res['workflow_id'] = request.GET['workflow_id']

        return render(request, 'process/Attachment/Attachment_Create.html', res)

    def post(self, request):
        res = dict(result=False)

        # 上傳附件
        Attachment.objects.create(workflow=int(request.POST['id']), attachment=request.FILES['attach_excel'])

        res['result'] = True

        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')


class AttachmentDeleteView(LoginRequiredMixin, View):
    """
    附件刪除視圖
    """

    def post(self, request):
        res = dict(result=False)

        # 判断获取前端传过来的要删除的id
        if 'id' in request.POST and request.POST.get('id'):
            ids = map(int, request.POST.get('id').split(','))

            Attachment.objects.filter(id__in=ids).delete()

            res['result'] = True

        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')


# class AttachmentDownloadView(LoginRequiredMixin, View):
#     """
#     附件文件下載
#     :param request: 請求對象
#     :return:
#     """
#     def get(self, request):
#
#         res = dict(result=False)
#         attachment = Attachment.objects.get(pk=int(request.GET['id']))
#
#         file = open(attachment.attachment.path, 'rb')
#
#         response = FileResponse(file)
#         response = HttpResponse(attachment.attachment, content_type='text/plain')
#         response['Content-Disposition'] = "attachment;filename=%s" % urlquote(attachment.attachment.name)
#         res['result'] = True
#
#         return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')

