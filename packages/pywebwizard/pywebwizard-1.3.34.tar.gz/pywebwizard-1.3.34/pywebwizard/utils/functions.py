from .exceptions import FieldError
from functools import wraps
import re


def is_valid_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None


def required_fields(fields: list):
    def wrapper(f):
        @wraps(f)
        def wrapped(self, *args, **kwargs):
            _args = list(args)
            _action = _args[0]
            for _field in fields:
                if _field not in _action.keys():
                    raise FieldError(f"'{_field}' not defined in config for {_action.get('action')}")
            _args[0] = self.prepare_action(_action)
            return f(self, *args, **kwargs)
        return wrapped
    return wrapper


def action_name(name: str):
    def wrapper(f):
        f._action_name = name
        
        @wraps(f)
        def wrapped(self, *args, **kwargs):
            return f(self, *args, **kwargs)
        return wrapped
    return wrapper
