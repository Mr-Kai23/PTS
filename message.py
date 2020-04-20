from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from suds.client import Client


def send_email(subject, message, from_email, receivers):
    """
    发送邮件
    :param subject: 邮件主旨
    :param message: 邮件内容
    :param from_email: 发送者
    :param receivers: 接收者
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
    :param moblie_list: 号码列表
    :param message: 短信内容
    :param FormatID: 短信模板ID
    :param SpaceNum: 短信模板填充栏数量
    :return:
    """

    for moblie in moblie_list:
        try:

            client = Client('http://sms.efoxconn.com/Framework/index.aspx')

            params = {'UserName': 'F8624523', 'PassWord': '42322317', 'Phone': [moblie], 'FormatID': FormatID,
                      'SpaceNum': SpaceNum, 'Content': message}

            client.service.SendFormatSMS(**params)

        except Exception:

            return HttpResponse('信息有誤！！')

        return '短信已发送！！'


# if __name__ == '__main__':
#     # send_email('Test', '郵件測試！', 'PMS@mail.foxconn.com', ['daniel.k.zhou@foxconn.com'])
#     send_message(['15364911676'], ['周凱', '2020', '4', '17', '9', '52', '短信測試'], '6311', '7')