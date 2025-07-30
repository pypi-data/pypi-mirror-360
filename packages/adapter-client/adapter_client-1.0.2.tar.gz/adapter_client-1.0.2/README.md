# Клиент для взаимодействия со СМЭВ3 посредством Адаптера
## Подключение
settings:

    INSTALLED_APPS = [
        'adapter_client'
    ]

services:
    
    from adapter_client.adapters.smev.adapter import adapter
    from adapter_client.adapters.smev.services.base import AbstractService
    from adapter_client.core.domain.model import Message


    class ROGDINFService(AbstractService):
        """
        Сервис обрабатывающий сообщения со сведениями о рождении.
        """
        message_type = 'urn://x-artefacts-zags-rogdinf/root/112-51/4.0.1'
    
        def process_message(self, message: Message):
			# сообщение на которое получен ответ
			reply_to = message.reply.to
            ...
    
    class ApplicationRequestService(AbstractService):
        """
        Сервис обрабатывающий запросы на зачисление (в качестве поставщика).
        """
        message_type = (
            'http://epgu.gosuslugi.ru/concentrator/kindergarten/3.2.1'
        )
        def process_message(self, message: Message):
            # обрабатываем сообщение-запрос
            ...

            # отправляем ответ на запрос
            adapter.send(
                Message(
                    # необходимо указать что сообщение является ответом
                    reply_to=message,
                    # остальные поля сообщения
                    ...
                )
            )


apps:

    from django.apps.config import AppConfig as AppConfigBase

    class AppConfig(AppConfigBase):

        name = __package__

        def ready(self):
            self._init_adapter_client()
            self._register_services()

        def _init_adapter_client(self):
            from adapter_client.config import ProductConfig, set_config
            from tasks import BaseTask

            set_config(ProductConfig(async_task_base=BaseTask))
        
        def _register_services(self):
        from adapter_client.adapters.smev.adapter import adapter
        from .services import ApplicationRequestService, ROGDINFService
        
        adapter.register_service(ApplicationRequestService(), ROGDINFService())


## Запуск тестов
    $ tox

## API

### Передача сообщения

    from adapter_client.adapters.smev.adapter import adapter
    from adapter_client.core.domain.model import Message

    message = Message(
        message_type='Foo',
        body='<foo>bar</foo>',
        attachments=['http://domain.com/attach1', 'http://domain.com/attach2'],
        test=True
    )

    adapter.send(message)

Дальнейшая обработка сообщений производится Celery в фоновом режиме.

### Получение ответа на сообщение

Ответы на отправленные сообщения собираются периодической задачей 
и передаются зарегистрированным сервисам.
