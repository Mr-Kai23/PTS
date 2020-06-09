# ======================================================
# @Author  :   Daniel                 
# @Time    :   2020-03
# @Desc    :   工單處理視圖
# ======================================================

import json, time, datetime, re

from django.core.files import File
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, FileResponse
from django.shortcuts import render, get_object_or_404
from django.utils.http import urlquote
from django.views import View
from django.views.decorators.cache import cache_page

from app_process.forms import WorkflowForm
from app_process.models import Segment, OrderInfo, Project, UnitType, Stations, Subject, Attachment
from system.models import UserInfo
from system.mixin import LoginRequiredMixin
from system.models import Menu
import pandas as pd
from .views import create_workflow, send_email_message
from django.core.cache import cache


class WorkFlowView(LoginRequiredMixin, View):
    """
    流程视图
    """

    def get(self, request):
        res = dict()

        pattern = re.compile(r'[/|，|, |\n]\s*')

        # 用戶部門
        department = request.user.department.name

        # 用戶專案
        projects = pattern.split(request.user.project)
        res['projects'] = projects
        # 段别
        res['segments'] = pattern.split(request.user.segment)
        # 機種
        res['unit_types'] = UnitType.objects.filter(project__in=projects)

        # 如果部門為 RF 或 TDL 只能拿自己部門的工站和主旨
        if department in ['RF', 'TDL']:
            # 工站
            res['stations'] = Stations.objects.filter(department=department)
            # 所有主旨
            res['subjects'] = Subject.objects.filter(department=department)
        else:
            # 工站
            res['stations'] = Stations.objects.all()
            # 所有主旨
            res['subjects'] = Subject.objects.all()

        menu = Menu.get_menu_by_request_url(url=self.request.path_info)
        if menu is not None:
            res.update(menu)

        return render(request, 'process/WorkFlow/WorkFlow_List.html', res)

    """
    @Author  :   Daniel                
    @Time    :   2020-5-20 Update
    @Desc    :   工单导入
    """

    def post(self, request):

        """
        工單導入
        :param request:
        :return: 返回渲染上传信息页面
        """
        msg = ''

        correct_workflow = []  # 上傳成功的流程
        error_department = []  # 部門錯誤的流程
        error_project = []  # 專案錯誤的流程
        error_publisher = []  # 段別錯誤的流程
        error_subject = []  # 主旨錯誤的流程
        error_station = []  # 工站錯誤的流程

        file = request.FILES['file']

        if file.name.endswith(".xlsx") or file.name.endswith(".xls"):  # 判断上传文件是否为表格
            df = pd.read_excel(file, keep_default_na=False)

            column_list = ['專案', '發佈者部門', '發佈者姓名', '主旨', '工單', '工站', '流程內容', '接收段別', 'DRI(白班)',
                           'DRI(晚班)']

            if list(df.columns) == column_list:

                pattern = re.compile(r'[/|，|, |\n]\s*')

                # 用户部门、專案
                department = request.user.department.name
                project = request.user.project
                projects = pattern.split(project)

                # 主旨
                subjects = list(Subject.objects.values_list('subject', flat=True))
                # 工站
                stations = list(Stations.objects.filter(department=department).values_list('station', flat=True))

                # 工單發佈時間、發佈者
                publisher = request.user.name

                # 讀取工單數據
                for i in range(len(df)):
                    if str(df.loc[i, '專案']) in projects:
                        if department == df.loc[i, '發佈者部門']:
                            if publisher == df.loc[i, '發佈者姓名']:
                                if pattern.split(df.loc[i, '主旨']) in subjects:
                                    if pattern.split(df.loc[i, '工站']) in stations:

                                        # 上傳成功的工單，将工单信息放入缓存中
                                        # 到上传信息页面查看是否信息有误
                                        correct_workflow.append(df.loc[i].tolist())
                                        cache.set('workflow_cache', correct_workflow, 60*60)

                                    else:
                                        msg = '流程工站錯誤！！'
                                        error_station.append(df.loc[i].tolist())
                                        break

                                else:
                                    msg = '流程主旨錯誤！！'
                                    error_subject.append(df.loc[i].tolist())
                                    break

                            else:
                                msg = '流程發佈者與當前用戶不匹配！！'
                                error_publisher.append(df.loc[i].tolist())
                                break

                        else:
                            msg = '請勿發佈其他部門工單！！'
                            error_department.append(df.loc[i].tolist())
                            break
                    else:
                        msg = '用戶無該專案工單發佈權限！！'
                        error_project.append(df.loc[i].tolist())
                        break

                if not error_project and not error_department:
                    msg = '流程上傳！！'

            else:
                msg = '請選擇正確的文件！！'

        return render(request, 'process/WorkFlow/WorkFlow_upload_info.html',
                      {"msg": msg, "correct_workflow": correct_workflow, "error_department": error_department,
                       "error_project": error_project, "error_publisher": error_publisher})


class WorkFlowListView(LoginRequiredMixin, View):
    """
    流程显示视图
    """

    def get(self, request):
        # 用戶專案、部門
        project = request.user.project
        projects = re.split(r'[/|，|, |\n]\s*', project)
        department = request.user.department.name
        name = request.user.name

        # 前端要显示的属性
        fields = ['id', 'project', 'build', 'order', 'publish_dept', 'publisher', 'publish_status',
                  'publish_time', 'subject', 'key_content', 'segment', 'receiver', 'receive_status',
                  'status', 'receive_time', 'unit_type', 'station', 'number', 'day_dri', 'night_dri', 'sn']

        searchfields = ['subject', 'segment', 'status', 'receive_status', 'station', 'order']

        filters = {i + '__icontains': request.GET.get(i, '') for i in searchfields if request.GET.get(i, '')}

        # 接收者工單顯示
        if request.user.account_type == 1:

            # 如果用戶為副線長
            if request.user.user_type == 0:
                # 接收者只能看接收人是自己的子工單
                workflows = OrderInfo.objects.filter(project__in=projects, receive_dept=department, receiver=name,
                                                     deleted=False, is_parent=False,
                                                     **filters).values(*fields).order_by('-id')

            else:
                # 获取当先用户的下级
                juniors = [junior for junior in request.user.userinfo_set.all()]
                juniors_name = [junior.name for junior in juniors]

                # 如果用戶為线长
                if request.user.user_type == 1:
                    # 看下级 副线长 的所有流程
                    workflows = OrderInfo.objects.filter(project__in=projects, receive_dept=department, is_parent=False,
                                                         deleted=False, receiver__in=juniors_name,
                                                         **filters).values(*fields).order_by('-id')
                # 如果用戶為专案主管
                elif request.user.user_type == 2:
                    lower_juniors = []
                    # 下级 线长
                    for junior in juniors:
                        # 线长 下级 副线长
                        # 看 所有下級線長 下的副線長的流程
                        for lower_junior in junior.userinfo_set.all():
                            lower_juniors.append(lower_junior.name)

                    workflows = OrderInfo.objects.filter(project__in=projects, receive_dept=department, is_parent=False,
                                                         receiver__in=lower_juniors, deleted=False,
                                                         **filters).values(*fields).order_by('-id')

        else:
            # 發佈者工單
            # 發佈者只能看自己發佈的流程，所有未被刪除的父流程
            workflows = OrderInfo.objects.filter(project__in=projects, publisher=name, is_parent=True, deleted=False,
                                                 **filters).values(*fields).order_by('-id')

        for workflow in workflows:
            order = OrderInfo.objects.get(id=workflow['id'])
            # workflow['status'] = order.get_status_display()
            workflow['receive_status'] = order.get_receive_status_display()

        res = dict(data=list(workflows))

        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')


class WorkFlowCreateView(LoginRequiredMixin, View):
    """
    流程創建视图
    """

    def get(self, request):
        """
        創建和更新頁面渲染數據
        :param request: 请求对象
        :return: 渲染创建页面
        """
        res = dict(msg='')
        # 用戶部門
        department = request.user.department.name

        # 用戶專案
        projects = re.split(r'[/|，|, |\n]\s*', request.user.project)
        res['projects'] = projects

        # 當為更新流程時
        if 'id' in request.GET and request.GET['id']:
            # 獲取要更新的流程
            workflow = get_object_or_404(OrderInfo, pk=request.GET.get('id'))

            # 将流程对象传到前端页面
            res['workflow'] = workflow

            # 如果部門為 RF 或 TDL 只能拿自己部門的工站和主旨
            if department in ['RF', 'TDL']:
                # 為編輯時只拿流程對應專案對應部門下的工站
                res['stations'] = Stations.objects.filter(project=workflow.project, department=department)
            else:
                # 為編輯時只拿流程對應專案下的工站
                res['stations'] = Stations.objects.filter(project=workflow.project)

            # 流程的发布时间
            res['time'] = workflow.publish_time.strftime('%Y-%m-%d %H:%M')

            # 用于将工单段别、工站分割
            pattern = re.compile(r'[/|;|\n]\s*')

            # 獲取流程的工站、段別主旨
            # 當為發佈者是，編輯的是父流程，有多個段別
            if request.user.account_type == 0:
                res['workflow_segments'] = pattern.split(workflow.segment)
            else:
                res['workflow_segments'] = workflow.segment

            res['workflow_stations'] = pattern.split(workflow.station)
            res['workflow_subjects'] = pattern.split(workflow.subject)

        else:
            # 新建流程时

            # 获取当前的时间为工单创建时间
            t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            res['time'] = t

            # 默认取用户第一个专案下的的工站
            res['stations'] = Stations.objects.filter(project=projects[0])

        # 機種
        res['unit_types'] = UnitType.objects.filter(project__in=projects)

        # 获取数据库中所有段别
        segments = Segment.objects.all()
        res['segments'] = segments

        # 如果部門為 RF 或 TDL 只能拿自己部門的主旨
        if department in ['RF', 'TDL']:
            res['subjects'] = Subject.objects.filter(department=department)
        else:
            res['subjects'] = Subject.objects.all()

        return render(request, 'process/WorkFlow/WorkFlow_Create.html', res)

    def post(self, request):
        res = dict(result=False)

        pattern = re.compile(r'[/|;|\n]\s*')

        # 手动更新流程状态保存
        if 'ids' in request.POST and request.POST['ids']:
            # 獲取出工單
            order = OrderInfo.objects.get(id=request.POST['ids'])

            # 判斷工單是否接收，0:未接收 1:已接收
            if order.receive_status == 0:
                res['msg'] = '流程未接收！！'
            else:
                order.status = int(request.POST['data'])
                order.save()
                res['result'] = True

            return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')

        # 上传信息页面，点击发布流程
        if 'publish' in request.POST and request.POST['publish']:

            # 从缓存中拿导入的工单数据
            workflows = cache.get('workflow_cache', None)

            if workflows:
                # 发布时间
                publish_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

                for workflow in workflows:
                    project = workflow[0]  # 专案
                    department = workflow[1]  # 部门
                    publisher = workflow[2]  # 发布者
                    subject = workflow[3]  # 主旨
                    order = workflow[4]  # 工单
                    work_station = workflow[5]  # 工站
                    key_content = workflow[6]  # 工单内容

                    # 對用戶段別進行判斷
                    if workflow[7] and not re.search(r'all', workflow[7], re.I):
                        segment = workflow[7]  # 接收段别

                    else:
                        segment = 'All'

                    # 工单属性
                    fields = {
                        'project': project, 'publish_dept': department, 'publisher': publisher,
                        'publish_time': publish_time, 'subject': subject, 'order': order, 'key_content': key_content,
                        'station': work_station
                    }

                    # 段别列表
                    segment_list = pattern.split(segment)
                    # 父流程中段別將所有段別合併顯示
                    segments = '/'.join(segment_list)

                    # 創建父流程
                    father_order = OrderInfo.objects.create(**fields, is_parent=True, segment=segments)

                    # 创建子流程，传入父流程，属性字典，段别列表
                    mobiles, emails = create_workflow(father_order, fields, segment_list)

                    # 郵件和信息發送
                    # send_email_message(fields, mobiles, emails)

                res['result'] = True

            return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')

        # 工单信息发布或编辑修改
        # 存在 ID 是为编辑已存在流程，否则为创建新的流程
        # 编辑更新流程
        if 'id' in request.POST and request.POST['id']:
            workflow = get_object_or_404(OrderInfo, id=int(request.POST['id']))

            # 更新發佈時間
            new_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

            # 更新流程
            workflow.project = request.POST['project']
            workflow.subject = request.POST['subject']
            workflow.order = request.POST['order']
            workflow.key_content = request.POST['key_content']
            workflow.publish_time = new_time
            workflow.number = '/'.join(request.POST.getlist('number'))

            # 原來和新的段別
            old_seg = set(pattern.split(workflow.segment))
            new_seg = set(request.POST.getlist('segment'))

            fields = {
                # 工单属性
                'project': request.POST['project'], 'publish_dept': workflow.publish_dept,
                'publisher': workflow.publisher, 'publish_time': new_time,
                'subject': request.POST['subject'], 'order': request.POST['order'],
                'key_content': request.POST['key_content'],
                'station': '/'.join(request.POST.getlist('station')),
                'number': '/'.join(request.POST.getlist('number')),
                'day_dri': request.POST['day_dri'], 'night_dri': request.POST['night_dri']
            }

            workflow.segment = '/'.join(request.POST.getlist('segment'))
            workflow.day_dri = request.POST['day_dri']
            workflow.night_dri = request.POST['night_dri']
            workflow.save()

            # 判斷新舊段別是否有不同
            if 'All' not in old_seg and 'All' not in new_seg and old_seg.difference(new_seg):
                # 更新子工單數量
                # 如果原來工單段別不為All
                if 'All' not in old_seg:

                    # 如果新段別不為 All,才需要去比較是否要刪除
                    if 'All' not in new_seg:
                        # 表示在新的段別中不存在的段別
                        # 表示要刪除該段別子流程
                        if old_seg - new_seg:
                            # 刪除錯發的子流程
                            OrderInfo.objects.filter(parent=workflow, segment__in=(old_seg - new_seg)).delete()

                        # 表示在舊的段別中不存在的段別
                        # 創建新子流程
                        if new_seg - old_seg:
                            # 創建新的段別的字流程
                            create_workflow(workflow, fields, new_seg - old_seg)

                    # 如果新段別是 All
                    else:

                        diff_segment = set(list(Segment.objects.values_list('segment', flat=True))) - old_seg
                        # 創建新的段別的子流程
                        create_workflow(workflow, fields, diff_segment)

                else:
                    # 當原來的segment 為 All
                    diff_segment = set(list(Segment.objects.values_list('segment', flat=True))) - new_seg

                    if diff_segment:
                        # 刪除錯發的字流程
                        OrderInfo.objects.filter(parent=workflow, segment__in=diff_segment).delete()

            # 用户为发布者时才更新子流程
            if request.user.account_type == 0:
                # 更新子流程
                OrderInfo.objects.filter(parent=workflow).update(**fields)

            res['result'] = True

        # 發佈新流程
        else:
            # 用户专案、發佈者
            publisher = request.POST['publisher']

            # 流程信息主旨 發佈時間 工站
            publish_time = request.POST['publish_time']
            subject = '/'.join(request.POST.getlist('subject'))

            stations = request.POST.getlist('station')

            special_stations = ['AP POR Stations', 'All AP Stations', 'All RF POR Stations', 'All RF Stations']

            re_stations = set(stations) & set(special_stations)
            if re_stations:
                station = '/'.join(list(re_stations))
            else:
                station = '/'.join(request.POST.getlist('station'))

            # 工单属性
            fields = {
                'project': request.POST['project'], 'publish_dept': request.POST['publish_dept'],
                'publisher': publisher, 'publish_time': publish_time, 'subject': subject,
                'order': request.POST['order'], 'key_content': request.POST['key_content'], 'station': station,
                'number': '/'.join(request.POST.getlist('number')), 'day_dri': request.POST['day_dri'],
                'night_dri': request.POST['night_dri']
            }

            # 判断工单接收DRI,以字符串的形式存储
            if 'All' not in request.POST.getlist('segment'):
                # 获取接收前端选中的接收者
                segment_list = request.POST.getlist('segment')

                # 父流程中段別將所有段別合併顯示
                segments = '/'.join(segment_list)
                # 創建父流程
                parent_order = OrderInfo.objects.create(**fields, is_parent=True, segment=segments)

                # 創建子流程，传入父流程，流程属性字典，段别列表
                mobiles, emails = create_workflow(parent_order, fields, segment_list)

            else:
                # 創建父工單，發佈者顯示父工單
                parent_order = OrderInfo.objects.create(**fields, is_parent=True, segment='All')
                # 創建工單，传入父流程，流程属性字典
                mobiles, emails = create_workflow(parent_order, fields)

            res['result'] = True

            # 郵件和信息發送需要的數據
            # send_email_message(fields, mobiles, emails)

        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')


class WorkFlowDeleteView(LoginRequiredMixin, View):
    """
    流程刪除視圖
    """

    def post(self, request):
        res = dict(result=False)

        # 判断获取前端传过来的要删除的id
        if 'id' in request.POST and request.POST.get('id'):
            ids = map(int, request.POST.get('id').split(','))

            orders = OrderInfo.objects.filter(id__in=ids)

            for order in orders:
                # 获取子流程
                child_orders = order.orderinfo_set
                if child_orders:
                    child_orders.update(deleted=True)

            orders.update(deleted=True)

            res['result'] = True

        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')


class WorkFlowDetailView(LoginRequiredMixin, View):
    """
    流程详情視圖
    """

    def get(self, request):
        res = dict()

        id = request.GET.get('workflowId')

        workflow = OrderInfo.objects.get(id=id)

        res['workflow'] = workflow

        # 獲取對應流程的附件
        Attachment.objects.filter(workflow=workflow.id)

        return render(request, 'process/WorkFlow/WorkFlow_Detail.html', res)


class WorkflowSnImport(LoginRequiredMixin, View):
    """
    流程SN導入
    """
    def post(self, request):
        res = dict()

        # 用於發佈流程時，SN的
        # 獲取文件
        file = request.FILES['sn_file']

        # sn列表，用於存放讀取出的sn
        sn_list = []

        if file.name.endswith(".xlsx") or file.name.endswith(".xls"):  # 判断上传文件是否为表格
            df = pd.read_excel(file, skiprows=1, index_col=0, keep_default_na=False)

            column_list = ['SN']

            if list(df.columns) == column_list:

                for i in range(len(df)):
                    df_list = list(df.values)[i]
                    sn_list.append(str(df_list[0]))

                res['sn'] = '/'.join(sn_list)

            return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')


