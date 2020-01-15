from custom import BreadcrumbMixin
from django.views.generic import TemplateView

from .mixin import LoginRequiredMixin


class SystemView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):  # BreadcrumbMixin, TemplateView

    template_name = 'system/system_index.html'


