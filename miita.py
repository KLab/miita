# coding: utf-8
import bson
import datetime
import flask
from flask import Flask
from flask.ext.googleauth import GoogleFederated  # for Google Apps
#from flask.ext.googleauth import GoogleAuth  # for Google account
import markdown
import pymongo
import sys
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

auth = GoogleFederated(app, 'klab.com')
#auth = GoogleAuth(app)


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


@app.route('/')
@auth.required
def index():
    articles = mongo.db.articles.find().sort('_id', -1)[:10]
    for article in articles:
        if not article.get('title'):
            article['title'] = flask.Markup(
                    article['source'].split('\n', 1)[0])
    return flask.render_template('index.html',
                                 articles=articles,
                                 user=flask.g.user)


@app.route('/article/<ObjectId:article_id>')
@auth.required
def article(article_id):
    article = mongo.db.articles.find_one(article_id)
    if article is None:
        flask.abort(404)
    return flask.render_template('article.html',
                                 article=article,
                                 user=flask.g.user)


@app.route('/edit/<ObjectId:article_id>')
@app.route('/edit')
@auth.required
def edit(article_id=None):
    if article_id is None:
        source = ''
    else:
        article = mongo.db.articles.find_one(article_id)
        if article is None:
            flask.abort(404)
        source = article.source
    return flask.render_template('edit.html',
                                 source=source,
                                 user=flask.g.user)


@app.route('/post', methods=['POST'])
@auth.required
def post():
    article_id = flask.request.form.get('article')
    source = flask.request.form.get('source')
    html = markdown.markdown(source,
                             output_format='html5',
                             extensions=['extra', 'codehilite'],
                             safe_mode=True)

    if article_id:
        article = mongo.db.articles.find_one_or_404(article_id)
        if article.get('author-email') != flask.g.user['email']:
            flask.abort(403)
    else:
        article = {}
    article['source'] = source
    article['html'] = html
    article['title'] = flask.request.form.get('title')
    article['author-name'] = flask.g.user['name']
    article['author-email'] = flask.g.user['email']
    article['last-update'] = datetime.datetime.utcnow()
    wrote_id = mongo.db.articles.save(article)
    return flask.redirect(flask.url_for('article', article_id=wrote_id))

if __name__ == '__main__':
    app.run(debug=True)
