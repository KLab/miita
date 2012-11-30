# coding: utf-8
import flask
from flask import Flask
from flask.ext.pymongo import PyMongo
import markdown


app = Flask(__name__)
mongo = PyMongo(app)


@app.route('/')
def index():
    articles = mongo.db.articles.find().limit(10).sort('_id', -1)
    return flask.render_template('index.html', articles=articles)


@app.route('/article/<ObjectId:article_id>')
def article(article_id):
    article = mongo.db.articles.find_one_or_404(article_id)
    return flask.render_template('article.html', article=article)


#@app.route('/edit/<ObjectId:article_id>')
@app.route('/edit')
def edit(article_id=None):
    if article_id is None:
        source = ''
    else:
        article = mongo.db.articles.find_one_or_404(article_id)
        source = article.source
    return flask.render_template('edit.html', source=source)


@app.route('/post', methods=['POSt'])
def post():
    article_id = flask.request.form.get('article')
    source = flask.request.form.get('source')
    html = markdown.markdown(source,
                             output_format='html5',
                             extensions=['extra', 'codehilite'],
                             safe_mode=True)

    if article_id:
        article = mongo.db.articles.find_one_or_404(article_id)
        #todo: 編集権チェック
    else:
        article = {}
    article['source'] = source
    article['html'] = html
    wrote_id = mongo.db.articles.save(article)
    print wrote_id
    return flask.redirect(flask.url_for('article', article_id=wrote_id))

if __name__ == '__main__':
    app.run(debug=True)
