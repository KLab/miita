# coding: utf-8
import bson.tz_util
import datetime
from flask import Flask
from flask.ext.googleauth import GoogleFederated  # for Google Apps
from flask.ext.googleauth import GoogleAuth  # for Google account
import pymongo
from werkzeug.routing import BaseConverter


class ObjectIdConverter(BaseConverter):
    def to_python(self, value):
        return bson.ObjectId(value)

    def to_url(self, value):
        return str(value)


app = Flask(__name__)
app.url_map.converters['ObjectId'] = ObjectIdConverter

app.secret_key = 'random secret key: Override on real environment'

# override settings with envvar
app.config.from_envvar('MIITA_SETTING_FILE', silent=True)


if 'DOMAIN' in app.config:
    auth = GoogleFederated(app, app.config['DOMAIN'])
else:
    auth = GoogleAuth(app)


class MongoProxy(object):
    @property
    def con(self):
        host = app.config.get('MONGO_URI', 'localhost')
        self.__dict__['con'] = con = pymongo.MongoClient(host)
        return con

    @property
    def db(self):
        return self.con.miita

mongo = MongoProxy()


@app.template_filter()
def localtime(dt, format='%Y-%m-%d %H:%M:%S'):
    u"""utcの時間を日本時間で指定されたフォーマットで文字列化する."""
    local = dt + datetime.timedelta(hours=9)
    return local.strftime(format)
