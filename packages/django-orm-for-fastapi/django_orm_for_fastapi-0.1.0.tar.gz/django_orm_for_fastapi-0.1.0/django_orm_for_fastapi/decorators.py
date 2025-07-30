from django.db import close_old_connections
from functools import wraps

def with_django_models():
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

