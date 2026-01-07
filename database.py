# database.py
import json
import os
import random
import time
from datetime import datetime, timedelta
from config import STOCKS_DATA

USER_DB_FILE = "cityos_users.json"
STOCK_DB_FILE = "cityos_chaos_market.json"

# --- 核心邏輯保持不變 (init_db, rebuild_market 等) ---
# (為了節省篇幅，請保留你原本的 init_db 和 rebuild_market)
# 請務必確認 User 的初始結構和下面一致：

def init_db():
    if not os.path.exists(USER_DB_FILE):
        # 注意這裡多了 "toxicity": 0
        users = {
            "admin": { "password": "admin", "name": "System OVERLORD", "money": 9999, "job": "Admin", "stocks": {}, "inventory": {}, "mailbox": [], "active_missions": [], "pending_claims": [], "last_hack": 0, "toxicity": 0 },
            "frank": { "password": "x", "name": "Frank (Dev)", "money": 50000, "job": "Gamemaster", "stocks": {"CYBR": 100}, "inventory": {"Trojan Virus": 5}, "mailbox": [], "active_missions": [], "pending_claims": [], "last_hack": 0, "toxicity": 20 }
        }
        with open(USER_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4, ensure_ascii=False)
            
    if not os.path.exists(STOCK_DB_FILE):
        rebuild_market()

def rebuild_market():
    # ... (請保留原本的 rebuild_market 代碼) ...
    print("🔥 SYSTEM: 重建市場...")
    current_prices = {} 
    history = []
    for i in range(60):
        row = {}
        for code, data in STOCKS_DATA.items():
            base_price = data["base"]
            fluctuation = random.uniform(0.5, 1.5) 
            new_price = int(base_price * fluctuation) + random.randint(-5, 5)
            new_price = max(1, new_price)
            current_prices[code] = new_price
            row[code] = new_price
        past_time = datetime.now() - timedelta(seconds=(60-i)*2)
        row["_time"] = past_time.strftime("%H:%M:%S")
        history.append(row)
    state = { "last_update": time.time(), "prices": current_prices, "history": history }
    with open(STOCK_DB_FILE, "w", encoding="utf-8") as f: json.dump(state, f, indent=4)
    return True

# --- 更新：存取與環境危害函數 ---

def get_all_users():
    try:
        with open(USER_DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def get_user(uid): 
    users = get_all_users()
    user = users.get(uid)
    if user:
        dirty = False
        # 自動修復：如果沒有 toxicity 欄位，補上
        if "toxicity" not in user:
            user["toxicity"] = 0
            dirty = True
        
        # 你的其他自動修復邏輯
        if "active_missions" not in user or not user["active_missions"]:
            user["active_missions"] = [{"title": "生存入門", "desc": "購買解毒劑或面具。", "reward": 150, "type": "shop_buy"}]
            dirty = True
        for field in ["pending_claims", "mailbox", "inventory", "stocks"]:
            if field not in user:
                user[field] = [] if field != "stocks" and field != "inventory" else {}
                dirty = True
        
        if dirty: save_user(uid, user)
    return user

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
        "mailbox": [], 
        "active_missions": [{"title": "新手報到", "desc": "去黑市買東西。", "reward": 100, "type": "shop_buy"}], 
        "pending_claims": [], "last_hack": 0,
        "toxicity": 0 # 初始無毒
    }
    with open(USER_DB_FILE, "w", encoding="utf-8") as f: 
        json.dump(users, f, indent=4, ensure_ascii=False)
    return True

# 🔥 新增：環境危害計算
def apply_environmental_hazard(uid, user):
    """ 計算是否因環境中毒 """
    # 基礎中毒機率 30%
    chance = 0.3
    
    # 如果有防毒面具，機率降為 5%
    if user.get("inventory", {}).get("Gas Mask", 0) > 0:
        chance = 0.05
        
    is_poisoned = False
    if random.random() < chance:
        dmg = random.randint(2, 8)
        user["toxicity"] = min(100, user["toxicity"] + dmg)
        is_poisoned = True
        save_user(uid, user)
        
    return is_poisoned

# ... (保留原本的 get_global_stock_state, save_global_stock_state, send_mail, check_mission) ...
def get_global_stock_state():
    try: with open(STOCK_DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return None
def save_global_stock_state(state):
    with open(STOCK_DB_FILE, "w", encoding="utf-8") as f: json.dump(state, f, indent=4)
def send_mail(to_uid, from_uid, title, msg):
    users = get_all_users()
    if to_uid in users:
        users[to_uid].setdefault("mailbox", []).append({"from": from_uid, "title": title, "msg": msg, "time": datetime.now().strftime("%Y-%m-%d %H:%M")})
        save_user(to_uid, users[to_uid]); return True
    return False
def check_mission(uid, user, action_type):
    updated = False; new_missions = []
    for m in user.get("active_missions", []):
        if m.get("type") == action_type:
            user.setdefault("pending_claims", []).append(m); updated = True
        else: new_missions.append(m)
    user["active_missions"] = new_missions
    if len(user["active_missions"]) < 3:
        tasks = [{"title": "解毒", "desc": "使用抗輻射藥劑。", "type": "use_item", "reward": 100},
                 {"title": "賭徒", "desc": "去股市交易。", "type": "stock_buy", "reward": 100},
                 {"title": "駭客", "desc": "使用 CLI。", "type": "cli_input", "reward": 50},
                 {"title": "消費", "desc": "購買物品。", "type": "shop_buy", "reward": 80}]
        t = random.choice(tasks); user["active_missions"].append(t); updated = True
    if updated: save_user(uid, user); return True
    return False
