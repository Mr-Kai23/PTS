from django.urls import path

from .views import SystemView
from . import views_structure, views_user, views_menu, views_role

from django.conf.urls import url

import system.views_project as views_project
import system.views_build as views_build
import system.views_segment as views_segment
import system.views_unit_type as views_unit_type
import system.views_stations as views_stations
import system.views_subject as views_subject

app_name = 'system'

urlpatterns = [
    path('', SystemView.as_view(), name='login'),

    path('basic/structure/', views_structure.StructureView.as_view(), name='basic-structure'),
    path('basic/structure/create/', views_structure.StructureCreateView.as_view(), name='basic-structure-create'),
    path('basic/structure/list/', views_structure.StructureListView.as_view(), name='basic-structure-list'),
    path('basic/structure/delete/', views_structure.StructureDeleteView.as_view(), name='basic-structure-delete'),
    path('basic/structure/add_user/', views_structure.Structure2UserView.as_view(), name='basic-structure-add_user'),

    path('basic/user/', views_user.UserView.as_view(), name='basic-user'),
    path('basic/user/list/', views_user.UserListView.as_view(), name='basic-user-list'),
    path('basic/user/create/', views_user.UserCreateView.as_view(), name='basic-user-create'),
    path('basic/user/detail/', views_user.UserDetailView.as_view(), name='basic-user-detail'),
    path('basic/user/user_info/', views_user.UserInfoView.as_view(), name='basic-user-user_info'),
    path('basic/user/passwordchange/', views_user.PasswdChangeView.as_view(), name='basic-passwordchange'),
    path('basic/user/update/', views_user.UserUpdateView.as_view(), name='basic-user-update'),
    path('basic/user/password_change/', views_user.PasswordChangeView.as_view(), name='basic-user-password_change'),
    path('basic/user/delete/', views_user.UserDeleteView.as_view(), name='basic-user-delete'),
    path('basic/user/enable/', views_user.UserEnableView.as_view(), name='basic-user-enable'),
    path('basic/user/disable/', views_user.UserDisableView.as_view(), name='basic-user-disable'),


    path('rbac/menu/', views_menu.MenuListView.as_view(), name='rbac-menu'),
    path('rbac/menu/create/', views_menu.MenuCreateView.as_view(), name='rbac-menu-create'),
    path('rbac/menu/update/', views_menu.MenuUpdateView.as_view(), name='rbac-menu-update'),

    path('rbac/role/', views_role.RoleView.as_view(), name='rbac-role'),
    path('rbac/role/create/', views_role.RoleCreateView.as_view(), name='rbac-role-create'),
    path('rbac/role/list/', views_role.RoleListView.as_view(), name='rbac-role-list'),
    path('rbac/role/update/', views_role.RoleUpdateView.as_view(), name='rbac-role-update'),
    path('rbac/role/delete/', views_role.RoleDeleteView.as_view(), name='rbac-role-delete'),
    path('rbac/role/role2user/', views_role.Role2UserView.as_view(), name="rbac-role-role2user"),
    path('rbac/role/role2menu/', views_role.Role2MenuView.as_view(), name="rbac-role-role2menu"),
    path('rbac/role/role2menu_list/', views_role.Role2MenuListView.as_view(), name="rbac-role-role2menu_list"),

    # 专案
    url(r'^basic/project/$', views_project.ProjectView.as_view(), name='basic-project'),
    url(r'^basic/project/list/$', views_project.ProjectListView.as_view(), name='basic-project-list'),
    url(r'^basic/project/update/$', views_project.ProjectUpdateView.as_view(), name='basic-project-update'),
    url(r'^basic/project/delete/$', views_project.ProjectDeleteView.as_view(), name='basic-project-delete'),

    # 阶段
    url(r'^basic/build/$', views_build.BuildView.as_view(), name='basic-build'),
    url(r'^basic/build/list/$', views_build.BuildListView.as_view(), name='basic-build-list'),
    url(r'^basic/build/update/$', views_build.BuildUpdateView.as_view(), name='basic-build-update'),
    url(r'^basic/build/delete/$', views_build.BuildDeleteView.as_view(), name='basic-build-delete'),

    # 阶段
    url(r'^basic/segment/$', views_segment.SegmentView.as_view(), name='basic-segment'),
    url(r'^basic/segment/list/$', views_segment.SegmentListView.as_view(), name='basic-segment-list'),
    url(r'^basic/segment/update/$', views_segment.SegmentUpdateView.as_view(), name='basic-segment-update'),
    url(r'^basic/segment/delete/$', views_segment.SegmentDeleteView.as_view(), name='basic-segment-delete'),

    # 机种
    url(r'^basic/unit_type/$', views_unit_type.UnitTypeView.as_view(), name='basic-unit_type'),
    url(r'^basic/unit_type/list/$', views_unit_type.UnitTypeListView.as_view(), name='basic-unit_type-list'),
    url(r'^basic/unit_type/update/$', views_unit_type.UnitTypeUpdateView.as_view(), name='basic-unit_type-update'),
    url(r'^basic/unit_type/delete/$', views_unit_type.UnitTypeDeleteView.as_view(), name='basic-unit_type-delete'),

    # 工站
    url(r'^basic/station/$', views_stations.StationView.as_view(), name='basic-station'),
    url(r'^basic/station/list/$', views_stations.StationListView.as_view(), name='basic-station-list'),
    url(r'^basic/station/update/$', views_stations.StationUpdateView.as_view(), name='basic-station-update'),
    url(r'^basic/station/delete/$', views_stations.StationDeleteView.as_view(), name='basic-station-delete'),

    # 主旨
    url(r'^basic/subject/$', views_subject.SubjectView.as_view(), name='basic-subject'),
    url(r'^basic/subject/list/$', views_subject.SubjectListView.as_view(), name='basic-subject-list'),
    url(r'^basic/subject/update/$', views_subject.SubjectUpdateView.as_view(), name='basic-subject-update'),
    url(r'^basic/subject/delete/$', views_subject.SubjectDeleteView.as_view(), name='basic-subject-delete'),

    # 专案 和 机种 联动
    url(r'^basic/project/unit_type$', views_project.ProjectAndUnitTypeLinkView.as_view(), name='basic-project-unit_type'),
]
