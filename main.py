from flask import Flask, flash, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '14t3!1t3c4'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(360))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32))
    password = db.Column(db.String(16))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


def logged_in_user():
    owner = User.query.filter_by(username=session['username']).first()
    return owner

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog', 'logout']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html',page_title="Blogz", users=users)

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if request.method =='POST':
        title = request.args.get('title')
        body = request.args.get('body')
        if title and body:
            return render_template('post.html', title=title, body=body)
    
    else:
        id = request.args.get('id')
        user = request.args.get('user')
        if id:
            blog = Blog.query.filter_by(id=id).first()
            return render_template('singleUser.html', blog=blog)
        elif user:
            blogs = Blog.query.filter_by(owner_id=user).all()
            return render_template('blog.html',page_title="Blogz", 
            blogs=blogs)
        else:
            blogs = Blog.query.all()
            return render_template('blog.html',page_title="Blogz", 
            blogs=blogs)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        if title and body:
            new_blog = Blog(title, body, logged_in_user())
            db.session.add(new_blog)
            db.session.flush()
            id = new_blog.id
            db.session.commit()
            blog = Blog.query.filter_by(id=id).first()
            return render_template('post.html', blog=blog)
        elif title == '':
            flash('Blog title cannot be blank.', 'error')
            return render_template('newpost.html', page_title="Blogz", title=title, body=body)
            #return render_template('newpost.html', page_title="Blogz", title=title, body=body, error='Blog title and body cannot be blank.')
        elif body == '':
            flash('Blog body cannot be blank.', 'error')
            return render_template('newpost.html', page_title="Blogz", title=title, body=body)
    else:
        return render_template('newpost.html', page_title="Blogz")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        
        elif not user:
            flash('Username does not exist.', 'error')

        elif password != user.password:
            flash('Password is incorrect.', 'error')

    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if username =='':
            flash('Username cannot be blank.', 'error')
            return redirect('/signup')
        elif len(username) < 3 or len(username) > 20:
            flash('Username must be between 3 and 20 characters.', 'error')
            return redirect('/signup')
        elif ' ' in username:
            flash('Username cannot contain spaces.', 'error')
            return redirect('/signup')
        elif password == "":
            flash('Password cannont be blank.', 'error')
            return redirect('/signup')
        elif len(password) <3 or len(password) > 20:
            flash('Password must be between 3 and 20 characters.', 'error')
            return redirect('/signup')
        elif ' ' in password:
            flash('Password cannot not contain spaces.', 'error')
            return redirect('/signup')
        elif password != verify:
            flash('Passwords do not match.', 'error')
            return redirect('/signup')

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        else:
            flash('Username exists.', 'error')

    return render_template('signup.html')

@app.route('/logout')
def logout():
    if 'username' in session:  
        del session['username']
        return redirect('/blog')
    else:
        return redirect('/blog')


if __name__ == '__main__':
    app.run()