from flask import Flask, render_template, request
import random
import string
import sqlite3

app = Flask(__name__)

# 📦 Generate locker code
def generate_unique_locker_code():
    conn = sqlite3.connect('lockers.db')
    cursor = conn.cursor()
    while True:
        code = "LK" + str(random.randint(1000, 9999))
        cursor.execute("SELECT 1 FROM lockers WHERE locker_code = ?", (code,))
        if not cursor.fetchone():
            conn.close()
            return code

# 🏢 Generate warehouse address
def generate_warehouse_address():
    section = random.choice(string.ascii_uppercase)
    row = random.randint(1, 5)
    bin_number = random.randint(10, 99)
    return f"WH-{section}{row}-{bin_number}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        receiver_address = request.form['receiver_address']
        receiver_phone = request.form['receiver_phone']
        sender_address = request.form['sender_address']
        sender_phone = request.form['sender_phone']

        locker_code = generate_unique_locker_code()
        warehouse_address = generate_warehouse_address()

        conn = sqlite3.connect('lockers.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO lockers (customer_name, receiver_address, receiver_phone,
                                 locker_code, warehouse_address, sender_address, sender_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (customer_name, receiver_address, receiver_phone,
              locker_code, warehouse_address, sender_address, sender_phone))
        conn.commit()
        conn.close()

        locker_data = {
            'customer_name': customer_name,
            'receiver_address': receiver_address,
            'receiver_phone': receiver_phone,
            'sender_address': sender_address,
            'sender_phone': sender_phone,
            'locker_code': locker_code,
            'warehouse_address': warehouse_address
        }

        return render_template('a_index.html', locker=locker_data)

    return render_template('a_index.html', locker=None)

@app.route('/all')
def show_all():
    conn = sqlite3.connect('lockers.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT customer_name, receiver_address, receiver_phone,
               locker_code, warehouse_address, sender_address, sender_phone
        FROM lockers
    ''')
    lockers = cursor.fetchall()
    conn.close()
    return render_template('b_all_lockers.html', lockers=lockers)

if __name__ == '__main__':
    app.run(debug=True)