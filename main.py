from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:ruihuangblogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'super secret key'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable = False)
    content = db.Column(db.Text, nullable = False)
    deleted = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

    def __init__(self, title, content, user):
        self.title = title
        self.content = content
        self.deleted = False
        self.user = user

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), nullable = False)
    password = db.Column(db.String(30), nullable = False)
    #not hashing the password? SAD!
    blogs = db.relationship('Blog', backref='user')

    def __init__(self, username, password):
        self.username = username
        self.password = password
    
def valid_post(title, content):
    if len(title)==0 or len(content)==0:
        return False
    else:
        return True

def valid_username(username):
    while not re.match("^[A-Za-z0-9]+$", username):
        return False
    else:
        return True

def valid_password(password):
    while not re.match("^[A-Za-z0-9]{4,19}$", password):
        return False
    else:
        return True

def valid_passwordconf(password, passwordconf):
    if password != passwordconf:
        return False
    elif len(password)==0 or len(passwordconf)==0:
        return False
    else:
        return True

posts = []

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'home']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/newpost', methods = ['GET', 'POST'])
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        title_error = ''
        content_error = ''

        if valid_post(title, content) is True:
            user = User.query.filter_by(username=session['username']).first()
            new_post= Blog(title, content, user)
            db.session.add(new_post)
            db.session.commit()
            post_url = "/blog?id=" + str(new_post.id)
            return redirect(post_url)

        else:
            if len(title) == 0:
                title_error = 'Please key in the title!'
            if len(content) == 0:
                content_error = 'Please key in the content!'
            return render_template('blog.html', title="BLOG!", title_error=title_error, content_error=content_error)

    else:
        return render_template('blog.html', title="BLOG!")

@app.route('/blog', methods=['GET', 'POST'])
def blog():
    post_value = request.args.get('id')
    user_value = request.args.get('user')
    post = Blog.query.filter_by(id=post_value).first()
    user = User.query.filter_by(id=user_value).first()
    #handle case when request is a specific post
    if post:
        return render_template('viewpost.html', title="POST!", post = post)
    #handle case when request is a specific user
    elif user:
        post = Blog.query.filter_by(user_id = user_value).all()
        return render_template('viewuser.html', title= "USER!", user = user, posts = post)
    #handle case when all are requested
    else:
        posts = Blog.query.filter_by(deleted=False).all()
        return render_template('posts.html', title = "ALL POSTS!", posts = posts)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        user = User.query.filter_by(username=username).first()
        
        username_error = ' '
        password_error = ' '

        
        if user.username == username and user.password==password :
            return redirect("/newpost")
        else:
            if not user:
                username_error='User Does Not Exist!'
            if user.password != password:
                password_error='Incorrect Password!'
            return render_template('login.html', username_error=username_error, password_error=password_error)

    return render_template("login.html", title="Log In")

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        passwordconf=request.form['passwordconf']
        username_error = ' '
        password_error = ' '
        passwordconf_error = ' '
        registered_user = User.query.filter_by(username=username)

        if valid_username(username) and valid_password(password) and valid_passwordconf(password, passwordconf):
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
            
        else:
            if registered_user:
                username_error = 'Username taken!'
            if valid_username(username)==False:
                username_error='Invalid username!'
            if valid_password(password)==False:
                password_error='Invalid password!'
            if valid_passwordconf(password, passwordconf)==False:
                passwordconf_error='Password do not match!'
            return render_template('signup.html', username_error=username_error, password_error=password_error, passwordconf_error=passwordconf_error)
    
    return render_template("signup.html", title="Register!", username="")

@app.route('/', methods=['GET'])
def home():
    userlist = User.query.all()
    return render_template('index.html', title = "Users!", userlist = userlist)

@app.route('/logout', methods=['POST'])
def logout():
    del session['username']
    return redirect("/")

if __name__ == '__main__':
    app.run()