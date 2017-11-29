from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_bootstrap import Bootstrap
from flask import Flask
from flask_login import LoginManager
bootstrap = Bootstrap()

app = Flask(__name__)
app.secret_key='sidskey'

app.config.from_pyfile('config.py')
#app.config['SQLALCHEMY_POOL_SIZE'] = 20
app.config['SQLALCHEMY_POOL_RECYCLE'] = 280
db = SQLAlchemy(app)
migrate = Migrate(app, db)



bootstrap.init_app(app)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)

#import models after creating db and login manager
from ssapp.models import *
from ssapp.views import *

