# coding: UTF-8
from google.appengine.ext import db
from pytils import dt


class User(db.Model):
    name = db.StringProperty()

class Post(db.Model):
    title = db.StringProperty(required=True)
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
        return dt.ru_strftime(u'%d %B', self.created, inflected=True)
