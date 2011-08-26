# coding: UTF-8
from flask import Flask
app = Flask(__name__)
app.config.from_object('blog.settings')
from flask import g
from flask import redirect
from flask import url_for
from flask import session
from flask import request
from flask import render_template
from flask import request
from google.appengine.api import users
from werkzeug.contrib.atom import AtomFeed
from blog.decorators import admin_login_required
from blog.models import Post
from blog.forms import PostForm
from urlparse import urljoin

@app.before_request
def before_request():
    """
    if the session includes a user_key it will also try to fetch
    the user's object from memcache (or the datastore).
    if this succeeds, the user object is also added to g.
    """
    if 'user_key' in session:
        user = cache.get(session['user_key'])

        if user is None:
            # if the user is not available in memcache we fetch
            # it from the datastore
            user = User.get_by_key_name(session['user_key'])

            if user:
                # add the user object to memcache so we
                # don't need to hit the datastore next time
                cache.set(session['user_key'], user)

        g.user = user
    else:
        g.user = None

@app.context_processor
def auth():
    return dict(
            users=users,
            user=users.get_current_user(),
            logout=users.create_logout_url('/')
        )

@app.route('/')
def posts():
    posts = Post.all()
    if not users.is_current_user_admin():
        posts = posts.filter('hidden =', False)
    posts = posts.order('-created')
    return render_template('posts.html',
            posts=posts,
            section='home'
        )

@app.route('/<int:post_id>/')
def view(post_id):
    return render_template('view.html',
            post=Post.get_by_id(post_id)
        )

@app.route('/add/', methods=['GET', 'POST'])
@admin_login_required
def add():
    form = PostForm(request.form)
    if request.method == 'POST' and form.validate():
        post = Post(title=form.title.data, content=form.content.data)
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

def make_external(url):
    return urljoin(request.url_root, url)

@app.route('/feed/')
def feed():
    feed = AtomFeed(u'Последние посты', feed_url=request.url, url=request.url_root)
    posts = Post.all().order('-created').fetch(limit=20)
    for post in posts:
        feed.add(post.title, unicode(post.content),
                 content_type='html',
                 author=u'Bers',
                 url=make_external(post.get_url()),
                 updated=post.created,
                 published=post.created)
    return feed.get_response()
