# coding: utf-8
from django.contrib.postgres.fields import JSONField
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from adapter_client.core.domain import model


class Config(models.Model):

    class Meta:
        verbose_name = verbose_name_plural = (
            'Настройки клиента к Адаптеру СМЭВ'
        )

    adapter_address = models.URLField(
        verbose_name=model.Config.adapter_address.title,
        null=True, blank=True
    )
    app_mnemonics = models.CharField(
        verbose_name=model.Config.app_mnemonics.title,
        max_length=200,
        null=True, blank=True
    )
    node_mnemonics = models.CharField(
        verbose_name=model.Config.node_mnemonics.title,
        max_length=200,
        null=True, blank=True
    )
    send_request_retry_time = models.IntegerField(
        verbose_name=model.Config.send_request_retry_time.title,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(6000)
        ],
        default=model.Config.send_request_retry_time.default,
        help_text='сек',
        null=True, blank=True
    )
    send_request_retry_count = models.IntegerField(
        verbose_name=model.Config.send_request_retry_count.title,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(20)
        ],
        default=model.Config.send_request_retry_count.default,
        null=True, blank=True
    )
    get_request_retry_time = models.IntegerField(
        verbose_name=model.Config.get_request_retry_time.title,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(6000)
        ],
        default=3,
        help_text='сек',
        null=True, blank=True
    )
    find_request_retry_time = models.IntegerField(
        verbose_name=model.Config.find_request_retry_time.title,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(6000)
        ],
        default=30,
        help_text='сек',
        null=True, blank=True
    )


class Message(models.Model):

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    message_type = models.TextField(
        verbose_name=model.Message.message_type.title
    )
    body = models.TextField(
        verbose_name=model.Message.body.title
    )
    attachments = JSONField(
        verbose_name=model.Message.attachments.title,
        null=True, blank=True
    )
    client_id = models.TextField(
        verbose_name=model.Message.client_id.title,
        null=True, blank=True, unique=True
    )
    message_id = models.TextField(
        verbose_name=model.Message.message_id.title,
        null=True, blank=True, unique=True
    )
    reference_message_id = models.TextField(
        verbose_name=model.Message.reference_message_id.title,
        null=True, blank=True
    )
    reply_to = models.ForeignKey(
        'adapter_client.Message',
        verbose_name=model.Message.reply_to.title,
        on_delete=models.PROTECT,
        null=True, blank=True
    )

    test = models.BooleanField(
        verbose_name=model.Message.test.title,
        default=model.Message.test.default
    )

    timestamp = models.DateTimeField(
        verbose_name='Дата и время создания',
        auto_now_add=True,
    )


class OutgoingMessage(models.Model):
    """Исходящее сообщение.

    Требуется отправить в адаптер.
    """
    message = models.ForeignKey(Message, on_delete=models.PROTECT)
    status = models.IntegerField(
        verbose_name=model.OutgoingMessage.status.title,
        default=model.OutgoingStatus.new.id,
        choices=[
            (item.id, item.verbose) for item in model.OutgoingStatus
        ]
    )
    timestamp = models.DateTimeField(
        verbose_name=model.OutgoingMessage.timestamp.title
    )
    attempts = models.IntegerField(
        verbose_name=model.OutgoingMessage.attempts.title
    )


class IncomingMessage(models.Model):
    """Входящее сообщение.

    Может быть как ответом на Find так и ответом на Get запрос.
    Это сообщение требуется обработать сервисом.
    """
    message = models.ForeignKey(Message, on_delete=models.PROTECT)
    status = models.IntegerField(
        verbose_name=model.IncomingMessage.status.title,
        default=model.IncomingStatus.received.id,
        choices=[
            (item.id, item.verbose) for item in model.IncomingStatus
        ]
    )
    timestamp = models.DateTimeField(
        verbose_name=model.IncomingMessage.timestamp.title
    )


@receiver(post_save, sender=Config)
def reconfigure_tasks(sender, **kwargs):
    """Перенастройка фоновых задач при обновлении конфигурации.

    .. note::
       Необходимо избавиться от сигнала, возможно, event bus, pubsub или observer.

    """
    from adapter_client.tasks import configure
    configure()


class JournalEntry(models.Model):

    class Meta:
        verbose_name = 'Запись журнала обмена'
        verbose_name_plural = 'Записи журнала обмена',
        ordering = ('timestamp',)

    address = models.TextField(
        verbose_name=model.JournalEntry.address.title,
        null=True, blank=True
    )
    timestamp = models.DateTimeField(
        verbose_name=model.JournalEntry.timestamp.title,
        auto_now_add=True,
    )
    request_type = models.IntegerField(
        verbose_name=model.JournalEntry.type.title,
        choices=[
            (item.id, item.verbose) for item in model.RequestType
        ],
    )
    request = models.TextField(
        verbose_name=model.JournalEntry.request.title,
        null=True, blank=True
    )
    response = models.TextField(
        verbose_name=model.JournalEntry.response.title,
        null=True, blank=True
    )
    error = models.TextField(
        verbose_name=model.JournalEntry.error.title,
        null=True, blank=True
    )
    message = models.ForeignKey(
        verbose_name=model.JournalEntry.message.title,
        to=Message,
        on_delete=models.CASCADE,
        blank=True, null=True,
    )
