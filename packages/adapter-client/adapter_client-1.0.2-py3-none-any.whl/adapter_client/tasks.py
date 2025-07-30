# coding: utf-8
from inspect import isclass
from typing import Optional
from typing import Type
import logging

from django_celery_beat.models import IntervalSchedule
from django_celery_beat.models import PeriodicTask
from django_celery_beat.models import PeriodicTasks
import celery

from adapter_client.adapters.smev.adapter import adapter
from adapter_client.config import get_config
from adapter_client.core import services
from adapter_client.core.domain import model


logger = logging.getLogger(__name__)


def get_full_qualname(cls):
    """Получение полного имени класса.

    .. code-block:: python
      assert get_full_qualname(SomeTask) == 'adapter_client.tasks.SomeTask'

    """
    assert isclass(cls)
    return f'{cls.__module__}.{cls.__qualname__}'


def register_task(task: celery.Task) -> celery.Task:
    """Регистрирует задание в Celery."""

    logger.info('Register task %s', get_full_qualname(type(task)))

    if celery.VERSION < (4, 0, 0):
        return task

    if celery.VERSION == (4, 0, 0):
        # В Celery 4.0.0 нет метода для регистрации заданий,
        # исправлено в 4.0.1
        raise Exception('Use Celery 4.0.1 or later.')

    app = celery.app.app_or_default()
    return app.register_task(task)


task_base: Type[celery.Task] = get_config().async_task_base

logger.info('Tasks base is %s', task_base)


class SendTask(task_base):  # type: ignore

    description = 'Отправка сообщений в Адаптер СМЭВ'

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)
        success_count = fail_count = 0
        for res in adapter.send_pending():
            if res.message_metadata.message.message_id:
                success_count += 1
            else:
                fail_count += 1
        logger.info(
            'Отправлено сообщений: успешно %d, с ошибкой %d',
            success_count,
            fail_count,
        )


send_task = register_task(SendTask())


class GetTask(task_base):

    description = 'Обработка сообщений в РИС (Get)'

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)
        success_count = fail_count = 0
        for res in adapter.get_pending():
            if res.status is model.IncomingStatus.processed:
                success_count += 1
            else:
                fail_count += 1
        logger.info(
            'Обработано сообщений в РИС: успешно %d, c ошибкой %d',
            success_count,
            fail_count,
        )


process_task = register_task(GetTask())


class FindTask(task_base):

    description = 'Получение ответов на сообщения от Адаптера СМЭВ'

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)
        success_count = fail_count = 0
        for res in adapter.find_pending():
            if res.message_metadata and res.message_metadata.message:
                success_count += 1
            else:
                fail_count += 1
        logger.info(
            'Получено ответов на сообщения: успешно %d, с ошибкой %d',
            success_count,
            fail_count,
        )


find_task = register_task(FindTask())


class ProcessTask(task_base):

    description = 'Обработка сообщений в РИС (Process)'

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)
        success_count = fail_count = 0
        for res in adapter.process_pending():
            if res.status is model.IncomingStatus.processed:
                success_count += 1
            else:
                fail_count += 1
        logger.info(
            'Обработано сообщений в РИС: успешно %d, c ошибкой %d',
            success_count,
            fail_count,
        )


process_task = register_task(ProcessTask())


def configure(config: Optional[model.Config] = None) -> None:
    """Настройка фоновых задач."""

    logger.info('Configuring periodic tasks...')

    config = config or services.load_config()

    for task_cls, retry_time in (
        (SendTask, config.send_request_retry_time),
        (FindTask, config.find_request_retry_time),
        (ProcessTask, config.find_request_retry_time),
    ):
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=retry_time,
            period=IntervalSchedule.SECONDS,
        )
        task_name = get_full_qualname(task_cls)
        task = PeriodicTask.objects.update_or_create(
            task=task_name, name=task_name,
            defaults={'interval': schedule}
        )
        PeriodicTasks.changed(task)

    logger.info('Periodic tasks configured')
