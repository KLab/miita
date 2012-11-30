# coding: utf-8
import flask
from flask import Flask
from flask.ext.pymongo import PyMongo
from flask.ext.googleauth import (GoogleFederated, GoogleAuth)
import markdown
import datetime


app = Flask(__name__)
app.secret_key = 'random secret key: Override on real environment'
mongo = PyMongo(app)
auth = GoogleFederated(app, 'klab.com')
#auth = GoogleAuth(app)


@app.route('/')
@auth.required
def index():
    articles = mongo.db.articles.find().limit(10).sort('_id', -1)
    return flask.render_template('index.html',
                                 articles=articles,
                                 user=flask.g.user)


@app.route('/article/<ObjectId:article_id>')
@auth.required
def article(article_id):
    article = mongo.db.articles.find_one_or_404(article_id)
    return flask.render_template('article.html',
                                 article=article,
                                 user=flask.g.user)


#@app.route('/edit/<ObjectId:article_id>')
@app.route('/edit')
@auth.required
def edit(article_id=None):
    if article_id is None:
        source = ''
    else:
        article = mongo.db.articles.find_one_or_404(article_id)
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
