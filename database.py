# database.py
import json
import os
import random
import time
from datetime import datetime, timedelta
from config import STOCKS_DATA

USER_DB_FILE = "cityos_users.json"
STOCK_DB_FILE = "cityos_full_chaos.json"

def init_db():
    if not os.path.exists(USER_DB_FILE):
        users = {
            "admin": { "password": "admin", "name": "System OVERLORD", "money": 99999, "job": "Admin", "stocks": {}, "inventory": {}, "mailbox": [], "active_missions": [], "pending_claims": [], "last_hack": 0 },
            "frank": { "password": "x", "name": "Frank (Dev)", "money": 9999999, "job": "Gamemaster", "stocks": {"CYBR": 1000}, "inventory": {"Trojan Virus": 10}, "mailbox": [], "active_missions": [], "pending_claims": [], "last_hack": 0 }
        }
        with open(USER_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4, ensure_ascii=False)
            
    if not os.path.exists(STOCK_DB_FILE):
        rebuild_market()

def rebuild_market():
    """ 綠線風格：生成 60 筆鋸齒狀歷史數據 """
    print("🔥 SYSTEM: 重建混亂股市歷史...")
    current_prices = {k: v["base"] for k, v in STOCKS_DATA.items()}
    history = []
    
    for i in range(60):
        row = {}
        for code, price in current_prices.items():
            pct = random.uniform(-0.3, 0.4)
            jitter = random.randint(-30, 30)
            if jitter == 0: jitter = 5
            
            new_price = int(price * (1 + pct) + jitter)
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

# --- 使用者與功能函數 (修正排版錯誤) ---

def get_all_users():
    try:
        # 修正：try 和 with 必須分行
        with open(USER_DB_FILE, "r", encoding="utf-8") as f: 
            return json.load(f)
    except: 
        return {}

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
        "password": pwd, "name": name, "money": 1000, "job": "Citizen", 
        "stocks": {}, "inventory": {}, 
        "mailbox": [{"from": "System", "title": "歡迎", "msg": "歡迎來到 CityOS。", "time": str(datetime.now())}],
        "active_missions": [{"title": "消費主義", "desc": "去黑市買東西。", "reward": 200, "type": "shop_buy"}],
        "pending_claims": [], "last_hack": 0
    }
    with open(USER_DB_FILE, "w", encoding="utf-8") as f: 
        json.dump(users, f, indent=4, ensure_ascii=False)
    return True

def get_global_stock_state():
    try: 
        # 修正：try 和 with 必須分行
        with open(STOCK_DB_FILE, "r", encoding="utf-8") as f: 
            return json.load(f)
    except: 
        return None

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
            {"title": "賭徒", "desc": "去股市交易。", "type": "stock_buy", "reward": 150},
            {"title": "駭客", "desc": "使用 CLI 終端機。", "type": "cli_input", "reward": 100},
            {"title": "消費", "desc": "購買物品。", "type": "shop_buy", "reward": 200}
        ]
        t = random.choice(tasks)
        user["active_missions"].append(t)
        save_user(uid, user)
        return True
    if updated: 
        save_user(uid, user)
        return True
    return False
