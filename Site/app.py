import sqlite3
from flask import Flask, render_template, g

app = Flask(__name__)

Database = './users.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(Database)
    return db


@app.route("/")
@app.route("/home")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/users")
def users():
    database = get_db()
    cursor = database.cursor()
    cursor.execute(f"SELECT * FROM Users")
    users_info = cursor.fetchall()
    return render_template("users.html", users_info=users_info)


if __name__ == "__main__":
    app.run(debug=True)
