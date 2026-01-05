# 檔案名稱: database.py
# 用途: 處理 JSON 讀寫、資料初始化、邏輯運算
import json
import os
import random
import streamlit as st
from datetime import datetime, date
from config import CITY_EVENTS, MISSIONS, ITEMS # 從 config 匯入資料

USER_DB_FILE = "cityos_users.json"
LOG_FILE = "intruder_log.txt"

def get_today_event():
    seed = int(date.today().strftime("%Y%m%d"))
    random.seed(seed)
    event = random.choice(CITY_EVENTS)
    random.seed()
    return event

def get_admin_data():
    return {
        "password": "x", "name": "Frank (Admin)", "level": 100, "exp": 999999, "money": 9999999, "bank_deposit": 50000000,
        "job": "Architect", "inventory": {"Mining GPU": 10}, "mining_balance": 100.0,
        "defense_code": 7, "mails": [], "completed_missions": []
    }

def get_npc_data(name, job, level, money):
    return {
        "password": "npc", "name": name, "level": level, "exp": level*100, "money": money, "bank_deposit": money*2,
        "job": job, "inventory": {}, "debt": 0, "defense_code": random.randint(0, 9), "mails": [],
        "completed_missions": []
    }

def init_db():
    if not os.path.exists(USER_DB_FILE):
        users = {
            "alice": get_npc_data("Alice", "Hacker", 15, 8000),
            "bob": get_npc_data("Bob", "Engineer", 10, 3500),
            "charlie": get_npc_data("Charlie", "Programmer", 22, 15000)
        }
        users["alice"]["inventory"]["Firewall"] = 1
        with open(USER_DB_FILE, "w", encoding="utf-8") as f:
            json.dump({"users": users, "bbs": []}, f, ensure_ascii=False, indent=4)

def load_db():
    init_db()
    try:
        with open(USER_DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "bbs" not in data: data["bbs"] = []
            for u in data["users"].values():
                if "defense_code" not in u: u["defense_code"] = random.randint(0, 9)
                if isinstance(u.get("inventory"), list): u["inventory"] = {}
                if "completed_missions" not in u: u["completed_missions"] = []
            return data
    except:
        return {"users": {}, "bbs": []}

def save_db(data):
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def check_mission(uid, user, action_type):
    """檢查並觸發任務完成"""
    completed_any = False
    for mid, m_data in MISSIONS.items():
        if m_data["target"] == action_type and mid not in user.get("completed_missions", []):
            user["completed_missions"].append(mid)
            user["money"] += m_data["reward"]
            user["exp"] = user.get("exp", 0) + 100
            st.toast(f"🎉 任務完成：{m_data['title']} (獎金 ${m_data['reward']})")
            completed_any = True
    
    if completed_any and uid != "frank":
        save_db({"users": load_db()["users"] | {uid: user}, "bbs": load_db().get("bbs", [])})
    return user

def log_intruder(username):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] Failed Login: {username}\n")
