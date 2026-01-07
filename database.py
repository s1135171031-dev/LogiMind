# database.py
# 用途: 絕對暴力版 (強制所有股票歷史大暴走)

import json
import os
import random
import time
from datetime import datetime, timedelta
from config import STOCKS_DATA

USER_DB_FILE = "cityos_users.json"
# 🔥 再改一次檔名，強制系統重新生成 (這是最後一次改名了)
STOCK_DB_FILE = "cityos_stocks_insane.json" 

def init_db():
    if not os.path.exists(USER_DB_FILE):
        users = {
            "admin": { "password": "admin", "name": "System OVERLORD", "money": 999999, "job": "Admin", "stocks": {}, "inventory": {}, "mailbox": [], "active_missions": [], "pending_claims": [], "last_hack": 0 },
            "frank": { "password": "x", "name": "Frank (Dev)", "money": 999999999, "job": "Gamemaster", "stocks": { "CYBR": 1000, "AI": 1000 }, "inventory": {}, "mailbox": [], "active_missions": [], "pending_claims": [], "last_hack": 0 }
        }
        with open(USER_DB_FILE, "w", encoding="utf-8") as f: json.dump(users, f, indent=4, ensure_ascii=False)
            
    if not os.path.exists(STOCK_DB_FILE):
        rebuild_market()

def rebuild_market():
    print("🔥 正在生成瘋狂股市 (無視任何穩定設定)...")
    current_prices = {k: v["base"] for k, v in STOCKS_DATA.items()}
    history = []
    
    # 模擬 50 輪
    for i in range(50):
        row = {}
        for code, price in current_prices.items():
            
            # 🔥🔥🔥 這裡不讀取 config 了，直接寫死超大波動 🔥🔥🔥
            # 每一輪強制波動 ±10% 到 ±40%
            change = random.uniform(-0.4, 0.4) 
            
            new_price = int(price * (1 + change))
            new_price = max(5, min(20000, new_price)) # 範圍拉很大
            
            current_prices[code] = new_price
            row[code] = new_price
        
        past_time = datetime.now() - timedelta(seconds=(50-i)*2)
        row["_time"] = past_time.strftime("%H:%M:%S")
        history.append(row)

    stock_state = { "last_update": time.time(), "prices": current_prices, "history": history }
    
    with open(STOCK_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(stock_state, f, indent=4)
    return True

# --- 以下標準函數不變 ---
def get_all_users():
    try: with open(USER_DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}
def get_user(uid): return get_all_users().get(uid)
def save_user(uid, data):
    users = get_all_users(); users[uid] = data
    with open(USER_DB_FILE, "w", encoding="utf-8") as f: json.dump(users, f, indent=4, ensure_ascii=False)
def create_user(uid, pwd, name):
    users = get_all_users()
    if uid in users: return False
    users[uid] = { "password": pwd, "name": name, "money": 500, "job": "Citizen", "stocks": {}, "inventory": {}, "mailbox": [], "active_missions": [], "pending_claims": [], "last_hack": 0 }
    with open(USER_DB_FILE, "w", encoding="utf-8") as f: json.dump(users, f, indent=4, ensure_ascii=False)
    return True
def get_global_stock_state():
    try: with open(STOCK_DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return None
def save_global_stock_state(state):
    with open(STOCK_DB_FILE, "w", encoding="utf-8") as f: json.dump(state, f, indent=4)
def send_mail(to_uid, from_uid, title, msg):
    users = get_all_users(); 
    if to_uid in users: users[to_uid].setdefault("mailbox", []).append({"from": from_uid, "title": title, "msg": msg, "time": datetime.now().strftime("%Y-%m-%d %H:%M")}); save_user(to_uid, users[to_uid]); return True
    return False
def check_mission(uid, user, action_type):
    updated = False; new_missions = []
    for m in user.get("active_missions", []):
        if m.get("type") == action_type: user.setdefault("pending_claims", []).append(m); updated = True
        else: new_missions.append(m)
    user["active_missions"] = new_missions
    if updated and len(user["active_missions"]) < 2:
        user["active_missions"].append({"title": "繼續亂搞", "desc": "系統很滿意你的混亂。", "reward": 100, "type": "stock_buy"})
    if updated: save_user(uid, user); return True
    return False
