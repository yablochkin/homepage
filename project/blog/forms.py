# coding: UTF-8
from wtforms import Form, BooleanField, TextField, validators
from wtforms.widgets import TextArea


class PostForm(Form):
    title = TextField(u'Заголовок', [validators.Length(max=200), validators.Required()])
    slug = TextField(u'Slug', [validators.Length(max=50), validators.Required()])
    content = TextField(u'Содержание', [validators.Required()], widget=TextArea())
