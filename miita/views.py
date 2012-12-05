# -*- coding: utf-8 -*-
import flask
from .application import auth
from .models import User, Item
import markdown
import datetime


bp = flask.Blueprint('miita', __name__)


@bp.before_request
@auth.required
def get_user():
    u"""flask.g.user を GoogleAuth が作ったオブジェクトから models.User に置き換える."""
    user = flask.g.user
    email = user.email
    name = user.last_name + ' ' + user.first_name
    user, _ = User.objects.get_or_create(name=name, email=email)
    flask.g.user = user


@bp.route('/')
def index():
    user = flask.g.user
    tags = user.follow_tags
    if not tags:
        items = Item.objects.order_by('-id')[:10]
    else:
        items = Item.objects(tags__in=tags).order_by('-id')[:10]
    items = list(items)
    return flask.render_template('index.html',
                                 articles=items,
                                 user=flask.g.user)


@bp.route('/follow')
def follow():
    user = flask.g.user
    tag = flask.request.args.get('tag')
    if tag:
        print tag
        user.follow_tags.append(tag)
        user.save()
    return "OK"


@bp.route('/tags/<tag>')
def tags(tag):
    items = Item.objects(tags=tag).order_by('-id')[:10]
    items = list(items)
    return flask.render_template('index.html',
                                 selected_tag=tag,
                                 articles=items,
                                 user=flask.g.user)


@bp.route('/items/<item_id>')
def items(item_id):
    item = Item.objects.get_or_404(id=item_id)
    return flask.render_template('article.html',
                                 article=item,
                                 user=flask.g.user)


@bp.route('/edit/<item_id>')
@bp.route('/edit')
def edit(item_id=None):
    if item_id is None:
        item = Item()
    else:
        item = Item.objects.get_or_404(id=item_id)
        if item.author != flask.g.user:
            flask.abort(403)
        source = item.source
        title = item.title
        tags = item.tags
    return flask.render_template('edit.html',
                                 item=item,
                                 user=flask.g.user)


@bp.route('/post', methods=['POST'])
def post():
    item_id = flask.request.form.get('article')
    source = flask.request.form.get('source')
    html = markdown.markdown(source,
                             output_format='html5',
                             extensions=['extra', 'codehilite', 'nl2br'],
                             safe_mode=True)

    if item_id:
        item = Item.objects.get_or_404(id=item_id)
        if item.author != flask.g.user:
            flask.abort(403)
    else:
        item = Item()
    item.source = source
    item.html = html
    item.title = flask.request.form.get('title')
    item.author = flask.g.user
    item.updated_at = datetime.datetime.utcnow()
    item.tags = flask.request.form.get('tags').split()
    item.save()
    return flask.redirect(flask.url_for('.items', item_id=item.id))
