import re
from abc import ABC, abstractmethod
from textwrap import dedent

import requests
from django.urls import reverse


class NotificationManager(ABC):
    @abstractmethod
    def send_notification(self, message_constructor, data):
        raise NotImplementedError(
            'Notification manager must implement a send_notification method')

    class NotificationSendingError(Exception):
        pass


class TelegramNotificationManager(NotificationManager):
    def __init__(self, token, chat_id):
        self.bot_token = token
        self.chat_id = chat_id

    def send_notification(self, message_constructor, data):
        text = self._get_text(message_constructor, data)

        response = requests.get(
            url=f'https://api.telegram.org/bot{self.bot_token}/sendMessage',
            params={'chat_id': self.chat_id, 'text': text})

        if response.ok is not True:
            raise self.NotificationSendingError('The notification has not been sent')

        return response.json()

    @staticmethod
    def _get_text(message_constructor, data):
        message_constructor = message_constructor(**data)
        return message_constructor.get_message()


class MessageConstructor(ABC):
    def __init__(self, phone_number, order, is_new_phone, request):
        self.phone_number = phone_number
        self.order = order
        self.is_new_phone = is_new_phone
        self.request = request

    @abstractmethod
    def get_message(self):
        raise NotImplementedError(
            'Message constructor must implement a get_message method')

    def _get_admin_url(self):
        protocol = 'https://' if self.request.is_secure() else 'http://'
        host = self.request.get_host()
        url = reverse('admin:%s_%s_change' % (self.order._meta.app_label, self.order._meta.model_name),
                      args=[self.order.pk])
        return protocol + host + url


class CallbackMessageConstructor(MessageConstructor):
    def get_message(self):
        message = dedent(f"""
            {'Поступил запрос на звонок от нового клиента'
             if self.is_new_phone else
             'Поступил повторный запрос на звонок от клиента'}
            {'Имя: ' + self.order.customer_name if self.order.customer_name else ''}
            Телефон: {self.phone_number}
            {'Статус: ' + self.order.status if self.order.status != self.order.DEFAULT_STATUS else ''}
            {'Заметки: ' + self.order.note if self.order.note else ''}
            Редактировать информацию о заявке: {self._get_admin_url()}
            """)

        message = re.sub(r'\n+', '\n', message)
        return message


class ProjectOrderMessageConstructor(MessageConstructor):
    def get_message(self):
        message = dedent(f"""
            {'Поступил заказ на разработку проекта от нового клиента'
             if self.is_new_phone else
             'Поступил заказ на разработку проекта от клиента'}
            {'Имя: ' + self.order.customer_name if self.order.customer_name else ''}
            Телефон: {self.phone_number}
            {'Тариф: ' + self.order.ordered_tariff.title if self.order.ordered_tariff else ''}
            {'Статус: ' + self.order.status if self.order.status != self.order.DEFAULT_STATUS else ''}
            {'Заметки: ' + self.order.note if self.order.note else ''}
            Редактировать информацию о заявке: {self._get_admin_url()}
            """)

        message = re.sub(r'\n+', '\n', message)
        return message







