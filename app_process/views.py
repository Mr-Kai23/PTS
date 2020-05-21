# ======================================================
# @Author  :   Daniel                 
# @Time    :   2020-03
# @Desc    :   看板
# ======================================================
from django.shortcuts import render

# Create your views here.
from django.views import View

from app_process.models import OrderInfo, Segment, Project
from system.models import UserInfo
from system.mixin import LoginRequiredMixin
import json, re
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.cache import cache_page

from message import send_email, send_message
from django.conf import settings

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

        orders = OrderInfo.objects.all()

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
                  'status', 'withdraw_time']

        search_fields = ['project', 'segment', 'receive_status', 'status']
        filters = {i + '__contains': json.loads(list(dict(request.GET).keys())[0])[i] for i in search_fields if
                   json.loads(list(dict(request.GET).keys())[0])[i]}

        # 开始、结束时间搜索
        if json.loads(list(dict(request.GET).keys())[0])['start_time'] and \
                json.loads(list(dict(request.GET).keys())[0])['end_time']:
            filters['publish_time__gte'] = json.loads(list(dict(request.GET).keys())[0])['start_time']
            filters['publish_time__lte'] = json.loads(list(dict(request.GET).keys())[0])['end_time']

        # 切片取50条数据
        # sli = slice(0, 50)
        workflows = OrderInfo.objects.filter(**filters).values(*fields).order_by('-id')

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
        orders = OrderInfo.objects.all()
        res = {
            'created': orders.count(),
            'receive': orders.filter(receive_status=0).count(),
            'finished': orders.filter(receive_status=1, status=1).count()
        }

        return render(request, 'process/order_index.html', res)


def create_workflow(project, fields={}, segment_list=None):
    """
    用於創建工單
    :param project: 工单专案
    :param fields: 工单属性字典
    :param segment_list: 創建工單時選中的 段別
    :return: 返回接收工單用戶的電話和郵箱列表
    """

    emails = set()  # 用于存放接收者邮箱
    mobiles = set()  # 用于存放接受者电话

    if segment_list:
        # 所有段別下的接收者
        users = UserInfo.objects.filter(project=project, account_type=1, segment__in=segment_list)
    else:
        # 所有段別下的接收者
        users = UserInfo.objects.filter(project=project, account_type=1)

    # 對應段別下 為 副線長（is_admin=False） 的接收者 的 部門、姓名、段別
    receivers = list(users.filter(is_admin=False).values_list('department__name', 'name', 'segment'))

    # 获取DRI下面的员工邮箱和电话
    for email, mobile in tuple(users.values_list('email', 'mobile')):
        emails.add(email)
        mobiles.add(mobile)

    # 根據不同的接收人，创建對應的多條工单
    workflow_list = [OrderInfo(**fields, receive_dept=receive_dept, receiver=receiver, segment=segment) for
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
    department = info_dict['department']  # 用戶部門
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
                 [project+"專案"+department+"部門"+publisher, year, month, day, hour, minute, subject],
                 '6311', '7')

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
