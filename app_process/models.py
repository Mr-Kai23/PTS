
# ======================================================
# @Author  :   Daniel                 
# @Time    :   2020-02
# @Desc    :   數據庫模型
# ======================================================
from django.contrib.auth.models import User
from django.db import models


class Project(models.Model):
    """
    专案信息表
    """
    project = models.CharField(max_length=10, null=True, blank=True, verbose_name='专案')

    def __str__(self):
        return self.project

    class Meta:
        verbose_name = '专案表'
        verbose_name_plural = '专案表'
        db_table = 'Project'


class Build(models.Model):
    """
    阶段信息表
    """
    project = models.CharField(max_length=10, null=True, blank=True, verbose_name='专案')
    build = models.CharField(max_length=10, null=True, blank=True, verbose_name='阶段')

    def __str__(self):
        return self.build

    class Meta:
        verbose_name = '阶段表'
        verbose_name_plural = '阶段表'
        db_table = 'Build'


class UnitType(models.Model):
    """
    机种信息表
    """
    unit_type = models.CharField(max_length=10, null=True, blank=True, default="", verbose_name='机种')

    class Meta:
        verbose_name = '机种表'
        verbose_name_plural = verbose_name
        db_table = 'UnitType'


class Segment(models.Model):
    """
    段别信息表
    """
    segment = models.CharField(max_length=20, null=True, blank=True, default="", verbose_name='段别')

    def __str__(self):
        return self.segment

    class Meta:
        verbose_name = '段别表'
        verbose_name_plural = '段别表'
        db_table = 'Segment'


class OrderInfo(models.Model):
    """
    工单基本信息表
    """
    publish_status_choice = (
        (0, '已發佈'),
        (1, '已撤回'),
    )

    receive_status_choice = (
        (0, '未接收'),
        (1, '已接收'),
    )

    # 执行状态
    status_choice = (
        (0, '未投產'),
        (1, 'Ongoing'),
        (2, 'Closed'),
    )

    project = models.CharField(max_length=10, null=True, blank=True, default='', verbose_name='专案')
    build = models.CharField(max_length=10, null=True, blank=True, default='', verbose_name='阶段')
    publish_dept = models.CharField(max_length=10, default='', verbose_name='发布部门')
    publisher = models.CharField(max_length=20, null=True, blank=True, verbose_name='发布人')
    publish_status = models.SmallIntegerField(choices=publish_status_choice, default=0, blank=True, verbose_name='发布状态')
    publish_time = models.DateTimeField(null=True, blank=True, default=None, verbose_name='发布时间')
    subject = models.CharField(max_length=500, null=True, blank=True, default='', verbose_name='主旨')
    order = models.CharField(max_length=50, null=True, blank=True, default='', verbose_name='工单')
    key_content = models.CharField(max_length=5000, null=True, blank=True, default='', verbose_name='重点注意流程内容')
    unit_type = models.CharField(max_length=10, null=True, blank=True, default="", verbose_name='机种')
    segment = models.CharField(max_length=32, null=True, blank=True, default='', verbose_name='接收段别')
    receiver = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='接收人')
    receive_dept = models.CharField(max_length=10, default='', verbose_name='接收部门')
    receive_status = models.SmallIntegerField(choices=receive_status_choice, default=0, blank=True, verbose_name='接收状态')
    status = models.SmallIntegerField(choices=status_choice, default=0, blank=True, verbose_name='执行状态')
    withdraw_time = models.DateTimeField(null=True, blank=True, default=None, verbose_name='接收时间')

    def __str__(self):
        """定义每个数据对象的显示信息"""
        return self.order

    class Meta:
        """内部类，它用于定义一些Django模型类的行为特性"""
        verbose_name = '工单基本信息表'
        verbose_name_plural = '工单基本信息表'
        ordering = ['-publish_time']
        db_table = 'OderInfo'

