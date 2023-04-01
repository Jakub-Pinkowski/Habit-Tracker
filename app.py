import sqlite3
from sqlite3 import Error
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology

# Create a database connection
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print("e")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    create_connection(r"test.db")
    

# Configure application
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])

def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
