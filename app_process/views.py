from django.db.models import Count
from django.shortcuts import render

# Create your views here.
from django.views import View

from app_process.models import OrderInfo, Segment
from system.mixin import LoginRequiredMixin
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.cache import cache_page

from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from suds.client import Client


class BoardView(View):
    """
    看板视图
    """
    def get(self, request):

        # 用于存放每个段别下的工单
        segment_orders = []
        # 用存放每个段别下每种执行状态下的工单
        un_accept_list = []
        un_product_list = []
        Ongoing_list = []
        Closed_list = []

        orders = OrderInfo.objects.all()

        # 获取所有段别下的工单数量
        segments = Segment.objects.all().order_by('id')

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
            'ongoing': orders.filter(status=1).count(),   # 进行中
            'closed': orders.filter(status=2).count(),   # 已完成
            'segments': segments,
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
        fields = ['id', 'project', 'build', 'order', 'publish_dept', 'publisher', 'publish_status',
                  'publish_time', 'subject', 'key_content', 'segment', 'receiver', 'receive_status',
                  'status', 'withdraw_time', 'unit_type']

        workflows = OrderInfo.objects.values(*fields).order_by('-id')

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


def send_email(subject, message, from_email, receivers):
    """
    发送邮件
    :param subject:
    :param message:
    :param from_email:
    :param receivers:
    :return:
    """

    if subject and message and from_email:
        try:
            send_mail(subject, message, from_email, receivers)

        except BadHeaderError:
            return HttpResponse('信息有誤！！')

        return '郵件已發送！！'

    else:

        return HttpResponse('請確認所有信息是否無誤！！')


def send_message(moblie_list, message, FormatID='6311', SpaceNum='7'):
    """
    发送短信
    :param moblie_list:
    :param message:
    :param FormatID:
    :param SpaceNum:
    :return:
    """

    for moblie in moblie_list:
        try:
            client = Client('http://sms.efoxconn.com/Framework/index.aspx')
            params = {'UserName': 'F8624523', 'PassWord': '42322317', 'Phone': moblie, 'FormatID': FormatID,
                      'SpaceNum': SpaceNum, 'Content': message}

            client.service.SendFormatSMS(**params)

        except Exception:

            return HttpResponse('信息有誤！！')

        return '短信已发送！！'

