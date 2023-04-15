import sqlite3
from sqlite3 import Error
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date

from helpers import apology, login_required


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
            flash("Please provide username!")
            alert_type = "alert-danger"
            return render_template("register.html", alert_type=alert_type)
        
        # Ensure password was submitted
        elif not password:
            flash("Please provide password!")
            alert_type = "alert-danger"
            return render_template("register.html", alert_type=alert_type)
        
        # Ensure the confirmation matches the original password
        elif password != confirmation:
            flash("Passwords do not match!")
            alert_type = "alert-danger"
            return render_template("register.html", alert_type=alert_type)
        
        # Check if username already exists
        conn = create_connection(database)
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT username FROM users WHERE username = ?", (username,))
            rows = cur.fetchall()
            if rows:
                flash("Username already exists")
                alert_type = "alert-danger"
                return render_template("register.html", alert_type=alert_type)

        # Insert new user into database
        conn = create_connection(database)
        with conn:
            user = (username, hash_password)
            user_id = create_user(conn, user)

        # Flash
        flash("Registered!")
        alert_type = "alert-primary"

        # Redirect user to login page
        return render_template("login.html", alert_type=alert_type)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
    
@app.route("/login", methods=["GET", "POST"])
def login():
    """ Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Create variables
        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure username was submitted
        if not username:
            flash("Please provide username!")
            alert_type = "alert-danger"
            return render_template("login.html", alert_type=alert_type)
            
        # Ensure password was submitted
        elif not password:
            flash("Please provide password!")
            alert_type = "alert-danger"
            return render_template("login.html", alert_type=alert_type)
        
        # Query database for username
        conn = create_connection(database)
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username = ?", (username,))
            rows = cur.fetchall()
            if len(rows) != 1 or not check_password_hash(rows[0][2], password):
                flash("Invalid username and/or password!")
                alert_type = "alert-danger"
                return render_template("login.html", alert_type=alert_type)
            
        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        # Flash
        flash("Logged in!")
        alert_type = "alert-primary"

        # Redirect user to home page
        return render_template("index.html", alert_type=alert_type)
    
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """ Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """ Homepage """

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Create variables
        user_id = session["user_id"]
        today = date.today()
        habit1 = request.form.get("habit1")
        value_habit1 = request.form.get("value1")

        # Check if there is already an entry for today for habit1 in the database
        conn = create_connection(database)
        with conn:
            cur = conn.cursor()
            # Checks if there is already the same entry for today for this habit in the database
            cur.execute("SELECT * FROM habits WHERE users_id = ? AND date = ? AND habit = ? AND value = ?", (user_id, today, habit1, value_habit1))
            rows1 = cur.fetchall()
            print(rows1)
            if rows1:
                return render_template("index.html")
            # Checks if there is already an entry for today for this habit in the database
            cur.execute("SELECT * FROM habits WHERE users_id = ? AND date = ? AND habit = ?", (user_id, today, habit1))
            rows2 = cur.fetchall()
            if rows2:
                # If there is an entry for today for this habit in the database, update the value
                cur.execute("UPDATE habits SET value = ? WHERE users_id = ? AND date = ? AND habit = ?", (value_habit1, user_id, today, habit1))
                conn.commit()
                return render_template("index.html")
            elif not rows2:
                # Insert habit entry into database if there is none for today
                cur.execute("INSERT OR IGNORE INTO habits (users_id, date, habit, value) VALUES(?, ?, ?, ?)", (user_id, today, habit1, value_habit1))
                conn.commit()
            




        



















        return render_template("index.html")
    
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("index.html")

@app.route("/habits", methods=["GET", "POST"])
@login_required
def habits():
    """ Habits page """

    return render_template("habits.html")

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    """ Dashboard page """

    return render_template("dashboard.html")







main()