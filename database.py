# database.py
# 用途: 資料處理 (含 Frank 帳號、職業系統、狂暴股市歷史)

import json
import os
import random
import time
from datetime import datetime, timedelta
from config import STOCKS_DATA

USER_DB_FILE = "cityos_users.json"
STOCK_DB_FILE = "cityos_stocks.json"

def init_db():
    # 1. 初始化使用者資料庫 (保持不變)
    if not os.path.exists(USER_DB_FILE):
        users = {
            "admin": {
                "password": "admin", "name": "System OVERLORD", "money": 999999, 
                "job": "Admin",
                "stocks": {}, "inventory": {}, "mailbox": [], "active_missions": [], "pending_claims": [],
                "last_hack": 0
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
            
    # 2. 初始化全域股市 (🔥 改動：加入狂暴波動邏輯)
    if not os.path.exists(STOCK_DB_FILE):
        print("正在生成充滿絕望的股市歷史...")
        
        current_prices = {k: v["base"] for k, v in STOCKS_DATA.items()}
        history = []
        
        # 模擬 50 輪 (增加長度，讓曲線更曲折)
        for i in range(50):
            row = {}
            for code, price in current_prices.items():
                base_vol = STOCKS_DATA[code]["volatility"]
                
                # 🔥 1. 基礎波動放大 3 倍：平靜是不被允許的
                change = random.uniform(-base_vol * 3, base_vol * 3)
                
                # 🔥 2. 黑天鵝事件 (15% 機率發生劇烈崩盤或暴漲)
                chaos_roll = random.random()
                if chaos_roll < 0.15: 
                    # 崩盤或暴漲 (-40% ~ +40%)
                    change += random.choice([-0.4, 0.4])
                
                new_price = int(price * (1 + change))
                # 確保價格不會歸零，也不會太誇張
                new_price = max(10, min(5000, new_price))
                
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

# --- 以下函數保持原樣 ---
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
        "password": pwd, 
        "name": name, 
        "money": 500, 
        "job": "Citizen",
        "stocks": {}, "inventory": {}, 
        "mailbox": [{
            "from": "System",
            "title": "入籍通知",
            "msg": "又一個浪費空氣的底層公民加入了 CityOS。別指望系統會同情你。",
            "time": str(datetime.now())
        }],
        "active_missions": [
            {"title": "消費主義奴隸", "desc": "去商店隨便買個垃圾。", "reward": 100, "type": "shop_buy"},
            {"title": "用點腦子", "desc": "去知識庫做對一題。", "reward": 50, "type": "quiz_done"}
        ],
        "pending_claims": [],
        "last_hack": 0
    }
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)
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
    new_mail = {"from": from_uid, "title": title, "msg": msg, "time": datetime.now().strftime("%Y-%m-%d %H:%M")}
    users[to_uid].setdefault("mailbox", []).append(new_mail)
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
            {"title": "乖乖納稅", "desc": "再去買個東西。錢不花掉就會貶值。", "type": "shop_buy"},
            {"title": "鍵盤俠", "desc": "在終端機隨便打個指令。假裝你是駭客。", "type": "cli_input"},
            {"title": "賭徒心態", "desc": "去股市買張廢紙(股票)。", "type": "stock_buy"}
        ]
        new_task = random.choice(task_pool)
        new_task["reward"] = reward
        user["active_missions"].append(new_task)

    if updated:
        save_user(uid, user)
        return True
    return False
