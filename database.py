import sqlite3
import json
import os
from datetime import datetime

# --- 設定檔名 ---
DB_FILE = "cityos.db"
STOCK_FILE = "stock_state.json"
LOG_FILE = "city_logs.json"

# --- 1. 資料庫初始化 (含 Frank 帳號強制修復) ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # 自動修復：確保表格存在且格式正確
    try:
        c.execute("PRAGMA table_info(users)")
        columns = c.fetchall()
        # 如果欄位數量不對(舊版)，就刪除重建
        if len(columns) > 0 and len(columns) != 9:
            print(">> [System] 偵測到舊版資料庫結構，正在重置...")
            c.execute("DROP TABLE IF EXISTS users")
    except: pass

    # 建立標準表格
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id TEXT PRIMARY KEY, password TEXT, name TEXT, 
                  level INTEGER, exp INTEGER, money INTEGER, 
                  toxicity INTEGER, inventory TEXT, stocks TEXT)''')
    
    # ⚡ 強制注入 Frank 帳號 (如果不存在)
    c.execute("SELECT id FROM users WHERE id='frank'")
    if not c.fetchone():
        print(">> [System] 正在重建 Frank 管理員帳號與資產...")
        # 初始背包與股票 (你的東西都在這裡!)
        inv = '{"Stim-Pack": 99, "Nutri-Paste": 99, "Cyber-Arm": 1, "Trojan Virus": 99}'
        stk = '{"NVID": 5000, "TSMC": 5000, "BTC": 10}'
        # (id, pw, name, lvl, exp, money, tox, inv, stock)
        god_data = ("frank", "x", "⚡ Frank (Admin)", 100, 0, 999999999, 0, inv, stk)
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", god_data)
        print(">> [System] Frank 資產恢復完成。")

    conn.commit()
    conn.close()

# --- 2. 使用者功能 (CRUD) ---
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
            return {
                "id": row[0], "password": row[1], "name": row[2],
                "level": row[3], "exp": row[4], "money": row[5],
                "toxicity": row[6],
                "inventory": json.loads(row[7]) if row[7] else {},
                "stocks": json.loads(row[8]) if row[8] else {}
            }
        except: return None
    return None

def create_user(user_id, password, name):
    if get_user(user_id): return False
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (user_id, password, name, 1, 0, 1000, 0, "{}", "{}"))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

def save_user(user_id, data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''UPDATE users SET 
                 money=?, toxicity=?, inventory=?, stocks=?, level=?, exp=?
                 WHERE id=?''',
              (data['money'], data['toxicity'], 
               json.dumps(data['inventory']), json.dumps(data['stocks']), 
               data['level'], data['exp'], user_id))
    conn.commit()
    conn.close()

# --- 3. 股市與環境功能 ---
def get_global_stock_state():
    if not os.path.exists(STOCK_FILE): return {"prices": {}, "history": [], "last_update": 0}
    try: with open(STOCK_FILE, "r") as f: return json.load(f)
    except: return {"prices": {}, "history": [], "last_update": 0}

def save_global_stock_state(state):
    with open(STOCK_FILE, "w") as f: json.dump(state, f)

def get_logs():
    if not os.path.exists(LOG_FILE): return []
    try: with open(LOG_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return []

def add_log(message):
    logs = get_logs()
    logs.insert(0, f"[{datetime.now().strftime('%H:%M')}] {message}") 
    if len(logs) > 30: logs = logs[:30]
    try: with open(LOG_FILE, "w", encoding="utf-8") as f: json.dump(logs, f, ensure_ascii=False)
    except: pass

def apply_environmental_hazard(uid, user):
    import random
    if random.random() < 0.05: # 降低一點機率，別太常中毒
        dmg = random.randint(1, 3)
        user['toxicity'] = min(100, user.get('toxicity', 0) + dmg)
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
            add_log(f"🆙 {user['name']} 晉升到了等級 {user['level']}！")
            return True # 回傳升級訊號
        save_user(uid, user)
    return False
