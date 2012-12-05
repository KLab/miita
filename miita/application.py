# -*- coding: utf-8 -*-
u"""
app オブジェクトの生成、カスタマイズをする
"""

import datetime
from flask import Flask
from flask.ext.googleauth import (GoogleFederated, GoogleAuth)
from flask.ext.mongoengine import MongoEngine
from .util import DummyAuth


app = Flask(__name__)

app.config.update(
    SECRET_KEY = 'random secret key: Override on real environment',
    MONGODB_SETTINGS = {'DB': 'miita'}
)

# 環境変数が設定されてる場合、それで設定をオーバーライドする.
app.config.from_envvar('MIITA_SETTING_FILE', silent=True)


domain = app.config.get('DOMAIN')
if domain == 'dummy':
    auth = DummyAuth(app)
elif domain is None:
    auth = GoogleAuth(app)
else:
    auth = GoogleFederated(app, app.config['DOMAIN'])


mongo = MongoEngine(app)


@app.template_filter()
def localtime(dt, format='%Y-%m-%d %H:%M:%S'):
    u"""utcの時間を日本時間で指定されたフォーマットで文字列化する."""
    local = dt + datetime.timedelta(hours=9)
    return local.strftime(format)
