
# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser


class Menu(models.Model):
    """
    菜单
    """
    name = models.CharField(max_length=30, unique=True, verbose_name="菜单名")  # unique=True, 这个字段在表中必须有唯一值.
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, verbose_name="父菜单")
    icon = models.CharField(max_length=50, null=True, blank=True, verbose_name="图标")
    code = models.CharField(max_length=50, null=True, blank=True, verbose_name="编码")
    url = models.CharField(max_length=128, unique=True, null=True, blank=True)
    number = models.FloatField(null=True, blank=True, verbose_name="编号")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '菜单'
        verbose_name_plural = verbose_name
        ordering = ['number']

    @classmethod
    def get_menu_by_request_url(cls, url):
        try:
            return dict(menu=Menu.objects.get(url=url))
        except:
            None


class Role(models.Model):
    """
    角色：用于权限绑定
    """
    name = models.CharField(max_length=32, unique=True, verbose_name="角色")
    permissions = models.ManyToManyField("menu", blank=True, verbose_name="URL授权")
    desc = models.CharField(max_length=50, blank=True, null=True, verbose_name="描述")


class Structure(models.Model):
    """
    组织架构
    """
    type_choices = (("unit", "单位"), ("department", "部门"))
    name = models.CharField(max_length=60, verbose_name="名称")
    type = models.CharField(max_length=20, choices=type_choices, default="department", verbose_name="类型")
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, verbose_name="父类架构")
    resetTime = models.CharField(max_length=20, blank=True, null=True, verbose_name="Reset时长")
    sendUserEmail = models.TextField(blank=True, null=True, verbose_name="部门邮件组")

    class Meta:
        verbose_name = "组织架构"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class UserInfo(AbstractUser):
    """
    用户信息表
    """
    account_type_choice = (
        (0, '發佈者'),
        (1, '接收者'),
    )

    name = models.CharField(max_length=20, default="", verbose_name="姓名")
    birthday = models.DateField(null=True, blank=True, verbose_name="出生日期")
    gender = models.CharField(max_length=10, choices=(("male", "男"), ("female", "女")), default="male",
                              verbose_name="性别")
    mobile = models.CharField(max_length=11, default="", verbose_name="手机号码")
    email = models.EmailField(max_length=50, verbose_name="邮箱")
    image = models.ImageField(upload_to="image/%Y/%m", default="image/default.jpg", max_length=100, null=True,
                              blank=True)
    department = models.ForeignKey("Structure", null=True, blank=True, on_delete=models.SET_NULL, verbose_name="部门")
    post = models.CharField(max_length=50, null=True, blank=True, verbose_name="职位")
    superior = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, verbose_name="上级主管")
    roles = models.ManyToManyField("role", verbose_name="角色", blank=True)

    work_num = models.CharField(max_length=10, null=True, blank=True, verbose_name='工号')
    project = models.CharField(max_length=10, null=True, blank=True, verbose_name='专案')
    segment = models.CharField(max_length=20, null=True, blank=True, verbose_name='段别')
    account_type = models.SmallIntegerField(choices=account_type_choice, default=0, verbose_name='账号类别')
    is_admin = models.BooleanField(default=False)
    remark = models.CharField(max_length=64, null=True, blank=True, verbose_name='备注')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '用户表'
        verbose_name_plural = '用户表'
        db_table = 'User'
        ordering = ['id']