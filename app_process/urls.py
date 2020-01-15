from django.urls import path

from app_process.views import OrderView
from system.views import SystemView

app_name = 'app_process'

urlpatterns = [
    path('', OrderView.as_view(), name='login'),
]