import sqlite3
from sqlite3 import Error
import json
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify, Response
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date, datetime, timedelta
import time
from helpers import login_required, Habit


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

database = (r"database.db")

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

# Create tables

def create_users_table(conn):
    """ Create users table """

    sql = ("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, hash TEXT NOT NULL)")
    cur = conn.cursor()
    cur.execute(sql)

def create_habits_table(conn):
    """ Create habits table """

    sql = ("CREATE TABLE IF NOT EXISTS habits (users_id INTEGER NOT NULL, habit TEXT NOT NULL, archived INTEGER NOT NULL DEFAULT 0, FOREIGN KEY(users_id) REFERENCES users(id))")
    cur = conn.cursor()
    cur.execute(sql)

def create_history_table (conn):
    """ Create history table """

    sql = ("CREATE TABLE IF NOT EXISTS history (users_id INTEGER NOT NULL, habit TEXT NOT NULL, date TEXT NOT NULL, value REAL, FOREIGN KEY(users_id) REFERENCES users(id), FOREIGN KEY(habit) REFERENCES habits(habit))")
    cur = conn.cursor()
    cur.execute(sql)

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

        # Check if password is at least 8 characters long
        elif len(password) < 8:
            flash("Password must be at least 8 characters long!")
            alert_type = "alert-danger"
            return render_template("register.html", alert_type=alert_type)
        
        # Check if password contains at least one number
        elif not any(char.isdigit() for char in password):
            flash("Password must contain at least one number!")
            alert_type = "alert-danger"
            return render_template("register.html", alert_type=alert_type)
        
        # Check if password contains at least one uppercase letter
        elif not any(char.isupper() for char in password):
            flash("Password must contain at least one uppercase letter!")
            alert_type = "alert-danger"
            return render_template("register.html", alert_type=alert_type)
        
        # Check if password contains at least one lowercase letter
        elif not any(char.islower() for char in password):
            flash("Password must contain at least one lowercase letter!")
            alert_type = "alert-danger"
            return render_template("register.html", alert_type=alert_type)
        
        # Check if password contains at least one special character
        elif not any(char in "!@#$%^&*()-+?_=,<>/;:[]{}" for char in password):
            flash("Password must contain at least one special character!")
            alert_type = "alert-danger"
            return render_template("register.html", alert_type=alert_type)
        
        # Ensure confirmation was submitted
        elif not confirmation:
            flash("Please provide confirmation!")
            alert_type = "alert-danger"
            return render_template("register.html", alert_type=alert_type)
        
        # Ensure the confirmation matches the original password
        elif password != confirmation:
            flash("Passwords do not match!")
            alert_type = "alert-danger"
            return render_template("register.html", alert_type=alert_type)
        
        # Create users table if it doesn't exist
        conn = create_connection(database)
        with conn:
            create_users_table(conn)

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

    # Redirect to register page if the user doesn't have an account
    register = request.form.get("register")
    if register:
        return redirect("/register")

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

    # Create variables
    user_id = session["user_id"]
    today = date.today()
    habit_name = request.form.get("habit_name")

    # Create a list of Habit objects
    habits = []

    # Create habits table if it doesn't exist
    conn = create_connection(database)
    with conn:
        create_habits_table(conn)

    # Create history table if it doesn't exist
    conn = create_connection(database)
    with conn:
        create_history_table(conn)

    # Append only unarchived habits list from database only for the current user 
    conn = create_connection(database)
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT habit FROM habits WHERE users_id = ? AND archived = 0", (user_id,))
        rows = cur.fetchall()
        for row in rows:
            habits.append(Habit(row[0], len(habits) + 1, 0))

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
                prev_date = None
                for row in rows:
                    if row[3] == 1:
                        curr_date = datetime.strptime(row[2], '%Y-%m-%d') # Convert string to datetime
                        if prev_date is None or (prev_date - curr_date) == timedelta(days=1):
                            streak += 1
                            prev_date = curr_date
                        else:
                            break
                    else:
                        break
                habit.streak = streak

        return render_template("index.html", habits=habits, alert_type=alert_type)
            
    # User reached route via GET (as by clicking a link or via redirect)
    else:

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
                prev_date = None
                for row in rows:
                    if row[3] == 1:
                        curr_date = datetime.strptime(row[2], '%Y-%m-%d') # Convert string to datetime
                        if prev_date is None or (prev_date - curr_date) == timedelta(days=1):
                            streak += 1
                            prev_date = curr_date
                        else:
                            break
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

        # List all habits from database except for the archived habits
        habits = []
        user_id = session["user_id"]
        conn = create_connection(database)
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT habit FROM habits WHERE users_id = ? AND archived = 0", (user_id,))
            rows = cur.fetchall()
            for row in rows:
                habits.append(row[0])

        # Create variables for different forms
        archive_habit = request.form.get("archive_habit")
        delete_habit = request.form.get("delete_habit")
        new_habit = request.form.get("new_habit")
        rename_habit = request.form.get("rename_habit")
        old_habit_name = request.form.get("old_habit_name")

        # Rename habit form
        if rename_habit:
            
            # Check if the new habit is already in the habits list
            if rename_habit in habits:
                flash("Habit already exists!")
                alert_type = "alert-danger"
                return render_template("habits.html", alert_type=alert_type, habits=habits)

            # Update habit in database
            user_id = session["user_id"]
            conn = create_connection(database)
            with conn:
                cur = conn.cursor()
                cur.execute("UPDATE habits SET habit = ? WHERE users_id = ? AND habit = ?", (rename_habit, user_id, old_habit_name))
                conn.commit()

            # Flash
            flash("Habit renamed!")
            alert_type = "alert-primary"

            # Update habits list but keeping the same order
            habits[habits.index(old_habit_name)] = rename_habit

            # Redirect user to habits page
            return render_template("habits.html", alert_type=alert_type, habits=habits)
        
        #Archive habit form
        if archive_habit:

            # Archive habit in database
            user_id = session["user_id"]
            conn = create_connection(database)
            with conn:
                cur = conn.cursor()
                cur.execute("UPDATE habits SET archived = 1 WHERE users_id = ? AND habit = ?", (user_id, archive_habit))
                conn.commit()

            # Flash
            flash("Habit archived!")
            alert_type = "alert-primary"

            # Update habits list but keeping the same order
            habits.remove(archive_habit)

            # Redirect user to habits page
            return render_template("habits.html", alert_type=alert_type, habits=habits)

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
            alert_type = "alert-primary"

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
    # List all habits from database except for the archived habits
    habits = []
    user_id = session["user_id"]
    conn = create_connection(database)
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT habit FROM habits WHERE users_id = ? AND archived = 0", (user_id,))
        rows = cur.fetchall()
        for row in rows:
            habits.append(row[0])
    
    return render_template("habits.html", habits=habits)

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    """ Dashboard page """

    # List all habits from database except for the archived habits
    habits = []
    user_id = session["user_id"]
    conn = create_connection(database)
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT habit FROM habits WHERE users_id = ? AND archived = 0", (user_id,))
        rows = cur.fetchall()
        for row in rows:
            habits.append(row[0])

    # Get the habit from the form
    habit = request.form.get("habit_dashboard")

    # Set default habit to the first habit in the list
    if habit == None:
        habit = habits[0]


    # Create a list with all the dates on which the habit were completed. 
    # The list will be used to color the calendar
    completed_dates = []
    conn = create_connection(database)
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT date FROM history WHERE users_id = ? AND habit = ? AND value = 1", (user_id, habit))
        rows = cur.fetchall()
        for row in rows:
            completed_dates.append(row[0])

    # Create a list with all the dates on which the habits were missed. 
    # The list will be used to color the calendar
    missed_dates = []
    conn = create_connection(database)
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT date FROM history WHERE users_id = ? AND habit = ? AND value = -1", (user_id, habit))
        rows = cur.fetchall()
        for row in rows:
            missed_dates.append(row[0])

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Remember the habit from the last time the page was refreshed
        session["habit"] = habit

        # Set default value to current date
        global pickedDate
        pickedDate = session["pickedDate"]

        # Get picked date from Javascript
        if request.data.decode('utf-8') != "":
            pickedDate = request.data.decode('utf-8')
            # Convert picked date to datetime object 
            pickedDate = datetime.strptime(pickedDate, '%Y-%m-%d').date()
        else:
            # Remember picked date from the last time the page was refreshed
            pickedDate = session["pickedDate"]
            print(f"session['pickedDate']: {session['pickedDate']}")
        # Store the value of pickedDate in the session
        session["pickedDate"] = pickedDate

        # Convert picked date to string
        stringDate = str(pickedDate)

        # Make sure that the picked date is not in the future
        if pickedDate > datetime.now().date():
            flash("Date cannot be in the future!")
            alert_type = "alert-danger"
            return render_template("dashboard.html", alert_type=alert_type, habit=habit, habits=habits, stringDate=stringDate, completed_dates=completed_dates, missed_dates=missed_dates)


        # Get current entry for habit from database from table "history" for the picked date
        user_id = session["user_id"]
        conn = create_connection(database)
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT value FROM history WHERE users_id = ? AND habit = ? AND date = ?", (user_id, habit, stringDate))
            global currentEntry
            currentEntry = cur.fetchone()
            if currentEntry:
                currentEntry = currentEntry[0]
                if currentEntry == 1:
                    currentEntry = "Done"
                elif currentEntry == -1:
                    currentEntry = "Missed"
                elif currentEntry == 0:
                    currentEntry = "Empty"
            else:
                currentEntry = "Empty"

        # Change entry form
        change_entry = request.form.get("change_entry")

        if change_entry:

            if change_entry == "Done":
                change_entry = 1
            elif change_entry == "Missed":
                change_entry = -1
            elif change_entry == "Empty":
                change_entry = 0

            # Update  entry in database
            # Check if there is already any entry for the picked date for the current user for the habit
            user_id = session["user_id"]
            conn = create_connection(database)
            with conn:
                cur = conn.cursor()
                cur.execute("SELECT value FROM history WHERE users_id = ? AND habit = ? AND date = ?", (user_id, habit, stringDate))
                entry = cur.fetchone()
                if entry:
                    # Update entry
                    cur.execute("UPDATE history SET value = ? WHERE users_id = ? AND habit = ? AND date = ?", (change_entry, user_id, habit, stringDate))
                    conn.commit()
                else:
                    # Insert entry
                    cur.execute("INSERT INTO history (users_id, habit, date, value) VALUES(?, ?, ?, ?)", (user_id, habit, stringDate, change_entry))
                    conn.commit()

            # Get current entry for habit from database from table "history" for the picked date
            user_id = session["user_id"]
            conn = create_connection(database)
            with conn:
                cur = conn.cursor()
                cur.execute("SELECT value FROM history WHERE users_id = ? AND habit = ? AND date = ?", (user_id, habit, stringDate))
                currentEntry = cur.fetchone()
                if currentEntry:
                    currentEntry = currentEntry[0]
                    if currentEntry == 1:
                        currentEntry = "Done"
                    elif currentEntry == -1:
                        currentEntry = "Missed"
                    elif currentEntry == 0:
                        currentEntry = "Empty"
                else:
                    currentEntry = "Empty"

            # Update completed_dates and missed_dates lists
            completed_dates = []
            conn = create_connection(database)
            with conn:
                cur = conn.cursor()
                cur.execute("SELECT date FROM history WHERE users_id = ? AND habit = ? AND value = 1", (user_id, habit))
                rows = cur.fetchall()
                for row in rows:
                    completed_dates.append(row[0])

            missed_dates = []
            conn = create_connection(database)
            with conn:
                cur = conn.cursor()
                cur.execute("SELECT date FROM history WHERE users_id = ? AND habit = ? AND value = -1", (user_id, habit))
                rows = cur.fetchall()
                for row in rows:
                    missed_dates.append(row[0])


            # Redirect user to dashboard page
            return render_template("dashboard.html", habit=habit, habits=habits, stringDate=stringDate, currentEntry=currentEntry, completed_dates=completed_dates, missed_dates=missed_dates)
        
        # Redirect user to dashboard page 
        else:
            return render_template("dashboard.html", habits=habits, habit=habit, stringDate=stringDate, currentEntry=currentEntry, completed_dates=completed_dates, missed_dates=missed_dates)

    # User reached route via GET (as by clicking a link or via redirect)
    else:

        # Set default value to current date
        pickedDate = datetime.now().date()

        # Use date from session instead of default value
        pickedDate = session["pickedDate"]

        # Convert picked date to string
        stringDate = str(pickedDate)

        # Get current entry for habit from database from table "history" for the picked date
        user_id = session["user_id"]
        conn = create_connection(database)
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT value FROM history WHERE users_id = ? AND habit = ? AND date = ?", (user_id, habit, stringDate))
            currentEntry = cur.fetchone()
            if currentEntry:
                currentEntry = currentEntry[0]
                if currentEntry == 1:
                    currentEntry = "Done"
                elif currentEntry == -1:
                    currentEntry = "Missed"
                elif currentEntry == 0:
                    currentEntry = "Empty"
            else:
                currentEntry = "Empty"

        return render_template("dashboard.html", habits=habits, habit=habit, stringDate=stringDate, currentEntry=currentEntry, completed_dates=completed_dates, missed_dates=missed_dates)


@app.route("/archive", methods=["GET", "POST"])
@login_required
def archive():
    """ Archive page """

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # List all the archived habits from database
        habits = []
        user_id = session["user_id"]
        conn = create_connection(database)
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT habit FROM habits WHERE users_id = ? AND archived = 1", (user_id,))
            rows = cur.fetchall()
            for row in rows:
                habits.append(row[0])

        restore_habit = request.form.get("restore_habit")
        delete_habit = request.form.get("delete_habit")

        # Restore habit form
        if restore_habit:

            # Restore habit in database
            user_id = session["user_id"]
            conn = create_connection(database)
            with conn:
                cur = conn.cursor()
                cur.execute("UPDATE habits SET archived = 0 WHERE users_id = ? AND habit = ?", (user_id, restore_habit))
                conn.commit()

            # Flash
            flash("Habit restored!")
            alert_type = "alert-primary"

            # Update habits list but keeping the same order
            habits.remove(restore_habit)

            # Redirect user to habits page
            return render_template("archive.html", alert_type=alert_type, habits=habits)

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
            alert_type = "alert-primary"

            # Update habits list
            habits.remove(delete_habit)

            # Redirect user to habits page
            return render_template("archive.html", alert_type=alert_type, habits=habits)

    # User reached route via GET (as by clicking a link or via redirect)
    # List all the archived habits from database
    habits = []
    user_id = session["user_id"]
    conn = create_connection(database)
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT habit FROM habits WHERE users_id = ? AND archived = 1", (user_id,))
        rows = cur.fetchall()
        for row in rows:
            habits.append(row[0])
    
    return render_template("archive.html", habits=habits)
                        

# Generate data for SSE
def generate_data():
    """ Update current entry """

    while True:
        yield f"data: {currentEntry}\n\n"
        time.sleep(0.01)

@app.route('/data')
def data():
    """ SSE route """
    return Response(generate_data(), mimetype='text/event-stream')

main()