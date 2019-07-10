from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:cool@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'randomsecretkey'

#mysql://root:build-a-blog@localhost/build-a-blog
#mysql+pymysql://build-a-blog:cool@localhost:8889/build-a-blog

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(240))

    def __init__(self, title, content):
        self.title = title
        self.content = content

@app.route('/')
def go():
    return redirect("/blog")

@app.route('/blog', methods=['POST', 'GET'])
def index():

    blogs = Blog.query.all()
    id = request.args.get('id')
    if id != None:
        blogs = Blog.query.filter_by(id=id).all()
        return render_template('specific.html',title="Build a Blog", blogs=blogs)

    return render_template('index.html',title="Build a Blog", blogs=blogs)

@app.route('/new', methods=['POST', 'GET'])
def new():

    if request.method == 'POST':
        blog_name = request.form['blog_name']
        blog_content = request.form['blog_content']
        if blog_name != "" and blog_content != "":
            new_blog = Blog(blog_name, blog_content)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id={}'.format(new_blog.id))
        else:
            flash('Enter both fields', 'error')

    blogs = Blog.query.all()
    return render_template('new.html',title="Build a Blog", blogs=blogs)


if __name__ == '__main__':
    app.run()