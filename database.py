# database.py
import json
import os
import random
import streamlit as st
from datetime import datetime, date
from config import CITY_EVENTS

# --- 檔案路徑 ---
USER_DB_FILE = "cityos_users.json"
QUIZ_FILE = "questions.txt"
MISSION_FILE = "missions.txt"
LOG_FILE = "intruder_log.txt"

# --- 🕵️ 隱藏任務定義 ---
HIDDEN_MISSIONS = {
    "H_ZERO": {"title": "💸 破產俱樂部", "desc": "現金歸零。身無分文也是一種修行。", "reward": 1000},
    "H_777":  {"title": "🎰 幸運七七七", "desc": "現金剛好等於 $777。", "reward": 7777},
    "H_SHOP": {"title": "🛍️ 囤積症患者", "desc": "背包內擁有超過 15 個物品。", "reward": 2000},
    "H_HACK": {"title": "💀 ROOT ACCESS", "desc": "在 CLI 發現了管理者指令。", "reward": 5000},
    "H_MATH": {"title": "🤓 數字敏感度", "desc": "在進位轉換器輸入了 '1024'。", "reward": 1024},
    "H_SPAM": {"title": "🤬 憤怒的駭客", "desc": "在 CLI 連續輸入錯誤指令超過 5 次。", "reward": 500},
    "H_BANK": {"title": "🏦 避險大師", "desc": "銀行存款 > $100,000 但身上現金 < $100。", "reward": 3000},
    "H_LOGIC":{"title": "⚡ 電路過載", "desc": "在數位實驗室把所有開關都打開 (Input A=1, B=1)。", "reward": 600},
    "H_PVP_W": {"title": "⚔️ 戰爭之王", "desc": "成功完成一次 PVP 入侵。", "reward": 1500}
}

# --- 讀取輔助 ---
def load_quiz_from_file():
    questions = []
    if not os.path.exists(QUIZ_FILE): return []
    try:
        with open(QUIZ_FILE, "r", encoding="utf-8") as f:
            for line in f:
                p = line.strip().split("|")
                if len(p) >= 5:
                    questions.append({"id":p[0], "level":p[1], "q":p[2], "options":p[3].split(","), "ans":p[4]})
    except: pass
    return questions

def load_missions_from_file():
    missions = {}
    if not os.path.exists(MISSION_FILE): return {}
    try:
        with open(MISSION_FILE, "r", encoding="utf-8") as f:
            for line in f:
                p = line.strip().split("|")
                if len(p) >= 5:
                    missions[p[0]] = {"title":p[1], "desc":p[2], "reward":int(p[3]), "target":p[4]}
    except: pass
    return missions

# --- 資料庫核心 ---
def get_today_event():
    seed = int(date.today().strftime("%Y%m%d"))
    random.seed(seed)
    event = random.choice(CITY_EVENTS)
    random.seed()
    return event

def get_admin_data():
    return {
        "password": "x12345678x", "defense_code": "9999", "name": "Frank (Admin)", 
        "level": 100, "exp": 999999, "money": 99999999, "bank_deposit": 900000000, 
        "job": "Architect", "inventory": {"Mining GPU": 99, "Firewall": 100}, "completed_missions": []
    }

def get_npc_data(name, job, level, money):
    return {
        "password": "npc", "defense_code": "1234", "name": name, 
        "level": level, "exp": level*100, "money": money, "bank_deposit": money*2, 
        "job": job, "inventory": {"Firewall": 1, "Chaos Heart": 1}, "completed_missions": []
    }

def init_db():
    # 初始化或遷移
    if not os.path.exists(USER_DB_FILE):
        users = {
            "alice": get_npc_data("Alice", "Hacker", 15, 8000),
            "bob": get_npc_data("Bob", "Engineer", 10, 3500),
            "charlie": get_npc_data("Charlie", "Programmer", 22, 15000),
            "frank": get_admin_data()
        }
        with open(USER_DB_FILE, "w", encoding="utf-8") as f:
            json.dump({"users": users, "bbs": []}, f, ensure_ascii=False, indent=4)
    else:
        # 簡易遷移：確保所有用戶都有 defense_code
        try:
            with open(USER_DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            changed = False
            for u in data["users"].values():
                if "defense_code" not in u:
                    u["defense_code"] = "0000"
                    changed = True
            if changed:
                with open(USER_DB_FILE, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
        except: pass

def load_db():
    init_db()
    try:
        with open(USER_DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"users": {}, "bbs": []}

def save_db(data):
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def log_intruder(username):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] Failed Login: {username}\n")

# --- 任務檢查 ---
def check_mission(uid, user, action_type, extra_data=None):
    missions = load_missions_from_file()
    completed_any = False
    
    # 普通任務
    for mid, m_data in missions.items():
        if m_data["target"] == action_type and mid not in user.get("completed_missions", []):
            user["completed_missions"].append(mid)
            user["money"] += m_data["reward"]
            user["exp"] = user.get("exp", 0) + 100
            st.toast(f"🎉 任務完成：{m_data['title']} (+${m_data['reward']})")
            completed_any = True

    # 隱藏任務邏輯
    def _unlock(mid):
        nonlocal completed_any
        if mid not in user["completed_missions"]:
            hm = HIDDEN_MISSIONS[mid]
            user["completed_missions"].append(mid)
            user["money"] += hm["reward"]
            st.toast(f"🏆 隱藏成就：{hm['title']}", icon="🔥")
            completed_any = True

    if user["money"] == 0: _unlock("H_ZERO")
    if user["money"] == 777: _unlock("H_777")
    if sum(user.get("inventory", {}).values()) >= 15: _unlock("H_SHOP")
    if user.get("bank_deposit",0) > 100000 and user["money"] < 100: _unlock("H_BANK")
    
    if action_type == "cli_input" and extra_data == "sudo su": _unlock("H_HACK")
    if action_type == "crypto_input" and str(extra_data) == "1024": _unlock("H_MATH")
    if action_type == "logic_state" and extra_data == "11": _unlock("H_LOGIC")
    if action_type == "pvp_win": _unlock("H_PVP_W")
    
    if action_type == "cli_error" and isinstance(extra_data, int) and extra_data >= 5:
        _unlock("H_SPAM")

    if completed_any and uid != "frank":
        save_db({"users": load_db()["users"] | {uid: user}, "bbs": load_db().get("bbs", [])})
    
    return user
