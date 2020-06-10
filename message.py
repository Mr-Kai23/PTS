from django.core.mail import send_mail, BadHeaderError

from django.http import HttpResponse
from suds.client import Client
from Celery_Task.service import celery


# def send_email(subject, message, from_email, receivers):
#     """
#     发送邮件
#     :param subject: 邮件主旨
#     :param message: 邮件内容
#     :param from_email: 发送者
#     :param receivers: 接收者
#     :return:
#     """
#
#     if subject and message and from_email:
#         try:
#             send_mail(subject, message, from_email, receivers)
#
#         except BadHeaderError:
#             return HttpResponse('信息有誤！！')
#
#         return '郵件已發送！！'
#
#     else:
#
#         return HttpResponse('請確認所有信息是否無誤！！')


@celery.task(name='send_message')
def send_message(mobile_list, message, FormatID='6311', SpaceNum='7'):
    """
    发送短信
    :param mobile_list: 号码列表
    :param message: 短信内容
    :param FormatID: 短信模板ID
    :param SpaceNum: 短信模板填充栏数量
    :return:
    """

    for moblie in mobile_list:
        try:

            client = Client('http://10.134.129.10:8888/SendSMSService.asmx?wsdl')

            params = {'UserName': 'F8624523', 'PassWord': '42322317', 'Phone': [moblie], 'FormatID': FormatID,
                      'SpaceNum': SpaceNum, 'Content': message}

            client.service.SendFormatSMS(**params)

        except Exception:

            return HttpResponse('信息有誤！！')

        return '短信已发送！！'
