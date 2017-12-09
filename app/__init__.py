from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_pymongo import PyMongo
from flask_sslify import SSLify


app = Flask(__name__)
app.config.from_object('config')
lm = LoginManager()

lm.init_app(app)
lm.login_view = 'login'

mail = Mail(app)
mongo = PyMongo(app)
sslify = SSLify(app, subdomains=True, permanent=True)


from app import views
