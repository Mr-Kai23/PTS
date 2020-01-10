from custom import BreadcrumbMixin
from django.views.generic import TemplateView

from django.shortcuts import render
from django.views.generic.base import View
from .mixin import LoginRequiredMixin
from datetime import datetime
from django.db.models import Count, Q
from system.models import Structure, Menu
from datetime import timedelta


class SystemView(LoginRequiredMixin, View): #BreadcrumbMixin, TemplateView

    template_name = 'system/system_index.html'
    def get(self, request):
        res = dict()
        # 锁定当天日期,查找出当天的公布信息，如果数据库没有，则显示无
        now = datetime.now().date()+timedelta(days = 1)
        oldtime = now - timedelta(days = 3)

        fields = ['id', 'tag', 'relDate', 'relContent', 'relUser', 'other', ]

        # #django 查询时间段
        # res = dict(datas=list(Notice.objects.filter(relDate__range = (oldtime,now) ).values(*fields).order_by('-relDate')))

        menu = Menu.get_menu_by_request_url(url=self.request.path_info)
        if menu is not None:
            res.update(menu)

        return render(request, 'system/system_index.html', res)

