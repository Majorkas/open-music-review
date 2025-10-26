from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
import hashlib
db = SQLAlchemy()


class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(null=False)
    password: Mapped[str] = mapped_column(null=False)

    reviews = db.relationship('Review', back_populates='author')

    def __str__(self):
        return self.username

class Review(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
