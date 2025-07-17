import sqlite3

conn = sqlite3.connect('entry.db')

cursor = conn.cursor() 

cursor.execute('''
CREATE TABLE IF NOT EXISTS journal(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               date TEXT,
               song TEXT, 
               note TEXT
               )
               ''')
