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
    @lru_cache(maxsize=None, typed=True)
    def cached_method(self, *args, **kwargs):
        return func(self, *args, **kwargs)
    return cached_method
