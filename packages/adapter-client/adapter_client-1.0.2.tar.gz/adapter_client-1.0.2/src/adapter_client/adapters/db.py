# coding: utf-8
from dataclasses import asdict
from datetime import datetime
from typing import Generator
from typing import Iterable
from typing import Optional
from typing import Type
from typing import Union
from uuid import UUID

from django.db.models import Model as DjangoModel
from django.forms.models import model_to_dict

from adapter_client import models as db
from adapter_client.core.domain import model

from .base import AbstractConfigRepository
from .base import AbstractIncomingMessageRepository
from .base import AbstractJournal
from .base import AbstractOutgoingMessageRepository
from .smev.interfaces.base import ExchangeResult


class ConfigRepository(AbstractConfigRepository):

    def load_config(self) -> model.Config:
        return model.Config(
            **model_to_dict(
                db.Config.objects.get_or_create(pk=1)[0]
            )
        )

    def write_config(self, config: model.Config) -> None:
        assert isinstance(config, model.Config)
        db.Config.objects.update_or_create(
            pk=1, defaults=asdict(config)
        )


config_repository = ConfigRepository()


class RelatedToMessageMixin:

    """Примесь для хранилищ данных связанных с сообщением."""

    db_model_cls: DjangoModel

    @property
    def _qs(self):
        return self.db_model_cls.objects.select_related('message__reply_to')

    def _message_to_db(self, message: model.Message) -> model.Message:
        defaults = asdict(
            message,
            dict_factory=lambda x: {k: v for (k, v) in x if k != 'reply_to'}
        )

        if message.reply_to is not None:
            assert message.reply_to.id is not None
            defaults.update(
                reply_to_id=message.reply_to.id,
            )

        dbinstance, _ = db.Message.objects.update_or_create(
            pk=message.id, defaults=defaults
        )

        message.id = dbinstance.id
        return message

    def _message_from_db(self, dbinstance: db.Message) -> model.Message:

        message_data = model_to_dict(dbinstance)
        # извлекаем reply_to
        if dbinstance.reply_to is not None:
            message_data.update(
                reply_to=model.Message(**model_to_dict(dbinstance.reply_to))
            )

        return model.Message(**message_data)


class MessageMetadataRepositoryMixin:

    """Примесь для хранилищ служебных данных сообщений."""

    statuses_enum:  Type[model.NamedIntEnum]
    db_model_cls: Union[Type[db.OutgoingMessage], Type[db.IncomingMessage]]
    data_model_cls: Union[
        Type[model.OutgoingMessage],
        Type[model.IncomingMessage]
    ]

    def add(self, message_metadata: 'data_model_cls') -> 'data_model_cls':
        return self._to_db(message_metadata)

    def update(self, outgoing_message: 'data_model_cls') -> 'data_model_cls':
        return self._to_db(outgoing_message)

    def get_by_id(self, id_: int) -> 'data_model_cls':
        """
        Получить связку метаданных и сообщения внутреннему идентификатору.
        """
        return self._from_db(self.db_model_cls.objects.get(pk=id_))

    def get_by_message_id(
        self,
        message_id: Union[UUID, str]
    ) -> 'data_model_cls':
        return self._from_db(self._qs.get(message__message_id=message_id))

    def get_by_client_id(
        self,
        client_id: Union[UUID, str]
    ) -> 'data_model_cls':
        return self._from_db(self._qs.get(message__client_id=client_id))

    def _to_db(self, message_metadata: 'data_model_cls') -> 'db_model_cls':
        # сохраняем/обновляем само сообщение в БД
        if message_metadata.message:
            assert isinstance(message_metadata.message, model.Message)
            message_metadata.message = self._message_to_db(
                message_metadata.message
            )

        defaults = {
            **asdict(
                message_metadata,
                dict_factory=lambda x: {k: v for (k, v) in x if k != 'message'}
            ),
            **{'status': message_metadata.status.id},
            **{'message_id': message_metadata.message.id},
        }

        dbinstance, _ = self.db_model_cls.objects.update_or_create(
            pk=message_metadata.id, defaults=defaults
        )

        message_metadata.id = dbinstance.id
        return message_metadata

    def _from_db(self, dbinstance: 'db_model_cls') -> 'data_model_cls':
        def get_status(dbinstance: 'db_model_cls'):
            for item in dbinstance._meta.get_field('status').choices:
                if item[0] == dbinstance.status:
                    return self.statuses_enum(item)

        return self.data_model_cls(
            message=self._message_from_db(dbinstance.message),
            status=get_status(dbinstance),
            **model_to_dict(dbinstance, exclude={'message', 'status'})
        )


class OutgoingMessageRepository(
    RelatedToMessageMixin,
    MessageMetadataRepositoryMixin,
    AbstractOutgoingMessageRepository
):

    """Хранилище исходящих сообщений."""

    statuses_enum = model.OutgoingStatus
    db_model_cls = db.OutgoingMessage
    data_model_cls = model.OutgoingMessage

    def get_unreplied_messages(self) -> Generator[model.OutgoingMessage, None, None]:
        # id сообщений на которые уже получен ответ
        reply_ids = db.Message.objects.filter(
            reply_to_id__isnull=False
        ).values('reply_to')
        # перебираем исходящие сообщения на которые еще не был получен ответ
        for reply in db.OutgoingMessage.objects.filter(
            status=model.OutgoingStatus.sent.id,
        ).exclude(id__in=reply_ids).iterator():
            yield self._from_db(reply)

    def get_pending_messages(self) -> Generator[model.OutgoingMessage, None, None]:
        for reply in db.OutgoingMessage.objects.filter(
            attempts__lt=self._config.send_request_retry_count,
            status__in=(model.OutgoingStatus.new.id, model.OutgoingStatus.retry.id),
        ).iterator():
            yield self._from_db(reply)


class IncomingMessageRepository(
    RelatedToMessageMixin,
    MessageMetadataRepositoryMixin,
    AbstractIncomingMessageRepository
):

    """Хранилище входящих сообщений."""

    statuses_enum = model.IncomingStatus
    db_model_cls = db.IncomingMessage
    data_model_cls = model.IncomingMessage

    def get_pending_messages(self) -> Generator[
        model.IncomingMessage,
        None,
        None
    ]:
        for reply in db.IncomingMessage.objects.filter(
            status=model.IncomingStatus.received.id,
        ).iterator():
            yield self._from_db(reply)


class Journal(RelatedToMessageMixin, AbstractJournal):

    """Журнал обмена сообщениями."""

    db_model_cls = db.JournalEntry

    def log_exchange_result(
        self,
        exchange_result: ExchangeResult
    ) -> model.JournalEntry:
        return self._to_db(exchange_result)

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
        sort_fields = sort_fields or ()
        filter_params = {}

        if timestamp_from:
            filter_params.update(timestamp__gte=timestamp_from)
        if timestamp_to:
            filter_params.update(timestamp__lte=timestamp_to)
        if client_id:
            filter_params.update(message__client_id=client_id)
        if request_types:
            filter_params.update(
                request_type__in=(t.id for t in request_types)
            )

        qs = self._qs.filter(
            **filter_params
        ).order_by(*sort_fields)[offset:limit]

        for dbinstance in qs.iterator():
            yield self._from_db(dbinstance)

    def get_entry_by_id(self, _id: Union[str, int]) -> model.JournalEntry:
        return self._from_db(self._qs.get(pk=_id))

    @property
    def _qs(self):
        return db.JournalEntry.objects.select_related('message__reply_to')

    def _from_db(self, dbinstance: db.JournalEntry) -> model.JournalEntry:
        def get_type(dbinstance: 'db_model_cls'):
            for item in dbinstance._meta.get_field('request_type').choices:
                if item[0] == dbinstance.request_type:
                    return model.RequestType(item)
        message = None
        if dbinstance.message:
            message = self._message_from_db(dbinstance.message)

        return model.JournalEntry(
            message=message,
            timestamp=dbinstance.timestamp,   # model_to_dict пропускает это поле
            type=get_type(dbinstance),
            **model_to_dict(dbinstance, exclude={'message', 'request_type'})
        )

    def _to_db(
        self,
        result: ExchangeResult
    ) -> model.JournalEntry:
        message_id = (
            result.message_metadata.message.id
            if result.message_metadata
            else None
        )
        params = {
            'message_id': message_id,
            'request': result.request,
            'response': result.response,
            'address': result.address,
            'request_type': result.request_type.id,
            'error': result.error
        }
        dbinstance = db.JournalEntry.objects.create(
            **params
        )
        journal_entry = self._from_db(dbinstance)
        return journal_entry
