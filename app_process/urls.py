from django.conf.urls import url
from django.urls import path

from app_process.views import OrderView
from app_process.views_workflow import WorkFlowView, WorkFlowListView
from system.views import SystemView

app_name = 'app_process'

urlpatterns = [
    path('', OrderView.as_view(), name='login'),

    # 工单路由
    url(r'^workflow$', WorkFlowView.as_view(), name='workflow'),
    url(r'^workflow/list$', WorkFlowListView.as_view(), name='workflow-list'),
    # url(r'^workflow/delete$', )

]