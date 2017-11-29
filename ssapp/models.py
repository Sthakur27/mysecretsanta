from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from ssapp import db
#engine = create_engine('sqlite:///ss.db', echo=True)
#Base = declarative_base()
########################################################################
class User(db.Model):
    __tablename__="users" 
    id = db.Column(db.Integer, db.Sequence('user_seq',start=1,increment=1), primary_key=True)
    username = db.Column(db.String(25))
    email = db.Column(db.String(45))
    password = db.Column(db.String(25))
    wishlist=db.Column(db.String(400))
    messages=db.relationship('Message',backref='user')
    pools=db.relationship('Pool',backref='user')
    #----------------------------------------------------------------------
    def __init__(self, username, password,email,wishlist):
        self.username = username
        self.password = password
        self.email=email
        self.wishlist=wishlist

class Pool(db.Model):
    __tablename__="pools"
    id = db.Column(db.Integer,db.Sequence('pool_seq',start=1,increment=1), primary_key=True)
    name=db.Column(db.String(40))
    users=db.Column(db.String(1000))
    # 0:false    1:true    for boolean integer columns
    active=db.Column(db.Integer)
    password=db.Column(db.String(30))
    admin=db.Column(db.Integer,db.ForeignKey('users.id'))
    description=db.Column(db.String(1000))
    messages=db.relationship('Message',backref='pool')
    def __init__(self,name,password,admin,users,description):
        self.users=users
        self.name=name
        self.password=password
        self.description=description
        self.admin=admin
        self.active=False

class Message(db.Model):
    __tablename__="messages"
    id=db.Column(db.Integer,db.Sequence('message_seq',start=1,increment=1), primary_key=True)
    text=db.Column(db.String(300))
    invitation=db.Column(db.Integer,db.ForeignKey('pools.id'))
    accepted=db.Column(db.Integer)
    to=db.Column(db.Integer, db.ForeignKey('users.id'))
    def __init__(self,to,text):
        self.to=to
        self.text=text
        self.accepted=False

    
   
 
# create tables
#Base.metadata.create_all(engine)


