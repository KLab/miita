# -*- coding: utf-8 -*-
from .application import mongo as m


class User(m.Document):
    email = m.StringField(primary_key=True)
    name = m.StringField()
    follow_tags = m.SortedListField(m.StringField())
    #follow_users = m.SortedListField(m.ReferenceField('User', dbref=True))


class Item(m.Document):
    source = m.StringField(default='')
    html = m.StringField(default='')
    title = m.StringField(default='')
    author = m.ReferenceField(User, dbref=True)
    updated_at = m.DateTimeField()
    tags = m.SortedListField(m.StringField())
