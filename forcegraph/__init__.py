from flask import Flask, g
from flask_bootstrap import Bootstrap, WebCDN
import sqlite3

D3_VERSION = "4.7.1"

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')
Bootstrap(app)
app.extensions['bootstrap']['cdns']['d3'] = WebCDN('//cdnjs.cloudflare.com/ajax/libs/d3/{}/'.format(D3_VERSION))

from . import database
from . import views
