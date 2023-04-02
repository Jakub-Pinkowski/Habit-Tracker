import sqlite3
from sqlite3 import Error
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology


# Main function
def main():
    
    # To be done - it's just a PLACEHOLDER
    print("Main funcion working now")



# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Databeses functions

database = (r"test.db")

def create_connection(db_file):
    """ Create a database connection to a SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn

def create_user(conn, user):
    """ Create a new user into the users table"""
    sql = ("INSERT INTO users (username, hash) VALUES(?, ?)")
    cur = conn.cursor()
    cur.execute(sql, user)
    conn.commit()
    return cur.lastrowid


# Define routes

@app.route("/", methods=["GET", "POST"])
def index():
    """ Homepage """

    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """ Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Create variables
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        hash_password = generate_password_hash(password)

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)
        
        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 400)
        
        # Ensure the confirmation matches the original password
        elif password != confirmation:
            return apology("passwords do not match", 400)
        
        # Check if username already exists
        conn = create_connection(database)
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT username FROM users WHERE username = ?", (username,))
            rows = cur.fetchall()
            if rows:
                return apology("username already exists", 400)

        # Insert new user into database
        conn = create_connection(database)
        with conn:
            user = (username, hash_password)
            user_id = create_user(conn, user)

        # Flash
        flash("Registered!")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
    
@app.route("/login", methods=["GET", "POST"])
def login():
    """ Log user in"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")









main()