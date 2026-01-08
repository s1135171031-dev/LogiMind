import sqlite3
import json
import os
from datetime import datetime

# 定義檔案名稱
DB_FILE = "cityos.db"
STOCK_FILE = "stock_state.json"
LOG_FILE = "city_logs.json"

def init_db():
    """初始化資料庫 (強制欄位檢查版)"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # 1. 檢查現有的資料表結構
    c.execute("PRAGMA table_info(users)")
    columns = c.fetchall()
    
    # 如果資料表存在，且欄位數量不是 9 個 (代表是舊版資料庫)
    if len(columns) > 0 and len(columns) != 9:
        print(f">> ⚠️ 偵測到資料庫版本過舊 (欄位數: {len(columns)})，正在執行強制重置...")
        c.execute("DROP TABLE IF EXISTS users")
        conn.commit() # 立即提交刪除
        columns = []  # 重置狀態

    # 2. 建立標準表格 (如果不存在)
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id TEXT PRIMARY KEY, password TEXT, name TEXT, 
                  level INTEGER, exp INTEGER, money INTEGER, 
                  toxicity INTEGER, inventory TEXT, stocks TEXT)''')
    
    # 3. ⚡ 上帝帳號注入
    # 先檢查 root 是否存在
    c.execute("SELECT id FROM users WHERE id='root'")
    if not c.fetchone():
        print(">> 正在建立 God Mode 帳號...")
        god_data = (
            "frank",            # id
            "x",           # password
            "⚡ SYSTEM ADMIN", # name
            100,               # level
            0,                 # exp
            999999999,         # money
            0,                 # toxicity
            # inventory
            '{"Stim-Pack": 99, "Nutri-Paste": 99, "Cyber-Arm": 1, "Trojan Virus": 999, "Anti-Rad Pill": 99}', 
            # stocks
            '{"NVID": 1000, "TSMC": 1000}')
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", god_data)
        print(">> ✅ root 帳號已建立")

    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM users WHERE id=?", (user_id,))
        row = c.fetchone()
    except:
        return None 
    conn.close()
    
    if row:
        # 防止讀取到舊格式造成的 index out of range
        try:
            return {
                "id": row[0], "password": row[1], "name": row[2],
                "level": row[3], "exp": row[4], "money": row[5],
                "toxicity": row[6],
                "inventory": json.loads(row[7]) if row[7] else {},
                "stocks": json.loads(row[8]) if row[8] else {}
            }
        except IndexError:
            return None # 格式錯誤視為無使用者
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
        users = [row[0] for row in c.fetchall()]
    except: users = []
    conn.close()
    return users

# --- 股市系統 ---
def get_global_stock_state():
    if not os.path.exists(STOCK_FILE):
        return {"prices": {}, "history": [], "last_update": 0}
    try:
        with open(STOCK_FILE, "r") as f: return json.load(f)
    except: return {"prices": {}, "history": [], "last_update": 0}

def save_global_stock_state(state):
    with open(STOCK_FILE, "w") as f: json.dump(state, f)

# --- 廣播系統 ---
def add_log(message):
    logs = get_logs()
    time_str = datetime.now().strftime("%H:%M")
    logs.insert(0, f"[{time_str}] {message}") 
    if len(logs) > 30: logs = logs[:30]
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False)
    except: pass

def get_logs():
    if not os.path.exists(LOG_FILE): return []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return []

# --- 輔助功能 ---
def apply_environmental_hazard(uid, user):
    import random
    if random.random() < 0.1: 
        dmg = random.randint(1, 5)
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
        save_user(uid, user)
