import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = '123'


def get_db_connection():
    conn = sqlite3.connect('habits.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            target_date TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


init_db()


@app.route('/')
def index():
    conn = get_db_connection()
    habits = conn.execute('SELECT * FROM habits ORDER BY target_date ASC').fetchall()
    conn.close()
    return render_template('index.html', habits=habits)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE login = ? AND password = ?', (login, password)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['login'] = user['login']
            return redirect(url_for('index'))
        else:
            flash('неправильний логинь или пароль')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')

        if not login or not password:
            flash('заполни все поля')
            return redirect(url_for('register'))

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (login, password) VALUES (?, ?)', (login, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            flash('пользователь с таким логином уже есть')
            return redirect(url_for('register'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/add', methods=['POST'])
def add_habit():
    task = request.form.get('task')
    date_str = request.form.get('date')
    if task and date_str:
        conn = get_db_connection()
        conn.execute('INSERT INTO habits (task, target_date) VALUES (?, ?)', (task, date_str))
        conn.commit()
        conn.close()
    return redirect(url_for('index'))


@app.route('/delete/<int:id>')
def delete_habit(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM habits WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, port=5003)