# ==========================================
# 檔案名稱: database.py
# 用途: 處理 JSON 讀寫、資料初始化、邏輯運算、讀取題庫
# ==========================================
import json
import os
import random
import streamlit as st
from datetime import datetime, date
from config import CITY_EVENTS, MISSIONS # 匯入設定

USER_DB_FILE = "cityos_users.json"
QUIZ_FILE = "questions.txt"  # 指定外部題庫
LOG_FILE = "intruder_log.txt"

# --- 讀取外部題目 ---
def load_quiz_from_file():
    """從 questions.txt 讀取題目"""
    questions = []
    if not os.path.exists(QUIZ_FILE):
        return []
    
    try:
        with open(QUIZ_FILE, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("|")
                # 格式: ID|難度|題目|選項(逗號隔開)|答案
                if len(parts) >= 5:
                    questions.append({
                        "id": parts[0],
                        "level": parts[1],
                        "q": parts[2],
                        "options": parts[3].split(","), 
                        "ans": parts[4]
                    })
    except Exception as e:
        print(f"Error loading quiz: {e}")
        return []
    return questions

# --- 遊戲邏輯與資料庫 ---

def get_today_event():
    seed = int(date.today().strftime("%Y%m%d"))
    random.seed(seed)
    event = random.choice(CITY_EVENTS)
    random.seed()
    return event

def get_admin_data():
    return {
        "password": "x12345678x", "name": "Frank (Admin)", "level": 100, "exp": 999999, "money": 99999999, "bank_deposit": 900000000,
        "job": "Architect", "inventory": {"Mining GPU": 99}, "mining_balance": 100.0,
        "defense_code": 777, "mails": [], "completed_missions": []
    }

def get_npc_data(name, job, level, money):
    return {
        "password": "npc", "name": name, "level": level, "exp": level*100, "money": money, "bank_deposit": money*2,
        "job": job, "inventory": {}, "debt": 0, "defense_code": random.randint(0, 9), "mails": [],
        "completed_missions": []
    }

def init_db():
    # 檢查資料庫是否存在
    if not os.path.exists(USER_DB_FILE):
        users = {
            "alice": get_npc_data("Alice", "Hacker", 15, 8000),
            "bob": get_npc_data("Bob", "Engineer", 10, 3500),
            "charlie": get_npc_data("Charlie", "Programmer", 22, 15000),
            "frank": get_admin_data() # 預設建立 Admin
        }
        users["alice"]["inventory"]["Firewall"] = 1
        with open(USER_DB_FILE, "w", encoding="utf-8") as f:
            json.dump({"users": users, "bbs": []}, f, ensure_ascii=False, indent=4)
    else:
        # 檢查 Frank 是否存在，若無則補回 (修復 Admin)
        with open(USER_DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "frank" not in data["users"]:
            data["users"]["frank"] = get_admin_data()
            with open(USER_DB_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

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
