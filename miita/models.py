# -*- coding: utf-8 -*-
from .application import mongo as m


class User(m.Document):
    email = m.StringField()
    name = m.StringField()


class Item(m.Document):
    source = m.StringField()
    html = m.StringField()
    title = m.StringField()
    author = m.ReferenceField(User, dbref=True)
    updated_at = m.DateTimeField()
    tags = m.SortedListField(m.StringField())