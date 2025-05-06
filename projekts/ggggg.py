from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

# --- VEIDOJA ---
# Sofija Dagenvalda un Alina Apine

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# --- Datubazes nosaukums ---
DB_NAME = 'hiphop.db'

@app.route('/')
def index():
    return render_template('index.html')

# --- Tabula un datubaze ---
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS solo_registration (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            birth_year TEXT NOT NULL,
            category TEXT NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS team_registration (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT NOT NULL,
            team_leader TEXT NOT NULL,
            team_category TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

init_db()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        conn = get_db_connection()
        c = conn.cursor()

        if 'name' in request.form:
            c.execute('INSERT INTO solo_registration (name, birth_year, category) VALUES (?, ?, ?)',
                      (request.form['name'], request.form['birth_year'], request.form['category']))
        elif 'team_name' in request.form:
            c.execute('INSERT INTO team_registration (team_name, team_leader, team_category) VALUES (?, ?, ?)',
                      (request.form['team_name'], request.form['team_leader'], request.form['team_category']))

        conn.commit()
        conn.close()
        return redirect(url_for('register'))

    return render_template('register.html')


@app.route('/saraksti')
def saraksti():
    conn = get_db_connection()
    c = conn.cursor()

    c.execute('SELECT name, birth_year, category FROM solo_registration')
    solos = c.fetchall()

    c.execute('SELECT team_name, team_leader, team_category FROM team_registration')
    teams = c.fetchall()

    conn.close()
    return render_template('saraksts.html', solos=solos, teams=teams)


# --- Admina lapa ---
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'admin_logged_in' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    teams = conn.execute('SELECT * FROM team_registration').fetchall()
    solos = conn.execute('SELECT * FROM solo_registration').fetchall()
    conn.close()
    return render_template('admin.html', teams=teams, solos=solos)


# --- Dzēst ierakstu ---
@app.route('/delete_team/<int:id>')
def delete_team(id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM team_registration WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/delete_solo/<int:id>')
def delete_solo(id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM solo_registration WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))


# --- Pieteikšanās adminam ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if check_password_hash(generate_password_hash('hiphop123'), password):   #PAROLE
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return 'Nepareiza parole'
    return render_template('login.html')


# --- Iziet ---
@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

# --- Rediģēt ---
@app.route('/update_team/<int:id>', methods=['POST'])
def update_team(id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('login'))

    team_name = request.form['team_name']
    team_leader = request.form['team_leader']
    team_category = request.form['team_category']

    conn = get_db_connection()
    conn.execute('UPDATE team_registration SET team_name = ?, team_leader = ?, team_category = ? WHERE id = ?',
                 (team_name, team_leader, team_category, id))
    conn.commit()
    conn.close()

    return redirect(url_for('admin'))

@app.route('/update_solo/<int:id>', methods=['POST'])
def update_solo(id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('login'))

    name = request.form['name']
    birth_year = request.form['birth_year']
    category = request.form['category']

    conn = get_db_connection()
    conn.execute('UPDATE solo_registration SET name = ?, birth_year = ?, category = ? WHERE id = ?',
                 (name, birth_year, category, id))
    conn.commit()
    conn.close()

    return redirect(url_for('admin'))



if __name__ == '__main__':
    app.run(debug=True)
