import os
import urllib

API_NAME = os.environ['api_name']
API_URI = os.environ['api_uri']
SERVER_NAME = os.environ['server_name']
SERVER_URI = os.environ['server_uri']

WTF_CSRF_ENABLED = True
SECRET_KEY = os.environ['secret_key']

MONGO_USERNAME = 'npdoty'
MONGO_PASSWORD = os.environ['mongodb_password']
MONGO_URI = 'mongodb://'+urllib.parse.quote_plus(MONGO_USERNAME)+':'+urllib.parse.quote_plus(MONGO_PASSWORD)+'@cluster0-shard-00-00-edece.mongodb.net:27017,cluster0-shard-00-01-edece.mongodb.net:27017,cluster0-shard-00-02-edece.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin'
MONGO_DBNAME = 'Cluster0'
DB_NAME = 'Cluster0'

valid_header = 'application/ld+json; profile="https://www.w3.org/ns/activitystreams"'
CONTENT_HEADERS = {'Content-Type': valid_header}
ACCEPT_HEADERS = {'Accept': valid_header}
# specified by ActivityPub/ActivityStreams
VALID_HEADERS = (
    'application/ld+json; profile="https://www.w3.org/ns/activitystreams"',
    'application/ld+json; profile=\https://www.w3.org/ns/activitystreams\'',
    'application/activity+json')
STRICT_HEADERS = True

# email server
MAIL_SERVER = 'smtp.mail.me.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

# administrator list
ADMINS = ['nick@npdoty.name']