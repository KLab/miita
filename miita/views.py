import flask
from .app import auth, mongo, app
import markdown


def get_author_name():
    user = flask.g.user
    return user['last_name'] + ' ' + user['first_name']


@app.route('/')
@auth.required
def index():
    articles = mongo.db.articles.find().sort('_id', -1)[:10]
    articles = list(articles)
    for article in articles:
        if not article.get('title'):
            article['title'] = flask.Markup(
                article['source'].split('\n', 1)[0])
    return flask.render_template('index.html',
                                 articles=articles,
                                 user=flask.g.user)


@app.route('/tags/<tag>')
def tags(tag):
    articles = mongo.db.articles.find({'tags': tag}).sort('_id', -1)[:10]
    articles = list(articles)
    for article in articles:
        if not article.get('title'):
            article['title'] = flask.Markup(
                article['source'].split('\n', 1)[0])
    return flask.render_template('index.html',
                                 selected_tag=tag,
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
        source = title = ''
        tags = []
    else:
        article = mongo.db.articles.find_one(article_id)
        if article is None:
            flask.abort(404)
        if article.get('author-email') != flask.g.user['email']:
            flask.abort(403)
        source = article['source']
        title = article['title']
        tags = article['tags']
    return flask.render_template('edit.html',
                                 article_id=article_id,
                                 title=title,
                                 source=source,
                                 tags=tags,
                                 user=flask.g.user)


@app.route('/post', methods=['POST'])
@auth.required
def post():
    article_id = flask.request.form.get('article')
    source = flask.request.form.get('source')
    html = markdown.markdown(source,
                             output_format='html5',
                             extensions=['extra', 'codehilite', 'nl2br'],
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
    article['author-name'] = get_author_name()
    article['author-email'] = flask.g.user['email']
    article['last-update'] = datetime.datetime.utcnow()
    article['tags'] = flask.request.form.get('tags').split()
    wrote_id = mongo.db.articles.save(article)
    return flask.redirect(flask.url_for('article', article_id=wrote_id))

