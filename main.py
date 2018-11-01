from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://build-a-blog:lanstar@localhost:8889/post"
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
app.secret_key = '123'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    db_title = db.Column(db.String(120))
    db_body = db.Column(db.String(10000))
    db_date = db.Column(db.String(120))
    deleted = db.Column(db.Boolean)

    def __init__(self, title, body, date):
        self.db_title = title
        self.db_body = body
        self.db_date = date
        self.deleted = False
    
    def __repr__(self):
        return "<Post %r>" % self.db_title

#get the previous entries in reverse order
def get_entries():
    return Post.query.filter_by(deleted=False).order_by(Post.id.desc()).all()

#delete an entry
@app.route("/del-entry", methods=['POST'])
def del_entry():
    post_id = request.form['post_id']
    print(post_id)
    
    deleted_post = Post.query.get(post_id)
    print(deleted_post)
    deleted_post.deleted = True
    db.session.add(deleted_post)
    db.session.commit()

    return redirect("/")

#display an entry on its own page
@app.route("/entry")
def single_entry():
    post_id = request.args.get("id")
    display_entry = Post.query.filter_by(id=post_id).first()

    if display_entry not in get_entries():
        flash("Entry ID '{0}' does not exist. ".format(post_id), "error")
        return redirect("/")

    return render_template('singleentry.html', post=display_entry)

#display new entry page
@app.route("/new-entry")
def new_entry():
    return render_template('newentry.html')

#add a new entry to database
@app.route("/add-entry", methods=['GET', 'POST'])
def add_entry():
    no_error = True

    if request.method == "POST":
        new_title = request.form['title']
        new_body = request.form['body']
    
    if new_title == "":
        flash("Please add a title. ", "error")
        no_error = False
    
    if new_body == "":
        flash("Please write an entry. ", "error")
        no_error = False

    if no_error:
        new_entry = Post(new_title, new_body, get_date())

        db.session.add(new_entry)
        db.session.commit()
        fetch_post = Post.query.filter_by(db_title=new_title).first()
        return redirect("/entry?id="+str(fetch_post.id))
    
    else:
        return render_template('newentry.html',entry_title=new_title, entry_body=new_body)

def get_date():
    postdate = datetime.datetime.now()
    at_date = postdate.strftime("%b %d %Y")
    at_time = postdate.strftime("%I:%M %p")
    return at_time+" | "+at_date

@app.route("/")
def index():

    return render_template('entries.html', post_list=get_entries())

if __name__ == "__main__":
    app.run()