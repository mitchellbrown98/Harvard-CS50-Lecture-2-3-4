import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
# set database url
DATABASE_URL='postgres://mtfhiiqwnhkwox:61b8344459c7c69313a726356526328b7cbc3238b4e3a1900f70efc40157dc78@ec2-18-204-74-74.compute-1.amazonaws.com:5432/dc6rki78aqhs9l'

# Check for environment variable
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

        # Check if username and password are correct
        #if result[0] == None
            #return render_template("error.html", message="invalid username and/or password")

        #If login successful, remember user session
        session["username"] = result[0]

        # Redirect user to home page
        return render_template("hello.html", user=session["username"])

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
        #send data to the database
        db.execute("INSERT INTO webuser (username, password, firstname, lastname) VALUES (:username, :password, :fname, :lname)",
                        {"username":request.form.get("username"),
                         "password":request.form.get("password"),
                         "fname":request.form.get("fname"),
                         "lname":request.form.get("lname"),
                         })
        #Save changes
        db.commit()
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


@app.route("/hello", methods=["POST"])
def hello():
    name=request.form.get("name")
    username=request.form.get("username")
    password=request.form.get("password")
    return render_template("hello.html", name=name, username=username, password=password)
