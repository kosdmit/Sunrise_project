from abc import ABC, abstractmethod
from textwrap import dedent

import requests


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
    @abstractmethod
    def get_message(self):
        raise NotImplementedError(
            'Message constructor must implement a get_message method')


class CallbackMessageConstructor(MessageConstructor):
    def __init__(self, phone_number, is_new_phone):
        self.phone_number = phone_number
        self.is_new_phone = is_new_phone

    def get_message(self):
        message = dedent(f"""
            {'Поступил запрос на звонок от нового клиента'
             if self.is_new_phone else
             'Поступил повторный запрос на звонок от клиента'}
            Телефон: {self.phone_number}
            """)
        return message





