from django.conf.urls import url
from django.urls import path

from app_process.views import OrderView, get_upload_module
import app_process.views_workflow as views_workflow
import app_process.views_recept as views_recept
import app_process.views_deleted as views_deleted
import app_process.views_contacts as views_contacts
import app_process.views_attachment as views_attachment

# import app_process.views as views
from system.views import SystemView

app_name = 'app_process'

urlpatterns = [
    path('', OrderView.as_view(), name='pmslogin'),


    # 流程路由
    url(r'^order/workflow/$', views_workflow.WorkFlowView.as_view(), name='order-workflow'),
    url(r'^order/workflow/list/$', views_workflow.WorkFlowListView.as_view(), name='order-workflow-list'),
    url(r'^order/workflow/create/$', views_workflow.WorkFlowCreateView.as_view(), name='order-workflow-create'),
    url(r'^order/workflow/delete/$', views_workflow.WorkFlowDeleteView.as_view(), name='order-workflow-delete'),
    url(r'^order/workflow/detail/$', views_workflow.WorkFlowDetailView.as_view(), name='order-workflow-detail'),

    # 待接收流程路由
    url(r'^order/receive/(?P<receive_id>[0-9]{1})/$', views_recept.ReceptView.as_view(), name='order-receive'),
    url(r'^order/receive/list/$', views_recept.ReceptListView.as_view(), name='order-receive-list'),
    url(r'^order/receive/accept/$', views_recept.WorkFlowReceiveView.as_view(), name='order-receive-accept'),
    url(r'^order/receive/detail/$', views_recept.ReceptDetailView.as_view(), name='order-receive-detail'),

    # 已刪除流程路由
    url(r'^order/deleted/$', views_deleted.DeletedView.as_view(), name='order-deleted'),
    url(r'^order/deleted/list/$', views_deleted.DeletedListView.as_view(), name='order-deleted-list'),
    url(r'^order/receive/withdraw/$', views_deleted.DeletedWithdrawView.as_view(), name='order-deleted-withdraw'),
    url(r'^order/deleted/detail/$', views_deleted.DeletedDetailView.as_view(), name='order-deleted-detail'),

    # 我的待辦流程數提醒
    url(r'^order/message/$', views_recept.MessageView.as_view(), name='order-message'),

    # 上传模板下载
    url(r'^download/(?P<download_id>[0-9]{1})/$', get_upload_module, name='download'),

    # 段別異常聯繫人路由
    url(r'^order/contact/$', views_contacts.ContactView.as_view(), name='order-contact'),
    url(r'^order/contact/list/$', views_contacts.ContactListView.as_view(), name='order-contact-list'),
    url(r'^order/contact/create/$', views_contacts.ContactCreateView.as_view(), name='order-contact-create'),
    url(r'^order/contact/delete/$', views_contacts.ContactDeleteView.as_view(), name='order-contact-delete'),

    # 段別異常聯繫人路由
    url(r'^order/attach/$', views_attachment.AttachmentView.as_view(), name='order-attach'),
    url(r'^order/attach/list/$', views_attachment.AttachmentListView.as_view(), name='order-attach-list'),
    url(r'^order/attach/create/$', views_attachment.AttachmentCreateView.as_view(), name='order-attach-create'),
    url(r'^order/attach/delete/$', views_attachment.AttachmentDeleteView.as_view(), name='order-attach-delete'),

    # SN上傳
    url(r'^order/import/$', views_workflow.WorkflowSnImport.as_view(), name='order-import'),

]
