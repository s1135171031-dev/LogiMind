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
    
    # 1. 自動檢查並修復舊資料表
    try:
        c.execute("PRAGMA table_info(users)")
        cols = c.fetchall()
        # 如果欄位少於 9 個 (舊版)，刪除重建
        if len(cols) > 0 and len(cols) != 9:
            print(">> [System] 偵測到舊版架構，正在重構電路...")
            c.execute("DROP TABLE IF EXISTS users")
    except: pass

    # 2. 建立標準表格
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id TEXT PRIMARY KEY, password TEXT, name TEXT, 
                  level INTEGER, exp INTEGER, money INTEGER, 
                  toxicity INTEGER, inventory TEXT, stocks TEXT)''')
    
    # 3. 確保 Frank 存在 (你的錢和股票都在這)
    c.execute("SELECT id FROM users WHERE id='frank'")
    if not c.fetchone():
        print(">> [System] 正在初始化 Frank 的資產庫...")
        inv = '{"Logic Gate: AND": 10, "Capacitor": 5}'
        stk = '{"TSMC": 1000, "NVID": 500}'
        # 給 Frank 9 億，讓他不用擔心錢
        data = ("frank", "x", "⚡ Frank (Admin)", 100, 0, 999999999, 0, inv, stk)
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
        print(">> [System] 資產恢復完成。")

    conn.commit()
    conn.close()

# --- CRUD 操作 ---
def get_user(uid):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM users WHERE id=?", (uid,))
        row = c.fetchone()
    except: return None
    finally: conn.close()
    
    if row:
        return {
            "id": row[0], "password": row[1], "name": row[2],
            "level": row[3], "exp": row[4], "money": row[5],
            "toxicity": row[6],
            "inventory": json.loads(row[7]) if row[7] else {},
            "stocks": json.loads(row[8]) if row[8] else {}
        }
    return None

def save_user(uid, data):
    conn = sqlite3.connect(DB_FILE)
    conn.execute('''UPDATE users SET money=?, toxicity=?, inventory=?, stocks=?, level=?, exp=? WHERE id=?''',
                 (data['money'], data['toxicity'], json.dumps(data['inventory']), 
                  json.dumps(data['stocks']), data['level'], data['exp'], uid))
    conn.commit()
    conn.close()

# --- 系統檔案 ---
def get_global_stock_state():
    if not os.path.exists(STOCK_FILE): return {"prices": {}, "history": [], "last_update": 0}
    try:
        with open(STOCK_FILE, "r") as f: return json.load(f)
    except: return {"prices": {}, "history": [], "last_update": 0}

def save_global_stock_state(state):
    try:
        with open(STOCK_FILE, "w") as f: json.dump(state, f)
    except: pass

def get_logs():
    if not os.path.exists(LOG_FILE): return []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return []

def add_log(msg):
    logs = get_logs()
    logs.insert(0, f"[{datetime.now().strftime('%H:%M')}] {msg}")
    if len(logs) > 30: logs = logs[:30]
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f: json.dump(logs, f, ensure_ascii=False)
    except: pass
    
def add_exp(uid, amount):
    user = get_user(uid)
    if user:
        user['exp'] += amount
        req = user['level'] * 100
        if user['exp'] >= req:
            user['exp'] -= req
            user['level'] += 1
            add_log(f"🆙 {user['name']} 知識量提升！現在是 Lv.{user['level']}")
            save_user(uid, user)
            return True
        save_user(uid, user)
    return False
