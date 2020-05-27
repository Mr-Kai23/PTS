import json
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder

from custom import BreadcrumbMixin
from app_process.forms import StationsForm
from app_process.models import Project, Build, Segment, UnitType, Stations
from system.mixin import LoginRequiredMixin
from system.models import Structure, Menu
import pandas as pd


class StationView(LoginRequiredMixin, View):
    """
    机种
    """
    def get(self, request):
        res = dict()

        menu = Menu.get_menu_by_request_url(url=self.request.path_info)
        if menu is not None:
            res.update(menu)

        return render(request, 'system/Stations/Stations_List.html', res)

    """
    @Author  :   Daniel                
    @Time    :   2020-5-28 10:35
    @Desc    :   工站导入
    """
    def post(self, request):

        """
        工單導入
        :param request:
        :return: 返回渲染上传信息页面
        """
        msg = ''

        correct_stations = []  # 上傳成功的工單
        error_department = []  # 部門錯誤的工單

        file = request.FILES['file']

        if file.name.endswith(".xlsx") or file.name.endswith(".xls"):  # 判断上传文件是否为表格
            df = pd.read_excel(file, keep_default_na=False)

            column_list = ['部門', '工站']

            if list(df.columns) == column_list:

                # 用户部门、專案
                department = request.user.department.name
                # 工站列表，存放創建的實例
                stations = []

                # 讀取工單數據
                for i in range(len(df)):

                    if department == df.loc[i, '部門']:

                        stations.append(Stations(department=df.loc[i, '部門'], station=df.loc[i, '工站']))

                        # 正確上傳的工站
                        correct_stations.append(df.loc[i].tolist())

                    else:
                        msg = '請勿上傳其他部門工站！！'
                        error_department.append(df.loc[i].tolist())
                        break

                if not error_department:
                    # 創建工站
                    Stations.objects.bulk_create(stations)
                    msg = '工站上傳！！'

            else:
                msg = '請選擇正確的文件！！'

        return render(request, 'system/Stations/Stations_upload_info.html',
                      {"msg": msg, "correct_stations": correct_stations, "error_department": error_department})


class StationListView(LoginRequiredMixin, View):
    """
    工站详情
    """
    def get(self, request):

        fields = ['id', 'department', 'station']
        searchFields = ['station', 'department']  # 与数据库字段一致
        filters = {i + '__icontains': request.GET.get(i, '') for i in searchFields if request.GET.get(i, '')}  # 此处的if语句有很大作用，如remark中数据为None,可通过if request.GET.get('')将传入为''的不将条件放入进去

        res = dict(data=list(Stations.objects.filter(**filters).values(*fields)))

        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')


class StationUpdateView(LoginRequiredMixin, View):
    """
    新增 和 修改
    """
    # 注意：编辑页面中type=hidden隐藏的id，目的就是为了标识是编辑/增加操作
    def get(self, request):
        res = dict()
        if 'id' in request.GET and request.GET['id']:
            station = get_object_or_404(Stations, pk=request.GET.get('id'))
            res['station'] = station
        else:
            station = Stations.objects.all()
            res['station'] = station

        return render(request, 'system/Stations/Stations_Update.html', res)

    def post(self, request):
        res = dict(result=False)
        if 'id' in request.POST and request.POST['id']:  # id的存在，就是为了说明是新增数据还是编辑数据
            station = get_object_or_404(Stations, pk=request.POST.get('id'))
        else:
            station = Stations()

        station_create_form = StationsForm(request.POST, instance=station)

        if station_create_form.is_valid():
            station_create_form.save()
            res['result'] = True

        return HttpResponse(json.dumps(res), content_type='application/json')


class StationDeleteView(LoginRequiredMixin, View):
    """
    删除视图
    """
    def post(self, request):
        res = dict(result=False)
        id = list(map(int, request.POST.get('id').split(',')))[0]

        if 'id' in request.POST and request.POST['id']:
            id_list = map(int, request.POST.get('id').split(','))
            Stations.objects.filter(id__in=id_list).delete()
            res['result'] = True

        return HttpResponse(json.dumps(res), content_type='application/json')


