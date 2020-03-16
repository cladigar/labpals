import logging
from logging.handlers import SMTPHandler
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from labpals import momentsjs
from elasticsearch import Elasticsearch
from flask_bootstrap import Bootstrap
# import pusher

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config.from_object(Config)
# Set jinja template global
app.jinja_env.globals['momentjs'] = momentsjs.momentjs
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) if app.config['ELASTICSEARCH_URL'] else None
if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure()
        mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='App Failure',
                credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
# Realtime uploads
# pusher_client = pusher.Pusher(
#   app_id='963721',
#   key='97bc56a1eb806d1e3cc9',
#   secret='87f06f98f688bae03551',
#   cluster='eu',
#   ssl=True
# )


from labpals import routes, models, errors, search
