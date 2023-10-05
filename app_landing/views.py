import os

from django.http import Http404
from django.views.generic import ListView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import sunrise_project.settings as settings
from app_landing.models import Project, Order, Tariff, TariffAdvantage, \
    Category
from app_landing.services import TelegramNotificationManager, \
    CallbackMessageConstructor, ProjectOrderMessageConstructor

notification_manager = TelegramNotificationManager(
    token=os.environ['TELEGRAM_ADMIN_BOT_TOKEN_SUNRISE'],
    chat_id=settings.TELEGRAM_ADMIN_CHAT_ID,
)


# Create your views here.
class MainView(ListView):
    template_name = 'index.html'
    paginate_by = 12

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.category_object = None

    def dispatch(self, request, *args, **kwargs):
        category_slug = self.request.GET.get('category')
        if category_slug:
            try:
                self.category_object = Category.objects.get(slug=category_slug)
            except Category.DoesNotExist:
                raise Http404

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.category_object:
            queryset = Project.objects.filter(category=self.category_object, is_active=True)
        else:
            queryset = Project.objects.filter(is_active=True)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['tariffs'] = Tariff.objects.all().order_by('price')
        context['tariff_advantages'] = TariffAdvantage.objects.all()

        context['categories'] = Category.objects.all()

        return context


class OrderCreateView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        order = Order.objects.filter(phone_number=phone_number).first()
        is_new_phone = False if order else True

        customer_name = request.data.get('customer_name')

        tariff_slug = request.data.get('tariff_slug')
        if tariff_slug:
            message_constructor = ProjectOrderMessageConstructor
            try:
                tariff = Tariff.objects.get(slug=tariff_slug)
            except Tariff.DoesNotExist:
                return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            message_constructor = CallbackMessageConstructor
            tariff = None


        if order:
            if tariff:
                order.ordered_tariff = tariff
            if customer_name:
                order.customer_name = customer_name

            order.save(update_fields=['ordered_tariff', 'customer_name'])
        else:
            order = Order.objects.create(
                phone_number=phone_number,
                customer_name=customer_name,
                ordered_tariff=tariff,
            )

        try:
            notification_manager.send_notification(
                message_constructor=message_constructor,
                data={'phone_number': phone_number,
                      'order': order,
                      'is_new_phone': is_new_phone,
                      'request': request},
            )
        except notification_manager.NotificationSendingError:
            return Response({'status': 'error'}, status=status.HTTP_424_FAILED_DEPENDENCY)

        return Response({'status': 'success'}, status=status.HTTP_201_CREATED)