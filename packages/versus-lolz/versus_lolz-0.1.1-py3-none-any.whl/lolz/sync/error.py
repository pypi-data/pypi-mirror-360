from typing import Literal
import colorama as cr
import os


NO_COLOR = os.getenv('PY_DOTEST_NO_COLOR') == '1'


class LolzError(Exception):
    '''
    Base class for PyLolzAPI errors
    '''
    reason: str = "Lolz error"
    '''Reason for the error'''
    tip: str = "Useful information"
    '''Useful information that can help you to solve the problem'''

    errors: list[str]
    '''List of errors given by the API or library'''

    errors_source: Literal["api", "lib"]
    '''Source of the errors'''

    def __init__(self, reason: str | None = None,
                 tip: str | None = None,
                 errors: list[str] | None = None,
                 errors_source: Literal["api", "lib"] = "api") -> None:
        '''
        Initialize LolzError
        '''
        self.reason += (": " + reason) if reason else ''
        self.tip += (", " + tip) if tip else ''
        self.errors = errors if errors else []
        self.errors_source = errors_source
    
    def __str__(self) -> str:
        '''
        String representation of the error
        '''
        if NO_COLOR:
            srcs = {
                'api': 'Lolz Team API',
                'lib': 'Library',
            }
        else:
            srcs = {
                'api': cr.Fore.MAGENTA + 'Lolz Team API' + cr.Style.RESET_ALL,
                'lib': cr.Fore.MAGENTA + 'Library' + cr.Style.RESET_ALL,
            }
        return f"{self.reason}\n\nTip: {self.tip}\n\n" \
            f"Errors provided by the {srcs[self.errors_source]}:\n- " + \
            "\n- ".join(self.errors) + "\n"


class InvalidRequest(LolzError):
    reason: str = "Request is invalid"
    tip: str = "Check your request parameters"


class Unauthorized(LolzError):
    reason: str = "Authorization is required"
    tip: str = "Check your authorization token"


class AccessDenied(LolzError):
    reason: str = "Access is denied"
    tip: str = "Check your authorization token"


class RateLimited(LolzError):
    reason: str = "Rate limit is exceeded"
    tip: str = "Try again later"


class ServerError(LolzError):
    reason: str = "Server error"
    tip: str = "Try again later"


class BadGateway(LolzError):
    reason: str = "Bad gateway"
    tip: str = "Try again later"


class ServiceUnavailable(LolzError):
    reason: str = "Service unavailable"
    tip: str = "Try again later"


class GatewayTimeout(LolzError):
    reason: str = "Gateway timeout"
    tip: str = "Try again later"


class UnknownError(LolzError):
    reason: str = "Unknown error in library or in API"
    tip: str = "Please try to investigate the problem and " \
        "send a bug report to https://t.me/vi_is_raven"
