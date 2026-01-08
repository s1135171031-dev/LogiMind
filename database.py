import sqlite3
import json
import os
from datetime import datetime

DB_FILE = "cityos.db"
STOCK_FILE = "stock_state.json"
LOG_FILE = "city_logs.json"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("PRAGMA table_info(users)")
    columns = c.fetchall()
    
    if len(columns) > 0 and len(columns) != 9:
        c.execute("DROP TABLE IF EXISTS users")
        conn.commit()

    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id TEXT PRIMARY KEY, password TEXT, name TEXT, 
                  level INTEGER, exp INTEGER, money INTEGER, 
                  toxicity INTEGER, inventory TEXT, stocks TEXT)''')
    
    c.execute("SELECT id FROM users WHERE id='frank'")
    if not c.fetchone():
        god_data = ("frank", "x", "⚡ Frank (Admin)", 100, 0, 999999999, 0, 
                    '{"Stim-Pack": 99}', '{"NVID": 1000}')
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", god_data)
        
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM users WHERE id=?", (user_id,))
        row = c.fetchone()
    except: return None 
    conn.close()
    if row:
        try:
            return {"id": row[0], "password": row[1], "name": row[2],
                    "level": row[3], "exp": row[4], "money": row[5],
                    "toxicity": row[6],
                    "inventory": json.loads(row[7]) if row[7] else {},
                    "stocks": json.loads(row[8]) if row[8] else {}}
        except: return None
    return None

def create_user(user_id, password, name):
    if get_user(user_id): return False
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (user_id, password, name, 1, 0, 1000, 0, "{}", "{}"))
    conn.commit()
    conn.close()
    return True

def save_user(user_id, data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''UPDATE users SET money=?, toxicity=?, inventory=?, stocks=?, level=?, exp=? WHERE id=?''',
              (data['money'], data['toxicity'], json.dumps(data['inventory']), json.dumps(data['stocks']), 
               data['level'], data['exp'], user_id))
    conn.commit()
    conn.close()

def get_global_stock_state():
    if not os.path.exists(STOCK_FILE): return {"prices": {}, "history": [], "last_update": 0}
    try: with open(STOCK_FILE, "r") as f: return json.load(f)
    except: return {"prices": {}, "history": [], "last_update": 0}

def save_global_stock_state(state):
    with open(STOCK_FILE, "w") as f: json.dump(state, f)

def get_all_users(): return [] # Placeholder
def apply_environmental_hazard(uid, user): return False
def add_exp(uid, amount): pass
def add_log(msg): pass
def get_logs(): return []
