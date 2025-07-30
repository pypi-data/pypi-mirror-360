# coding: utf-8
from typing import TYPE_CHECKING
from typing import Type
from typing import Union

from pydantic.fields import Field
import celery


if TYPE_CHECKING:
    from dataclasses import dataclass  # noqa
else:
    from pydantic.dataclasses import dataclass  # noqa


@dataclass
class ProductConfig:

    async_task_base: Type[celery.Task] = Field(
        title='Базовый класс фоновых задач'
    )


# Продукт-специфичная конфигурация
__product_config = None  # type: Union[ProductConfig, None]


def set_config(config: ProductConfig) -> None:
    global __product_config

    if not isinstance(config, ProductConfig):
        raise ValueError(f'{config} is not an instance of ProductConfig')

    __product_config = config


def get_config() -> ProductConfig:
    global __product_config

    if __product_config is None:
        raise ValueError('Config is not set')

    return __product_config
