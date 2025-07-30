from typing import Dict

from functools import wraps

from django.apps import AppConfig, apps
from django.conf import settings
from django.db import close_old_connections
from .consts import DEFAULT_CONNECTION_ID

def configure(config: Dict):
    settings.DATABASES = {
        DEFAULT_CONNECTION_ID: config
    }


class OrmAppConfig(AppConfig):
    path: None

    def __init__(self, path):
        self.path = path
        super().__init__(app_name="orm", app_module=path)


def use_models():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            close_old_connections()
            result = func(
                *args, **kwargs
            )
            close_old_connections()
            return result

        return wrapper

    return decorator



def init(models_file_or_module: str | Path, debug: bool = False):
    my_settings = {"DEFAULT_TABLESPACE": "", "DEBUG": debug,}
    settings.configure(**my_settings)
    apps.populate((OrmAppConfig(path=models_file_or_module),))
