from django.conf.urls import url
from django.urls import path

from app_process.views import OrderView
import app_process.views_workflow as views_workflow
from system.views import SystemView

app_name = 'app_process'

urlpatterns = [
    path('', OrderView.as_view(), name='pmslogin'),

    # 工单路由
    url(r'^order/workflow/$', views_workflow.WorkFlowView.as_view(), name='order-workflow'),
    url(r'^order/workflow/list$', views_workflow.WorkFlowListView.as_view(), name='order-workflow-list'),
    url(r'^order/workflow/create$', views_workflow.WorkFlowCreateView.as_view(), name='order-workflow-create'),
    url(r'^order/workflow/delete$', views_workflow.WorkFlowDeleteView.as_view(), name='order-workflow-delete'),
    url(r'^order/workflow/detail$', views_workflow.WorkFlowDetailView.as_view(), name='order-workflow-detail')

]