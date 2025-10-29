from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
db = SQLAlchemy()


class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    admin: Mapped[bool] = mapped_column(nullable=False, default=False)

    reviews = db.relationship('Review', back_populates='author')
    reports = db.relationship('User_Report', back_populates='reporter')
    form_submissions = db.relationship('Form_Submission', back_populates='user')
    def __str__(self):
        return f"This User is '{self.username}'"

    def make_admin(self):
        self.admin = True
        return self.admin

    def hash_password(self, unhashed_password: str):
        self.password = generate_password_hash(unhashed_password)


    def validate_password(self, unhashed_password: str):
        return check_password_hash(self.password, unhashed_password)

class Review(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    artist: Mapped[str] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    album: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    score: Mapped[int] = mapped_column(nullable=False)
    song_link: Mapped[str] = mapped_column(nullable=False)

    author_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)

    author = db.relationship('User', back_populates='reviews')

    def __str__(self):
        return f'{self.title} a review written by {self.author.username} with a score of {self.score} out of 100'

    def get_song_embed_code(self):
        split = self.song_link.split("/")
        split = split[-1].split("?")
        code = split[0]
        embed_link = f"https://open.spotify.com/embed/track/{code}?utm_source=generator&theme=0"
        return embed_link

class User_Report(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    reason: Mapped[str] = mapped_column(nullable=False)

    reporter_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    review_id: Mapped[int] = mapped_column(ForeignKey("review.id"), nullable=False)

    reporter = db.relationship('User', back_populates='reports')

    def __str__(self):
        return f'{self.reporter.username} reported {self.review_id} because: {self.reason}'


class Form_Submission(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    message: Mapped[str] =mapped_column(nullable=False)

    user = db.relationship('User', back_populates='form_submissions')
    def __str__(self):
        return f'''
        {self.name}
        {self.email}
        {self.message}
        '''
