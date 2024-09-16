from app.core.interfaces.proxies import RestrictedAccessError, OverrideError


class RestrictedAccessError(Exception, RestrictedAccessError):
    ...


class OverrideError(Exception, OverrideError):
    ...
