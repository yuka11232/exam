import sqlite3
from datetime import datetime


class LibraryDB:
   
    
    def __init__(self, db_name="libraryDB.s13"):
        self.connect = sqlite3.connect(db_name)
        self.cursor = self.connect.cursor()
        self.init_db()

    def init_db(self):
        
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY,
            title TEXT,
            author TEXT,
            year INTEGER,
            copies INTEGER
        );""")
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            surname TEXT,
            email TEXT
        );""")
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            book_id INTEGER,
            issue_date TEXT,
            return_date TEXT,
            status TEXT
        );""")
        self.connect.commit()

    def execute(self, query, params=()):
        self.cursor.execute(query, params)
        self.connect.commit()

    def fetchall(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def fetchone(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def close(self):
        self.connect.close()


class User:
    
    
    def __init__(self, name, surname, email):
        self.name = name
        self.surname = surname
        self.email = email

    def register(self, db):
        db.execute(
            "INSERT INTO users (name, surname, email) VALUES (?, ?, ?);",
            (self.name, self.surname, self.email)
        )
        print(f"User {self.name} {self.surname} is registered")




def add_book(db):
    print("\n=== add a book ===")
    title = input("the name of the book: ").strip()
    author = input("Author: ").strip()
    try:
        year = int(input("Publication year: ").strip())
        copies = int(input("the amount of books: ").strip())
        db.execute("INSERT INTO books (title, author, year, copies) VALUES (?, ?, ?, ?);", 
                   (title, author, year, copies))
        print(f" the book '{title}' is added")
    except ValueError:
        print("Error. year and copies must be an integer")


def view_books(db):
    print("\n=== book list ===")
    books = db.fetchall("SELECT id, title, author, year, copies FROM books;")
    if not books:
        print("out of stock :(")
    else:
        for book in books:
            print(f"ID: {book[0]} | book name: {book[1]} | author: {book[2]} | publication year: {book[3]} | amount of books: {book[4]}")


def view_history(db):
    print("\n=== transactions ===")
    transactions = db.fetchall("SELECT * FROM transactions;")
    if not transactions:
        print("history is clean")
    else:
        for trans in transactions:
            print(f"ID: {trans[0]} | User ID: {trans[1]} | Book ID: {trans[2]} | Issuance: {trans[3]} | returnal: {trans[4]} | status: {trans[5]}")




def issue_book(db):
    print("\n=== book Issuance ===")
    try:
        user_id = int(input("user ID: ").strip())
        book_id = int(input("book ID: ").strip())
        issue_date = datetime.now().strftime("%Y-%m-%d")
        copies = db.fetchone("SELECT copies FROM books WHERE id = ?;", (book_id,))
        if not copies:
            print(" error. book ID not found")
            return
        if copies[0] <= 0:
            print("books are out of stock")
            return
        db.execute("INSERT INTO transactions (user_id, book_id, issue_date, status) VALUES (?, ?, ?, 'the book is given');", 
                   (user_id, book_id, issue_date))
        db.execute("UPDATE books SET copies = copies - 1 WHERE id = ?;", (book_id,))
        print("the book is handed out")
    except ValueError:
        print("error. ID must be an integer")


def return_book(db):
    print("\n=== book returnal ===")
    try:
        transaction_id = int(input("ID transactions: ").strip())
        return_date = datetime.now().strftime("%Y-%m-%d")
        book_id = db.fetchone("SELECT book_id FROM transactions WHERE id = ?;", (transaction_id,))
        if not book_id:
            print("transaction Error. ID not found")
            return
        db.execute("UPDATE transactions SET return_date = ?, status = 'has been returned' WHERE id = ?;", 
                   (return_date, transaction_id))
        db.execute("UPDATE books SET copies = copies + 1 WHERE id = ?;", (book_id[0],))
        print("the book has been returned")
    except ValueError:
        print("Error ID must be an integer")



def main_menu():
    db = LibraryDB()
    while True:
        print("\n=== Main Menu ===")
        print("1. add book")
        print("2. Register")
        print("3. loan a book")
        print("4. give back a book")
        print("5. show books")
        print("6. history")
        print("0. exit")
        choice = input("Choose: ").strip()

        if choice == "1":
            add_book(db)
        elif choice == "2":
            user = User(
                name=input("name: "),
                surname=input("surname: "),
                email=input("Email: ")
            )
            user.register(db)
        elif choice == "3":
            issue_book(db)
        elif choice == "4":
            return_book(db)
        elif choice == "5":
            view_books(db)
        elif choice == "6":
            view_history(db)
        elif choice == "0":
            print("exit code")
            db.close()
            break
        else:
            print("Error")

if __name__ == "__main__":
    main_menu()
