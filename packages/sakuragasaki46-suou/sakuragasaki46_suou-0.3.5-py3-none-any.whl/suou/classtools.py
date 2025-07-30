"""
Class and metaclass utilities.

---

Copyright (c) 2025 Sakuragasaki46.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
See LICENSE for the specific language governing permissions and
limitations under the License.

This software is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""

from typing import Any, Callable, Generic, Iterable, TypeVar

_T = TypeVar('_T')

class Wanted(Generic[_T]):
    """
    Placeholder for parameters wanted by Incomplete().
    Must be passed in place of the wanted argument.
    
    May take a getter function, a string or None.
    The getter function takes the same parameters as __set_name__(), those being
    the owner class and the assigned name.
    The string is an attribute name to be sourced from the owner class.
    None is replaced with the name.

    Owner class will call .__set_name__() on the parent Incomplete instance;
    the __set_name__ parameters (owner class and name) will be passed down here.
    """
    _target: Callable | str | None | Ellipsis
    def __init__(self, getter: Callable | str | None | Ellipsis):
        self._target = getter
    def __call__(self, owner: type, name: str | None = None) -> _T:
        if self._target is None or self._target is Ellipsis:
            return name
        elif isinstance(self._target, str):
            return getattr(owner, self._target)
        elif callable(self._target):
            try:
                return self._target(owner, name)
            except TypeError:
                return self._target(owner)
        else:
            raise TypeError(f'Wanted() requires a str, callable, or None, got {self._target.__class__.__name__!r}')

class Incomplete(Generic[_T]):
    """
    functools.partial() emulation for use in class properties.
    Object is instantiated when .__set_name__() is called.

    Missing arguments must be passed in the appropriate positions
    (positional or keyword) as a Wanted() object.
    """
    # XXX disabled for https://stackoverflow.com/questions/45864273/slots-conflicts-with-a-class-variable-in-a-generic-class
    #__slots__ = ('_obj', '_args', '_kwargs')
    _obj = Callable[Any, _T]
    _args: Iterable
    _kwargs: dict
    def __init__(self, obj: Callable[Any, _T] | Wanted, *args, **kwargs):
        if isinstance(obj, Wanted):
            self._obj = lambda x: x
            self._args = (obj, )
            self._kwargs = {}
        else:
            self._obj = obj
            self._args = args
            self._kwargs = kwargs
    def __set_name__(self, owner, name: str):
        args = []
        for arg in self._args:
            if isinstance(arg, Wanted):
                args.append(arg(owner, name))
            else:
                args.append(arg)
        kwargs = dict()
        for ak, av in self._kwargs.items():
            if isinstance(av, Wanted):
                kwargs[ak] = av(owner, name)
            else:
                kwargs[ak] = av
        self._args = args
        self._kwargs = kwargs

        setattr(owner, name, self.instance())
    def instance(self, /) -> _T:
        if [x for x in self._args if isinstance(x, Wanted)]:
            raise RuntimeError('trying to instance an Incomplete')
        return self._obj(*self._args, **self._kwargs)
    @classmethod
    def unfold(cls, clsdict: dict) -> dict:
        for k, v in clsdict.items():
            if isinstance(v, Incomplete):
                clsdict[k] = v.instance()
        return clsdict

__all__ = (
    'Wanted', 'Incomplete'
)