from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
import sqlalchemy_utils
import os
import smtplib
import datetime as dt

load_dotenv()
app = Flask(__name__)
ckeditor = CKEditor(app)
Bootstrap(app)
my_email = os.environ["MY_EMAIL"]
my_password = os.environ["PASSWORD"]
app.config['SECRET_KEY'] = os.environ["SECRET_KEY"]
# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f'<BlogPost {self.name}>'


# WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


if not sqlalchemy_utils.functions.database_exists('sqlite:///posts.db'):
    db.create_all()


@app.route('/')
def get_all_posts():
    posts = db.session.query(BlogPost).all()
    return render_template("index.html", blog_posts=posts)


@app.route("/post/<int:post_id>")
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    if requested_post:
        return render_template("post.html", post=requested_post)


@app.route("/edit-post/<post_id>", methods=["POST", "GET"])
def edit_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(title=requested_post.title,
                               subtitle=requested_post.subtitle,
                               author=requested_post.author,
                               img_url=requested_post.img_url,
                               body=requested_post.body)
    if edit_form.validate_on_submit():
        requested_post.title = edit_form.title.data
        requested_post.subtitle = edit_form.subtitle.data
        requested_post.img_url = edit_form.img_url.data
        requested_post.author = edit_form.author.data
        requested_post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for('show_post', post_id=post_id))
    return render_template("make-post.html", is_edit=True, form=edit_form)


@app.route("/new-post", methods=["POST", "GET"])
def new_post():
    form = CreatePostForm()
    today_date = dt.datetime.now()
    if form.validate_on_submit():
        post = BlogPost(title=form.title.data,
                        subtitle=form.title.data,
                        date=f"{today_date.strftime('%B')} {today_date.strftime('%d')}, {today_date.strftime('%Y')}",
                        body=form.body.data,
                        author=form.author.data,
                        img_url=form.img_url.data)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return render_template("make-post.html", form=form)


@app.route("/delete/<post_id>")
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route('/contact', methods=['POST', 'GET'])
def contact():
    if request.method == 'POST':
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()  # make the connection secure
            connection.login(user=my_email, password=my_password)
            connection.sendmail(from_addr="", to_addrs=my_email,
                                msg=f"Subject:I want to contact\n\n{request.form['message']}\n"
                                    f"{request.form['name']}\n{request.form['email']}\n{request.form['phone']}\n")
        return render_template("contact.html", used_method='post')
    else:
        return render_template("contact.html", used_method='get')


if __name__ == "__main__":
    app.run(debug=True)
