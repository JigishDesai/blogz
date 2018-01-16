from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(360))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        newblog = Blog(title, body)
        db.session.add(newblog)
        db.session.commit()
    
    
    blogs = Blog.query.all()
    return render_template('blog.html', blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        newblog = Blog(title, body)
        db.session.add(newblog)
        db.session.commit()

        blogs = Blog.query.all()
        blogs.append(newblog)
        return redirect('/blog')

    return render_template('newpost.html')

@app.route('/blog/<int:id>')
def single_post(id=None):
    blog = Blog.query.filter_by(id=id).first()
    return render_template('singlepost.html', blog=blog)


if __name__ == "__main__":
    app.run()
