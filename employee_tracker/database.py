import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            action TEXT,
            timestamp DATETIME
        )
    ''')
    conn.commit()
    conn.close()
    
def clear_actions():
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    c.execute('DELETE FROM actions')
    conn.commit()
    conn.close()


def log_action(employee_id, action):
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    c.execute('INSERT INTO actions (employee_id, action, timestamp) VALUES (?, ?, ?)',
              (employee_id, action, datetime.now()))
    conn.commit()
    conn.close()

def get_latest_actions(limit=10):
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    c.execute('SELECT * FROM actions ORDER BY timestamp DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    conn.close()
    return rows
