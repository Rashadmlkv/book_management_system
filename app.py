from flask import request, jsonify, abort
from salam.models import Book
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from app2 import *

app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
jwt = JWTManager(app)

@app.route('/books', methods=['GET'])
def get_books():
    query = Book.query
    sort_by = request.args.get('sort_by', 'title')
    order = request.args.get('order', 'asc')
    if order == 'desc':
        query = query.order_by(getattr(Book, sort_by).desc())
    else:
        query = query.order_by(getattr(Book, sort_by).asc())

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    books = query.paginate(page=page, per_page=per_page).items
    return jsonify([book.as_dict() for book in books])

@app.route('/books/<int:id>', methods=['GET'])
def get_book(id):
    book = Book.query.get_or_404(id)
    return jsonify(book.as_dict())

@app.route('/books', methods=['POST'])
@jwt_required()
def add_book():
    current_user = get_jwt_identity()
    data = request.get_json()
    new_book = Book(
        title=data['title'],
        author=data['author'],
        publication_date=data['publication_date'],
        genre=data['genre'],
        isbn=data['isbn']
    )
    db.session.add(new_book)
    db.session.commit()
    return jsonify(new_book.as_dict()), 201

@app.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    book = Book.query.get_or_404(id)
    data = request.get_json()
    book.title = data.get('title', book.title)
    book.author = data.get('author', book.author)
    book.publication_date = data.get('publication_date', book.publication_date)
    book.genre = data.get('genre', book.genre)
    book.isbn = data.get('isbn', book.isbn)
    db.session.commit()
    return jsonify(book.as_dict())

@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return '', 204

@app.route('/books/search', methods=['GET'])
def search_books():
    query_params = request.args
    query = Book.query
    if 'title' in query_params:
        query = query.filter(Book.title.ilike(f"%{query_params['title']}%"))
    if 'author' in query_params:
        query = query.filter(Book.author.ilike(f"%{query_params['author']}%"))
    if 'genre' in query_params:
        query = query.filter(Book.genre.ilike(f"%{query_params['genre']}%"))
    if 'publication_date' in query_params:
        query = query.filter(Book.publication_date == query_params['publication_date'])
    books = query.all()
    return jsonify([book.as_dict() for book in books])

@app.route('/books/filter', methods=['GET'])
def filter_books():
    query_params = request.args
    query = Book.query
    if 'genre' in query_params:
        query = query.filter(Book.genre == query_params['genre'])
    if 'start_year' in query_params and 'end_year' in query_params:
        query = query.filter(Book.publication_date.between(query_params['start_year'], query_params['end_year']))
    books = query.all()
    return jsonify([book.as_dict() for book in books])

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'User already exists'}), 400
    new_user = User(username=data['username'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user is None or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    access_token = create_access_token(identity=user.username)
    return jsonify(access_token=access_token), 200


if __name__ == '__main__':
    app.run(debug=True)

