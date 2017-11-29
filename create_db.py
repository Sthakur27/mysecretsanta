from ssapp.config import SQLALCHEMY_DATABASE_URI
from ssapp.config import SQLALCHEMY_MIGRATE_REPO
from ssapp import db
import os.path
db.create_all()

