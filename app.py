from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
import db
import connect

app = Flask(__name__)
app.secret_key = "Library Demo 2025 Secret Key"

# Initialize database connection
db.init_db(
    app, connect.dbuser, connect.dbpass, connect.dbhost, connect.dbname, connect.dbport
)


# ========================================
# 1. Home Page Routes
# ========================================
@app.route("/")
def home():
    # Display top 3 most popular books on home page
    cursor = db.get_cursor()

    # Query to get top 3 most borrowed books
    qstr = """
    SELECT b.bookid, b.booktitle, b.author, b.bookcategory, b.yearofpublication, 
           b.image, COUNT(l.loanid) as loan_count
    FROM books b
    JOIN bookcopies bc ON b.bookid = bc.bookid  
    JOIN loans l ON bc.bookcopyid = l.bookcopyid
    GROUP BY b.bookid, b.booktitle, b.author, b.bookcategory, b.yearofpublication, b.image
    ORDER BY loan_count DESC
    LIMIT 3
    """

    cursor.execute(qstr)
    popular_books = cursor.fetchall()
    cursor.close()
    return render_template("home.html", popular_books=popular_books)


# ========================================
# End of Home Page Routes
# ========================================


# ========================================
# 2. Book Management Routes
# ========================================
@app.route("/book_list")
def book_list():
    # First time entering page - show empty list
    cursor = db.get_cursor()

    # Get all categories for dropdown
    categories_qstr = "SELECT category FROM categories ORDER BY category"
    cursor.execute(categories_qstr)
    categories = cursor.fetchall()
    cursor.close()

    return render_template(
        "book_list.html",
        books=[],
        categories=categories,
        title_search="",
        author_search="",
        category_search="",
    )


@app.route("/book_search", methods=["POST"])
def book_search():
    # Handle book search after clicking search button
    cursor = db.get_cursor()

    # Get all categories for dropdown
    categories_qstr = "SELECT category FROM categories ORDER BY category"
    cursor.execute(categories_qstr)
    categories = cursor.fetchall()

    title_search = request.form.get("title", "").strip()
    author_search = request.form.get("author", "").strip()
    category_search = request.form.get("category", "").strip()

    # Build dynamic query - if no search criteria, show all books
    where_conditions = []
    params = []

    if title_search:
        where_conditions.append("booktitle LIKE %s")
        params.append(f"%{title_search}%")

    if author_search:
        where_conditions.append("author LIKE %s")
        params.append(f"%{author_search}%")

    if category_search:
        where_conditions.append("bookcategory = %s")
        params.append(category_search)

    # Build query - if no conditions, get all books
    if where_conditions:
        books_qstr = f"""
        SELECT bookid, booktitle, author, bookcategory, yearofpublication
        FROM books 
        WHERE {' AND '.join(where_conditions)}
        ORDER BY booktitle
        """
        cursor.execute(books_qstr, params)
    else:
        # No search criteria - show all books
        books_qstr = """
        SELECT bookid, booktitle, author, bookcategory, yearofpublication
        FROM books 
        ORDER BY booktitle
        """
        cursor.execute(books_qstr)

    books = cursor.fetchall()
    cursor.close()

    return render_template(
        "book_list.html",
        books=books,
        categories=categories,
        title_search=title_search,
        author_search=author_search,
        category_search=category_search,
    )


@app.route("/book_add")
def book_add():
    # Click add new book - show new book form
    cursor = db.get_cursor()

    # Get all categories for dropdown
    categories_qstr = "SELECT category FROM categories ORDER BY category"
    cursor.execute(categories_qstr)
    categories = cursor.fetchall()
    cursor.close()

    return render_template(
        "book_manage.html", book=None, is_edit=False, categories=categories
    )


@app.route("/book_manage/<int:book_id>")
def book_edit(book_id):
    # Click edit book - show edit book form with pre-filled data
    cursor = db.get_cursor()

    # Get all categories for dropdown
    categories_qstr = "SELECT category FROM categories ORDER BY category"
    cursor.execute(categories_qstr)
    categories = cursor.fetchall()

    # Get book details
    book_qstr = """
    SELECT bookid, booktitle, author, bookcategory, yearofpublication, description, image
    FROM books 
    WHERE bookid = %s
    """
    cursor.execute(book_qstr, (book_id,))
    book = cursor.fetchone()
    cursor.close()

    if not book:
        flash("Book not found.", "danger")
        return redirect(url_for("book_list"))

    return render_template(
        "book_manage.html", book=book, is_edit=True, categories=categories
    )


@app.route("/book_save", methods=["POST"])
def book_save():
    # Save new book
    cursor = db.get_cursor()

    # Get form data
    booktitle = request.form.get("booktitle", "").strip()
    author = request.form.get("author", "").strip()
    bookcategory = request.form.get("bookcategory", "").strip()
    yearofpublication = request.form.get("yearofpublication", "").strip()
    description = request.form.get("description", "").strip()
    image = request.form.get("image", "").strip()

    # Basic server-side validation
    if not booktitle or not author:
        flash("Title and Author are required.", "danger")
        cursor.close()
        return redirect(url_for("book_add"))

    # Handle empty values
    bookcategory = bookcategory if bookcategory else None
    yearofpublication = int(yearofpublication) if yearofpublication.isdigit() else None
    description = description if description else None
    image = image if image else None

    insert_qstr = """
    INSERT INTO books (booktitle, author, bookcategory, yearofpublication, description, image)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(
        insert_qstr,
        (booktitle, author, bookcategory, yearofpublication, description, image),
    )
    flash("Book created successfully!", "success")
    cursor.close()
    return redirect(url_for("book_list"))


@app.route("/book_save/<int:book_id>", methods=["POST"])
def book_update(book_id):
    # Update existing book
    cursor = db.get_cursor()

    # Get form data
    booktitle = request.form.get("booktitle", "").strip()
    author = request.form.get("author", "").strip()
    bookcategory = request.form.get("bookcategory", "").strip()
    yearofpublication = request.form.get("yearofpublication", "").strip()
    description = request.form.get("description", "").strip()
    image = request.form.get("image", "").strip()

    # Basic server-side validation
    if not booktitle or not author:
        flash("Title and Author are required.", "danger")
        cursor.close()
        return redirect(url_for("book_edit", book_id=book_id))

    # Handle empty values
    bookcategory = bookcategory if bookcategory else None
    yearofpublication = int(yearofpublication) if yearofpublication.isdigit() else None
    description = description if description else None
    image = image if image else None

    update_qstr = """
    UPDATE books 
    SET booktitle = %s, author = %s, bookcategory = %s, yearofpublication = %s, description = %s, image = %s
    WHERE bookid = %s
    """
    cursor.execute(
        update_qstr,
        (
            booktitle,
            author,
            bookcategory,
            yearofpublication,
            description,
            image,
            book_id,
        ),
    )
    flash("Book updated successfully!", "success")
    cursor.close()
    return redirect(url_for("book_list"))


@app.route("/book/<int:book_id>")
def book_detail(book_id):
    # Display detailed information for a specific book
    cursor = db.get_cursor()

    # Get book details
    book_qstr = """
    SELECT bookid, booktitle, author, bookcategory, yearofpublication, description, image
    FROM books 
    WHERE bookid = %s
    """
    cursor.execute(book_qstr, (book_id,))
    book = cursor.fetchone()

    cursor.close()

    if not book:
        return "Book not found", 404

    return render_template("book_detail.html", book=book)


# ========================================
# End of Book Management Routes
# ========================================


# ========================================
# 3. Loan Management Routes
# ========================================
@app.route("/loan", methods=["GET", "POST"])
def loan():
    cursor = db.get_cursor()

    # Get all borrowers and books for the dropdowns
    borrowers_qstr = """
    SELECT borrowerid, firstname, familyname 
    FROM borrowers 
    ORDER BY familyname, firstname
    """
    cursor.execute(borrowers_qstr)
    borrowers = cursor.fetchall()

    books_qstr = """
    SELECT bookid, booktitle, author 
    FROM books 
    ORDER BY booktitle
    """
    cursor.execute(books_qstr)
    books = cursor.fetchall()

    if request.method == "POST":
        # Handle loan creation only
        borrower_id = request.form.get("borrower_id")
        book_id = request.form.get("book_id")
        copy_id = request.form.get("copy_id")

        # Basic validation (frontend handles most validation)
        if borrower_id and book_id and copy_id:
            loan_qstr = """
            INSERT INTO loans (bookcopyid, borrowerid, loandate, returned)
            VALUES (%s, %s, CURDATE(), NULL)
            """
            cursor.execute(loan_qstr, (copy_id, borrower_id))
            flash("Book borrowed successfully!", "success")
            cursor.close()
            return redirect(url_for("loan_by_borrower"))
        else:
            flash("Please select all required fields.", "warning")

    cursor.close()
    return render_template("loan.html", borrowers=borrowers, books=books)


@app.route("/loan_select_book", methods=["POST"])
def loan_select_book():
    cursor = db.get_cursor()

    # Get all borrowers and books for the dropdowns
    borrowers_qstr = """
    SELECT borrowerid, firstname, familyname 
    FROM borrowers 
    ORDER BY familyname, firstname
    """
    cursor.execute(borrowers_qstr)
    borrowers = cursor.fetchall()

    books_qstr = """
    SELECT bookid, booktitle, author 
    FROM books 
    ORDER BY booktitle
    """
    cursor.execute(books_qstr)
    books = cursor.fetchall()

    # Get form data
    borrower_id = request.form.get("borrower_id")
    book_id = request.form.get("book_id")

    # Initialize variables
    selected_borrower = borrower_id
    selected_book = book_id
    available_copies = []
    book_detail = None

    if book_id:
        # Get book details
        book_qstr = """
        SELECT bookid, booktitle, author, bookcategory, yearofpublication, description, image
        FROM books 
        WHERE bookid = %s
        """
        cursor.execute(book_qstr, (book_id,))
        book_detail = cursor.fetchone()

        # Get available copies for the selected book
        copies_qstr = """
        SELECT bc.bookcopyid, bc.format
        FROM bookcopies bc
        WHERE bc.bookid = %s
        AND bc.bookcopyid NOT IN (
            SELECT l.bookcopyid 
            FROM loans l 
            WHERE l.returned IS NULL
        )
        ORDER BY bc.format
        """
        cursor.execute(copies_qstr, (book_id,))
        available_copies = cursor.fetchall()

    cursor.close()

    return render_template(
        "loan.html",
        borrowers=borrowers,
        books=books,
        selected_borrower=selected_borrower,
        selected_book=selected_book,
        available_copies=available_copies,
        book_detail=book_detail,
    )


# ========================================
# End of Loan Management Routes
# ========================================


# ========================================
# 4. Borrower Management Routes
# ========================================
@app.route("/borrower_list", methods=["GET", "POST"])
def borrower_list():
    cursor = db.get_cursor()

    if request.method == "POST":
        # Handle borrower search
        firstname_search = request.form.get("firstname", "").strip()
        familyname_search = request.form.get("familyname", "").strip()

        # Build dynamic query
        where_conditions = []
        params = []

        if firstname_search:
            where_conditions.append("firstname LIKE %s")
            params.append(f"%{firstname_search}%")

        if familyname_search:
            where_conditions.append("familyname LIKE %s")
            params.append(f"%{familyname_search}%")

        # Build query - if no conditions, get all borrowers
        if where_conditions:
            borrowers_qstr = f"""
            SELECT borrowerid, firstname, familyname, dateofbirth, address, suburb, city, postcode
            FROM borrowers 
            WHERE {' AND '.join(where_conditions)}
            ORDER BY familyname, firstname
            """
            cursor.execute(borrowers_qstr, params)
        else:
            # No search criteria - show all borrowers
            borrowers_qstr = """
            SELECT borrowerid, firstname, familyname, dateofbirth, address, suburb, city, postcode
            FROM borrowers 
            ORDER BY familyname, firstname
            """
            cursor.execute(borrowers_qstr)

        borrowers_list = cursor.fetchall()
        cursor.close()

        return render_template(
            "borrower_list.html",
            borrowers=borrowers_list,
            firstname_search=firstname_search,
            familyname_search=familyname_search,
        )
    else:
        # GET request - show empty list initially
        cursor.close()

        return render_template(
            "borrower_list.html",
            borrowers=[],
            firstname_search="",
            familyname_search="",
        )


@app.route("/borrower_manage")
@app.route("/borrower_manage/<int:borrower_id>")
def borrower_manage(borrower_id=None):
    if borrower_id is None:
        # Display new borrower form
        return render_template("borrower_manage.html", borrower=None, is_edit=False)
    else:
        # Display edit borrower form with pre-filled data
        cursor = db.get_cursor()

        borrower_qstr = """
        SELECT borrowerid, firstname, familyname, dateofbirth, address, suburb, city, postcode
        FROM borrowers 
        WHERE borrowerid = %s
        """
        cursor.execute(borrower_qstr, (borrower_id,))
        borrower = cursor.fetchone()
        cursor.close()

        if not borrower:
            flash("Borrower not found.", "danger")
            return redirect(url_for("borrower_list"))

        return render_template("borrower_manage.html", borrower=borrower, is_edit=True)


@app.route("/borrower_save", methods=["POST"])
@app.route("/borrower_save/<int:borrower_id>", methods=["POST"])
def borrower_save(borrower_id=None):
    # Handle borrower creation or update
    cursor = db.get_cursor()

    # Get form data
    firstname = request.form.get("firstname", "").strip()
    familyname = request.form.get("familyname", "").strip()
    dateofbirth = request.form.get("dateofbirth", "").strip()
    address = request.form.get("address", "").strip()
    suburb = request.form.get("suburb", "").strip()
    city = request.form.get("city", "").strip()
    postcode = request.form.get("postcode", "").strip()

    # Basic server-side validation (minimal, frontend handles detailed validation)
    if not firstname.strip() or not familyname.strip():
        flash("Please fill in all required fields correctly.", "danger")
        cursor.close()
        if borrower_id:
            return redirect(url_for("borrower_manage", borrower_id=borrower_id))
        else:
            return redirect(url_for("borrower_manage"))

    # Keep empty strings as blank except for date fields
    dateofbirth = dateofbirth if dateofbirth else None

    if borrower_id:
        # Update existing borrower
        update_qstr = """
        UPDATE borrowers 
        SET firstname = %s, familyname = %s, dateofbirth = %s, 
            address = %s, suburb = %s, city = %s, postcode = %s
        WHERE borrowerid = %s
        """
        cursor.execute(
            update_qstr,
            (
                firstname,
                familyname,
                dateofbirth,
                address,
                suburb,
                city,
                postcode,
                borrower_id,
            ),
        )

        if cursor.rowcount > 0:
            flash("Borrower updated successfully!", "success")
        else:
            flash("No changes were made or borrower not found.", "warning")
    else:
        # Create new borrower
        insert_qstr = """
        INSERT INTO borrowers (firstname, familyname, dateofbirth, address, suburb, city, postcode)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            insert_qstr,
            (firstname, familyname, dateofbirth, address, suburb, city, postcode),
        )
        flash("Borrower created successfully!", "success")

    cursor.close()
    return redirect(url_for("borrower_list"))


# ========================================
# End of Borrower Management Routes
# ========================================


# ========================================
# 5. Loans by Borrower Routes
# ========================================
@app.route("/loan_by_borrower")
def loan_by_borrower():
    # Display all loans grouped by borrower
    cursor = db.get_cursor()

    loans_qstr = """
    SELECT 
        l.loanid,
        l.loandate,
        l.returned,
        br.borrowerid,
        br.firstname,
        br.familyname,
        bc.bookcopyid,
        bc.format,
        b.booktitle,
        b.author,
        b.bookcategory,
        b.yearofpublication,
        CASE 
            WHEN l.returned IS NULL THEN 'On Loan'
            ELSE 'Returned'
        END as loan_status,
        DATEDIFF(CURDATE(), l.loandate) AS days_borrowed
    FROM loans l
    JOIN borrowers br ON l.borrowerid = br.borrowerid
    JOIN bookcopies bc ON l.bookcopyid = bc.bookcopyid
    JOIN books b ON bc.bookid = b.bookid
    ORDER BY br.familyname, br.firstname, l.loandate DESC
    """

    cursor.execute(loans_qstr)
    all_loans = cursor.fetchall()
    cursor.close()

    # Group loans by borrower
    loans_by_borrower = {}
    for loan in all_loans:
        borrower_key = f"{loan['borrowerid']}"
        if borrower_key not in loans_by_borrower:
            loans_by_borrower[borrower_key] = {
                "borrower": {
                    "borrowerid": loan["borrowerid"],
                    "firstname": loan["firstname"],
                    "familyname": loan["familyname"],
                },
                "loans": [],
            }
        
        # Add overdue flag for on loan records >= 36 days
        loan_dict = dict(loan)
        if loan['loan_status'] == 'On Loan' and loan['days_borrowed'] >= 36:
            loan_dict['is_overdue'] = True
        else:
            loan_dict['is_overdue'] = False
        
        loans_by_borrower[borrower_key]["loans"].append(loan_dict)

    return render_template("loan_by_borrower.html", loans_by_borrower=loans_by_borrower)


@app.route("/return_book/<int:loan_id>", methods=["POST"])
def return_book(loan_id):
    # Handle book return
    cursor = db.get_cursor()

    # Update loan record with return date
    return_qstr = """
    UPDATE loans 
    SET returned = CURDATE() 
    WHERE loanid = %s AND returned IS NULL
    """
    cursor.execute(return_qstr, (loan_id,))

    if cursor.rowcount > 0:
        flash("Book returned successfully!", "success")
    else:
        flash("Error: Book was already returned or loan not found.", "warning")

    cursor.close()
    return redirect(url_for("loan_by_borrower"))


# ========================================
# End of Loans by Borrower Routes
# ========================================


# ========================================
# 6. Current Loans Routes
# ========================================
@app.route("/loan_current", methods=["GET", "POST"])
def loan_current():
    # Display all current loans (not returned) with search functionality
    cursor = db.get_cursor()

    firstname_search = ""
    lastname_search = ""

    # Handle search parameters
    if request.method == "POST":
        firstname_search = request.form.get("firstname", "").strip()
        lastname_search = request.form.get("lastname", "").strip()

    # Build dynamic query for current loans (not returned)
    where_conditions = ["loans.returned IS NULL"]  # Only current loans
    params = []

    if firstname_search:
        where_conditions.append("borrowers.firstname LIKE %s")
        params.append(f"%{firstname_search}%")

    if lastname_search:
        where_conditions.append("borrowers.familyname LIKE %s")
        params.append(f"%{lastname_search}%")

    # SQL query to get current loans with all required fields
    current_loans_qstr = f"""
    SELECT 
        loans.loanid,
        loans.loandate,
        borrowers.firstname,
        borrowers.familyname,
        books.booktitle,
        books.author,
        books.bookcategory,
        books.yearofpublication,
        bookcopies.bookcopyid,
        bookcopies.format,
        DATEDIFF(CURDATE(), loans.loandate) AS days_borrowed,
        CASE 
            WHEN DATEDIFF(CURDATE(), loans.loandate) >= 36 THEN 'Overdue'
            ELSE 'On Loan'
        END AS loan_status
    FROM loans
    JOIN bookcopies ON loans.bookcopyid = bookcopies.bookcopyid
    JOIN books ON bookcopies.bookid = books.bookid
    JOIN borrowers ON loans.borrowerid = borrowers.borrowerid
    WHERE {' AND '.join(where_conditions)}
    ORDER BY borrowers.familyname, borrowers.firstname, loans.loandate
    """

    cursor.execute(current_loans_qstr, params)
    loans = cursor.fetchall()
    cursor.close()

    return render_template(
        "loan_current.html",
        loans=loans,
        firstname_search=firstname_search,
        lastname_search=lastname_search,
    )


# ========================================
# End of Current Loans Routes
# ========================================
