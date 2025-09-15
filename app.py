from flask import Flask, render_template, request, abort, url_for

import os, json
from werkzeug.utils import secure_filename
from twilio.rest import Client

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["POSTS_FILE"] = "posts.json"


TWILIO_ACCOUNT_SID = "AC61c49e6409b7326bff3153b41ef9ebdc"
TWILIO_AUTH_TOKEN = "e70bcdd423e1bfd5f877c7ac4ca5081f"
TWILIO_PHONE_NUMBER = "+14435959028"   
MY_PHONE_NUMBER = "+919861899492"      

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def load_posts():
    """Load posts safely from JSON file."""
    if not os.path.exists(app.config["POSTS_FILE"]):
        return []
    with open(app.config["POSTS_FILE"], "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []   

def save_posts(posts):
    """Save posts to JSON file."""
    with open(app.config["POSTS_FILE"], "w") as f:
        json.dump(posts, f, indent=2)


def load_posts():
    with open("posts.json", "r", encoding="utf-8") as f:
        return json.load(f)

@app.route("/")
def home():
    posts = load_posts()
    return render_template("index.html", posts=posts)

@app.route("/post/<int:post_id>")
def post_detail(post_id):
    posts = load_posts()
    post = posts[post_id]
    return render_template("post_detail.html", post=post)


@app.route("/search")
def search():
    query = request.args.get("q", "").lower()
    posts = load_posts()

    if not query:
        return render_template("index.html", posts=posts)

    filtered = [
        post for post in posts
        if query in post["title"].lower()
        or query in post["content"].lower()
        or query in post.get("full_content", "").lower()
    ]

    return render_template("index.html", posts=filtered, query=query)

@app.route("/gallery")
def gallery():
    posts = load_posts()
    return render_template("gallery.html", posts=posts)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    popup_message = None
    popup_type = None  # success or error

    if request.method == "POST":
        name = request.form["name"]
        subject = request.form["subject"]
        message = request.form["message"]
        number = request.form["number"]

        sms_text = f"📩 New Message from {name}\nPlace: {subject}\nPhone Number:{number}\n\n{message}"

        try:
            client.messages.create(
                body=sms_text,
                from_=TWILIO_PHONE_NUMBER,
                to=MY_PHONE_NUMBER
            )
            popup_message = "✅ Message sent successfully to your phone!"
            popup_type = "success"
        except Exception as e:
            popup_message = f"❌ Failed to send SMS: {str(e)}"
            popup_type = "error"

    return render_template("contact.html", popup_message=popup_message, popup_type=popup_type)


if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    if not os.path.exists(app.config["POSTS_FILE"]):
        with open(app.config["POSTS_FILE"], "w") as f:
            json.dump([], f)
    app.run(host='0.0.0.0', port=5000, debug=True)



