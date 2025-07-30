# coding: utf-8

from adapter_client.adapters.db import config_repository
from adapter_client.core.domain.model import Config


def load_config() -> Config:
    return config_repository.load_config()


def write_config(config: Config):
    return config_repository.write_config(config)
