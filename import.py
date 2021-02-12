import os, csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# set database url
DATABASE_URL='postgres://mtfhiiqwnhkwox:61b8344459c7c69313a726356526328b7cbc3238b4e3a1900f70efc40157dc78@ec2-18-204-74-74.compute-1.amazonaws.com:5432/dc6rki78aqhs9l'

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

books = open ("books.csv")
reader = csv.reader(books)
for isbn, title, author, year in reader:
    db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
    {"isbn": isbn, "title": title, "author": author, "year": year})
print("import success")

db.commit()
