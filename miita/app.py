# -*- coding: utf-8 -*-
u"""
app オブジェクトの生成、カスタマイズをする
"""

import bson.tz_util
import datetime
from flask import Flask
from flask.ext.googleauth import GoogleFederated  # for Google Apps
from flask.ext.googleauth import GoogleAuth  # for Google account
import pymongo
from werkzeug.routing import BaseConverter
from werkzeug.utils import cached_property


class ObjectIdConverter(BaseConverter):
    u"""route に <ObjectId:xxxx> と書けるようにする"""
    def to_python(self, value):
        return bson.ObjectId(value)

    def to_url(self, value):
        return str(value)


app = Flask(__name__)
app.url_map.converters['ObjectId'] = ObjectIdConverter

app.secret_key = 'random secret key: Override on real environment'

# 環境変数が設定されてる場合、それで設定をオーバーライドする.
app.config.from_envvar('MIITA_SETTING_FILE', silent=True)


if 'DOMAIN' in app.config:
    auth = GoogleFederated(app, app.config['DOMAIN'])
else:
    auth = GoogleAuth(app)


# mogno.db.collection_name でアクセスできるようにするプロキシ
class MongoProxy(object):
    @cached_property
    def con(self):
        host = app.config.get('MONGO_URI', 'localhost')
        return pymongo.MongoClient(host)

    @cached_property
    def db(self):
        return self.con.miita

mongo = MongoProxy()


@app.template_filter()
def localtime(dt, format='%Y-%m-%d %H:%M:%S'):
    u"""utcの時間を日本時間で指定されたフォーマットで文字列化する."""
    local = dt + datetime.timedelta(hours=9)
    return local.strftime(format)
