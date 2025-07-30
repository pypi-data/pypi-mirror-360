# coding: utf-8
from abc import ABC
from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor
from typing import Generator
import logging

from django.utils.module_loading import import_string

from adapter_client.adapters.smev.interfaces.base import ExchangeResult
from adapter_client.adapters.smev.services.base import AbstractService
from adapter_client.adapters.smev.services.registry import ServiceRegistry
from adapter_client.core.domain import model

from ..base import AbstractIncomingMessageRepository
from ..base import AbstractJournal
from ..base import AbstractOutgoingMessageRepository
from ..db import config_repository
from .interfaces.base import AbstractInterface


logger = logging.getLogger(__name__)


class AbstractAdapter(ABC):

    """Адаптер СМЭВ."""

    _interface: AbstractInterface
    # хранилище исходящих сообщений
    _outgoing_message_repository: AbstractOutgoingMessageRepository
    # хранилище входящих сообщений
    _incoming_message_repository: AbstractIncomingMessageRepository
    # реестр сервисов обрабатывающих данные со стороны РИС
    _service_registry: ServiceRegistry

    # журнал обмена
    _journal: AbstractJournal

    def __init__(self):
        self._service_registry = ServiceRegistry()

    def register_service(
        self, service: AbstractService
    ) -> None:
        """Регистрирует сервис обрабатывающий сообщения в РИС."""
        assert isinstance(service, AbstractService)
        self._service_registry.register_service(service)
        logger.info('Service %s registered', type(service))

    @abstractmethod
    def process_pending(self) -> Generator[bool, None, None]:
        """Передача сообщений на обработку в РИС.

        Передаёт на обработку в РИС сообщения которые
        ранее не удалось успешно обработать.
        """
        self._reload_config()

    @abstractmethod
    def send(self, message: model.Message):
        """Получение сообщения из ИС для передачи в Адаптер СМЭВ."""
        self._reload_config()

    @abstractmethod
    def send_pending(self) -> Generator[ExchangeResult, None, None]:
        """Передача сообщений из очереди ИС в Адаптер СМЭВ."""
        self._reload_config()

    @abstractmethod
    def get_pending(self) -> ExchangeResult:
        self._reload_config()

    @abstractmethod
    def find_pending(self) -> Generator[ExchangeResult, None, None]:
        """Получение ответов на сообщения переданные в адаптер СМЭВ."""
        self._reload_config()

    def _reload_config(self) -> None:
        config = config_repository.load_config()
        self._interface = import_string(config.adapter_interface)(config)
        self._outgoing_message_repository = import_string(
            config.outgoing_message_repository
        )(config)
        self._incoming_message_repository = import_string(
            config.incoming_message_repository
        )(config)
        self._journal = import_string(config.journal)(config)
        logger.info('Adapter config reloaded')


class Adapter(AbstractAdapter):

    def _process_one(
        self,
        incoming_message: model.IncomingMessage
    ) -> model.IncomingMessage:

        """Передача одного сообщения на обработку в РИС."""
        message = incoming_message.message
        logger.info(
            'Processing message: %s' % message.client_id
        )
        try:
            service = self._service_registry.get_by_message_type(
                message.message_type)
        except ValueError:
            logger.error(
                'Service for this message was not found: %s, type: %s' % (
                    message.client_id,
                    message.message_type
                )
            )
        else:
            try:
                service.process_message(message)
            except Exception:
                logger.error(
                    'Processing failed for message: %s' % message.client_id)
            else:
                incoming_message.status = model.IncomingStatus.processed
                logger.info(
                    'Processing complete for message: %s' % message.client_id)
        return incoming_message

    def process_pending(self) -> Generator[model.IncomingMessage, None, None]:
        logger.info('Processing pending messages...')
        super().process_pending()
        incoming_messages = (
            self._incoming_message_repository.get_pending_messages()
        )
        with ThreadPoolExecutor() as executor:
            for incoming_message in executor.map(
                self._process_one, incoming_messages
            ):
                yield self._update_incoming_message(incoming_message)

    def send(self, message: model.Message):
        logger.info('Message received: %s', message.client_id)

        super().send(message)

        self._validate_message(message)
        self._enqueue_message(message)

    def _validate_message(self, message: model.Message):
        assert isinstance(message, model.Message)

    def _enqueue_message(self, message: model.Message):
        """Добавление исходящего сообщения в очередь"""
        assert message.id is None
        self._outgoing_message_repository.add(
            model.OutgoingMessage(message=message)
        )

    def _process_exchange_result(
        self,
        exchange_result: ExchangeResult
    ) -> ExchangeResult:
        """
        Добавление и попытка обработки входящего сообщения из ExchangeResult.
        """
        if (
            exchange_result.message_metadata and
            exchange_result.message_metadata.id is None
        ):
            assert isinstance(
                exchange_result.message_metadata,
                model.IncomingMessage
            )
            # отправляем в РИС на обработку и в хранилище
            exchange_result.message_metadata = (
                self._incoming_message_repository.add(
                    self._process_one(exchange_result.message_metadata)
                )
            )
        return exchange_result

    def _update_incoming_message(
        self,
        incoming_message: model.IncomingMessage
    ) -> model.IncomingMessage:
        assert incoming_message.id is not None
        return self._incoming_message_repository.update(incoming_message)

    def send_pending(self) -> Generator[ExchangeResult, None, None]:
        logger.info('Sending pending messages...')

        super().send_pending()

        for exchange_result in self._interface.send(
            *self._outgoing_message_repository.get_pending_messages()
        ):
            assert isinstance(exchange_result, ExchangeResult)
            assert isinstance(
                exchange_result.message_metadata,
                model.OutgoingMessage
            )
            self._outgoing_message_repository.update(
                exchange_result.message_metadata
            )
            self._journal.log_exchange_result(exchange_result)
            yield exchange_result

        logger.info('Pending messages sent')

    def get_pending(self) -> ExchangeResult:
        logger.info('Receiving ...')
        super().get_pending()
        exchange_result = self._process_exchange_result(self._interface.get())
        self._journal.log_exchange_result(exchange_result)
        return exchange_result

    def find_pending(self) -> Generator[ExchangeResult, None, None]:
        logger.info('Receiving pending replies...')

        super().find_pending()

        with ThreadPoolExecutor() as executor:
            for exchange_result in executor.map(
                self._process_exchange_result,
                self._interface.find(
                    *self._outgoing_message_repository.get_unreplied_messages()
                )
            ):
                self._journal.log_exchange_result(exchange_result)
                yield exchange_result

        logger.info('Pending replies received')


adapter = Adapter()
