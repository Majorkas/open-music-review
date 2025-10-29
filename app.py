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

with app.test_request_context():
    '''Make default Admin user so you can access the admin panel'''
    admin = User(username="Admin") #type: ignore
    admin.hash_password("admin")
    admin.make_admin()
    db.session.add(admin)
    db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def index():
    # picks random review to display as the
    # featured review on the home page
    reviews = Review.query.all()
    random_review = random.choice(reviews) if reviews else None
    return render_template("index.html", featured_review=random_review)


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
        flash(f"Invalid password for the user '{username}'", "error")
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
    confirm = request.form["confirm_password"]



    if User.query.filter_by(username=username).first():
        flash(f"The username '{username}' is already taken", "error")
        return redirect(url_for("create_account"))
    if password != confirm:
            flash("Passwords do not match please try again", "error")
            return redirect(url_for("create_account"))
    else:
        user = User(username=username) #type: ignore
        user.hash_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f"Welcome to Open Music Review {username}!")
        return redirect(url_for("index"))


@app.route("/logout", methods=["GET"])
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
            album = request.form["album"], #type:ignore
            content = request.form["content"], #type: ignore
            score = request.form["score"], #type: ignore
            song_link = request.form["spotify_link"], #type: ignore
            author = current_user #type: ignore
        )
    db.session.add(review)
    db.session.commit()
    return render_template("reviews.html", reviews=Review.query.all())


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
        message = request.form["message"], #type: ignore
        user_id = current_user.id #type: ignore
    )
    db.session.add(form)
    db.session.commit()
    flash(f"Thank you {current_user.username}, We have recieved your message and hope to get back to you soon")

    return redirect(url_for("index"))


@app.route("/report/<int:review_id>", methods=["GET"])
@login_required
def report(review_id):
    review = Review.query.filter_by(id = review_id).first()
    if not review:
        flash("Review not found", "error")
        return redirect(url_for("review"))
    return render_template("report.html", review=review)

@app.route("/delete/<int:review_id>", methods=["GET"])
@login_required
def delete_review(review_id):
    review = Review.query.filter_by(id = review_id).first()
    if not review:
        flash("Review not found", "error")
        return redirect(url_for("admin_page"))
    if current_user.admin == False:
        flash("Not authorized to delete this review", "error")
        return redirect(url_for("index"))
    User_Report.query.filter_by(review_id=review.id).delete()
    db.session.delete(review)
    db.session.commit()
    flash("Review Removed")
    return redirect(url_for("admin_page"))

@app.route("/ignore/<int:report_id>", methods=["GET"])
@login_required
def ignore_report(report_id):
    report = User_Report.query.filter_by(id = report_id)
    if not report:
        flash("Report not found", "error")
        return redirect(url_for("admin_page"))
    if current_user.admin == False:
        flash("Not authorized to ignore this report", "error")
        return redirect(url_for("index"))
    report.delete()
    db.session.commit()
    flash("Report Ignored")
    return redirect(url_for("admin_page"))



@app.route("/report/<int:review_id>", methods=["POST"])
@login_required
def report_action(review_id):

    review = Review.query.filter_by(id = review_id).first()
    if not review:
        flash("Review not found", "error")
        return redirect(url_for("review"))
    report = User_Report(
        reporter = current_user, #type: ignore
        reason = request.form["report"], #type: ignore
        review_id = review.id #type: ignore
    )
    db.session.add(report)
    db.session.commit()
    flash(f"Report ID:{report.id} on Review:{review_id} submitted, Thank You!")
    return redirect(url_for("review"))

@app.route("/AdminView")
@login_required
def admin_page():
    '''
    renders the admin page but firsts checks to see if the current user
    is allowed to view the page by checking the bool is not false
    '''
    user = current_user
    if user.admin == False:
        flash("User Not Authorised")
        return redirect(url_for("index"))
    else:
        return render_template("admin_view.html", forms = Form_Submission.query.all(), reports = User_Report.query.all())

@app.errorhandler(NotFound)
def page_not_found(error_message):
    '''
    404 Error Handling for if the user types in the wrong
    url if entering manually
    '''
    attempted_url = request.path
    return render_template("404.html", attempted_url=attempted_url), 404


if __name__ == "__main__":
    app.run(debug=True, port=8181)
