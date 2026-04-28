from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "secret123"

# ----------- DATABASE -----------

def get_db():
    return sqlite3.connect("users.db")

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ----------- FUNCTIONS -----------

def add_user(username, password):
    conn = get_db()
    cur = conn.cursor()

    hashed = generate_password_hash(password)

    try:
        cur.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed)
        )
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

def check_user(username, password):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT password FROM users WHERE username=?",
        (username,)
    )
    user = cur.fetchone()

    conn.close()

    if user and check_password_hash(user[0], password):
        return True
    return False

# ----------- ROUTES -----------

# LOGIN
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        pwd = request.form.get('password')

        if check_user(user, pwd):
            session['user'] = user
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Invalid Credentials")

    return render_template('login.html')

# SIGNUP
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user = request.form.get('username')
        pwd = request.form.get('password')

        if add_user(user, pwd):
            return redirect(url_for('login'))
        else:
            return render_template('signup.html', error="User already exists")

    return render_template('signup.html')

# HOME
@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))

    return render_template("index.html")

# LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# ----------- RUN -----------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))