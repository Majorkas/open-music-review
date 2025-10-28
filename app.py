from flask import Flask, flash, render_template, redirect, request, url_for
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.exceptions import NotFound

from models import User, Review, db

app = Flask(__name__)
app.config.from_object('config')  # Load configuration from config.py

login_manager = LoginManager(app)
login_manager.login_view = "login_page" # type: ignore

with app.app_context():
    db.init_app(app)
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_action():
    return render_template("index.html")

@app.route("/create/account", methods=["GET"])
def create_account():
    return render_template("create_account.html")

@app.route("/create/account", methods=["POST"])
def create_account_action():
    return render_template("login.html")

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    return render_template("index.html")

@app.route("/reviews")
def review():
    return render_template("reviews.html")

@app.route("/create/review", methods=["GET"])
@login_required
def create_review():
    return render_template("create_review.html")

@app.route("/create/review", methods=["POST"])
@login_required
def create_review_action():
    return render_template("reviews.html")


@app.route("/contact", methods=["GET"])
@login_required
def contact():
    return render_template("contact.html")

@app.route("/contact", methods=["POST"])
@login_required
def contact_action():
    return render_template("index.html")

@app.route("/report", methods=["GET"])
@login_required
def report():
    return render_template("report.html")

@app.route("/report", methods=["POST"])
@login_required
def report_action():
    return render_template("index.html")

@app.errorhandler(NotFound)
def page_not_found(error_message):
    attempted_url = request.path
    return render_template("404.html", attempted_url=attempted_url), 404


if __name__ == "__main__":
    app.run(debug=True, port=8181)
