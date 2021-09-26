from app import app
from flask_sqlalchemy import SQLAlchemy
from os import getenv


uri = getenv("DATABASE_URL")  # or other relevant config var
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)


app.config["SQLALCHEMY_DATABASE_URI"] = getenv(uri)

db = SQLAlchemy(app)


