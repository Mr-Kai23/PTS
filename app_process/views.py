from django.shortcuts import render

# Create your views here.
from django.views import View

from app_process.models import OrderInfo
from system.mixin import LoginRequiredMixin
import json
from django.core.serializers.json import DjangoJSONEncoder

from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
# from suds.client import Client


class BoardView(View):
    """
    看板视图
    """
    def get(self, request):
        return render(request, 'process/Board.html', locals())


class BoardListView(View):
    """
    看板数据显示视图
    """
    def get(self, request):
        fields = ['id', 'project', 'build', 'order', 'publish_dept', 'publisher', 'publish_status',
                  'publish_time', 'subject', 'key_content', 'segment', 'receiver', 'receive_status',
                  'status', 'withdraw_time', 'unit_type']

        orders = list(OrderInfo.objects.values(*fields).order_by('-id'))

        res = dict(data=orders)

        return HttpResponse(json.dumps(res, cls=DjangoJSONEncoder), content_type='application/json')


class OrderView(LoginRequiredMixin, View):
    def get(self, request):
        res = {
            'created': OrderInfo.objects.all().count(),
            'receive': OrderInfo.objects.filter(receive_status=0).count(),
            'finished': OrderInfo.objects.filter(receive_status=1, status=1).count()
        }

        return render(request, 'process/order_index.html', res)


def send_email(subject, message, from_email, receivers):
    """
    發送郵件
    """

    if subject and message and from_email:
        try:
            send_mail(subject, message, from_email, receivers)

        except BadHeaderError:
            return HttpResponse('信息有誤！！')

        return '郵件已發送！！'

    else:

        return HttpResponse('請確認所有信息是否無誤！！')


def send_message(moblie_list, message, FormatID, SpaceNum):

    for moblie in moblie_list:
        try:
            client = Client('http://sms.efoxconn.com/Framework/index.aspx')
            params = {'UserName': 'F8624523', 'PassWord': '42342314', 'Phone': moblie, 'FormatID': FormatID,
                      'SpaceNum': SpaceNum, 'Content': message}

            client.service.SendFormatSMS(**params)

        except Exception:

            return HttpResponse('信息有誤！！')

        return '短信已发送！！'

