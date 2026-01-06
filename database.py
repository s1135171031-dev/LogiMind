# database.py
# 用途: 資料處理 (低獎勵、毒舌版)

import json
import os
import random
import time
from datetime import datetime
from config import STOCKS_DATA

USER_DB_FILE = "cityos_users.json"
STOCK_DB_FILE = "cityos_stocks.json"

def init_db():
    if not os.path.exists(USER_DB_FILE):
        users = {
            "admin": {
                "password": "admin", "name": "System OVERLORD", "money": 999999, 
                "stocks": {}, "inventory": {}, "mailbox": [], "active_missions": [], "pending_claims": [],
                "last_hack": 0
            }
        }
        with open(USER_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4)
            
    if not os.path.exists(STOCK_DB_FILE):
        stock_state = {
            "last_update": time.time(),
            "prices": {k: v["base"] for k, v in STOCKS_DATA.items()},
            "history": []
        }
        with open(STOCK_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(stock_state, f, indent=4)

def get_all_users():
    try:
        with open(USER_DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
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
    
    # 初始獎勵極低，讓玩家感到飢餓
    # 任務文字充滿諷刺
    users[uid] = {
        "password": pwd, "name": name, "money": 500, # 初始資金也變少
        "stocks": {}, "inventory": {}, 
        "mailbox": [{
            "from": "System",
            "title": "入籍通知",
            "msg": "又一個浪費空氣的底層公民加入了 CityOS。別指望系統會同情你，活下去，或者死在路邊。",
            "time": str(datetime.now())
        }],
        "active_missions": [
            {
                "title": "消費主義奴隸", 
                "desc": "去商店隨便買個垃圾。證明你對經濟有貢獻。", 
                "reward": 100, # 低獎勵
                "type": "shop_buy"
            },
            {
                "title": "用點腦子", 
                "desc": "去知識庫做對一題。雖然我不抱期望。", 
                "reward": 50,  # 極低獎勵
                "type": "quiz_done"
            }
        ],
        "pending_claims": [],
        "last_hack": 0
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
    if to_uid not in users: return False
    
    new_mail = {
        "from": from_uid,
        "title": title,
        "msg": msg,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    users[to_uid].setdefault("mailbox", []).append(new_mail)
    
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)
    return True

def check_mission(uid, user, action_type):
    updated = False
    new_missions = []
    
    for m in user.get("active_missions", []):
        if m.get("type") == action_type:
            user.setdefault("pending_claims", []).append(m)
            updated = True
        else:
            new_missions.append(m)
            
    user["active_missions"] = new_missions
    
    # 如果任務被解完了，隨機生成一個新的低報酬任務 (50-200元)
    if updated and len(user["active_missions"]) < 2:
        reward = random.randint(50, 200)
        task_pool = [
            {"title": "乖乖納稅", "desc": "再去買個東西。錢不花掉就會貶值，懂嗎？", "type": "shop_buy"},
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
