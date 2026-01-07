# database.py
import json
import os
import random
import time
from datetime import datetime, timedelta
from config import STOCKS_DATA, LEVEL_TITLES

USER_DB_FILE = "cityos_users.json"
STOCK_DB_FILE = "cityos_chaos_market.json"

def init_db():
    if not os.path.exists(USER_DB_FILE):
        users = {
            "admin": { "password": "admin", "name": "System OVERLORD", "money": 9999, "job": "Admin", "stocks": {}, "inventory": {}, "mailbox": [], "active_missions": [], "pending_claims": [], "last_hack": 0, "toxicity": 0, "level": 10, "exp": 0 },
            "frank": { "password": "x", "name": "Frank (Dev)", "money": 50000, "job": "Gamemaster", "stocks": {"CYBR": 100}, "inventory": {"Trojan Virus": 5}, "mailbox": [], "active_missions": [], "pending_claims": [], "last_hack": 0, "toxicity": 20, "level": 5, "exp": 100 }
        }
        with open(USER_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4, ensure_ascii=False)
    if not os.path.exists(STOCK_DB_FILE):
        rebuild_market()

def get_all_users():
    try:
        with open(USER_DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def save_user(uid, data):
    users = get_all_users()
    users[uid] = data
    with open(USER_DB_FILE, "w", encoding="utf-8") as f: 
        json.dump(users, f, indent=4, ensure_ascii=False)

def get_user(uid):
    users = get_all_users()
    user = users.get(uid)
    if user:
        dirty = False
        # 自動補足缺失欄位 (Migration)
        if "level" not in user: user["level"] = 1; dirty = True
        if "exp" not in user: user["exp"] = 0; dirty = True
        if "toxicity" not in user: user["toxicity"] = 0; dirty = True
        if "inventory" not in user: user["inventory"] = {}; dirty = True
        if dirty: save_user(uid, user)
    return user

def create_user(uid, pwd, name):
    users = get_all_users()
    if uid in users: return False
    users[uid] = { 
        "password": pwd, "name": name, "money": 500, 
        "job": "Citizen", "stocks": {}, "inventory": {}, 
        "mailbox": [], "active_missions": [], "pending_claims": [], 
        "last_hack": 0, "toxicity": 0,
        "level": 1, "exp": 0
    }
    with open(USER_DB_FILE, "w", encoding="utf-8") as f: 
        json.dump(users, f, indent=4, ensure_ascii=False)
    return True

# 🔥 經驗值與升級系統
def add_exp(uid, amount):
    user = get_user(uid)
    if not user: return False, 0
    
    user["exp"] += amount
    leveled_up = False
    required_exp = user["level"] * 100
    
    if user["exp"] >= required_exp:
        user["exp"] -= required_exp
        user["level"] += 1
        leveled_up = True
        # 升級獎勵：回滿血(解毒) + 獎金
        user["toxicity"] = 0
        bonus = user["level"] * 50
        user["money"] += bonus
    
    save_user(uid, user)
    return leveled_up, user["level"]

# ☣️ 毒氣系統
def apply_environmental_hazard(uid, user):
    chance = 0.3
    if user.get("inventory", {}).get("Gas Mask", 0) > 0:
        chance = 0.05
        
    is_poisoned = False
    if random.random() < chance:
        dmg = random.randint(2, 8)
        user["toxicity"] = min(100, user["toxicity"] + dmg)
        is_poisoned = True
        save_user(uid, user)
        
    return is_poisoned

def rebuild_market():
    current_prices = {} 
    history = []
    for i in range(60):
        row = {}
        for code, data in STOCKS_DATA.items():
            base_price = data["base"]
            fluctuation = random.uniform(0.5, 1.5) 
            new_price = int(base_price * fluctuation) + random.randint(-5, 5)
            row[code] = max(1, new_price)
        past_time = datetime.now() - timedelta(seconds=(60-i)*2)
        row["_time"] = past_time.strftime("%H:%M:%S")
        history.append(row)
    state = { "last_update": time.time(), "prices": current_prices, "history": history }
    with open(STOCK_DB_FILE, "w", encoding="utf-8") as f: json.dump(state, f, indent=4)

def get_global_stock_state():
    try: with open(STOCK_DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return None

def save_global_stock_state(state):
    with open(STOCK_DB_FILE, "w", encoding="utf-8") as f: json.dump(state, f, indent=4)

def check_mission(uid, user, action_type):
    # 簡化版任務檢查，保留擴充性
    return False

def send_mail(to_uid, from_uid, title, msg):
    users = get_all_users()
    if to_uid in users:
        users[to_uid].setdefault("mailbox", []).append({"from": from_uid, "title": title, "msg": msg, "time": datetime.now().strftime("%Y-%m-%d %H:%M")})
        save_user(to_uid, users[to_uid]); return True
    return False
