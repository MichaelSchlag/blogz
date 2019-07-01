from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8888/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(240))

    def __init__(self, title, content):
        self.title = title
        self.content = content


@app.route('/', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        blog_name = request.form['blog_name']
        blog_content = request.form['blog_content']
        new_blog = Blog(blog_name, blog_content)
        db.session.add(new_blog)
        db.session.commit()

    blogs = Blog.query.all()
    return render_template('index.html',title="Build a Blog", blogs=blogs)


if __name__ == '__main__':
    app.run()