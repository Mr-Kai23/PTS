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

        # 所有專案
        res['projects'] = Project.objects.all()
        # 所有段別
        res['segments'] = Segment.objects.all()

        menu = Menu.get_menu_by_request_url(url=self.request.path_info)
        if menu is not None:
            res.update(menu)

        return render(request, 'system/Stations/Stations_List.html', res)

    """
    @Author  :   Daniel                
    @Time    :   2020-6-2 16:34
    @Desc    :   工站导入
    """
    def post(self, request):

        """
        工站上傳
        :param request:
        :return: 返回渲染上传信息页面
        """
        msg = ''

        correct_stations = []  # 上傳成功的工站
        error_segment = []  # 段別錯誤的工站
        repeat_stations = []  # 重複上傳工站

        file = request.FILES['file']

        # 過濾函數，用於過濾為空的值
        def not_null(x):
            if x:
                return True

        if file.name.endswith(".xlsx") or file.name.endswith(".xls"):  # 判断上传文件是否为表格
            # df = pd.read_excel(file, skiprows=3, keep_default_na=False, index_col=0)
            # 讀取excel
            excel = pd.ExcelFile(file)

            # 所有 sheet
            sheets = excel.sheet_names

            # 列名
            column_list = ['#', 'Stage', 'Test Station name']

            for index, sheet in enumerate(sheets):
                df = excel.parse(sheets[index], skiprows=3, keep_default_na=False, index_col=0)

                # 工站專案
                project = sheets[index].split()[0]
                # 獲取所有段別
                segments = list(Segment.objects.values_list('segment', flat=True))

                if list(df.columns) == column_list:

                    # 用户部门、專案
                    department = request.user.department.name
                    # 工站列表，存放創建的實例
                    stations = []

                    # 上傳的 segment
                    upload_segment = list(filter(not_null, df.Stage))

                    # 臨時存放段別
                    tem_segment = ''
                    # 讀取工單數據
                    for i in range(len(df)):
                        df_list = list(df.values)[i]

                        if upload_segment in segments:
                            # 如果段別有值，將段別賦值給 臨時段別
                            if df_list[1]:
                                segment = df_list[1]
                                tem_segment = segment
                            else:
                                segment = tem_segment
                                df_list[1] = tem_segment

                            # 獲取或創建工站
                            station, create = Stations.objects.get_or_create(project=project, department=department,
                                                                             station=df_list[2], segment=segment)
                            # 如果為創建
                            if create:
                                stations.append(station)
                                # 正確上傳的工站
                                correct_stations.append(df_list)

                            else:
                                # 重複上傳工站
                                repeat_stations.append(df_list)

                        else:
                            error_segment.append(df_list)

                    # 如果沒有錯誤工站信息
                    if not error_segment:
                        # 創建工站
                        Stations.objects.bulk_create(stations)
                        msg = '工站上傳！！'

                else:
                    msg = '請選擇正確的文件！！'

        return render(request, 'system/Stations/Stations_upload_info.html',
                      {"msg": msg, "correct_stations": correct_stations, 'repeat_stations': repeat_stations,
                       "error_segment": error_segment})


class StationListView(LoginRequiredMixin, View):
    """
    工站详情
    """
    def get(self, request):
        # 用戶部門
        department = request.user.department.name

        fields = ['id', 'project', 'department', 'segment', 'station']
        searchFields = ['project', 'station', 'segment', 'department']  # 与数据库字段一致

        # 此处的if语句有很大作用，如remark中数据为None,可通过if request.GET.get('')将传入为''的不将条件放入进去
        filters = {i + '__icontains': request.GET.get(i, '') for i in searchFields if request.GET.get(i, '')}

        stations = Stations.objects.filter(**filters, department=department).values(*fields)

        res = dict(data=list(stations))

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


