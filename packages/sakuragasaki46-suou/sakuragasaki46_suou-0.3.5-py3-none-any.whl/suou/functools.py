"""
Function utilities (decorators et al.).

---

Copyright (c) 2025 Sakuragasaki46.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
See LICENSE for the specific language governing permissions and
limitations under the License.

This software is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""

from typing import Callable
import warnings
from functools import wraps

try:
    from warnings import deprecated
except ImportError:
    # Python <=3.12 does not implement warnings.deprecated
    def deprecated(message: str, /, *, category=DeprecationWarning, stacklevel:int=1):
        """
        Backport of PEP 702 for Python <=3.12.
        The stack_level stuff is not reimplemented on purpose because
        too obscure for the average programmer.
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*a, **ka):
                if category is not None:
                    warnings.warn(message, category, stacklevel=stacklevel)
                return func(*a, **ka)
            func.__deprecated__ = True
            wrapper.__deprecated__ = True
            return wrapper
        return decorator

## this syntactic sugar for deprecated() is ... deprecated, which is ironic.
## Needed move because VSCode seems to not sense deprecated_alias()es as deprecated.
@deprecated('use deprecated(message)(func) instead')
def deprecated_alias(func: Callable, /, message='use .{name}() instead', *, category=DeprecationWarning) -> Callable:
    """
    Syntactic sugar helper for renaming functions.

    DEPRECATED use deprecated(message)(func) instead
    """
    return deprecated(message.format(name=func.__name__), category=category)(func)

def not_implemented(msg: Callable | str | None = None):
    """
    A more elegant way to say a method is not implemented, but may get in the future.
    """
    def decorator(func: Callable) -> Callable:
        da_msg = msg if isinstance(msg, str) else 'method {name}() is not implemented'.format(name=func.__name__)
        @wraps(func)
        def wrapper(*a, **k):
            raise NotImplementedError(da_msg)
        return wrapper
    if callable(msg):
        return decorator(msg)
    return decorator

__all__ = (
    'deprecated', 'not_implemented'
)