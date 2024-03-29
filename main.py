from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:cool@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'randomsecretkey'

#mysql://root:build-a-blog@localhost/build-a-blog
#mysql+pymysql://build-a-blog:cool@localhost:8889/build-a-blog

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(240))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, content, author):
        self.title = title
        self.content = content
        self.author = author

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30))
    password = db.Column(db.String(30))
    blogs = db.relationship('Blog', backref="author")

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return str(self.username)


@app.route("/")
def index():
    #encoded_error = request.args.get("error")
    #return render_template('allblogs.html')
    #, watchlist=get_current_watchlist(logged_in_user().id), error=encoded_error and cgi.escape(encoded_error, quote=True)
    authors = User.query.all()
    return render_template('index.html',title="Blogz", authors=authors)

def logged_in_user():
    owner = User.query.filter_by(username=session['user']).first()
    return owner

@app.route('/blog', methods=['POST', 'GET'])
def allblogs():

    blogs = Blog.query.all()
    blogs.reverse()

    id = request.args.get('id')
    if id != None:
        blogs = Blog.query.filter_by(id=id).all()
        return render_template('specific.html',title="Blogz", blogs=blogs)

    author = request.args.get('author')
    if author != None:
        writer = User.query.filter_by(username=author).first()
        blogs = Blog.query.filter_by(author_id=writer.id).all()
        return render_template('author.html',title="Blogz", blogs=blogs)

    return render_template('allblogs.html',title="Blogz", blogs=blogs)

@app.route('/new', methods=['POST', 'GET'])
def new():

    author = User.query.filter_by(username=session['user']).first()

    if request.method == 'POST':
        blog_name = request.form['blog_name']
        blog_content = request.form['blog_content']
        if blog_name != "" and blog_content != "":
            new_blog = Blog(blog_name, blog_content, author)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id={}'.format(new_blog.id))
        else:
            flash('Enter both fields', 'error')

    blogs = Blog.query.all()
    return render_template('new.html',title="Build a Blog", blogs=blogs)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = User.query.filter_by(username=username)
        if users.count() == 1:
            user = users.first()
            if password == user.password:
                session['user'] = user.username
                flash('Welcome back, '+user.username)
                return redirect("/new")
        flash('Invalid username and password combination')
        return redirect("/login")

#todo: fix dis
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        cool_letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
        for letter in username:
            if not letter in cool_letters:
                flash('Username may only contain letters, numbers, and underscores')
                return redirect('/register')
        if len(username) < 3:
            flash('Username must be 3 characters or more')
            return redirect('/register')
        if User.query.filter_by(username=username).count() > 0:
            flash('That username is taken. Try ' + str(taken_count(username)))
            return redirect('/register')
        if password != verify:
            flash('Passwords must match')
            return redirect('/register')
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.username
        return redirect("/new")
    else:
        return render_template('register.html')

def taken_count(name):
    nums = "0123456789"
    dummy = 0
    front = ''
    back = ''
    tens = 1
    for pos in range(len(name)-1, 0, -1):
        if not name[pos] in nums:
            front = name[0:pos+1]
            back = name[pos+1:]
            break
        dummy += int(name[pos]) * tens
        tens *= 10
    dummy += 1
    new_name = str(front) + str(dummy)
    while User.query.filter_by(username=new_name).count() > 0:
        dummy += 1
        new_name = str(front) + str(dummy)
    return new_name

@app.route("/logout", methods=['POST'])
def logout():
    del session['user']
    return redirect("/")



@app.before_request
def require_login():
    endpoints_without_login = ['login', 'register', 'allblogs', 'index']
    if not ('user' in session or request.endpoint in endpoints_without_login):
        return redirect("/register")

if __name__ == '__main__':
    app.run()