from book_shelf import db, app


class Author(db.Model):
    """
    Creates the author table, with id, name, birth_date and date of death columns
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date)
    date_of_death = db.Column(db.Date)

    def __repr__(self):
        """ String representation of the Author Object"""
        return f"Author(id = {self.id}, name = {self.name}, birth_date = {self.birth_date}, date_of_death = {self.date_of_death})"


class Book(db.Model):
    """
    Creates the book table, with isbn, cover url, title, publication_year, author_id columns
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    cover_url = db.Column(db.String, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)

    author = db.relationship('Author', backref=db.backref('books', lazy=True))

    def __repr__(self):
        """ String representation of the Book Object"""

        return f"<Book(id={self.id}, isbn='{self.isbn}', title='{self.title}', publication_year={self.publication_year}, author_id={self.author_id})>"


# Create tables
with app.app_context():
    db.create_all()