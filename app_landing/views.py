import os

from django.views.generic import TemplateView, ListView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import sunrise_project.settings as settings
from app_landing.forms import OrderCreateForm
from app_landing.models import Project, Order
from app_landing.services import TelegramNotificationManager, \
    CallbackMessageConstructor

notification_manager = TelegramNotificationManager(
    token=os.environ['TELEGRAM_ADMIN_BOT_TOKEN_SUNRISE'],
    chat_id=settings.TELEGRAM_ADMIN_CHAT_ID,
)


# Create your views here.
class MainView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        featured_project = Project.objects.filter(is_featured=True, is_active=True).first()
        context['featured_project'] = featured_project

        projects = Project.objects.filter(is_featured=False, is_active=True).order_by('?')[:2]
        context['projects'] = projects

        order_create_form = OrderCreateForm()
        context['order_create_form'] = order_create_form

        return context


class ProjectListView(ListView):
    template_name = 'projects.html'
    model = Project
    paginate_by = 9


class OrderCreateView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        is_new_phone = not Order.objects.filter(phone_number=phone_number).exists()

        try:
            notification_manager.send_notification(
                message_constructor=CallbackMessageConstructor,
                data={'phone_number': phone_number, 'is_new_phone': is_new_phone},
            )
        except notification_manager.NotificationSendingError:
            return Response({'status': 'error'}, status=status.HTTP_424_FAILED_DEPENDENCY)

        return Response({'status': 'success'}, status=status.HTTP_201_CREATED)