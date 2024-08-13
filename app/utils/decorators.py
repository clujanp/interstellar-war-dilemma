from collections import OrderedDict
from functools import lru_cache, wraps
from typing import Union, Tuple


def caster(type: Union[type, Tuple[type]]) -> callable:
    assert type not in (list, tuple, dict, OrderedDict), (
        "Casting type cannot be a collection")

    def decorator(cast_func: callable) -> callable:
        def caster_handler(obj: any) -> any:
            if isinstance(obj, (list, tuple)):
                for i, sub_obj in enumerate(obj):
                    obj[i] = caster_handler(obj=sub_obj)
                return obj
            if isinstance(obj, (dict, OrderedDict)):
                for k, v in obj.items():
                    obj[k] = caster_handler(obj=v)
                return obj
            if isinstance(obj, type):
                return cast_func(obj)
            return obj
        return caster_handler
    return decorator


def cached(func):
    @lru_cache(maxsize=None)
    def cached_method(self, *args, **kwargs):
        return func(self, *args, **kwargs)

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        return cached_method(self, *args, **kwargs)

    wrapper.cache_clear = cached_method.cache_clear
    return wrapper


def restrict_access(allowed_contexts: list) -> callable:
    def decorator(func: callable) -> callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> any:
            context = kwargs.pop('context', None)
            if context is None:
                raise ValueError(
                    "Context permissions must be passed as a keyword argument")
            if context not in allowed_contexts:
                raise PermissionError(
                    f"Access to {func.__name__} is restricted "
                    "in the current context."
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator
