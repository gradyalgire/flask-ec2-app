import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Absolute paths (required when running under Apache)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'users.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = 'change-this-to-any-random-text'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 MB upload limit


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_user(username):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user


def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        firstname TEXT NOT NULL,
        lastname TEXT NOT NULL,
        email TEXT NOT NULL,
        address TEXT NOT NULL,
        filename TEXT,
        wordcount INTEGER
    )''')
    conn.commit()
    conn.close()


init_db()


# 4a + 4b + 4e: registration form (with file upload)
@app.route('/')
def index():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username'].strip()
    password = request.form['password']
    firstname = request.form['firstname'].strip()
    lastname = request.form['lastname'].strip()
    email = request.form['email'].strip()
    address = request.form['address'].strip()
    upload = request.files.get('file')

    if get_user(username):
        return render_template('register.html', error='That username is already taken.')

    # 4e-i: store the file, and count its words
    filename = None
    wordcount = None
    if upload and upload.filename:
        filename = secure_filename(username + '_' + upload.filename)
        path = os.path.join(UPLOAD_FOLDER, filename)
        upload.save(path)
        with open(path, encoding='utf-8', errors='ignore') as f:
            wordcount = len(f.read().split())

    conn = get_db()
    conn.execute(
        'INSERT INTO users (username, password, firstname, lastname, email, address, filename, wordcount) '
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (username, generate_password_hash(password), firstname, lastname, email, address, filename, wordcount))
    conn.commit()
    conn.close()

    # 4c: redirect to the display page
    session['username'] = username
    return redirect(url_for('profile'))


# 4d: re-login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = get_user(request.form['username'].strip())
        if user and check_password_hash(user['password'], request.form['password']):
            session['username'] = user['username']
            return redirect(url_for('profile'))
        return render_template('login.html', error='Invalid username or password.')
    return render_template('login.html')


# 4c + 4e-ii: display user info, word count, download button
@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    user = get_user(session['username'])
    if user is None:
        session.clear()
        return redirect(url_for('login'))
    return render_template('profile.html', user=user)


@app.route('/download')
def download():
    if 'username' not in session:
        return redirect(url_for('login'))
    user = get_user(session['username'])
    if user is None or not user['filename']:
        return redirect(url_for('profile'))
    return send_from_directory(UPLOAD_FOLDER, user['filename'], as_attachment=True)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
