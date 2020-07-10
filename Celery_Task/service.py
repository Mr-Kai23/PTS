#! usr/bin/python
# -*- coding:utf-8 -*-
# @Author: winston he
# @File: service.py
# @Time: 2020-04-15 16:58
# @Email: winston.wz.he@gmail.com
# @Desc: 定義異步郵件發送的任務

from celery import Celery
import smtplib
from email.header import Header
from email.mime.text import MIMEText


EMAIL_SERVER = '10.134.28.97'
EMAIL_PORT = 25
DEFAULT_EMAIL_ADDRESS = 'PTS'
DEFAULT_EMAIL_PASSWORD = ''

BACKEND_USERNAME = 'application_user'
BACKEND_PASSWORD = '123456'
BACKEND_IP = '10.141.7.36'
BACKEND_PORT = 80


def make_celery():
    celery = Celery(
        'tasks',
        # backend='mysql://{}:{}@{}:{}/PTS'.format('root', 'xiayanxia12', BACKEND_IP, BACKEND_PORT),
        broker='amqp://10.134.82.243:5900//'
        # broker = 'amqp://guest:guest@127.0.0.1:5672//'  # 本地 rabbitmq-server
    )
    return celery


celery = make_celery()


@celery.task(name='service.send_email_async')
def send_email_async(*, email_address=None, email_password=None, send_to: str, subject: str, msg: str, send_from=None, **ssh_info):
    """

    :param email_address: 发件邮箱地址
    :param email_password: 发件邮箱密码
    :param send_to: 收件的邮箱地址
    :param subject: 邮件标题
    :param msg: 邮件内容
    :param send_from: 显示的发件人地址（实际发件地址仍为email_address）
    :param ssh_info: 包含远程IP，登录账号、密码
    :return:
    """
    if email_address is None:
        email_address = DEFAULT_EMAIL_ADDRESS
    if email_password is None:
        email_password = DEFAULT_EMAIL_PASSWORD
    if send_from is None:
        send_from = email_address

    client = smtplib.SMTP()
    client.connect(EMAIL_SERVER, EMAIL_PORT)
    # client.login(content['email_address'], content['email_password'])
    # client.login('', '')  # 此处是账号，密码
    msg = MIMEText(msg, 'html', _charset='UTF-8')
    msg['from'] = send_from
    msg['to'] = send_to if isinstance(send_to, str) else ', '.join(send_to)
    msg['Subject'] = Header(subject, 'utf-8')
    client.sendmail('SW Project Management System', send_to, msg.as_string())
    client.quit()

