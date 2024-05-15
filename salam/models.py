from app2 import app
from werkzeug.security import generate_password_hash, check_password_hash
from app2 import db

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    publication_date = db.Column(db.String(10), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    isbn = db.Column(db.String(13), unique=True, nullable=False)

    def as_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'publication_date': self.publication_date,
            'genre': self.genre,
            'isbn': self.isbn
        }


    def __repr__(self):
        return f'<Book {self.title}>'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
