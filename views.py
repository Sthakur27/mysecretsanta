from flask import request, redirect, render_template, url_for, \
    stream_with_context, \
    flash, send_from_directory

from ssapp.models import *
from ssapp import app, db#, login_manager
#from flask_login import LoginManager, login_user, login_required
#import flask_login
from flask import request,session,abort
import random
import urllib
import random
from difflib import SequenceMatcher as SM
'''@login_manager.user_loader
def load_user(user_id):
    u=User.query.filter_by(email=user_id).first()
    return u
'''
def is_safe_url(target):
    ref_url = urllib.parse.urlparse(request.host_url)
    test_url = urllib.parse.urlparse(urllib.parse.urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def redirect_url():
    return request.args.get('next') or \
           request.referrer or \
           url_for('/')
def redirect_dest():
    dest_url = request.args.get('next')
    if not dest_url:
        dest_url = url_for('/')
    return redirect(dest_url)


#####login view#######
@app.route('/login', methods=['GET', 'POST'])
def login():
    username = str(request.form['username'])
    password = str(request.form['password'])
    user=User.query.filter(User.username.in_([username]),User.password.in_([password]) ).first()
    if(user):
        session['logged_in']=True
        session['currentuser']=user.id
        flash("Logged in successfully","bg-success")
        return redirect(url_for('home'))
    else:
        flash("Wrong Credentials","bg-success")
        return redirect(url_for('home'))

 
@app.route('/logout', methods=['GET','POST'])
def logout():
    session['logged_in']=False
    session['currentuser']=-1
    return redirect(url_for('home'))

@app.route('/home',methods=['GET','POST'])
@app.route('/',methods=['GET','POST'])
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        flash("Welcome",'bg-success')
        currentuser=User.query.get(session['currentuser'])
        uid=str(currentuser.id)
        pools=Pool.query.all()
        for i in range(len(pools)-1,-1,-1):
            if uid not in pools[i].users.split(","):
                del pools[i]
        msgs=Message.query.filter_by(to=session['currentuser']).filter_by(accepted=False).all()
        return render_template('home.html',user=currentuser,pools=pools,msgs=len(msgs))

@app.route('/newpool',methods=['GET','POST'])
def newpool():
    if not session.get('logged_in'):
        return redirect(url_for('home'))
    if request.method=='POST':
        if(request.form['name'] and request.form['password'] and request.form['description']):
              p=Pool(str(request.form['name']), str(request.form['password']),session['currentuser'],"{}".format(session["currentuser"]),str(request.form['description']))
              db.session.add(p)
              db.session.commit()
        return redirect(url_for('home'))
    else:
        return render_template('newpool.html')
@app.route('/createuser',methods=['GET','POST'])
def createuser():
    if request.method=='POST':
        if(request.form['username'] and request.form['password'] and request.form['email'] and request.form['wishlist'] ):
              u=User(str(request.form['username']),str(request.form['password']),str(request.form['email']),str(request.form['wishlist']))
              db.session.add(u)
              db.session.commit()
              flash("Added User", 'bg-success')
              session['logged_in']=True
              session['currentuser']=u.id
              return redirect(url_for('home'))
        flash("error")
        return redirect(url_for('home'))
    else: 
        return render_template('makeaccount.html')


@app.route('/searchpools',methods=['GET','POST'])
def searchpool():
    if request.method=='POST':
        term=request.form['term']
        pools=Pool.query.all()
        for i in range(len(pools)-1,-1,-1):
            if(SM(None,term,pools[i].name).ratio()<0.50):
                 del pools[i]
       
        return render_template('search.html',pools=pools)
    else:
        return render_template('home.html')
        

@app.route('/editpool/<int:poolid>',methods=['GET','POST'])
def editpool(poolid):
    pool=Pool.query.get(poolid)
    if request.method=='POST':
       try:
           if(request.form['activate']):
                #flash(request.form['activate'],"bg-success")
                temp=pool.users.split(',')
                random.shuffle(temp)
                for person in temp:
                    msg=Message(int(person),pool.name+"'s Secret Santa has started!")
                    db.session.add(msg)
                temp=",".join(temp)
                pool.users=temp
                pool.active=True
                
                db.session.add(pool)
                db.session.commit()
                flash("Group Activated! Messages have been sent out!","bg-success")
       except:
           pass
       pool.name=request.form['name']
       pool.password=request.form['password']
       pool.description=request.form['description']
       db.session.add(pool)
       db.session.commit()
       return redirect("/poolinfo/"+str(pool.id))
    if session['currentuser']==pool.admin:
       return render_template('editpool.html',pool=pool)  
    else:
       return redirect(url_for('/home'))


 
@app.route('/poolinfo/<int:poolid>',methods=['GET','POST'])
def poolinfo(poolid):
    pool=Pool.query.get(poolid)
    isMember=False
    currentuser=User.query.get(session['currentuser'])
    if request.method=='POST':
        if request.form['password']==pool.password:
            flash("Added to Group","bg-success")
            pool.users=pool.users+",{}".format(currentuser.id)
            msg=Message(currentuser.id,"Welcome to '"+pool.name+"' Group")
            db.session.add(msg)
            flash(msg.text,"bg-success")
            db.session.add(pool)
            db.session.commit()
            return redirect("/poolinfo/"+str(pool.id))
    if str(currentuser.id) in pool.users.split(','):
         isMember=True
    target=str(currentuser.id)
    if(pool.active==True):
         userlist=pool.users.split(',')
         target=userlist.index(str(currentuser.id))+1
         if(target>=len(userlist)):
              target=userlist[0]
         else:
              target=userlist[target]
    target=User.query.get(int(target))
    if(currentuser.id==pool.admin):
         return render_template('poolinfo.html',pool=pool,user=currentuser,isMember=True,admin=True,target=target)      
    else:
         return render_template('poolinfo.html',pool=pool,user=currentuser,isMember=isMember,admin=False,target=target)

@app.route('/msgs/<int:userid>',methods=['GET','POST'])
def usermsgs(userid):
    msgs=Message.query.filter_by(to=session['currentuser']).all()
    for msg in msgs:
        if(msg.accepted==0):
             msg.accepted=1
             db.session.add(msg)
             flash(msg.text,'bg-primary')
        else:
             flash(msg.text,'bg-success')
    db.session.commit()
    return render_template('usermsgs.html')
