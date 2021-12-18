from dotenv import load_dotenv
from flask import Flask, render_template, request
import requests
import os
import smtplib

load_dotenv()
app = Flask(__name__)

blog_url = os.environ["BLOG_API"]
my_email = os.environ["MY_EMAIL"]
my_password = os.environ["PASSWORD"]

response = requests.get(url=blog_url)
all_blog_posts = response.json()


@app.route('/')
def home():
    return render_template("index.html", blog_posts=all_blog_posts)


@app.route('/about')
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
