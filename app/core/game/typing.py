from typing import Annotated, Callable, Literal, TypeAlias, TYPE_CHECKING
from functools import partial
from pydantic import AfterValidator
from ..domain.value_objects import Decision


if TYPE_CHECKING:
    from .dto import AstroBodyDTO  # type checking only


def uri_protocol_validator(
    uri: str,  mode: Literal['both', 'http', 'app'] = "both"
) -> str:
    match mode:
        case "both":
            if not uri.startswith("https://") and not uri.startswith("app://"):
                raise ValueError("URI supports https or app protocol")
        case "http":
            if not uri.startswith("https://"):
                raise ValueError("URI just supports https protocol")
        case "app":
            if not uri.startswith("app://"):
                raise ValueError("URI just supports app protocol")
    return uri


URIAppHttps = Annotated[str, AfterValidator(uri_protocol_validator)]
URIHttp = Annotated[
    str, AfterValidator(partial(uri_protocol_validator, mode="http"))]
URIApp = Annotated[
    str, AfterValidator(partial(uri_protocol_validator, mode="app"))]

StrategyCallable: TypeAlias = Callable[[str, 'AstroBodyDTO', float], Decision]
