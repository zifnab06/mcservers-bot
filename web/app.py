__author__ = 'zifnab'
from flask import Flask, redirect, request, render_template, flash, abort
from flask_admin import Admin
from mongoengine import *
from flask_admin.contrib.mongoengine import ModelView

class Submission(Document):
    i = StringField()
    u = StringField()
    t = StringField()
    s = StringField()
    d = DateTimeField()
    r = BooleanField()
app = Flask(__name__)

admin = Admin(app, url='/mcservers/admin')
with app.app_context():
    import local_config
    app.config.from_object(local_config)
    connect('mcservers')


class PostView(ModelView):
    can_edit = False
    can_delete = False
    can_create = False
    column_default_sort = ('d', True)
    column_descriptions = dict(d='datetime that post was processed by bot', r='removed by mcservers-bot. does not include post removals by other moderators.')
    column_labels = dict(i='link', t='title', u='user', s='selftext', d='datetime', r='removed')
    column_searchable_list = ('t', 'u', 's')
    column_formatters = dict(i=lambda v, c, m, p: 'http://redd.it/{0}/'.format(m.i))
    pass

admin.add_view(PostView(Submission))



app.debug = app.config['DEBUG']

def run():
    app.run(
        host=app.config.get('HOST', None),
        port=app.config.get('PORT', None)
    )



if __name__ == '__main__':
    run()
