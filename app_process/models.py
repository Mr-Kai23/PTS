
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
    project = models.CharField(max_length=10, null=True, blank=True, verbose_name='专案')
    unit_type = models.CharField(max_length=10, null=True, blank=True, default="", verbose_name='机种')

    class Meta:
        verbose_name = '机种表'
        verbose_name_plural = verbose_name
        db_table = 'UnitType'


class Stations(models.Model):
    """
    工站信息表
    """
    project = models.CharField(max_length=10, null=True, blank=True, verbose_name='专案')
    department = models.CharField(max_length=10, null=True, blank=True, verbose_name='部门')
    segment = models.CharField(max_length=20, null=True, blank=True, verbose_name='段别')
    station = models.CharField(max_length=50, null=True, blank=True, default="", verbose_name='工站')
    number = models.CharField(max_length=100, null=True, blank=True, default="", verbose_name='工站号')

    class Meta:
        verbose_name = '工站表'
        verbose_name_plural = verbose_name
        db_table = 'Stations'


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


class Subject(models.Model):
    """
    主旨信息表
    """
    department = models.CharField(max_length=10, default='', verbose_name='部门')
    subject = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='主旨')

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = '主旨表'
        verbose_name_plural = '主旨表'
        db_table = 'Subject'

class Orderclass(models.Model):
    '''
    工单类型表
    '''
    orderclass = models.CharField(max_length=32, null=True, blank=True, verbose_name='工单类型')

    def __str__(self):
        return self.orderclass

    class Meta:
        verbose_name = '工单类型表'
        verbose_name_plural = '工单类型表'
        db_table = 'Orderclass'


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
        (0, '未執行'),
        (1, '執行中'),
        (2, '已完成'),
    )

    # 更新状况
    # status_fresh = (
    #     (1, '已更新'),
    #     (0, '未更新')
    # )

    project = models.CharField(max_length=50, null=True, blank=True, default='', verbose_name='专案')
    build = models.CharField(max_length=10, null=True, blank=True, default='', verbose_name='阶段')
    publish_dept = models.CharField(max_length=10, default='', verbose_name='发布部门')
    publisher = models.CharField(max_length=20, null=True, blank=True, verbose_name='发布人')
    publish_status = models.SmallIntegerField(choices=publish_status_choice, default=0, blank=True, verbose_name='发布状态')
    publish_time = models.DateTimeField(null=True, blank=True, default=None, verbose_name='发布时间')
    subject = models.CharField(max_length=50, null=True, blank=True, default='', verbose_name='主旨')
    order = models.CharField(max_length=500, null=True, blank=True, default='', verbose_name='工单')
    key_content = models.CharField(max_length=5000, null=True, blank=True, default='', verbose_name='重点注意流程内容')
    unit_type = models.CharField(max_length=32, null=True, blank=True, default="", verbose_name='机种')
    segment = models.CharField(max_length=300, null=True, blank=True, default='', verbose_name='接收段别')
    receiver = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='接收人')
    receive_dept = models.CharField(max_length=10, default='', blank=True, verbose_name='接收部门')
    station = models.CharField(max_length=500, null=True, blank=True, default="", verbose_name='工站')
    receive_status = models.SmallIntegerField(choices=receive_status_choice, default=0, blank=True, verbose_name='接收状态')
    # fresh_status = models.SmallIntegerField(choices=status_fresh, default=0, blank=None, verbose_name='更新状况')
    status = models.SmallIntegerField(choices=status_choice, default=0, blank=True, verbose_name='执行状态')
    receive_time = models.DateTimeField(null=True, blank=True, default=None, verbose_name='接收时间')

    # EPM工单
    # per_order = models.IntegerField(default=1, blank=True, verbose_name='优先等级')
    # order_class = models.CharField(max_length=50, null=True, blank=True, default='', verbose_name='工单类型')


    # 用於判斷該條工單是否為父工單，發佈者發佈的時候生成的父工單
    # 父工單保存發佈者發佈時的工單信息，例如多個段別、工站等信息
    is_parent = models.BooleanField(default=False)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, default=None, verbose_name="上级主管")

    # 用于标记流程是否已删除
    deleted = models.BooleanField(default=False)

    # 優先級, 用與看板頁面的主旨為重点流程的流程排序
    priority = models.BooleanField(default=False)

    # RF新增
    # SN、白晚DRI、工站號、工站版本號
    sn = models.CharField(max_length=500, null=True, blank=True, verbose_name='SN')
    day_dri = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='白班工站DRI')
    night_dri = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='晚班工站DRI')
    number = models.CharField(max_length=250, null=True, blank=True, default="", verbose_name='工站号')
    station_version = models.CharField(max_length=250, null=True, blank=True, default="", verbose_name='工站版本号')

    def __str__(self):
        """定义每个数据对象的显示信息"""
        return self.order

    class Meta:
        """内部类，它用于定义一些Django模型类的行为特性"""
        verbose_name = '工单基本信息表'
        verbose_name_plural = '工单基本信息表'
        ordering = ['-publish_time']
        db_table = 'OderInfo'


class ExceptionContact(models.Model):
    """
    段别异常联系人
    """
    project = models.CharField(max_length=50, null=True, blank=True, default='', verbose_name='专案')
    segment = models.CharField(max_length=50, null=True, blank=True, default='', verbose_name='接收段别')
    contact = models.CharField(max_length=50, null=True, blank=True, default='', verbose_name='联系人')
    department = models.CharField(max_length=10, default='', verbose_name='联系人部门')
    phone = models.CharField(max_length=50, null=True, blank=True, default='', verbose_name='联系人电话')

    def __str__(self):
        """定义每个数据对象的显示信息"""
        return self.contact

    class Meta:
        """内部类，它用于定义一些Django模型类的行为特性"""
        verbose_name = '段别异常联系人信息表'
        verbose_name_plural = '段别异常联系人信息表'
        db_table = 'ExceptionContact'


class Attachment(models.Model):
    workflow = models.IntegerField(null=True, blank=True, default=None, verbose_name="流程ID")
    # 流程附件上傳
    attachment = models.FileField(upload_to='upload/%Y/%m/%d/', max_length=500, null=True, blank=True)

    # def file_link(self):
    #     if self.attachment:
    #         return "<a href='%s'>download</a>" % (self.attachment.url,)
    #     else:
    #         return "No attachment"
    #
    # file_link.allow_tags = True

    def __str__(self):
        """定义每个数据对象的显示信息"""
        return self.workflow

    class Meta:
        """内部类，它用于定义一些Django模型类的行为特性"""
        verbose_name = '附件信息表'
        verbose_name_plural = '附件信息表'
        db_table = 'Attachment'