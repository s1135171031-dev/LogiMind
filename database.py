# database.py
import sqlite3
import json
import time

DB_FILE = "cityos_core.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, data TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS system_state (key TEXT PRIMARY KEY, value TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs (timestamp REAL, message TEXT)''')
    conn.commit()
    conn.close()
    
    if not get_user("frank"):
        default_user = {"name": "Frank", "password": "x", "level": 1, "exp": 0, "money": 1000, "stocks": {}}
        save_user("frank", default_user)

def get_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT data FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return json.loads(row[0]) if row else None

def save_user(user_id, data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (id, data) VALUES (?, ?)", (user_id, json.dumps(data)))
    conn.commit()
    conn.close()

def get_global_stock_state():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT value FROM system_state WHERE key='stock_market'")
    row = c.fetchone()
    conn.close()
    return json.loads(row[0]) if row else {"prices": {}, "history": [], "last_update": 0}

def save_global_stock_state(state):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO system_state (key, value) VALUES (?, ?)", ('stock_market', json.dumps(state)))
    conn.commit()
    conn.close()

def add_exp(user_id, amount):
    u = get_user(user_id)
    if u:
        u['exp'] += amount
        new_level = 1 + (u['exp'] // 100)
        if new_level > u['level']: u['level'] = new_level
        save_user(user_id, u)

def add_log(message):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO logs (timestamp, message) VALUES (?, ?)", (time.time(), message))
    conn.commit()
    conn.close()

def get_logs(limit=10):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT message FROM logs ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]
