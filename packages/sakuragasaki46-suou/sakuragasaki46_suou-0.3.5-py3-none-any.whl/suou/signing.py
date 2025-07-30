"""
Utilities for signing/integrity, on top of ItsDangerous.

---

Copyright (c) 2025 Sakuragasaki46.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
See LICENSE for the specific language governing permissions and
limitations under the License.

This software is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""

from abc import ABC
from base64 import b64decode
from typing import Any, Callable, Sequence
from itsdangerous import TimestampSigner

from suou.itertools import rtuple

from .functools import not_implemented
from .codecs import jsondecode, jsonencode, want_bytes, want_str
from .iding import Siq

class UserSigner(TimestampSigner):
    """
    itsdangerous.TimestampSigner() instanced from a user ID, with token generation and validation capabilities.
    """
    user_id: int
    def __init__(self, master_secret: bytes, user_id: int, user_secret: bytes, **kwargs):
        super().__init__(master_secret + user_secret, salt=Siq(user_id).to_bytes(), **kwargs)
        self.user_id = user_id
    def token(self) -> str:
        return self.sign(Siq(self.user_id).to_base64()).decode('ascii')
    @classmethod
    def split_token(cls, /, token: str | bytes) :
        a, b, c = want_str(token).rsplit('.', 2)
        return b64decode(a), b, b64decode(c)
    def sign_object(self, obj: dict, /, *, encoder=jsonencode, **kwargs):
        """
        Return a signed JSON payload of an object.

        MUST be passed as a dict: ser/deser it's not the signer's job.
        """
        return self.sign(encoder(obj), **kwargs)
    def unsign_object(self, payload: str | bytes, /, *, decoder=jsondecode, **kwargs):
        """
        Unsign and parse a JSON object signed payload. Returns a dict.
        """
        return decoder(self.unsign(payload, **kwargs))
    def split_signed(self, payload: str | bytes) -> Sequence[bytes]:
        return rtuple(want_bytes(payload).rsplit(b'.', 2), 3, b'')


class HasSigner(ABC):
    '''
    Abstract base class for INTERNAL USE.
    '''
    signer: Callable[Any, UserSigner]

    @classmethod
    def __instancehook__(cls, obj) -> bool:
        return callable(getattr(obj, 'signer', None))


__all__ = ('UserSigner', )