# -*- coding: utf-8 -*-

import flask
import flask_googleauth
import functools


class DummyAuth(object):
    u"""オフラインでも使える GoogleAuth 互換プラグイン."""
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

    def required(self, f):
        @functools.wraps(f)
        def wrapped(*args, **kw):
            flask.g.user = user = flask_googleauth.ObjectDict()
            user.email = 'dummy@example.com'
            user.last_name = 'dummy_last_name'
            user.first_name = 'dummy_first_name'
            user.name = 'dummy_first_name dummy_last_name'
            return f(*args, **kw)
        return wrapped