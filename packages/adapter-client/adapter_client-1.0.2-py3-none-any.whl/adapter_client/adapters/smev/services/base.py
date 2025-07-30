# coding: utf-8
from abc import ABC

from adapter_client.core.domain.model import Message


class AbstractService(ABC):

    message_type: str

    def process_message(self, message: Message):
        """Обработка входящего сообщения."""
        raise NotImplementedError()
