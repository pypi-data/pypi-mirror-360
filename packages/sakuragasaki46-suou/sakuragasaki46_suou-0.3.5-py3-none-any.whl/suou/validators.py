"""
Utilities for marshmallow, a schema-agnostic serializer/deserializer.

---

Copyright (c) 2025 Sakuragasaki46.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
See LICENSE for the specific language governing permissions and
limitations under the License.

This software is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""

import re

def matches(regex: str | int, /, length: int = 0, *, flags=0):
    """
    Return a function which returns true if X is shorter than length and matches the given regex.
    """
    if isinstance(regex, int):
        length = regex
        regex = '.*'
    def validator(s: str):
        return (not length or len(s) < length) and bool(re.fullmatch(regex, s, flags=flags))
    return validator


__all__ = ('matches', )