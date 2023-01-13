from functools import wraps
import inspect

import lightbulb


def parse_options():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in args:
                if isinstance(i, lightbulb.Context):
                    for k, e in i.options.items():
                        kwargs.update({k: e})
            return func(*args, **kwargs)

        return wrapper

    return decorator
