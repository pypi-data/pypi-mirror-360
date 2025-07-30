# coding: utf-8
from typing import Type

from adapter_client.adapters.smev.services.base import AbstractService


class ServiceRegistered(Exception):
    def __init__(self, service: AbstractService, *args):
        super().__init__('Служба уже зарегистрирована', *args)

        assert isinstance(service, AbstractService)
        self.service = service


class ServiceRegistry:

    _registry: dict

    def __init__(self):
        self._registry = {}

    def register_service(
        self, service: AbstractService
    ) -> None:
        assert isinstance(service, AbstractService)

        if service.message_type in self._registry:
            raise ServiceRegistered(service)

        self._registry[service.message_type] = service

    def replace_service(
        self, service: AbstractService
    ) -> None:
        assert isinstance(service, AbstractService)

        self._registry[service.message_type] = service

    def get_by_type(self, type_: Type[AbstractService]) -> AbstractService:
        for service in self._registry.values():
            if isinstance(service, type_):
                return service

        raise ValueError('Служба данного типа не найдена')

    def get_by_message_type(self, message_type: str) -> AbstractService:
        try:
            return self._registry[message_type]
        except LookupError as e:
            raise ValueError('Служба данного типа не найдена') from e
