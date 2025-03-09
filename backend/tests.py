import requests

BASE_URL = "http://localhost:5000"

def pause():
    input("\nPress Enter to continue to the next test...")

def print_separator():
    print("=" * 50)

def test_add_books():
    print_separator()
    print(">> Testing: Add Multiple Books")
    books_to_add = [
        {
            "isbn": "978-3-16-148410-0",
            "title": "Sample Book",
            "author": "Author Name",
            "genre": ["Fiction", "Mystery"],
            "copies": 3,
            "available_copies": 2,
            "location": "Section A-12",
            "rating": 4.5,
            "borrowed_count": 15
        },
        {
            "isbn": "978-0-12-345678-9",
            "title": "Another Book",
            "author": "Second Author",
            "genre": ["Non-Fiction", "Biography"],
            "copies": 4,
            "available_copies": 4,
            "location": "Section B-34",
            "rating": 4.0,
            "borrowed_count": 8
        },
        {
            "isbn": "978-1-234-56789-7",
            "title": "Interactive Python",
            "author": "Python Guru",
            "genre": ["Education", "Technology"],
            "copies": 10,
            "available_copies": 9,
            "location": "Section C-56",
            "rating": 4.8,
            "borrowed_count": 20
        }
    ]
    for book in books_to_add:
        response = requests.post(f"{BASE_URL}/books", json=book)
        print(f"Added book '{book['title']}' - Status Code: {response.status_code}")
        print("Response:", response.json())
    print_separator()

def test_get_books():
    print_separator()
    print(">> Testing: Get All Books")
    response = requests.get(f"{BASE_URL}/books")
    print("Status Code:", response.status_code)
    print("Response:", response.json())

def test_get_book(isbn):
    print_separator()
    print(f">> Testing: Get Book by ISBN: {isbn}")
    response = requests.get(f"{BASE_URL}/books/{isbn}")
    print("Status Code:", response.status_code)
    print("Response:", response.json())

def test_search_books(query):
    print_separator()
    print(f">> Testing: Search Books by query: '{query}'")
    response = requests.get(f"{BASE_URL}/books?search={query}")
    print("Status Code:", response.status_code)
    print("Response:", response.json())

def test_update_book(isbn, payload):
    print_separator()
    print(f">> Testing: Update Book with ISBN: {isbn}")
    response = requests.put(f"{BASE_URL}/books/{isbn}", json=payload)
    print("Status Code:", response.status_code)
    print("Response:", response.json())

def test_delete_book(isbn):
    print_separator()
    print(f">> Testing: Delete Book with ISBN: {isbn}")
    response = requests.delete(f"{BASE_URL}/books/{isbn}")
    print("Status Code:", response.status_code)
    print("Response:", response.json())

if __name__ == '__main__':
    print("\nInteractive API Test Suite\n")
    
    # Add multiple books
    test_add_books()
    pause()
    
    # Get list of all books
    test_get_books()
    pause()
    
    # Get individual books
    test_get_book("978-3-16-148410-0")
    pause()
    
    test_get_book("978-0-12-345678-9")
    pause()
    
    test_get_book("978-1-234-56789-7")
    pause()
    
    # Search books by a keyword in the title/author
    test_search_books("Python")
    pause()
    
    # Update one of the books
    test_update_book("978-1-234-56789-7", {"title": "Interactive Python - Updated", "copies": 12})
    pause()
    
    test_get_book("978-1-234-56789-7")
    pause()
    
    # Delete one of the books
    test_delete_book("978-0-12-345678-9")
    pause()
    
    # Show final list of books
    test_get_books()
    print_separator()
    print("All tests completed!")
