from typing import Dict
from fastapi import HTTPException

from functools import wraps
from pathlib import Path

from django.apps import AppConfig, apps
from django.conf import settings
from django.db import close_old_connections
from .consts import DEFAULT_CONNECTION_ID


def configure(
    config: Dict | None = None,
    url: str | None = None,
    conn_max_age: int | None = None,
    conn_health_checks: bool | None = None,
):
    if config is None and url is None:
        raise ValueError("You must provide either config or url")

    if url is not None:
        try:
            import dj_database_url

            config = dj_database_url.parse(url)
        except ImportError:
            raise Exception("Please install dj_database_url for url param support")

    if config is not None:
        if conn_max_age is not None:
            config["CONN_MAX_AGE"] = conn_max_age

        if conn_health_checks is not None:
            config["CONN_HEALTH_CHECKS"] = conn_health_checks

        settings.DATABASES = {
            DEFAULT_CONNECTION_ID: config,
        }


def _get_queryset(klass):
    if hasattr(klass, "_default_manager"):
        return klass._default_manager.all()
    return klass


def get_object_or_404(klass, *args, **kwargs):
    queryset = _get_queryset(klass)
    if not hasattr(queryset, "get"):
        klass__name = (
            klass.__name__ if isinstance(klass, type) else klass.__class__.__name__
        )
        raise ValueError(
            "First argument to get_object_or_404() must be a Model, Manager, "
            "or QuerySet, not '%s'." % klass__name
        )
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        raise HTTPException(
            status_code=404,
            detail="No %s matches the given query." % queryset.model._meta.object_name,
        )


async def aget_object_or_404(klass, *args, **kwargs):
    """See get_object_or_404()."""
    queryset = _get_queryset(klass)
    if not hasattr(queryset, "aget"):
        klass__name = (
            klass.__name__ if isinstance(klass, type) else klass.__class__.__name__
        )
        raise ValueError(
            "First argument to aget_object_or_404() must be a Model, Manager, or "
            f"QuerySet, not '{klass__name}'."
        )
    try:
        return await queryset.aget(*args, **kwargs)
    except queryset.model.DoesNotExist:
        raise HTTPException(
            status=404,
            detail=f"No {queryset.model._meta.object_name} matches the given query.",
        )


class OrmAppConfig(AppConfig):
    path: None

    def __init__(self, path, app_label, app_name="models"):
        self.path = path
        self.label = app_label

        super().__init__(
            app_name=app_name,
            app_module=path.parent,
        )


def use_models():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            close_old_connections()
            result = func(*args, **kwargs)
            close_old_connections()
            return result

        return wrapper

    return decorator


def init(
    models_file_or_module: str,
    debug: bool = False,
    app_label: str = "orm",
    default_tablespace: str = "",
):
    my_settings = {
        "DEFAULT_TABLESPACE": default_tablespace,
        "DEBUG": debug,
    }
    settings.configure(**my_settings)

    apps.populate(
        (OrmAppConfig(path=Path(models_file_or_module), app_label=app_label),)
    )
