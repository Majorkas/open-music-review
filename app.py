import random
from flask import Flask, flash, render_template, redirect, request, url_for
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.exceptions import NotFound

from models import User, Review,Form_Submission,User_Report, db

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

def allow_edit(review):
    return review.author == current_user

@app.route("/")
def index():
    # picks random review to display as the
    # featured review on the home page
    reviews = Review.query.all()
    amount_of_reviews = len(reviews)
    if amount_of_reviews > 1 :
        random_id = random.choice(range(1, amount_of_reviews,1))
        random_review = Review.query.filter_by(id = random_id).first()
        return render_template("index.html", featured_review = random_review)
    else:
        return render_template("index.html")


@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_action():
    username = request.form["username"]
    password = request.form["password"]
    user = User.query.filter_by(username=username).first()
    if not user:
        flash(f"No such user '{username}'")
        return redirect(url_for("login_page"))
    if user.validate_password(password) == False:
        flash(f"Invalid password for the user '{username}'")
        return redirect(url_for("login_page"))

    login_user(user)
    flash(f"Welcome back, {username}!")
    return redirect(url_for("index"))


@app.route("/create/account", methods=["GET"])
def create_account():
    return render_template("create_account.html")


@app.route("/create/account", methods=["POST"])
def create_account_action():
    username = request.form["username"]
    password = request.form["password"]
    if User.query.filter_by(username=username).first():
        flash(f"The username '{username}' is already taken")
        return redirect(url_for("create_account"))

    user = User(username=username) #type: ignore
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    flash(f"Welcome to Open Music Review {username}!")
    return redirect(url_for("index"))


@app.route("/logout", methods=["POST"])
@login_required
def logout_action():
    logout_user()
    flash("You have been logged out, Have a great day!")
    return redirect(url_for("index"))

@app.route("/reviews")
def review():
    return render_template("reviews.html", reviews=Review.query.all())


@app.route("/create/review", methods=["GET"])
@login_required
def create_review():
    return render_template("create_review.html")


@app.route("/create/review", methods=["POST"])
@login_required
def create_review_action():
    review = Review (
        artist = request.form["artist"], #type: ignore
        title = request.form["title"], #type: ignore
        content = request.form["content"], #type: ignore
        score = request.form["score"], #type: ignore
        song_link = request.form["song-link"], #type: ignore
        author = current_user #type: ignore
    )
    db.session.add(review)
    db.session.commit()
    return render_template("reviews.html", review=Review.query.all())


@app.route("/contact", methods=["GET"])
@login_required
def contact():
    return render_template("contact.html")


@app.route("/contact", methods=["POST"])
@login_required
def contact_action():
    form = Form_Submission(
        user = current_user, #type: ignore
        name = request.form["name"], #type: ignore
        email = request.form["email"], #type: ignore
        message = request.form["message"] #type: ignore
    )
    db.session.add(form)
    db.session.commit()
    flash(f"Thank you {current_user}, We have recieved your message and hope to get back to you soon")

    return redirect(url_for("index"))


@app.route("/report", methods=["GET"])
@login_required
def report():
    return render_template("report.html")


@app.route("/report", methods=["POST"])
@login_required
def report_action():
    review_id = request.form["review_id"]
    # make sure the review exists
    review = Review.query.get_or_404(int(review_id))
    report = User_Report(
        reporter = current_user, #type: ignore
        reason = request.form["report"], #type: ignore
        review_id = review.id #type: ignore
    )
    db.session.add(report)
    db.session.commit()
    flash(f"Report {report.id} on {review_id} submitted, Thank You!")
    return render_template("index.html")

@app.route("/adminView")
def admin_page():
    user = current_user
    if user.admin == False:
        flash("User Not Authorised")
        return redirect(url_for("index"))
    else:
        return render_template("adminView.html", form = Form_Submission.query.all(), reports = User_Report.query.all())

@app.errorhandler(NotFound)
def page_not_found(error_message):
    attempted_url = request.path
    return render_template("404.html", attempted_url=attempted_url), 404


if __name__ == "__main__":
    app.run(debug=True, port=8181)
