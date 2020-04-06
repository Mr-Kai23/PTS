from django.conf.urls import url
from django.urls import path

from app_process.views import OrderView
import app_process.views_workflow as views_workflow
import app_process.views_recept as views_recept
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
    # url(r'^order/workflow/hello$', views_workflow.HelloView.as_view(), name='hello-detail'),

    #待接收工單路由
    url(r'^order/receve/$', views_recept.ReceptView.as_view(), name='order-receve'),
    url(r'^order/receve/list/$', views_recept.ReceptListView.as_view(), name='order-receve-list'),
    url(r'^order/receve/create/$', views_recept.ReceptCreateView.as_view(), name='order-receve-create'),
    url(r'^order/receve/delete/$', views_recept.ReceptDeleteView.as_view(), name='order-receve-delete'),
    # url(r'^order/workflow/detail$', views_workflow.WorkFlowDetailView.as_view(), name='order-workflow-detail'),
]
