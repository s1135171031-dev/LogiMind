# database.py
# 用途: 處理所有 JSON 檔案讀寫 (Users, Global Stocks)

import json
import os
import random
import time
from datetime import datetime
from config import STOCKS_DATA

USER_DB_FILE = "cityos_users.json"
STOCK_DB_FILE = "cityos_stocks.json"

# --- 初始化 ---
def init_db():
    # 1. 初始化使用者資料庫
    if not os.path.exists(USER_DB_FILE):
        users = {
            "admin": {
                "password": "admin", "name": "Administrator", "money": 999999, 
                "stocks": {}, "inventory": {}, "mailbox": [], "active_missions": [], "pending_claims": [],
                "last_hack": 0
            }
        }
        with open(USER_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4)
            
    # 2. 初始化全域股市資料庫 (🔥 重點修正：讓所有人共享股價)
    if not os.path.exists(STOCK_DB_FILE):
        stock_state = {
            "last_update": time.time(),
            "prices": {k: v["base"] for k, v in STOCKS_DATA.items()},
            "history": [] # 簡單存最後幾筆歷史
        }
        with open(STOCK_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(stock_state, f, indent=4)

# --- 使用者操作 ---
def get_all_users():
    try:
        with open(USER_DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return {}

def get_user(uid):
    users = get_all_users()
    return users.get(uid)

def save_user(uid, data):
    # 讀取全部 -> 更新單一 -> 寫回 (避免覆蓋其他人的操作，雖然 JSON 仍有競爭風險，但比覆蓋全檔好)
    users = get_all_users()
    users[uid] = data
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

def create_user(uid, pwd, name):
    users = get_all_users()
    if uid in users: return False
    users[uid] = {
        "password": pwd, "name": name, "money": 1000, 
        "stocks": {}, "inventory": {}, 
        "mailbox": [{"from":"System","title":"Welcome","msg":"Welcome to CityOS!","time":str(datetime.now())}],
        "active_missions": [{"title":"First Step","desc":"Buy something in shop","reward":500,"type":"shop_buy"}],
        "pending_claims": [],
        "last_hack": 0
    }
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)
    return True

# --- 股市操作 (全域) ---
def get_global_stock_state():
    try:
        with open(STOCK_DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return None

def save_global_stock_state(state):
    with open(STOCK_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

# --- 輔助功能 ---
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
    # 簡單的任務觸發器
    updated = False
    new_missions = []
    
    for m in user.get("active_missions", []):
        if m.get("type") == action_type:
            user.setdefault("pending_claims", []).append(m)
            updated = True
        else:
            new_missions.append(m)
            
    user["active_missions"] = new_missions
    if updated:
        save_user(uid, user)
        return True
    return False
