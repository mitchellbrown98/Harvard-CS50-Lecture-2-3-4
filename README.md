This project is based on Harvard CS50 Web Programming with Python and Javascript 2018 - Lecture 2 (Flask), Lecture 3 (SQL), and Lecture 4 (ORMS & APIs).

application.py:
This file is the main python application used to run the backend of the website. 
There is a route for the home page where users can log on or register for an accouunt @app.route("/")
- renders index.html

There is a route to go through the login process: @app.route("/login")
- Checks if the username/password is correct. Renders to hello.html if access granted.
- If username/password is incorrect, error.html is rendered.

There is a route to go through the registration process: @app.route("/register")
- Checks if the username is available or not. If not, error.html is rendered.
- If username is unique, the password is hashed (method='pbkdf2:sha256', salt_length=8), and 
all form field values, and the hashed password value is sent to the webuser table in the database.
- After succesful registration, a success banner is shown and index.html is rendered to allow logon

There is a route to log out: @app.route("/logout")
- There is a logout button which simply clears the session info, and returns the user to the main logon page.

There is a route to search for books: @app.route("/search")
- Takes the search text and adds '%  %', and capitalizes it. A db query is performed to check for text similar
to the user entry in the isbn, title, and author columns.
- If no results are found, error2.html is rendered.
- If results are found, they are passed to the results.html page and it is rendered.

There is a route to navigate to a page for a selected book from the search results: @app.route("/<isbn>")
- Upon clicking on a book result in the results.html page this route is called. 
- url is just /<isbn> of book selected
- a google book api call is performed, and the result is converted to a json object. 
The avg rating and the number of reviews are then pulled out from the object to pass to the book.html page.
- if the request method is GET, a db query is performed to find the title, author, and year of the book from
the books table using the isbn. a 2nd query is performed to check for any reviews for the isbn. If no 
website reviews are found, only the book info, and google book api call info are passed to the book.html
page and it is rendered.
- If reviews are found, they are passed to the book.html page, along with the book info, and google book api
call info.
- If request method is POST, a check is done to see if the user has already submitted a review for the book,
if they have, error2.html is rendered and their review is not saved.
- If they have not submitted a review for the book yet, it is added to the table, another review table query
is performed for the book to get the most recent review, and the page is reloaded to show their new review, along
with any old ones. 

There is a route for an API call to my website: @app.route("/api/<isbn>")
- Called if a url is typed in with an ISBN /api/<isbn>
- If the isbn does not exist in my books table in the database, error2.html is rendered as a 404 error page.
- If the isbn does exist, an api call is perfomed to google books to get the title, author, publishedDate, 
ISBN_10, ISBN_13, ratingsCount, and averageRating values. The call result is converted into a json object,
and the values I want are pulled out. They are appended into an array, then a jsonify() object is returned using
the array values. 
- *app.config['JSON_SORT_KEYS'] = False had to be set so the jsonify object would be organized in the way I had arranged it

import.py:
This file reads and imports the books.csv file to my 'books' database table


HTML FILES (in templates folder):

layout.html - this file contains a basic layout and all styling elements for other html pages to use

index.html - this is the home page where users can log in/register for an account

register.html - this is the page where a user can register for an account. They must fill out their first name, 
last name, username, and password.

hello.html - this is the user home page, which can be seen once logged in. There is a search bar to search for 
books by title, author, or isbn

results.html - this page contains the list of book results after a search has been performed. Users can click
on any item in the list to navigate to a page for the specified book.

book.html - this page contains the book title, image of the cover, author, published date, isbn, average rating
from google books api, number of reviews from google books api, reviews from my website, and a form to submit 
a review for the book. 

error.html - this error page is used to navigate a user back to the login/registration page (ex. if they
enter the wrong username/password, or the username they want is not available when trying to register). 
A custom error message can be passed to this page.

error2.html - this error page is used within the website when the user is already logged in. It allows them
to navigate back to the user home / search page. A custom error message can be passed to this page.

*All form validation is done in the html pages by using javascript to check if all fields have some value each time the user stops typing. if they do, the button becomes enabled. It is disabled until all fields have value. 



