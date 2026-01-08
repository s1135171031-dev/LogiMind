# database.py
import sqlite3
import json
import os
from datetime import datetime

# 定義檔案名稱
DB_FILE = "cityos.db"
STOCK_FILE = "stock_state.json"
LOG_FILE = "city_logs.json"

# database.py (只修改這個函式，其他保留)

def init_db():
    """初始化資料庫並植入上帝帳號"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # 1. 建立表格
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id TEXT PRIMARY KEY, password TEXT, name TEXT, 
                  level INTEGER, exp INTEGER, money INTEGER, 
                  toxicity INTEGER, inventory TEXT, stocks TEXT)''')
    
    # 2. ⚡ 後門植入：檢查是否存在 root 帳號，沒有則建立
    c.execute("SELECT id FROM users WHERE id='root'")
    if not c.fetchone():
        print(">> ⚠️ 偵測到系統重置，正在注入管理員權限...")
        # 格式: (id, password, name, level, exp, money, toxicity, inventory, stocks)
        god_mode_data = (
            "root",            # ID
            "admin",           # 密碼
            "⚡ SYSTEM ADMIN", # 顯示名稱
            100,               # 等級
            0,                 # 經驗
            999999999,         # 金錢 (無限)
            0,                 # 毒素
            '{"Stim-Pack": 99, "Nutri-Paste": 99, "Cyber-Arm": 1, "Trojan Virus": 999, "Anti-Rad Pill": 99}', # 滿背包
            '{"NVID": 1000, "TSMC": 1000}' # 初始股票
        )
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", god_mode_data)
        print(">> ✅ 上帝帳號 'root' 已恢復。")

    conn.commit()
    conn.close()
def get_user(user_id):
    """讀取使用者資料"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            "id": row[0], "password": row[1], "name": row[2],
            "level": row[3], "exp": row[4], "money": row[5],
            "toxicity": row[6],
            "inventory": json.loads(row[7]) if row[7] else {},
            "stocks": json.loads(row[8]) if row[8] else {}
        }
    return None

def create_user(user_id, password, name):
    """建立新使用者"""
    if get_user(user_id): return False
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (user_id, password, name, 1, 0, 1000, 0, "{}", "{}"))
    conn.commit()
    conn.close()
    return True

def save_user(user_id, data):
    """儲存使用者狀態"""
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
    """取得所有使用者ID (用於PVP)"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id FROM users")
    users = [row[0] for row in c.fetchall()]
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

# --- 廣播系統 (New) ---
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
    """隨機環境傷害"""
    import random
    if random.random() < 0.1: # 10% 機率
        dmg = random.randint(1, 5)
        user['toxicity'] = min(100, user.get('toxicity', 0) + dmg)
        save_user(uid, user)
        return True
    return False

def add_exp(uid, amount):
    """增加經驗值與升級"""
    user = get_user(uid)
    if user:
        user['exp'] += amount
        req = user['level'] * 100
        if user['exp'] >= req:
            user['exp'] -= req
            user['level'] += 1
            add_log(f"🆙 {user['name']} 晉升到了等級 {user['level']}！")
        save_user(uid, user)
