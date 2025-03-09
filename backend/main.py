import os
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

DATA_FILE = 'library.json'

def load_data():
    if not os.path.exists(DATA_FILE):  # initialize file if it doesn't exist
        with open(DATA_FILE, 'w') as f:
            json.dump([], f)
    with open(DATA_FILE, 'r') as f:
        try:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                return []
        except json.JSONDecodeError:
            return []

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/books', methods=['GET'])
def get_books():
    books = load_data()
    search_query = request.args.get('search', '').lower()
    if search_query:  # filter books by title or author if search query provided
        books = [book for book in books if search_query in book.get('title', '').lower() or 
                 search_query in book.get('author', '').lower()]
    return jsonify(books)

@app.route('/books', methods=['POST'])
def add_book():
    new_book = request.get_json()
    books = load_data()
    if any(book.get('isbn') == new_book.get('isbn') for book in books):  # prevent duplicate isbn
        return jsonify({'error': 'book with this isbn already exists.'}), 400
    if 'genre' in new_book:
        if not isinstance(new_book['genre'], list):  # convert genre to list if provided as string
            new_book['genre'] = [g.strip() for g in new_book['genre'].split(',')]
    else:
        new_book['genre'] = []
    books.append(new_book)
    save_data(books)
    return jsonify(new_book), 201

@app.route('/books/<isbn>', methods=['GET'])
def get_book(isbn):
    books = load_data()
    for book in books:
        if book.get('isbn') == isbn:
            return jsonify(book)
    return jsonify({'error': 'book not found.'}), 404

@app.route('/books/<isbn>', methods=['PUT'])
def update_book(isbn):
    update_data = request.get_json()
    books = load_data()
    for i, book in enumerate(books):
        if book.get('isbn') == isbn:
            book['title'] = update_data.get('title', book.get('title'))
            book['author'] = update_data.get('author', book.get('author'))
            if 'genre' in update_data:
                if isinstance(update_data['genre'], list):
                    book['genre'] = update_data['genre']
                else:  # convert genre to list if necessary
                    book['genre'] = [g.strip() for g in update_data['genre'].split(',')]
            book['copies'] = update_data.get('copies', book.get('copies', 0))
            book['available_copies'] = update_data.get('available_copies', book.get('available_copies', 0))
            book['location'] = update_data.get('location', book.get('location', ''))
            book['rating'] = update_data.get('rating', book.get('rating', 0.0))
            book['borrowed_count'] = update_data.get('borrowed_count', book.get('borrowed_count', 0))
            books[i] = book
            save_data(books)
            return jsonify(book)
    return jsonify({'error': 'book not found.'}), 404

@app.route('/books/<isbn>', methods=['DELETE'])
def delete_book(isbn):
    books = load_data()
    for i, book in enumerate(books):
        if book.get('isbn') == isbn:
            books.pop(i)
            save_data(books)
            return jsonify({'message': 'book deleted successfully.'})
    return jsonify({'error': 'book not found.'}), 404

if __name__ == '__main__':
    app.run(debug=True)
