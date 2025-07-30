'''
Iteration utilities.

---

Copyright (c) 2025 Sakuragasaki46.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
See LICENSE for the specific language governing permissions and
limitations under the License.

This software is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
'''

from typing import Any, Iterable, MutableMapping, TypeVar
import warnings

_T = TypeVar('_T')

def makelist(l: Any) -> list:
    '''
    Make a list out of an iterable or a single value.
    '''
    if isinstance(l, (str, bytes, bytearray)):
        return [l]
    elif isinstance(l, Iterable):
        return list(l)
    elif l in (None, NotImplemented, Ellipsis):
        return []
    else:
        return [l]

def ltuple(seq: Iterable[_T], size: int, /, pad = None) -> tuple:
    """
    Truncate an iterable into a fixed size tuple, if necessary padding it.
    """
    seq = tuple(seq)[:size]
    if len(seq) < size:
        seq = seq + (pad,) * (size - len(seq))
    return seq

def rtuple(seq: Iterable[_T], size: int, /, pad = None) -> tuple:
    """
    Same as rtuple() but the padding and truncation is made right to left.
    """
    seq = tuple(seq)[-size:]
    if len(seq) < size:
        seq = (pad,) * (size - len(seq)) + seq
    return seq


def kwargs_prefix(it: dict[str, Any], prefix: str, *, remove = True, keep_prefix = False) -> dict[str, Any]:
    '''
    Subset of keyword arguments. Useful for callable wrapping.

    By default, it removes arguments from original kwargs as well. You can prevent by
    setting remove=False.

    By default, specified prefix is removed from each key of the returned
    dictionary; keep_prefix=True keeps the prefix on keys.
    '''
    keys = [k for k in it.keys() if k.startswith(prefix)]

    ka = dict()
    for k in keys:
        ka[k if keep_prefix else k.removeprefix(prefix)] = it[k]
    if remove:
        for k in keys:
            it.pop(k)
    return ka

def additem(obj: MutableMapping, /, name: str = None):
    """
    Syntax sugar for adding a function to a mapping, immediately.
    """
    def decorator(func):
        key = name or func.__name__
        if key in obj:
            warnings.warn(f'mapping does already have item {key!r}')
        obj[key] = func
        return func
    return decorator


__all__ = ('makelist', 'kwargs_prefix', 'ltuple', 'rtuple', 'additem')

