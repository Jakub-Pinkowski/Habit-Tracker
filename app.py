from flask import Flask
from flask_session import Session

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Nope</p>"