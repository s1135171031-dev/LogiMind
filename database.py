# ==========================================
# 檔案: database.py
# ==========================================
import json
import os
import random
import streamlit as st
from datetime import datetime, date
from config import CITY_EVENTS

USER_DB_FILE = "cityos_users.json"
QUIZ_FILE = "questions.txt"
MISSION_FILE = "missions.txt" # 👈 新增任務檔案
LOG_FILE = "intruder_log.txt"

# --- 讀取外部檔案 ---

def load_quiz_from_file():
    """讀取題庫"""
    questions = []
    if not os.path.exists(QUIZ_FILE): return []
    try:
        with open(QUIZ_FILE, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) >= 5:
                    questions.append({"id": parts[0], "level": parts[1], "q": parts[2], "options": parts[3].split(","), "ans": parts[4]})
    except: pass
    return questions

def load_missions_from_file():
    """讀取任務列表"""
    missions = {}
    if not os.path.exists(MISSION_FILE): return {}
    try:
        with open(MISSION_FILE, "r", encoding="utf-8") as f:
            for line in f:
                # 格式: ID | Title | Desc | Reward | Target
                parts = line.strip().split("|")
                if len(parts) >= 5:
                    missions[parts[0]] = {
                        "title": parts[1],
                        "desc": parts[2],
                        "reward": int(parts[3]),
                        "target": parts[4]
                    }
    except: pass
    return missions

# --- 核心邏輯 ---

def get_today_event():
    seed = int(date.today().strftime("%Y%m%d"))
    random.seed(seed); event = random.choice(CITY_EVENTS); random.seed()
    return event

def get_admin_data():
    return {"password": "x12345678x", "name": "Frank (Admin)", "level": 100, "exp": 999999, "money": 99999999, "bank_deposit": 900000000, "job": "Architect", "inventory": {"Mining GPU": 99}, "completed_missions": []}

def get_npc_data(name, job, level, money):
    return {"password": "npc", "name": name, "level": level, "exp": level*100, "money": money, "bank_deposit": money*2, "job": job, "inventory": {}, "completed_missions": []}

def init_db():
    if not os.path.exists(USER_DB_FILE):
        users = {"alice": get_npc_data("Alice", "Hacker", 15, 8000), "bob": get_npc_data("Bob", "Engineer", 10, 3500), "charlie": get_npc_data("Charlie", "Programmer", 22, 15000), "frank": get_admin_data()}
        with open(USER_DB_FILE, "w", encoding="utf-8") as f: json.dump({"users": users, "bbs": []}, f, ensure_ascii=False, indent=4)
    else:
        with open(USER_DB_FILE, "r", encoding="utf-8") as f: data = json.load(f)
        if "frank" not in data["users"]:
            data["users"]["frank"] = get_admin_data()
            with open(USER_DB_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

def load_db():
    init_db()
    try:
        with open(USER_DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {"users": {}, "bbs": []}

def save_db(data):
    with open(USER_DB_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

def check_mission(uid, user, action_type):
    """根據 action_type 檢查所有任務"""
    missions = load_missions_from_file() # 👈 動態讀取
    completed_any = False
    
    for mid, m_data in missions.items():
        if m_data["target"] == action_type and mid not in user.get("completed_missions", []):
            user["completed_missions"].append(mid)
            user["money"] += m_data["reward"]
            user["exp"] = user.get("exp", 0) + 100
            st.toast(f"🎉 任務完成：{m_data['title']} (+${m_data['reward']})")
            completed_any = True
            
    if completed_any and uid != "frank":
        save_db({"users": load_db()["users"] | {uid: user}, "bbs": load_db().get("bbs", [])})
    return user

def log_intruder(username):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f: f.write(f"[{timestamp}] Failed Login: {username}\n")
