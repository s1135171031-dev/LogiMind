# database.py
import json
import os
import random
import time
from datetime import datetime, timedelta
# ⚠️ 注意：這裡會嘗試讀取 config.py，如果 config.py 不在同個資料夾，這裡就會報錯
from config import STOCKS_DATA

USER_DB_FILE = "cityos_users.json"
STOCK_DB_FILE = "cityos_chaos_market.json"

def init_db():
    if not os.path.exists(USER_DB_FILE):
        users = {
            "admin": { "password": "admin", "name": "System OVERLORD", "money": 99999, "job": "Admin", "stocks": {}, "inventory": {}, "mailbox": [] },
            "frank": { "password": "x", "name": "Frank (Dev)", "money": 50000, "job": "Hacker", "stocks": {"CYBR": 100}, "inventory": {}, "mailbox": [] }
        }
        with open(USER_DB_FILE, "w", encoding="utf-8") as f: json.dump(users, f, indent=4, ensure_ascii=False)
            
    if not os.path.exists(STOCK_DB_FILE):
        rebuild_market()

def rebuild_market():
    current_prices = {k: v["base"] for k, v in STOCKS_DATA.items()}
    history = []
    
    for i in range(50):
        row = {}
        for code, price in current_prices.items():
            change_pct = random.uniform(-0.2, 0.2)
            force_jitter = random.randint(-5, 5) 
            if force_jitter == 0: force_jitter = 1
            
            new_price = int(price * (1 + change_pct) + force_jitter)
            new_price = max(1, new_price)
            
            current_prices[code] = new_price
            row[code] = new_price
        
        past_time = datetime.now() - timedelta(seconds=(50-i)*2)
        row["_time"] = past_time.strftime("%H:%M:%S")
        history.append(row)

    state = { "last_update": time.time(), "prices": current_prices, "history": history }
    with open(STOCK_DB_FILE, "w", encoding="utf-8") as f: json.dump(state, f, indent=4)

def get_all_users():
    try:
        with open(USER_DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def get_user(uid): return get_all_users().get(uid)

def save_user(uid, data):
    users = get_all_users(); users[uid] = data
    with open(USER_DB_FILE, "w", encoding="utf-8") as f: json.dump(users, f, indent=4, ensure_ascii=False)

def create_user(uid, pwd, name):
    users = get_all_users()
    if uid in users: return False
    users[uid] = { "password": pwd, "name": name, "money": 1000, "job": "Citizen", "stocks": {}, "inventory": {}, "mailbox": [] }
    with open(USER_DB_FILE, "w", encoding="utf-8") as f: json.dump(users, f, indent=4, ensure_ascii=False)
    return True

def get_global_stock_state():
    try: with open(STOCK_DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return None

def save_global_stock_state(state):
    with open(STOCK_DB_FILE, "w", encoding="utf-8") as f: json.dump(state, f, indent=4)
