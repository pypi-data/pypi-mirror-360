"""
Utilities for Flask-SQLAlchemy binding.

---

Copyright (c) 2025 Sakuragasaki46.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
See LICENSE for the specific language governing permissions and
limitations under the License.

This software is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""

from functools import partial
from typing import Any, Callable, Never

from flask import abort, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Session

from .codecs import want_bytes
from .sqlalchemy import AuthSrc, require_auth_base

class FlaskAuthSrc(AuthSrc):
    '''
    
    '''
    db: SQLAlchemy
    def __init__(self, db: SQLAlchemy):
        super().__init__()
        self.db = db
    def get_session(self) -> Session:
        return self.db.session
    def get_token(self):
        if request.authorization:
            return request.authorization.token
    def get_signature(self) -> bytes:
        sig = request.headers.get('authorization-signature', None)
        return want_bytes(sig) if sig else None
    def invalid_exc(self, msg: str = 'Validation failed') -> Never:
        abort(400, msg)
    def required_exc(self):
        abort(401, 'Login required')

def require_auth(cls: type[DeclarativeBase], db: SQLAlchemy) -> Callable:
    """
    Make an auth_required() decorator for Flask views.

    This looks for a token in the Authorization header, validates it, loads the
    appropriate object, and injects it as the user= parameter.

    NOTE: the actual decorator to be used on routes is **auth_required()**,
    NOT require_auth() which is the **constructor** for it.

    cls is a SQLAlchemy table.
    db is a flask_sqlalchemy.SQLAlchemy() binding.

    Usage:

    auth_required = require_auth(User, db)

    @route('/admin')
    @auth_required(validators=[lambda x: x.is_administrator])
    def super_secret_stuff(user):
        pass
        
    NOTE: require_auth() DOES NOT work with flask_restx.
    """
    def auth_required(**kwargs):
        return require_auth_base(cls=cls, src=FlaskAuthSrc(db), **kwargs)

    auth_required.__doc__ = require_auth_base.__doc__

    return auth_required


__all__ = ('require_auth', )
