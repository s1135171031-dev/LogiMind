# database.py
# 資料核心：負責存檔、讀檔、以及製造混亂

import json
import os
import random
import time
from datetime import datetime, timedelta
from config import STOCKS_DATA

USER_DB_FILE = "cityos_users.json"
STOCK_DB_FILE = "cityos_final_stock.json" # 最終版資料庫名稱

# --- 初始化與重置 ---

def init_db():
    # 1. 初始化使用者
    if not os.path.exists(USER_DB_FILE):
        users = {
            "admin": { 
                "password": "admin", "name": "System OVERLORD", "money": 9999, "job": "Admin", 
                "stocks": {}, "inventory": {}, "mailbox": []
            },
            "frank": { 
                "password": "x", "name": "Frank (Dev)", "money": 99999999, "job": "Gamemaster", 
                "stocks": {"CYBR": 5000}, "inventory": {"Firewall Key": 10}, "mailbox": []
            }
        }
        with open(USER_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4, ensure_ascii=False)
            
    # 2. 如果沒有股市，直接炸出來
    if not os.path.exists(STOCK_DB_FILE):
        rebuild_market()

def rebuild_market():
    """核彈級重置：生成 50 筆極度混亂的歷史數據"""
    print("🔥 SYSTEM: 重建股市歷史 (CHAOS MODE)...")
    current_prices = {k: v["base"] for k, v in STOCKS_DATA.items()}
    history = []
    
    # 模擬 50 輪歷史
    for i in range(50):
        row = {}
        for code, price in current_prices.items():
            # 無視設定，強制大幅波動 (±30% ~ ±50%)
            change = random.uniform(-0.4, 0.4)
            
            # 隨機黑天鵝
            if random.random() < 0.2: change += random.choice([-0.5, 0.5])
            
            new_price = int(price * (1 + change))
            new_price = max(1, min(50000, new_price)) # 價格不設上限，下限為1
            
            current_prices[code] = new_price
            row[code] = new_price
        
        # 偽造時間
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

# --- 使用者存取 ---

def get_all_users():
    try:
        with open(USER_DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def get_user(uid):
    return get_all_users().get(uid)

def save_user(uid, data):
    users = get_all_users()
    users[uid] = data
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

def create_user(uid, pwd, name):
    users = get_all_users()
    if uid in users: return False
    users[uid] = {
        "password": pwd, "name": name, "money": 1000, "job": "Unemployed",
        "stocks": {}, "inventory": {}, 
        "mailbox": [{"from": "System", "title": "歡迎", "msg": "歡迎來到地獄。", "time": str(datetime.now())}]
    }
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)
    return True

# --- 股市存取 ---

def get_global_stock_state():
    try:
        with open(STOCK_DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return None

def save_global_stock_state(state):
    with open(STOCK_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)
