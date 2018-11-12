from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key= "#someSecretString"

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created = db.Column(db.DateTime)

    def __init__(self, title, body, owner ):
        self.title = title
        self.body = body
        self.owner = owner
        self.created = datetime.utcnow()

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')
    
    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['index','blog','login','signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/',  methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route("/blog", methods=["GET", "POST"])
def display_blog():
    if "user" in request.args:
        user_id = request.args.get("user")
        user = User.query.get(user_id)
        user_blogs = Blog.query.filter_by(owner=user).all()
        return render_template("singleUser.html", page_title = user.username + "'s Posts!", 
                user_blogs=user_blogs)

    blog_id = request.args.get("id")
    if (blog_id) == None:
        blogs = Blog.query.all()
        return render_template("blog.html", title="All Post", blogs=blogs)
    else:
       blog = Blog.query.get(blog_id)
       return render_template("single_entry.html", title="Blog Entry", blog=blog)


@app.route("/newpost", methods=["GET", "POST"])
def newpost():
    if request.method == "POST":
        newpost_owner = User.query.filter_by(username=session['username']).first()
        newpost_title = request.form['title']
        newpost_body = request.form['body']
        new_blog = Blog(newpost_title, newpost_body, newpost_owner)
    
        db.session.add(new_blog)
        db.session.commit()

        url = "/blog?id=" + str(new_blog.id)
        return redirect(url)

    else:
        return render_template('new_entry.html', title="Create new blog entry")

@app.route("/signup", methods=['GET','POST'])
def signup():
    if request.method == 'GET':
        return render_template("signup.html")
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            username_error = "That username already exists"
            return render_template('signup.html', username_error=username_error)

        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
    else:
        return render_template('signup.html')
        
@app.route("/login", methods=['GET','POST'])
def login():

    if request.method == 'GET':
        if 'username' not in session:
            return render_template("login.html", page_title='Login')
        else:
            return redirect('/newpost')

    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')

        if user and user.password != password:
            password_error = "Incorrect Password"
            return render_template('login.html', password_error=password_error)

        if not user:
            username_error = "Incorrect Username"
            return render_template('login.html', username_error=username_error)

    else:
        return render_template('login.html')
   
@app.route("/logout")
def logout():
    del session['username']
    return redirect('/')

if __name__ == '__main__':
    app.run()