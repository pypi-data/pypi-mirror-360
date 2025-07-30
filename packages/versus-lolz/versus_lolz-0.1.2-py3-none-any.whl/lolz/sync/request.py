from .session import BaseSession
from .. import types as T
from . import error


__all__ = ["request"]


URL = "https://prod-api.lzt.market"


def request(
        session     : BaseSession,
        method      : str,
        path        : str,
        **kwargs) -> T.Object:

    params = {k: v for k, v in kwargs.items() if v is not None}
    _kwargs = {"params": params}

    if "_body" in kwargs:
        body = kwargs["_body"]
        del kwargs["_body"]
        _kwargs["json"] = body

    resp = session.request(method, URL + path, **_kwargs)

    if resp.status_code == 200:
        return T.Object(resp.json())
    elif resp.status_code == 400:
        raise error.BadRequest(errors = resp.json()["errors"])
    elif resp.status_code == 401:
        raise error.Unauthorized(errors = resp.json()["errors"])
    elif resp.status_code == 403:
        raise error.AccessDenied(errors = resp.json()["errors"])
    elif resp.status_code == 429:
        raise error.RateLimited(errors = resp.json()["errors"])
    elif resp.status_code == 500:
        raise error.ServerError(errors = resp.json()["errors"])
    elif resp.status_code == 502:
        raise error.BadGateway(errors=["Bad gateway"])
    elif resp.status_code == 503:
        raise error.ServiceUnavailable(errors = resp.json()["errors"])
    elif resp.status_code == 504:
        raise error.GatewayTimeout(errors = resp.json()["errors"])
    
    raise error.UnknownError(errors=[f"Server returned unexpected status code {resp.status_code}"])
