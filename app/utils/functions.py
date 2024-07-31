from decimal import Decimal
from typing import Union
from datetime import datetime
from .decorators import caster


@caster(type=Decimal)
def replace_decimals(obj: any) -> Union[float, int, any]:
    return int(obj) if obj % 1 == 0 else float(obj)


@caster(type=float)
def replace_to_decimal(obj: any) -> Union[Decimal, any]:
    return Decimal(str(obj))


cast_datetime_to_isoformat = caster(type=datetime)(datetime.isoformat)
