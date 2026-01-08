import sqlite3
import json
import os
from datetime import datetime

# --- 設定檔名 ---
DB_FILE = "cityos.db"
STOCK_FILE = "stock_state.json"
LOG_FILE = "city_logs.json"

# --- 1. 資料庫初始化 (含 Frank 帳號) ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # 自動修復：檢查欄位數，若不對則重置
    c.execute("PRAGMA table_info(users)")
    columns = c.fetchall()
    if len(columns) > 0 and len(columns) != 9:
        print(">> 偵測到舊版資料庫，正在重置...")
        c.execute("DROP TABLE IF EXISTS users")
        conn.commit()

    # 建立表格
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id TEXT PRIMARY KEY, password TEXT, name TEXT, 
                  level INTEGER, exp INTEGER, money INTEGER, 
                  toxicity INTEGER, inventory TEXT, stocks TEXT)''')
    
    # 注入 Frank 帳號
    c.execute("SELECT id FROM users WHERE id='frank'")
    if not c.fetchone():
        print(">> 正在建立 Frank 管理員帳號...")
        # 設定初始背包與股票
        inv = '{"Stim-Pack": 99, "Nutri-Paste": 99, "Cyber-Arm": 1}'
        stk = '{"NVID": 1000, "TSMC": 1000}'
        # (id, pw, name, lvl, exp, money, tox, inv, stock)
        god_data = ("frank", "x", "⚡ Frank (Admin)", 100, 0, 999999999, 0, inv, stk)
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", god_data)

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

def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("SELECT id FROM users")
        return [row[0] for row in c.fetchall()]
    except: return []
    finally: conn.close()

# --- 3. 股市功能 ---
def get_global_stock_state():
    if not os.path.exists(STOCK_FILE):
        return {"prices": {}, "history": [], "last_update": 0}
    try:
        with open(STOCK_FILE, "r") as f: return json.load(f)
    except: return {"prices": {}, "history": [], "last_update": 0}

def save_global_stock_state(state):
    with open(STOCK_FILE, "w") as f: json.dump(state, f)

# --- 4. 系統日誌與環境功能 (缺的就是這些！) ---
def get_logs():
    if not os.path.exists(LOG_FILE): return []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return []

def add_log(message):
    logs = get_logs()
    time_str = datetime.now().strftime("%H:%M")
    logs.insert(0, f"[{time_str}] {message}") 
    if len(logs) > 30: logs = logs[:30] # 只保留最近30條
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False)
    except: pass

def apply_environmental_hazard(uid, user):
    import random
    # 10% 機率受到環境傷害 (輻射)
    if random.random() < 0.1: 
        dmg = random.randint(1, 5)
        user['toxicity'] = min(100, user.get('toxicity', 0) + dmg)
        save_user(uid, user)
        add_log(f"⚠️ {user['name']} 暴露在輻射中，毒素上升！")
        return True
    return False

def add_exp(uid, amount):
    user = get_user(uid)
    if user:
        user['exp'] += amount
        req = user['level'] * 100
        # 升級邏輯
        if user['exp'] >= req:
            user['exp'] -= req
            user['level'] += 1
            add_log(f"🆙 {user['name']} 晉升到了等級 {user['level']}！")
        save_user(uid, user)
