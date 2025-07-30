# coding: utf-8
from abc import ABC
from abc import abstractmethod
from datetime import datetime
from typing import Generator
from typing import Iterable
from typing import Optional
from typing import Union

from adapter_client.core.domain import model

from .smev.interfaces.base import ExchangeResult


class AbstractConfigRepository(ABC):

    @abstractmethod
    def load_config(self) -> model.Config:
        """Загрузить кофигурацию адаптера."""

    @abstractmethod
    def write_config(self, config: model.Config) -> None:
        """Записать кофигурацию адаптера."""


class AbstractOutgoingMessageRepository(ABC):

    """Абстрактное хранилище исходящих сообщений."""

    def __init__(self, config: model.Config) -> None:
        assert isinstance(config, model.Config)
        self._config = config

    @abstractmethod
    def add(self, reply: model.OutgoingMessage) -> model.OutgoingMessage:
        """Добавить исходящее сообщение."""

    @abstractmethod
    def update(self, reply: model.OutgoingMessage) -> model.OutgoingMessage:
        """Обновить исходящее сообщение."""

    @abstractmethod
    def get_pending_messages(self) -> Generator[
        model.OutgoingMessage, None, None
    ]:
        """Получить исходящие сообщения ожидающие отправки."""

    @abstractmethod
    def get_unreplied_messages(self) -> Generator[
        model.OutgoingMessage, None, None
    ]:
        """Получить исходящие сообщения ожидающие ответа."""


class AbstractIncomingMessageRepository(ABC):

    """Абстрактное хранилище входящих сообщений."""

    def __init__(self, config: model.Config) -> None:
        assert isinstance(config, model.Config)
        self._config = config

    @abstractmethod
    def add(self, reply: model.IncomingMessage) -> model.IncomingMessage:
        """Добавить входящее сообщение."""

    @abstractmethod
    def update(self, reply: model.IncomingMessage) -> model.IncomingMessage:
        """Обновить входящее сообщение."""

    @abstractmethod
    def get_pending_messages(self) -> Generator[
        model.IncomingMessage, None, None
    ]:
        """Получить входящие сообщения ожидающие обработки в РИС."""


class AbstractJournal(ABC):

    """Абстрактный журнал обмена сообщениями."""

    def __init__(self, config: model.Config) -> None:
        assert isinstance(config, model.Config)
        self._config = config

    @abstractmethod
    def log_exchange_result(
        self,
        exchange_result: ExchangeResult
    ) -> model.JournalEntry:
        """Записывает результат обмена в журнал и возвращает запись журнала."""

    @abstractmethod
    def get_entries(
        self,
        offset: int = 0,
        limit: int = 25,
        sort_fields: Optional[Iterable[str]] = None,
        client_id: Optional[str] = None,
        request_types: Optional[Iterable[model.RequestType]] = None,
        timestamp_from: Optional[datetime] = None,
        timestamp_to: Optional[datetime] = None,
    ) -> Generator[model.JournalEntry, None, None]:
        """Возвращает генератор с записями журнала."""

    @abstractmethod
    def get_entry_by_id(self, _id: Union[str, int]) -> model.JournalEntry:
        """Возвращает одну запись по id."""
