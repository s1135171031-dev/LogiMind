import sqlite3
import json
import os
from datetime import datetime

# --- 設定檔名 ---
DB_FILE = "cityos.db"
STOCK_FILE = "stock_state.json"
LOG_FILE = "city_logs.json"

# --- 1. 資料庫初始化 ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # 檢查是否為舊版資料庫
    try:
        c.execute("PRAGMA table_info(users)")
        cols = c.fetchall()
        if len(cols) > 0 and len(cols) != 9:
            print(">> 重置舊版資料庫...")
            c.execute("DROP TABLE IF EXISTS users")
    except: pass

    # 建立 User 表格
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id TEXT PRIMARY KEY, password TEXT, name TEXT, 
                  level INTEGER, exp INTEGER, money INTEGER, 
                  toxicity INTEGER, inventory TEXT, stocks TEXT)''')
    
    # 強制修復 Frank 帳號
    c.execute("SELECT id FROM users WHERE id='frank'")
    if not c.fetchone():
        print(">> 重建 Frank 管理員...")
        inv = '{"Stim-Pack": 99, "Nutri-Paste": 99, "Cyber-Arm": 1, "Trojan Virus": 99}'
        stk = '{"NVID": 5000, "TSMC": 5000, "BTC": 10, "CYBR": 2000, "ARAS": 100, "DOGE": 10000}'
        # id, pw, name, lvl, exp, money, tox, inv, stock
        data = ("frank", "x", "⚡ Frank (Admin)", 100, 0, 999999999, 0, inv, stk)
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
        
    conn.commit()
    conn.close()

# --- 2. 使用者 CRUD ---
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

def create_user(uid, pwd, name):
    if get_user(uid): return False
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                     (uid, pwd, name, 1, 0, 1000, 0, "{}", "{}"))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

def save_user(uid, data):
    conn = sqlite3.connect(DB_FILE)
    conn.execute('''UPDATE users SET money=?, toxicity=?, inventory=?, stocks=?, level=?, exp=? WHERE id=?''',
                 (data['money'], data['toxicity'], json.dumps(data['inventory']), 
                  json.dumps(data['stocks']), data['level'], data['exp'], uid))
    conn.commit()
    conn.close()

# --- 3. 檔案存取 (已修正語法錯誤) ---
def get_global_stock_state():
    if not os.path.exists(STOCK_FILE):
        return {"prices": {}, "history": [], "last_update": 0}
    try:
        # 修正重點：這裡分行寫，Python 就不會報錯了
        with open(STOCK_FILE, "r") as f:
            return json.load(f)
    except:
        return {"prices": {}, "history": [], "last_update": 0}

def save_global_stock_state(state):
    try:
        with open(STOCK_FILE, "w") as f:
            json.dump(state, f)
    except: pass

def get_logs():
    if not os.path.exists(LOG_FILE): return []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return []

def add_log(msg):
    logs = get_logs()
    logs.insert(0, f"[{datetime.now().strftime('%H:%M')}] {msg}")
    if len(logs) > 30: logs = logs[:30]
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False)
    except: pass

# --- 4. 遊戲邏輯 ---
def apply_environmental_hazard(uid, user):
    import random
    if random.random() < 0.05:
        user['toxicity'] = min(100, user.get('toxicity', 0) + 2)
        save_user(uid, user)
        return True
    return False

def add_exp(uid, amount):
    user = get_user(uid)
    if user:
        user['exp'] += amount
        req = user['level'] * 100
        if user['exp'] >= req:
            user['exp'] -= req
            user['level'] += 1
            add_log(f"🆙 {user['name']} 升級到了 Lv.{user['level']}！")
            save_user(uid, user)
            return True 
        save_user(uid, user)
    return False
