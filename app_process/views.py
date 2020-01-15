from django.shortcuts import render

# Create your views here.
from django.views import View

from app_process.models import OrderInfo
from system.mixin import LoginRequiredMixin


class OrderView(LoginRequiredMixin, View):
    def get(self, request):
        res = {
            'created': OrderInfo.objects.all().count(),
            'receive': OrderInfo.objects.filter(receive_status=0).count(),
            'finished': OrderInfo.objects.filter(receive_status=1, status=1).count()
        }

        return render(request, 'process/order_index.html', res)
