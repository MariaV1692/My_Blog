from dotenv import load_dotenv
from flask import Flask, render_template
import requests
import os

load_dotenv()
app = Flask(__name__)

blog_url = os.environ["BLOG_API"]

response = requests.get(url=blog_url)
all_blog_posts = response.json()


@app.route('/')
def home():
    return render_template("index.html", blog_posts=all_blog_posts)


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact')
def contact():
    return render_template("contact.html")


@app.route('/post/<int:post_id>')
def blog_post(post_id):
    requested_post = None
    post_id_str = str(post_id)
    for post in all_blog_posts:
        if post["id"] == post_id:
            requested_post = post
    return render_template("post.html", requested_post=requested_post, post_id_string=post_id_str)


if __name__ == "__main__":
    app.run(debug=True)
