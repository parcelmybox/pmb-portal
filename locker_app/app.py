from flask import Flask, render_template, request
import random
import string
import sqlite3
import os

app = Flask(__name__)

# 📌 Step 1: Create DB and table if not exists
def create_db():
    if not os.path.exists('lockers.db'):
        conn = sqlite3.connect('lockers.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lockers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                locker_code TEXT NOT NULL UNIQUE,
                warehouse_address TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

# Run this once when app starts
create_db()

# 🔐 Generate unique locker code
def generate_unique_locker_code():
    conn = sqlite3.connect('lockers.db')
    cursor = conn.cursor()
    while True:
        code = "LK" + str(random.randint(1000, 9999))
        cursor.execute("SELECT 1 FROM lockers WHERE locker_code = ?", (code,))
        if not cursor.fetchone():
            conn.close()
            return code

# 📦 Generate warehouse address
def generate_warehouse_address():
    section = random.choice(string.ascii_uppercase)
    row = random.randint(1, 5)
    bin_number = random.randint(10, 99)
    return f"WH-{section}{row}-{bin_number}"

# 🏠 Home route
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        locker_code = generate_unique_locker_code()
        warehouse_address = generate_warehouse_address()

        conn = sqlite3.connect('lockers.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO lockers (customer_name, locker_code, warehouse_address)
            VALUES (?, ?, ?)
        ''', (customer_name, locker_code, warehouse_address))
        conn.commit()
        conn.close()

        locker_data = {
            'customer_name': customer_name,
            'locker_code': locker_code,
            'warehouse_address': warehouse_address
        }

        return render_template('a_index.html', locker=locker_data)

    return render_template('a_index.html', locker=None)

# 📋 View all lockers
@app.route('/all')
def show_all():
    conn = sqlite3.connect('lockers.db')
    cursor = conn.cursor()
    cursor.execute('SELECT customer_name, locker_code, warehouse_address FROM lockers')
    rows = cursor.fetchall()
    conn.close()
    return render_template('b_all_lockers.html', lockers=rows)
if __name__ == '__main__':
    app.run(debug=True)