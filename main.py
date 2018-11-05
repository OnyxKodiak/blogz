from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    created = db.Column(db.DateTime)

    def __init__(self, title, body ):
        self.title = title
        self.body = body
        self.created = datetime.utcnow()

@app.route("/")
def index():
    return redirect("/blog")

@app.route("/blog")
def blog_post():

    blog_id = request.args.get('id')
    if (blog_id):
        blog = Blog.query.get(blog_id)
        return render_template('single_entry.html', title="Blog Entry", blog=blog)
    
    all_post = Blog.query.all()   
    return render_template('index.html', title="All Post", all_post=all_post)
    


@app.route("/newpost", methods=["GET", "POST"])
def newpost():
     return render_template('new_entry.html', title="Create new blog entry")


if __name__ == '__main__':
    app.run()