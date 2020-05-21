"""PMS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include

from app_process.views import BoardView, BoardListView
from system.views_user import IndexView, LoginView, LogoutView
from django.conf.urls.static import static
from PMS.settings import *

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', IndexView.as_view(), name='pmsLogin'),
    # path('', SystemView.as_view(), name='login'),
    path('board/', BoardView.as_view(), name='board'),
    path('board/list/', BoardListView.as_view(), name='board-list'),
    # 登录、登出
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # 系统管理
    path('system/', include('system.urls', namespace='system')),

    # process
    path('process/', include('app_process.urls', namespace='process')),

]

# ] + static(STATIC_URL, document_root=STATIC_ROOT)
