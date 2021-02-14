import os

from flask import Flask, session, render_template, request, flash, json, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from werkzeug.security import check_password_hash, generate_password_hash

import requests


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Check for environment variable s
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


# Start at the login/register page
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/user")
def user():
    return render_template("hello.html", user=session["username"])


@app.route("/login", methods=["GET", "POST"])
def login():
    #Clear out session incase someone is logged in
    session.clear();
    username = request.form.get("username")

    if request.method == "POST":
        #Query database to see if username exists
        rows = db.execute("SELECT * FROM webuser WHERE username = :username",
                                    {"username": username})
        result = rows.fetchone()

        # Check if username and password are correct, display error if not
        if result == None or not check_password_hash(result[1], request.form.get("password")):
            return render_template("error.html", message="invalid username and/or password")

        #If login successful, remember user session
        session["username"] = result[0]

        # Redirect user to home page

        return render_template("hello.html", user=session["username"])
        #return redirect(url_for('user')

    else:
        return render_template("index.html")


#For registering new user
@app.route("/register", methods=["GET", "POST"])
def register():
    #Clear out session incase someone is logged in
    session.clear();

    if request.method == "POST":
        username=request.form.get("username")
        #verify username is unique
        unique = db.execute("SELECT * FROM webuser WHERE username = :username",
                          {"username":request.form.get("username")}).fetchone()
        #show error if not unique
        if unique:
            return render_template("error.html", message="username not available")

        #hash the password
        hashedPassword = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)
        #send data to the database
        db.execute("INSERT INTO webuser (username, password, firstname, lastname) VALUES (:username, :password, :fname, :lname)",
                        {"username":request.form.get("username"),
                         "password":hashedPassword,
                         "fname":request.form.get("fname"),
                         "lname":request.form.get("lname"),
                         })
        #Save changes
        db.commit()
        flash('Account created', 'success')
        return render_template("index.html")

    else:
        return render_template("register.html")

#To log user out
@app.route("/logout")
def logout():
    #clear the session
    session.clear()
    #go back to logon/home page
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():

    searchtext = "%" + request.form.get("searchinput") + "%"
    searchtext = searchtext.title()
    #search for books based on isbn, author, title compared to similar text
    books = db.execute("SELECT isbn, title, author, year FROM books WHERE \
                        isbn LIKE :searchtext OR \
                        title LIKE :searchtext OR \
                        author LIKE :searchtext",
                        {"searchtext": searchtext})

    if books.rowcount == 0:
        return render_template("error2.html", message="No results found")

    booklist = books.fetchall()
    return render_template("results.html", booklist=booklist)


@app.route("/<isbn>", methods=["POST", "GET"])
def bookinfo(isbn):
    bookid=isbn
    key = "AIzaSyCyfcKdwtREM6cGbHJzO-tp4hIkIYjaDjQ"

    #Google Books api
    #send request with the book isbn
    res = requests.get("https://www.googleapis.com/books/v1/volumes",
                params={"key": key, "q": bookid})
    #convert the response to a Json object
    rep = res.json()
    #create object to store avg rating and rating count
    Gbooks=[]
    Gbooks.append(rep['items'][0]['volumeInfo']['averageRating'])
    Gbooks.append(rep['items'][0]['volumeInfo']['ratingsCount'])
    Gbooks.append(rep['items'][0]['volumeInfo']['imageLinks']['thumbnail'])

    if request.method == "GET":
        #Search book by isbn
        search = db.execute("SELECT isbn, title, author, year FROM books WHERE \
                        isbn = :isbn",
                        {"isbn": bookid})

        bookinfo = search.fetchall()

        reviews = db.execute ("SELECT * FROM reviews WHERE isbn = :isbn",
                          {"isbn": bookid})

        #if no website reviews found, display page without passing review array
        if reviews.rowcount == 0:
            return render_template("book.html", bookinfo=bookinfo, Gbooks=Gbooks)

        return render_template("book.html", bookinfo=bookinfo, reviews=reviews, Gbooks=Gbooks)

    #if user submits a review to the book page
    if request.method == "POST":
        #verify the user has not already submitted a review for this book
        unique = db.execute("SELECT * FROM reviews WHERE username = :username AND isbn = :isbn",
                          {"username":session["username"],
                           "isbn": bookid
                             })

        #show error if there is already a review for the book by the user
        if unique.rowcount == 1:
            return render_template("error2.html", message="You have already submitted 1 review for this book")

        #add review to the table
        db.execute("INSERT INTO reviews (username, review, rating, isbn) VALUES (:username, :review, :rating, :isbn)",
                    {"username":session["username"],
                     "review":request.form.get("comments"),
                     "rating":request.form.get("rating"),
                     "isbn":bookid
                        })
        #Save changes
        db.commit()
        flash('Review submitted', 'success')

        #re-query table and send to page
        search = db.execute("SELECT isbn, title, author, year FROM books WHERE \
                    isbn = :isbn",
                    {"isbn": bookid})

        bookinfo = search.fetchall()

        reviews = db.execute ("SELECT * FROM reviews WHERE isbn = :isbn",
                        {"isbn": bookid})

        if reviews.rowcount == 0:
            return render_template("book.html", bookinfo=bookinfo, Gbooks=Gbooks)

        return render_template("book.html", bookinfo=bookinfo, reviews=reviews, Gbooks=Gbooks)


@app.route("/api/<isbn>", methods=['GET'])
def api_call(isbn):
    bookid=isbn
    key = "AIzaSyCyfcKdwtREM6cGbHJzO-tp4hIkIYjaDjQ"

    #check if isbn exists in db, if not throw error
    check = db.execute ("SELECT * FROM books WHERE isbn = :isbn",
                    {"isbn": bookid})

    if check.rowcount == 0:
        return render_template("error2.html", message="404 Error - ISBN not found"), 404

    #Google Books api
    #send request with the book isbn
    res = requests.get("https://www.googleapis.com/books/v1/volumes",
                params={"key": key, "q": bookid})
    #convert the response to a Json object
    rep = res.json()

    #create object to store avg rating and rating count
    Gbooks=[]
    Gbooks.append(rep['items'][0]['volumeInfo']['title'])
    Gbooks.append(rep['items'][0]['volumeInfo']['authors'][0])
    Gbooks.append(rep['items'][0]['volumeInfo']['publishedDate'])
    Gbooks.append(rep['items'][0]['volumeInfo']['industryIdentifiers'][0]['identifier'])
    Gbooks.append(rep['items'][0]['volumeInfo']['industryIdentifiers'][1]['identifier'])
    Gbooks.append(rep['items'][0]['volumeInfo']['ratingsCount'])
    Gbooks.append(rep['items'][0]['volumeInfo']['averageRating'])

    return jsonify({
    "title": Gbooks[0],
    "author": Gbooks[1],
    "publishedDate": Gbooks[2],
    "ISBN_10": Gbooks[3],
    "ISBN_13": Gbooks[4],
    "reviewCount": Gbooks[5],
    "averageRating": Gbooks[6]
    })
