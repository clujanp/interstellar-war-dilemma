from pydantic import field_validator
from collections import OrderedDict
from typing import Union, Tuple


def model_validator(*fileds, each_item: bool = False, **kwargs) -> callable:
    def decorator(func) -> callable:
        def wrapper(cls, v: any) -> any:
            # iterate over list case
            if each_item and isinstance(v, list):
                for item in v:
                    func(cls, item)
                return v
            # normal case
            func(cls, v)
            return v
        return field_validator(*fileds, **kwargs)(wrapper)
    return decorator


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
