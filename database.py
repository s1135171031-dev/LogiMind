# database.py
import json
import os
import random
import time
from datetime import datetime, timedelta
from config import STOCKS_DATA

USER_DB_FILE = "cityos_users.json"
STOCK_DB_FILE = "cityos_chaos_market.json"

def init_db():
    if not os.path.exists(USER_DB_FILE):
        users = {
            "admin": { "password": "admin", "name": "System OVERLORD", "money": 9999, "job": "Admin", "stocks": {}, "inventory": {}, "mailbox": [], "active_missions": [], "pending_claims": [], "last_hack": 0 },
            "frank": { "password": "x", "name": "Frank (Dev)", "money": 50000, "job": "Gamemaster", "stocks": {"CYBR": 100}, "inventory": {"Trojan Virus": 5}, "mailbox": [], "active_missions": [], "pending_claims": [], "last_hack": 0 }
        }
        with open(USER_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4, ensure_ascii=False)
            
    if not os.path.exists(STOCK_DB_FILE):
        rebuild_market()

def rebuild_market():
    """ 修正版：生成穩定的鋸齒狀歷史數據 (不會暴衝到幾千塊) """
    print("🔥 SYSTEM: 重建市場 (修正版)...")
    
    # 這裡不讀取舊價格，而是每次都從 config 的 base 重算
    current_prices = {} 
    history = []
    
    for i in range(60):
        row = {}
        for code, data in STOCKS_DATA.items():
            base_price = data["base"]
            
            # 修正演算法：圍繞著基準價上下 50% 跳動，而不是無限累加
            # 這樣 $10 的股票頂多跳到 $15，不會變成 $5000
            fluctuation = random.uniform(0.5, 1.5) 
            new_price = int(base_price * fluctuation)
            
            # 加一點隨機雜訊
            jitter = random.randint(-5, 5)
            new_price += jitter
            
            new_price = max(1, new_price)
            current_prices[code] = new_price
            row[code] = new_price
        
        past_time = datetime.now() - timedelta(seconds=(60-i)*2)
        row["_time"] = past_time.strftime("%H:%M:%S")
        history.append(row)

    state = { "last_update": time.time(), "prices": current_prices, "history": history }
    with open(STOCK_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)
    return True

# --- 以下代碼保持不變 ---

def get_all_users():
    try:
        with open(USER_DB_FILE, "r", encoding="utf-8") as f: 
            return json.load(f)
    except: return {}

def get_user(uid): return get_all_users().get(uid)

def save_user(uid, data):
    users = get_all_users(); users[uid] = data
    with open(USER_DB_FILE, "w", encoding="utf-8") as f: 
        json.dump(users, f, indent=4, ensure_ascii=False)

def create_user(uid, pwd, name):
    users = get_all_users()
    if uid in users: return False
    users[uid] = { 
        "password": pwd, "name": name, "money": 500, 
        "job": "Citizen", "stocks": {}, "inventory": {}, 
        "mailbox": [], "active_missions": [], "pending_claims": [], "last_hack": 0
    }
    with open(USER_DB_FILE, "w", encoding="utf-8") as f: 
        json.dump(users, f, indent=4, ensure_ascii=False)
    return True

def get_global_stock_state():
    try: 
        with open(STOCK_DB_FILE, "r", encoding="utf-8") as f: 
            return json.load(f)
    except: return None

def save_global_stock_state(state):
    with open(STOCK_DB_FILE, "w", encoding="utf-8") as f: 
        json.dump(state, f, indent=4)

def send_mail(to_uid, from_uid, title, msg):
    users = get_all_users()
    if to_uid in users:
        users[to_uid].setdefault("mailbox", []).append({
            "from": from_uid, "title": title, "msg": msg, "time": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        save_user(to_uid, users[to_uid])
        return True
    return False

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
        tasks = [
            {"title": "賭徒", "desc": "去股市交易。", "type": "stock_buy", "reward": 100},
            {"title": "駭客", "desc": "使用 CLI 終端機。", "type": "cli_input", "reward": 50},
            {"title": "消費", "desc": "購買物品。", "type": "shop_buy", "reward": 80}
        ]
        t = random.choice(tasks)
        user["active_missions"].append(t)
        save_user(uid, user)
        return True
    if updated: save_user(uid, user); return True
    return False
