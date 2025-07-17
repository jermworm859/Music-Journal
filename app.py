import sqlite3
from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = 'keyword'

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        date = request.form['date']
        song = request.form['song']
        note = request.form['note']

        conn = sqlite3.connect('entry.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO journal (date, song, note) VALUES (?, ?, ?)", (date, song, note))
        conn.commit()
        conn.close()
    

    filter_date = request.args.get('date')
    conn = sqlite3.connect('entry.db')
    cursor = conn.cursor()
    if filter_date:
        cursor.execute("SELECT * FROM journal WHERE date = ? ORDER BY id DESC", (filter_date,))
    else:
        cursor.execute("SELECT * FROM journal ORDER BY id DESC")
    
    entries = cursor.fetchall()
    conn.close()
    
    return render_template('index.html', entries=entries)



@app.route('/delete', methods=['POST'])
def delete():
    entry_id = request.form['id']
    conn = sqlite3.connect('entry.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM journal WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/edit', methods=['GET'])
def show_edit_form():
    entry_id = request.args.get('id')
    conn = sqlite3.connect('entry.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM journal WHERE id = ?", (entry_id,))
    entry = cursor.fetchone()
    conn.close()
    return render_template('edit.html', entry=entry)

@app.route('/edit', methods=['POST'])
def edit():
    entry_id = request.form['id']
    date = request.form['date']
    song = request.form['song']
    note = request.form['note']

    conn = sqlite3.connect('entry.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE journal SET date = ?, song = ?, note = ? WHERE id = ?", (date, song, note, entry_id))
    conn.commit()
    conn.close()

    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('entry.db')
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[0], password):
            session['user'] = username
            return redirect('/')
        else:
            error = 'Invalid credentials. Try again.'
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

@app.route ('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        try:
            conn = sqlite3.connect('entry.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            conn.close()

            session['user'] = username
            return redirect('/')
        except sqlite3.IntegrityError:
            error = "Username already exists."
    return render_template('register.html', error=error)

if __name__ == '__main__':
    app.run(debug=True)