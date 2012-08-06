# coding: UTF-8
from google.appengine.ext import db
from flask import url_for
from pytils import dt

import datetime


class User(db.Model):
    name = db.StringProperty()


class Post(db.Model):
    title = db.StringProperty(required=True)
    slug = db.StringProperty()
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    hidden = db.BooleanProperty(default=True)

    def id(self):
        return self.key().id()
    id = property(id)

    def get_date(self):
        '''
        Formated date
        '''
        today = datetime.date.today()
        if today.year == self.created.year:
            return dt.ru_strftime(u'%d %B', self.created, inflected=True)
        else:
            return dt.ru_strftime(u'%B %Y', self.created)

    def get_url(self):
        return url_for('view', slug=self.slug)
