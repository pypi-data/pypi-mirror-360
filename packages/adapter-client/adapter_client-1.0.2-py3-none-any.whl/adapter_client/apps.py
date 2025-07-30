# coding: utf-8
from importlib import import_module
from inspect import currentframe

from django.apps import apps
from django.apps.config import AppConfig as AppConfigBase
from django.db import ProgrammingError
from django.db import connections
from django.db import router
from django_postgres_partitioning import init
from django_postgres_partitioning import is_initialized
from django_postgres_partitioning import set_partitioning_for_model


class AppConfig(AppConfigBase):

    name = __package__

    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        self._configure_tasks()
        self._apply_partitioning()

    def _configure_tasks(self):
        """Настройка фоновых задач при старте приложения."""

        def is_in_management_command() -> bool:
            """Возвращает True, если код выполняется в рамках миграций Django."""
            from django.core.management import ManagementUtility

            def is_in_command(command):
                frame = currentframe()
                while frame:
                    if 'self' in frame.f_locals:
                        self_object = frame.f_locals['self']
                        if isinstance(self_object, command):
                            return True

                        if isinstance(self_object, ManagementUtility):
                            # Срабатывает при использовании функции в AppConfig
                            if 'subcommand' in frame.f_locals:
                                subcommand = frame.f_locals['subcommand']
                                return subcommand in ['migrate', 'test']

                    frame = frame.f_back

            modules = (
                'django.core.management.commands.migrate',
                'django.core.management.commands.makemigrations',
                'django.core.management.commands.sqlmigrate',
                'django.core.management.commands.showmigrations',
                'django.core.management.commands.test',
            )

            for module_name in modules:
                if is_in_command(import_module(module_name).Command):  # type: ignore
                    return True

            return False

        if is_in_management_command():
            return

        from adapter_client.tasks import configure
        configure()

    @staticmethod
    def _apply_partitioning():
        """Применяет механизм партиционирования для таблиц адаптера."""

        Message = apps.get_model('adapter_client', 'Message')
        OutgoingMessage = apps.get_model('adapter_client', 'OutgoingMessage')
        IncomingMessage = apps.get_model('adapter_client', 'IncomingMessage')
        JournalEntry = apps.get_model('adapter_client', 'JournalEntry')
        for model in (Message, OutgoingMessage, IncomingMessage, JournalEntry):

            db_alias = router.db_for_write(model)
            # Проверяем наличие таблицы
            with connections[db_alias].cursor() as cursor:
                try:
                    cursor.execute(
                        f'SELECT "id" FROM "{model._meta.db_table}" LIMIT 1'
                    )
                    cursor.fetchone()
                except ProgrammingError:
                    continue

            if not is_initialized(db_alias):
                init(db_alias)

            set_partitioning_for_model(
                model, 'timestamp', force=True
            )
