import sqlite3

conn = sqlite3.connect('lockers.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS lockers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        receiver_address TEXT NOT NULL,
        receiver_phone TEXT NOT NULL,
        locker_code TEXT NOT NULL UNIQUE,
        warehouse_address TEXT NOT NULL,
        sender_address TEXT NOT NULL,
        sender_phone TEXT NOT NULL
    )
''')

conn.commit()
conn.close()
print("Database initialized.")