from django.conf.urls import url
from django.urls import path

from app_process.views import OrderView, get_upload_module
import app_process.views_workflow as views_workflow
import app_process.views_recept as views_recept

# import app_process.views as views
from system.views import SystemView

app_name = 'app_process'

urlpatterns = [
    path('', OrderView.as_view(), name='pmslogin'),


    # 工单路由
    url(r'^order/workflow/$', views_workflow.WorkFlowView.as_view(), name='order-workflow'),
    url(r'^order/workflow/list$', views_workflow.WorkFlowListView.as_view(), name='order-workflow-list'),
    url(r'^order/workflow/create$', views_workflow.WorkFlowCreateView.as_view(), name='order-workflow-create'),
    url(r'^order/workflow/delete$', views_workflow.WorkFlowDeleteView.as_view(), name='order-workflow-delete'),
    url(r'^order/workflow/detail$', views_workflow.WorkFlowDetailView.as_view(), name='order-workflow-detail'),

    # 待接收工單路由
    url(r'^order/receive/(?P<receive_id>[0-9]{1})/$', views_recept.ReceptView.as_view(), name='order-receive'),
    url(r'^order/receive/list/$', views_recept.ReceptListView.as_view(), name='order-receive-list'),
    url(r'^order/receive/accept/$', views_recept.WorkFlowReceiveView.as_view(), name='order-receive-accept'),
    url(r'^order/receive/detail$', views_recept.ReceptDetailView.as_view(), name='order-receive-detail'),

    # 上传模板下载
    url(r'^download/(?P<download_id>[0-9]{1})/$', get_upload_module, name='download')


]
