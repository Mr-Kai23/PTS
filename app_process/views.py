# ======================================================
# @Author  :   Daniel                 
# @Time    :   2020-03
# @Desc    :   看板
# ======================================================
from django.shortcuts import render

# Create your views here.
from django.views import View

from app_process.models import OrderInfo, Segment, Project, Subject
from system.models import UserInfo
from system.mixin import LoginRequiredMixin
import json, re
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.cache import cache_page

from message import send_email, send_message
from django.conf import settings
# import xlsxwriter
from io import BytesIO

from django.http import HttpResponse


class BoardView(View):
    """
    看板视图
    """

    def get(self, request):
        """
        用于渲染看板页面
        :param request:
        :return:
        """

        # 用于存放每个段别下的工单
        segment_orders = []
        # 用存放每个段别下每种执行状态下的工单
        un_accept_list = []
        un_product_list = []
        Ongoing_list = []
        Closed_list = []

        # 只看未被刪除的子流程
        # 父流程只是給發佈者看，方便修改
        orders = OrderInfo.objects.filter(is_parent=False, deleted=False)

        # 獲取所有专案
        projects = Project.objects.all()

        # 获取所有段别下的工单数量
        segments = Segment.objects.exclude(segment__icontains='all').order_by('id')

        for segment in segments:
            # 获取每个段别下的工单
            segment_orders.append(orders.filter(segment=segment).all())
            # 获取每个段别下的未接收的工单
            un_accept_list.append(orders.filter(receive_status=0, segment=segment).count())
            # 获取每个段别下的未投产的工单
            un_product_list.append(orders.filter(status=0, segment=segment).count())
            # 获取每个段别下的Ongoing的工单
            Ongoing_list.append(orders.filter(status=1, segment=segment).count())
            # 获取每个段别下的Closed的工单
            Closed_list.append(orders.filter(status=2, segment=segment).count())

        # 用于echarts显示
        res = {
            'un_receive': orders.filter(receive_status=0).count(),  # 待接收工单数量
            'un_product': orders.filter(status=0).count(),  # 未投产工单数量
            'ongoing': orders.filter(status=1).count(),  # 进行中
            'closed': orders.filter(status=2).count(),  # 已完成
            'segments': segments,
            'projects': projects,
            'segment_orders': segment_orders,
            'un_accept_list': un_accept_list,
            'un_product_list': un_product_list,
            'Ongoing_list': Ongoing_list,
            'Closed_list': Closed_list,
        }

        return render(request, 'process/Board.html', res)


class BoardListView(View):
    """
    看板数据显示视图
    """

    def get(self, request):
        """
        用于看板页面数据显示
        :param request: 请求
        :return:
        """
        fields = ['id', 'project', 'build', 'order', 'publish_dept', 'publisher', 'publish_status',
                  'publish_time', 'subject', 'key_content', 'segment', 'receiver', 'receive_status',
                  'status', 'receive_time']

        search_fields = ['project', 'segment', 'receive_status', 'status']
        filters = {i + '__icontains': json.loads(list(dict(request.GET).keys())[0])[i] for i in search_fields if
                   json.loads(list(dict(request.GET).keys())[0])[i]}

        # 开始、结束时间搜索
        if json.loads(list(dict(request.GET).keys())[0])['start_time'] and \
                json.loads(list(dict(request.GET).keys())[0])['end_time']:
            filters['publish_time__gte'] = json.loads(list(dict(request.GET).keys())[0])['start_time']
            filters['publish_time__lte'] = json.loads(list(dict(request.GET).keys())[0])['end_time']

        # 獲取数据
        workflows = OrderInfo.objects.filter(**filters).exclude(subject='重點流程', status=2).values(*fields).order_by('-id')

        for workflow in workflows:
            order = OrderInfo.objects.get(id=workflow['id'])
            workflow['status'] = order.get_status_display()
            workflow['receive_status'] = order.get_receive_status_display()
            workflow['publish_time'] = order.publish_time.strftime("%Y/%m/%d %H:%M")

        res = dict(data=list(workflows))

        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')


class OrderView(LoginRequiredMixin, View):
    """
    工单主页面视图
    """

    def get(self, request):
        # orders = OrderInfo.objects.all()
        # res = {
        #     'created': orders.count(),
        #     'receive': orders.filter(receive_status=0).count(),
        #     'finished': orders.filter(receive_status=1, status=1).count()
        # }

        # 用于存放每个段别下的工单
        segment_orders = []
        # 用存放每个段别下每种执行状态下的工单
        un_accept_list = []
        un_product_list = []
        Ongoing_list = []
        Closed_list = []

        # 只看未被刪除的子流程
        # 父流程只是給發佈者看，方便修改
        orders = OrderInfo.objects.filter(is_parent=False, deleted=False)

        # 獲取所有专案
        projects = Project.objects.all()

        # 获取所有段别下的工单数量
        segments = Segment.objects.exclude(segment__icontains='all').order_by('id')

        for segment in segments:
            # 获取每个段别下的工单
            segment_orders.append(orders.filter(segment=segment).all())
            # 获取每个段别下的未接收的工单
            un_accept_list.append(orders.filter(receive_status=0, segment=segment).count())
            # 获取每个段别下的未投产的工单
            un_product_list.append(orders.filter(status=0, segment=segment).count())
            # 获取每个段别下的Ongoing的工单
            Ongoing_list.append(orders.filter(status=1, segment=segment).count())
            # 获取每个段别下的Closed的工单
            Closed_list.append(orders.filter(status=2, segment=segment).count())

        # 用于echarts显示
        res = {
            'un_receive': orders.filter(receive_status=0).count(),  # 待接收工单数量
            'un_product': orders.filter(status=0).count(),  # 未投产工单数量
            'ongoing': orders.filter(status=1).count(),  # 进行中
            'closed': orders.filter(status=2).count(),  # 已完成
            'segments': segments,
            'projects': projects,
            'segment_orders': segment_orders,
            'un_accept_list': un_accept_list,
            'un_product_list': un_product_list,
            'Ongoing_list': Ongoing_list,
            'Closed_list': Closed_list,
        }

        return render(request, 'process/Index.html', res)


def create_workflow(parent_order, fields={}, segment_list=None):
    """
    用於創建工單
    :param fields: 工单属性字典
    :param parent_order: 當前創建所有工單的父工單
    :param segment_list: 創建工單時選中的 段別
    :return: 返回接收工單用戶的電話和郵箱列表
    """

    emails = set()  # 用于存放接收者邮箱
    mobiles = set()  # 用于存放接受者电话

    if segment_list and 'All' not in segment_list:
        # 对应段別下的接收者
        users = UserInfo.objects.filter(project__icontains=fields['project'], account_type=1, segment__in=segment_list)
    else:
        # 所有段別下的接收者
        users = UserInfo.objects.filter(project__icontains=fields['project'], account_type=1)

    # 获取接收者用戶邮箱和电话
    for email, mobile in tuple(users.values_list('email', 'mobile')):
        emails.add(email)
        mobiles.add(mobile)

    # 對應段別下 為 副線長（is_admin=False） 的接收者 的 部門、姓名、段別
    receivers = list(users.filter(is_admin=False).values_list('department__name', 'name', 'segment'))

    # 根據不同的接收人，创建對應的多條工单
    workflow_list = [OrderInfo(**fields, parent=parent_order, receive_dept=receive_dept, receiver=receiver, segment=segment) for
                     receive_dept, receiver, segment in receivers]

    OrderInfo.objects.bulk_create(workflow_list)

    return mobiles, emails


def send_email_message(info_dict, mobiles, emails):
    """
    用來發送郵件和信息
    :param info_dict: 信息，包括專案、用戶部門和姓名、發佈時間、工單主旨、重點注意事項
    :param mobiles: 電話列表
    :param emails: 郵箱列表
    :return:
    """
    project = info_dict['project']  # 專案
    department = info_dict['publish_dept']  # 用戶部門
    publisher = info_dict['publisher']  # 發佈者
    publish_time = info_dict['publish_time']  # 發佈時間
    subject = info_dict['subject']  # 工單主旨
    key_content = info_dict['key_content']  # 重點注意事項

    # 邮件和短息发送
    date = re.split(r'[-, :, \s]\s*', publish_time)
    year = date[0]
    month = date[1]
    day = date[2]
    hour = date[3]
    minute = date[4]

    # 發送郵件
    send_email(subject,
               key_content,
               settings.DEFAULT_FROM_EMAIL,
               list(emails))
    # 發送短信
    send_message(list(mobiles),
                 [project + "專案" + department + "部門" + publisher, year, month, day, hour, minute, subject],
                 '6311', '7')


def get_upload_module(request, download_id):
    """
    模板下载函数
    :param request: 请求对象
    :param download_id: 下載模板的ID
    :return:
    """
    excel = BytesIO()
    workbook = xlsxwriter.Workbook(excel, {'encoding': 'utf-8'})
    sheet = workbook.add_worksheet(request.GET['data'])

    # 表頭樣式
    title_format = workbook.add_format({
        # 单元格样式
        'bold': True,  # 字体
        'font_color': 'black',  # 颜色
        'bg_color': '#FFF2CC',
        'border': 1,  # 单元格边框宽度
        'align': 'center',  # 水平对齐方式
        'valign': 'vcenter',  # 垂直对齐方式
        'text_wrap': True,  # 是否自动换行
        'font_name': '华文楷体',
        'font_size': 14,
    })

    # 字段樣式
    field_format = workbook.add_format({
        # 单元格样式
        'bold': True,  # 字体
        'font_color': 'black',  # 颜色
        'border': 1,  # 单元格边框宽度
        'align': 'center',  # 水平对齐方式
        'valign': 'vcenter',  # 垂直对齐方式
        'text_wrap': True,  # 是否自动换行
        'font_name': '华文楷体',
        'font_size': 14,
    })

    if download_id == '0':
        title = ['專案', '發佈者部門', '發佈者姓名', '主旨', '工單', '工站', '流程內容', '接收段別']

        # 数据库所有主旨
        subjects = list(Subject.objects.values_list('subject', flat=True))
        sheet.data_validation('D2', {'validate': 'list', 'source': subjects})

    else:
        title = ['姓名', '工號', '用戶名', '郵箱', '手機', '部門', '上級', '專案', '段別', '備註', '賬號類型', '用戶類型',
                 '所屬角色组']

        # 数据库所有段别
        segments = list(Segment.objects.values_list('segment', flat=True))
        sheet.data_validation('I2', {'validate': 'list', 'source': segments})
        sheet.data_validation('K2', {'validate': 'list', 'source': ['發佈者', '接收者']})
        sheet.data_validation('L2', {'validate': 'list', 'source': ['副線長', '線長', '專案主管']})
        sheet.data_validation('M2', {'validate': 'list', 'source': ['系統管理', '流程管理']})

    # 設置第一行為空值
    sheet.write_row('A1', title, title_format)
    # 給一行空值
    sheet.write_row('A2', ['' for i in range(len(title))], field_format)

    workbook.close()
    excel.seek(0)

    # 将表中数据字节形式写入响应并返回
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=' + request.GET['data'] + ".xlsx"
    response.write(excel.getvalue())

    return response


# @cache_page(15*60)
# def OrderView(request):
#
#     orders = OrderInfo.objects.all()
#     res = {
#         'created': orders.count(),
#         'receive': orders.filter(receive_status=0).count(),
#         'finished': orders.filter(receive_status=1, status=1).count()
#     }
#
#     return render(request, 'process/order_index.html', res)
