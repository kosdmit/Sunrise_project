import os

from django.views.generic import ListView
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView

import sunrise_project.settings as settings
from app_landing.models import Project, Order, Tariff, TariffAdvantage
from app_landing.serializers import ProjectSerializer
from app_landing.services import TelegramNotificationManager, \
    CallbackMessageConstructor

notification_manager = TelegramNotificationManager(
    token=os.environ['TELEGRAM_ADMIN_BOT_TOKEN_SUNRISE'],
    chat_id=settings.TELEGRAM_ADMIN_CHAT_ID,
)


# Create your views here.
class MainView(ListView):
    template_name = 'index.html'
    model = Project
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['tariffs'] = Tariff.objects.all().order_by('price')
        context['tariff_advantages'] = TariffAdvantage.objects.all()

        return context


class ProjectListAPIView(generics.ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class OrderCreateView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        order = Order.objects.filter(phone_number=phone_number).first()
        is_new_phone = False if order else True

        if not order:
            order = Order.objects.create(phone_number=phone_number)

        try:
            notification_manager.send_notification(
                message_constructor=CallbackMessageConstructor,
                data={'phone_number': phone_number,
                      'order': order,
                      'is_new_phone': is_new_phone,
                      'request': request},
            )
        except notification_manager.NotificationSendingError:
            return Response({'status': 'error'}, status=status.HTTP_424_FAILED_DEPENDENCY)

        return Response({'status': 'success'}, status=status.HTTP_201_CREATED)