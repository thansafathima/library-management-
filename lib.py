import sqlite3
conn = sqlite3.connect("project.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS books(
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT,
    category TEXT,
    quantity INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS borrow(
    borrow_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    book_id INTEGER,
    status TEXT,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(book_id) REFERENCES books(book_id)
)
""")

conn.commit()


# ------ REGISTER ---------

def register():

    print("\n----- REGISTER -----")

    username = input("Enter Username: ")
    password = input("Enter Password: ")

    print("1. Admin")
    print("2. User")

    choice = input("Choose Role: ")

    if choice == "1":
        role = "Admin"
    else:
        role = "User"

    try:
        cursor.execute(
            "INSERT INTO users(username, password, role) VALUES(?,?,?)",
            (username, password, role)
        )

        conn.commit()
        print("Registration Successful!")

    except sqlite3.IntegrityError:
        print("Username Already Exists!")


# ---------LOGIN -----------

def login():

    print("\n----- LOGIN -----")

    username = input("Enter Username: ")
    password = input("Enter Password: ")

    cursor.execute(
        "SELECT user_id, role FROM users WHERE username=? AND password=?",
        (username, password)
    )

    user = cursor.fetchone()

    if user:
        print("Login Successful!")
        return user

    print("Invalid Username or Password!")
    return None


# --------- ADD BOOK---------

def add_book():

    print("\n--- ADD BOOK ---")

    title = input("Book Title: ")
    author = input("Author: ")
    category = input("Category: ")
    quantity = int(input("Quantity: "))

    cursor.execute(
        """INSERT INTO books(title, author, category, quantity)
        VALUES(?,?,?,?)""",
        (title, author, category, quantity)
    )

    conn.commit()

    print("Book Added Successfully!")


# -----------VIEW BOOKS---------

def view_books():

    print("\n--- BOOK LIST ---")

    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()

    if not books:
        print("No Books Available.")
        return

    print("\nID | Title | Author | Category | Quantity")
    print("-" * 60)

    for book in books:
        print(book[0], "|", book[1], "|", book[2], "|", book[3], "|", book[4])
# ---------- UPDATE BOOK ----------------

def update_book():

    print("\n--- UPDATE BOOK ---")

    book_id = input("Enter Book ID: ")
    quantity = int(input("Enter New Quantity: "))

    cursor.execute(
        "UPDATE books SET quantity=? WHERE book_id=?",
        (quantity, book_id)
    )

    conn.commit()

    if cursor.rowcount > 0:
        print("Book Updated Successfully!")
    else:
        print("Book Not Found!")


# ---------- DELETE BOOK ------------

def delete_book():

    print("\n--- DELETE BOOK ---")

    book_id = input("Enter Book ID: ")

    cursor.execute(
        "DELETE FROM books WHERE book_id=?",
        (book_id,)
    )

    conn.commit()

    if cursor.rowcount > 0:
        print("Book Deleted Successfully!")
    else:
        print("Book Not Found!")


# ----------- VIEW BORROW RECORDS ----------

def view_borrow_records():

    print("\n--- BORROW RECORDS ---")

    cursor.execute("""
    SELECT borrow.borrow_id, users.username,
           books.title, borrow.status
    FROM borrow
    JOIN users ON borrow.user_id = users.user_id
    JOIN books ON borrow.book_id = books.book_id
    """)

    records = cursor.fetchall()

    if records:
        print("\nID | Username | Book | Status")
        print("-" * 40)

        for record in records:
            print(record)

    else:
        print("No Borrow Records.")


# ------ ADMIN MENU--------

def admin_menu():

    while True:

        print("\n===== ADMIN MENU =====")
        print("1. Add Book")
        print("2. View Books")
        print("3. Update Book")
        print("4. Delete Book")
        print("5. View Borrow Records")
        print("6. Logout")

        choice = input("Enter Choice: ")

        if choice == "1":
            add_book()

        elif choice == "2":
            view_books()

        elif choice == "3":
            update_book()

        elif choice == "4":
            delete_book()

        elif choice == "5":
            view_borrow_records()

        elif choice == "6":
            print("Logged Out!")
            break

        else:
            print("Invalid Choice!")


# -------- BORROW BOOK-------

def borrow_book(user_id):

    print("\n--- BORROW BOOK ---")

    book_id = input("Enter Book ID: ")

    cursor.execute(
        "SELECT quantity FROM books WHERE book_id=?",
        (book_id,)
    )

    book = cursor.fetchone()

    if not book:
        print("Book Not Found!")
        return

    if book[0] <= 0:
        print("Book Not Available!")
        return

    cursor.execute(
        """INSERT INTO borrow(user_id, book_id, status)
        VALUES(?,?,?)""",
        (user_id, book_id, "Borrowed")
    )

    cursor.execute(
        "UPDATE books SET quantity=quantity-1 WHERE book_id=?",
        (book_id,)
    )

    conn.commit()

    print("Book Borrowed Successfully!")


# --------- RETURN BOOK ------------

def return_book(user_id):

    print("\n--- RETURN BOOK ---")

    book_id = input("Enter Book ID: ")

    cursor.execute(
        """SELECT borrow_id FROM borrow
        WHERE user_id=? AND book_id=? AND status='Borrowed'""",
        (user_id, book_id)
    )

    borrow = cursor.fetchone()

    if not borrow:
        print("Borrow Record Not Found!")
        return

    cursor.execute(
        "UPDATE books SET quantity=quantity+1 WHERE book_id=?",
        (book_id,)
    )

    cursor.execute(
        "UPDATE borrow SET status='Returned' WHERE borrow_id=?",
        (borrow[0],)
    )

    conn.commit()

    print("Book Returned Successfully!")


# -----USER MENU --------

def user_menu(user_id):

    while True:

        print("\n===== USER MENU =====")
        print("1. View Books")
        print("2. Borrow Book")
        print("3. Return Book")
        print("4. Logout")

        choice = input("Enter Choice: ")

        if choice == "1":
            view_books()

        elif choice == "2":
            borrow_book(user_id)

        elif choice == "3":
            return_book(user_id)

        elif choice == "4":
            print("Logged Out Successfully!")
            break

        else:
            print("Invalid Choice!")


# ----------- MAIN MENU -----------

while True:

    print("\n===== LIBRARY MANAGEMENT SYSTEM =====")
    print("1. Register")
    print("2. Login")
    print("3. Exit")

    choice = input("Enter Choice: ")

    if choice == "1":
        register()

    elif choice == "2":

        user = login()

        if user:
            user_id = user[0]
            role = user[1]

            if role == "Admin":
                admin_menu()

            elif role == "User":
                user_menu(user_id)

    elif choice == "3":
        print("Thank You!")
        break

    else:
        print("Invalid Choice!")
        
conn.close()