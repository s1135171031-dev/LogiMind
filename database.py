# database.py
# 用途: 強制讓所有股票都發瘋 (無視 config 設定)

import json
import os
import random
import time
from datetime import datetime, timedelta
from config import STOCKS_DATA

USER_DB_FILE = "cityos_users.json"
# 🔥 為了確保你一定能看到新圖表，我再一次改了檔名
STOCK_DB_FILE = "cityos_stocks_total_chaos.json" 

def init_db():
    if not os.path.exists(USER_DB_FILE):
        users = {
            "admin": { "password": "admin", "name": "System OVERLORD", "money": 999999, "job": "Admin", "stocks": {}, "inventory": {}, "mailbox": [], "active_missions": [], "pending_claims": [], "last_hack": 0 },
            "frank": {
                "password": "x", "name": "Frank (Dev)", "money": 999999999, "job": "Gamemaster",
                "stocks": { "CYBR": 1000, "AI": 1000 }, 
                "inventory": { "Trojan Virus": 99, "Firewall": 99 }, 
                "mailbox": [], "active_missions": [], "pending_claims": [], "last_hack": 0
            }
        }
        with open(USER_DB_FILE, "w", encoding="utf-8") as f: json.dump(users, f, indent=4, ensure_ascii=False)
            
    if not os.path.exists(STOCK_DB_FILE):
        rebuild_market()

def rebuild_market():
    print("🔥 正在引發全面金融崩潰 (無視穩定性)...")
    current_prices = {k: v["base"] for k, v in STOCKS_DATA.items()}
    history = []
    
    # 模擬 50 輪
    for i in range(50):
        row = {}
        for code, price in current_prices.items():
            base_vol = STOCKS_DATA[code]["volatility"]
            
            # 🔥🔥🔥 強制修正區 🔥🔥🔥
            # 如果原本波動率小於 0.08，強制提升到 0.08。
            # 這樣就算是用來養老的債券，也會像加密貨幣一樣亂跳。
            effective_vol = max(base_vol, 0.08)
            
            # 1. 波動放大 3 倍 (因為基數變大了，倍率稍微調小一點點以免直接歸零)
            change = random.uniform(-effective_vol * 3, effective_vol * 3)
            
            # 2. 隨機暴走 (30% 機率)
            if random.random() < 0.3:
                change += random.choice([-0.3, 0.3, -0.5, 0.5])
            
            new_price = int(price * (1 + change))
            new_price = max(5, min(15000, new_price)) # 上限拉高，下限拉低
            
            current_prices[code] = new_price
            row[code] = new_price
        
        past_time = datetime.now() - timedelta(seconds=(50-i)*2)
        row["_time"] = past_time.strftime("%H:%M:%S")
        history.append(row)

    stock_state = { "last_update": time.time(), "prices": current_prices, "history": history }
    
    with open(STOCK_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(stock_state, f, indent=4)
    return True

# --- 以下保持不變 ---
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
    users[uid] = { "password": pwd, "name": name, "money": 500, "job": "Citizen", "stocks": {}, "inventory": {}, "mailbox": [], "active_missions": [], "pending_claims": [], "last_hack": 0 }
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
    updated = False; new_missions = []
    for m in user.get("active_missions", []):
        if m.get("type") == action_type: user.setdefault("pending_claims", []).append(m); updated = True
        else: new_missions.append(m)
    user["active_missions"] = new_missions
    if updated and len(user["active_missions"]) < 2:
        new_task = random.choice([{"title": "消費", "type": "shop_buy"}, {"title": "指令", "type": "cli_input"}, {"title": "投資", "type": "stock_buy"}])
        new_task["reward"] = 100; new_task["desc"] = "繼續當個好公民。"; user["active_missions"].append(new_task)
    if updated: save_user(uid, user); return True
    return False
