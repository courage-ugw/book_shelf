from book_shelf import app, db
from data_models import Author, Book
from datetime import datetime
from flask import abort, flash, render_template, request, redirect, url_for
from sqlalchemy import func, or_
import requests


def get_cover_image_url(isbn):
    """
    Sends a request to the book cover api using book ISBN and Returns book cover url
    :param isbn: Book ISBN
    :return: url for book cover (String)
    """
    url = "https://book-cover-api2.p.rapidapi.com/api/public/books/v1/cover/url"
    querystring = {"languageCode": "en", "isbn": f"{isbn}"}
    headers = {
        "X-RapidAPI-Key": "9bcf117f10msh4043aa916958825p12243fjsnd31208cf6b30",
        "X-RapidAPI-Host": "book-cover-api2.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers, params=querystring)
        return response.json()['url']
    except requests.exceptions.JSONDecodeError:
        return ' '


@app.route('/sort')
@app.route('/')
def home():
    """
    Displays all books in the database on the home page.
    The books displayed are sorted by book title or author name
    :return: renders the home template
    """
    sort_param = request.args.get('query', 'book-title')

    if sort_param == 'book-title':
        books = Book.query.order_by(Book.title).all()
        return render_template('home.html', books=books)

    elif sort_param == 'author-name':
        books = db.session.query(Book).join(Author).order_by(Author.name).all()
        return render_template('home.html', books=books)
    else:
        abort(403)


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    """
    Gets book title, publication year, author name, book isbn if request is POST
    Adds a book to the database. If book is added successfully, user is redirected to the home page
    :return: renders the home page if post request and books added to database successfully otherwise renders the `add
    book page`.
    """
    if request.method == 'GET':
        return render_template('add_book.html')

    else:
        book_title = request.form.get('book-title')
        publication_year = request.form.get('publication-year')
        isbn = request.form.get('isbn')
        author_name = request.form.get('author-name')
        cover_url = get_cover_image_url(isbn=isbn)

        # Converts author name to lowercase
        # Checks if author and isbn already exists.
        author_name_lowercase = author_name.lower() if author_name else None
        existing_author = Author.query.filter(func.lower(Author.name) == author_name_lowercase).first()
        book_with_existing_isbn = Book.query.filter_by(isbn=isbn).first()

        # checks if ISBN exists. If it exists it means the book is already in the shelf
        if book_with_existing_isbn:
            flash('Book already exists in your shelf', 'danger')
            return render_template('add_book.html')

        # Checks if author is already in the authors table.
        # Maintains data integrity and prevents duplication of authors with many books
        if existing_author:
            book = Book(isbn=isbn, cover_url=cover_url, title=book_title, publication_year=publication_year,
                        author=existing_author)
        else:
            author = Author(name=author_name)
            book = Book(isbn=isbn, cover_url=cover_url, title=book_title, publication_year=publication_year,
                        author=author)

        # Add the book to the database session
        db.session.add(book)

        # Commit the changes to the database
        db.session.commit()

        # Send success message to the user
        flash("Book added successfully!", 'success')

        return redirect(url_for('home'))


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """
    Gets author name, birth date and death date from form if request is POST.
    Adds author to the database. If author is added successfully, user is redirected to the home page
    :return: renders the home page if post request and author added to database successfully; otherwise renders the
    `add author` page.
    """
    if request.method == 'GET':
        return render_template('add_author.html')

    else:
        author_name = request.form.get('name')
        birth_date = request.form.get('birth-date')
        death_date = request.form.get('death-date')

        # Converts the birth and death dates to python's date object
        birth_date = datetime.strptime(birth_date, '%Y-%m-%d')
        death_date = datetime.strptime(death_date, '%Y-%m-%d')

        if birth_date > death_date:
            flash('birth date must be earlier than death date', 'danger')
            return render_template('add_author.html')

        # Converts author name to lower
        # Search if author exists.
        author_name_lowercase = author_name.lower() if author_name else None
        existing_author = Author.query.filter(func.lower(Author.name) == author_name_lowercase).first()

        # If the author details does not exist in the database, then create a new record of the author
        # Else update the details of existing author
        if not existing_author:
            author = Author(name=author_name, birth_date=birth_date, date_of_death=death_date)

            # Add the author to the database session
            db.session.add(author)

            # Commit the changes to the database
            db.session.commit()

            flash('Author details added successfully!', 'success')
        else:
            # Update the Author's record
            existing_author.name = author_name
            existing_author.birth_date = birth_date
            existing_author.date_of_death = death_date

            # Commit the changes to the database
            db.session.commit()

            flash('Author details updated successfully!', 'success')

        return redirect(url_for('home'))


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """
    Gets book id from the url, queries the database by book id and deletes the book from the database
    After successful deletion, user is redirected to home page
    :param book_id: book id of book to delete from the database
    :return: renders the home template after successful deletion of book
    """
    book = Book.query.get_or_404(book_id)

    # Delete Book
    db.session.delete(book)

    # Commit the changes to the database
    db.session.commit()

    # Send success message to the user
    flash("Book deleted successfully!", 'success')

    return redirect(url_for('home'))


@app.route('/search_book', methods=['POST'])
def search_book():
    """
    Gets a search string from the url query parameters. Query the database using the search string.
    Returns book data if string matches any data in the database.
    """
    search_string = request.form.get('search-book')

    if not search_string:
        flash('You are did not type a word to search...', 'danger')
        return redirect(url_for('home'))

    # Perform a case-insensitive search for books or authors matching the search term
    matched_books = db.session.query(Book) \
        .join(Author).filter(
        or_(Book.title.ilike(f'%{search_string}%'), Author.name.ilike(f'%{search_string}%'))).all()

    if matched_books:
        # Convert the matched_books to a list of dictionaries
        books_data = [{'title': book.title,
                       'author': book.author.name,
                       'publication_year': book.publication_year,
                       'cover_url': book.cover_url,
                       } for book in matched_books]

        # show users the number of result found
        flash(f'{len(matched_books)} books found', 'success')

        return render_template('search.html', books_data=books_data)
    else:
        flash('No result found', 'danger')
        return redirect(url_for('home'))