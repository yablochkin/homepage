# coding: UTF-8
from flask import Flask
app = Flask(__name__)
app.config.from_object('blog.settings')
from flask import redirect
from flask import url_for
from flask import request
from flask import render_template
from flask import abort

from blog.decorators import admin_login_required
from blog.models import Post
from blog.forms import PostForm

from google.appengine.api import users
from werkzeug.contrib.atom import AtomFeed
from urlparse import urljoin


@app.context_processor
def auth():
    return dict(
            users=users,
            user=users.get_current_user(),
            logout=users.create_logout_url('/')
        )


@app.route('/')
def index():
    return redirect('about')


@app.route('/blog/')
def posts():
    posts = Post.all()
    if not users.is_current_user_admin():
        posts = posts.filter('hidden =', False)
    posts = posts.order('-created')
    return render_template('posts.html',
            posts=posts,
            section='home'
        )


@app.route('/<slug>/')
def view(slug):
    post = Post.all().filter('slug =', slug).get()
    if not post:
        abort(404)
    return render_template('view.html',
            section='home',
            post=post
        )


@app.route('/add/', methods=['GET', 'POST'])
@admin_login_required
def add():
    form = PostForm(request.form)
    if request.method == 'POST' and form.validate():
        post = Post(title=form.title.data, slug=form.slug.data, content=form.content.data)
        post.put()
        return redirect(post.get_url())
    return render_template('form.html',
            form=form,
            section='add'
        )


@app.route('/edit/<int:post_id>/', methods=['GET', 'POST'])
@admin_login_required
def edit(post_id):
    post = Post.get_by_id(post_id)
    form = PostForm(request.form, obj=post)
    if request.method == 'POST' and form.validate():
        form.populate_obj(post)
        post.put()
        return redirect(post.get_url())
    return render_template('form.html',
            form=form
        )


@app.route('/status/<int:post_id>/')
@admin_login_required
def change_status(post_id):
    post = Post.get_by_id(post_id)
    post.hidden = not post.hidden
    post.put()
    return redirect(post.get_url())


@app.route('/delete/<int:post_id>/')
@admin_login_required
def delete(post_id):
    post = Post.get_by_id(post_id)
    post.delete()
    return redirect(url_for('posts'))


@app.route('/about/')
def about():
    return render_template('about.html',
            section='about'
        )


@app.route('/contacts/')
def contacts():
    return render_template('contacts.html',
            section='contacts'
        )


@app.route('/links/')
def links():
    return render_template('about.html',
            section='links'
        )


@app.route('/login/')
def login():
    user = users.get_current_user()
    if user:
        return redirect(url_for('posts'))
    else:
        return redirect(users.create_login_url(url_for('posts')))


@app.route('/feed/')
def feed():
    feed = AtomFeed(u'Bers blog', feed_url=request.url, url=request.url_root)
    posts = Post.all().filter('hidden =', False).order('-created').fetch(limit=20)
    for post in posts:
        feed.add(post.title, unicode(post.content),
                 content_type='html',
                 author=u'Bers',
                 url=urljoin(request.url_root, post.get_url()),
                 updated=post.created,
                 published=post.created)
    return feed.get_response()
