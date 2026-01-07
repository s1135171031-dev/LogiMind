# database.py
# 用途: 資料處理 (新增強制重置股市功能)

import json
import os
import random
import time
from datetime import datetime, timedelta
from config import STOCKS_DATA

USER_DB_FILE = "cityos_users.json"
STOCK_DB_FILE = "cityos_stocks.json"

def init_db():
    # 1. 初始化使用者
    if not os.path.exists(USER_DB_FILE):
        users = {
            "admin": {
                "password": "admin", "name": "System OVERLORD", "money": 999999, 
                "job": "Admin",
                "stocks": {}, "inventory": {}, "mailbox": [], "active_missions": [], "pending_claims": [], "last_hack": 0
            },
            "frank": {
                "password": "x",
                "name": "Frank (Dev)",
                "money": 999999999,
                "job": "Gamemaster",
                "stocks": { "CYBR": 1000, "AI": 1000 }, 
                "inventory": { "Trojan Virus": 99, "Firewall": 99, "Brute Force Script": 99, "Mining GPU": 10 }, 
                "mailbox": [{"from":"System", "title":"Dev Access", "msg":"Developer mode activated.", "time":str(datetime.now())}],
                "active_missions": [], "pending_claims": [], "last_hack": 0
            }
        }
        with open(USER_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4, ensure_ascii=False)
            
    # 2. 如果沒有股市檔案，建立一個
    if not os.path.exists(STOCK_DB_FILE):
        rebuild_market()

# 🔥 新增這個函數：強制重置股市邏輯
def rebuild_market():
    print("🔥 正在引發金融海嘯 (重置股市)...")
    current_prices = {k: v["base"] for k, v in STOCKS_DATA.items()}
    history = []
    
    # 模擬 50 輪極度狂暴的歷史
    for i in range(50):
        row = {}
        for code, price in current_prices.items():
            base_vol = STOCKS_DATA[code]["volatility"]
            
            # 1. 基礎波動放大 4 倍
            change = random.uniform(-base_vol * 4, base_vol * 4)
            
            # 2. 黑天鵝事件 (20% 機率)
            if random.random() < 0.2: 
                # 暴漲暴跌 (-50% ~ +50%)
                change += random.choice([-0.5, 0.5])
            
            new_price = int(price * (1 + change))
            new_price = max(10, min(8000, new_price)) # 放寬上限
            
            current_prices[code] = new_price
            row[code] = new_price
        
        past_time = datetime.now() - timedelta(seconds=(50-i)*2)
        row["_time"] = past_time.strftime("%H:%M:%S")
        history.append(row)

    stock_state = {
        "last_update": time.time(),
        "prices": current_prices,
        "history": history
    }
    
    with open(STOCK_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(stock_state, f, indent=4)
    
    return True

# --- 以下保持不變 ---
def get_all_users():
    try:
        with open(USER_DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def get_user(uid):
    users = get_all_users()
    return users.get(uid)

def save_user(uid, data):
    users = get_all_users()
    users[uid] = data
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

def create_user(uid, pwd, name):
    users = get_all_users()
    if uid in users: return False
    users[uid] = {
        "password": pwd, "name": name, "money": 500, "job": "Citizen",
        "stocks": {}, "inventory": {}, 
        "mailbox": [{"from": "System", "title": "入籍通知", "msg": "歡迎來到 CityOS。", "time": str(datetime.now())}],
        "active_missions": [], "pending_claims": [], "last_hack": 0
    }
    with open(USER_DB_FILE, "w", encoding="utf-8") as f: json.dump(users, f, indent=4, ensure_ascii=False)
    return True

def get_global_stock_state():
    try:
        with open(STOCK_DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return None

def save_global_stock_state(state):
    with open(STOCK_DB_FILE, "w", encoding="utf-8") as f: json.dump(state, f, indent=4)

def send_mail(to_uid, from_uid, title, msg):
    users = get_all_users()
    if to_uid not in users: return False
    users[to_uid].setdefault("mailbox", []).append({"from": from_uid, "title": title, "msg": msg, "time": datetime.now().strftime("%Y-%m-%d %H:%M")})
    with open(USER_DB_FILE, "w", encoding="utf-8") as f: json.dump(users, f, indent=4, ensure_ascii=False)
    return True

def check_mission(uid, user, action_type):
    updated = False
    new_missions = []
    for m in user.get("active_missions", []):
        if m.get("type") == action_type:
            user.setdefault("pending_claims", []).append(m)
            updated = True
        else: new_missions.append(m)
    user["active_missions"] = new_missions
    if updated and len(user["active_missions"]) < 2:
        reward = random.randint(50, 200)
        task_pool = [
            {"title": "乖乖納稅", "desc": "再去買個東西。", "type": "shop_buy"},
            {"title": "鍵盤俠", "desc": "打個指令。", "type": "cli_input"},
            {"title": "賭徒心態", "desc": "買張股票。", "type": "stock_buy"}
        ]
        new_task = random.choice(task_pool); new_task["reward"] = reward
        user["active_missions"].append(new_task)
    if updated: save_user(uid, user); return True
    return False
