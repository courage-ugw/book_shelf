import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# create the app
app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY')

# create the extension
db = SQLAlchemy()

# get the path to the database file
root_dir = os.path.dirname(__file__)
db_file_path = os.path.join(root_dir, 'data', 'library.sqlite')

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + db_file_path

# initialize the app with the extension
db.init_app(app)

from book_shelf import routes