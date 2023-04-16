import sqlite3
from sqlite3 import Error
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date

from helpers import apology, login_required, Habit


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
        return redirect("/")
    
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

    # create a list of Habit objects
    habits = []

    # Append habits list from database
    conn = create_connection(database)
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT habit FROM habits")
        rows = cur.fetchall()
        for row in rows:
            habits.append(Habit(row[0], len(habits) + 1, 0))

    # Create variables
    user_id = session["user_id"]
    today = date.today()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Loop through all habits and values
        for habit_id, habit_name in request.form.items():
            if habit_id.startswith("habit") and habit_name:
                value_id = habit_id.replace("habit", "value")
                value = request.form.get(value_id)

                # If the value of pressed button is 1 then flash user with message "Well done" if the value is -1 then flash user with message "You can do it"
                if value == "1":
                    flash("Well done!")
                    alert_type = "alert-success"
                elif value == "-1":
                    flash("Git gut lol")
                    alert_type = "alert-danger"

                # Check if there is already an entry for today for the habit in the database
                conn = create_connection(database)
                with conn:
                    cur = conn.cursor()
                    # Checks if there is already the same entry for today for this habit in the database
                    cur.execute("SELECT * FROM history WHERE users_id = ? AND date = ? AND habit = ? AND value = ?", (user_id, today, habit_name, value))
                    rows1 = cur.fetchall()
                    if rows1:
                        # Skip to next habit
                        continue 

                    # Checks if there is already an entry (no matter the value) for today for this habit in the database
                    cur.execute("SELECT * FROM history WHERE users_id = ? AND date = ? AND habit = ?", (user_id, today, habit_name))
                    rows2 = cur.fetchall()
                    if rows2:
                        # If there is an entry for today for this habit in the database, update the value
                        cur.execute("UPDATE history SET value = ? WHERE users_id = ? AND date = ? AND habit = ?", (value, user_id, today, habit_name))
                        conn.commit()
                    else:
                        # Insert habit entry into database if there is none for today
                        cur.execute("INSERT OR IGNORE INTO history (users_id, date, habit, value) VALUES(?, ?, ?, ?)", (user_id, today, habit_name, value))
                        conn.commit()

        # Count streak for each habit and update this value in the Habit object
        for habit in habits:
            user_id = session["user_id"]
            streak = 0
            habit_name = habit.name
            habit_id = habit.id
            conn = create_connection(database)
            with conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM history WHERE users_id = ? AND habit = ? ORDER BY date DESC", (user_id, habit_name))
                rows = cur.fetchall()
                for row in rows:
                    if row[2] == 1:
                        streak += 1
                    else:
                        break
            habit.streak = streak

        return render_template("index.html", habits=habits, alert_type=alert_type)
            
    # User reached route via GET (as by clicking a link or via redirect)
    else:

        # Count streak for each habit and update this value in the Habit object
        for habit in habits:
            streak = 0
            habit_name = habit.name
            habit_id = habit.id
            user_id = session["user_id"]
            conn = create_connection(database)
            with conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM history WHERE users_id = ? AND habit = ? ORDER BY date DESC", (user_id, habit_name))
                rows = cur.fetchall()
                for row in rows:
                    if row[2] == 1:
                        streak += 1
                    else:
                        break
            habit.streak = streak

        return render_template("index.html", habits=habits)

@app.route("/habits", methods=["GET", "POST"])
@login_required
def habits():
    """ Habits page """

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # List all habits from database
        habits = []
        user_id = session["user_id"]
        conn = create_connection(database)
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT habit FROM habits WHERE users_id = ?", (user_id,))
            rows = cur.fetchall()
            for row in rows:
                habits.append(row[0])

        # Create variables for different forms
        delete_habit = request.form.get("delete_habit")
        new_habit = request.form.get("new_habit")

        # Delete habit form
        if delete_habit:

            # Delete habit from database
            user_id = session["user_id"]
            conn = create_connection(database)
            with conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM habits WHERE users_id = ? AND habit = ?", (user_id, delete_habit))
                conn.commit()

            # Flash
            flash("Habit deleted!")
            alert_type = "alert-success"

            # Update habits list
            habits.remove(delete_habit)

            # Redirect user to habits page
            return render_template("habits.html", alert_type=alert_type, habits=habits)

        # New habit form
        if new_habit:

            # Check if the new habit is already in the habits list
            if new_habit in habits:
                flash("Habit already exists!")
                alert_type = "alert-danger"
                return render_template("habits.html", alert_type=alert_type, habits=habits)

            # Insert habit into database
            user_id = session["user_id"]
            conn = create_connection(database)
            with conn:
                cur = conn.cursor()
                cur.execute("INSERT OR IGNORE INTO habits (users_id, habit) VALUES(?, ?)", (user_id, new_habit))
                conn.commit()

            # Flash
            flash("Habit added!")
            alert_type = "alert-primary"

            # Update habits list
            habits.append(new_habit)
            
            # Redirect user to habits page
            return render_template("habits.html", alert_type=alert_type, habits=habits)
        
    # User reached route via GET (as by clicking a link or via redirect)
    habits = []
    user_id = session["user_id"]
    conn = create_connection(database)
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT habit FROM habits WHERE users_id = ?", (user_id,))
        rows = cur.fetchall()
        for row in rows:
            habits.append(row[0])
    
    return render_template("habits.html", habits=habits)

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    """ Dashboard page """

    return render_template("dashboard.html")







main()