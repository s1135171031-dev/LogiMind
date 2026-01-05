# ==========================================
# 檔案名稱: database.py
# 用途: 資料庫存取與核心邏輯 (含隱藏任務定義)
# ==========================================

import json
import os
import random
import streamlit as st
from datetime import datetime, date
from config import CITY_EVENTS

# --- 檔案路徑設定 ---
USER_DB_FILE = "cityos_users.json"
QUIZ_FILE = "questions.txt"
MISSION_FILE = "missions.txt"
LOG_FILE = "intruder_log.txt"

# --- 🕵️ 隱藏任務定義 (這就是缺少的變數) ---
HIDDEN_MISSIONS = {
    # 既有成就
    "H_ZERO": {"title": "💸 破產俱樂部", "desc": "現金歸零。身無分文也是一種修行。", "reward": 1000},
    "H_777":  {"title": "🎰 幸運七七七", "desc": "現金剛好等於 $777。", "reward": 7777},
    "H_SHOP": {"title": "🛍️ 囤積症患者", "desc": "背包內擁有超過 15 個物品。", "reward": 2000},
    "H_HACK": {"title": "💀 ROOT ACCESS", "desc": "在 CLI 發現了管理者指令。", "reward": 5000},
    
    # 新增的奇怪成就
    "H_MATH": {"title": "🤓 數字敏感度", "desc": "在進位轉換器輸入了 '1024' (工程師的整數)。", "reward": 1024},
    "H_SPAM": {"title": "🤬 憤怒的駭客", "desc": "在 CLI 連續輸入錯誤指令超過 5 次。", "reward": 500},
    "H_BANK": {"title": "🏦 避險大師", "desc": "銀行存款超過 $100,000 但身上現金低於 $100。", "reward": 3000},
    "H_LOGIC":{"title": "⚡ 電路過載", "desc": "在數位實驗室把所有開關都打開 (Input A=1, B=1)。", "reward": 600}
}

# --- 讀取輔助函數 ---

def load_quiz_from_file():
    questions = []
    if not os.path.exists(QUIZ_FILE): return []
    try:
        with open(QUIZ_FILE, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) >= 5:
                    questions.append({
                        "id": parts[0], "level": parts[1], 
                        "q": parts[2], "options": parts[3].split(","), "ans": parts[4]
                    })
    except: pass
    return questions

def load_missions_from_file():
    missions = {}
    if not os.path.exists(MISSION_FILE): return {}
    try:
        with open(MISSION_FILE, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) >= 5:
                    missions[parts[0]] = {
                        "title": parts[1], "desc": parts[2], 
                        "reward": int(parts[3]), "target": parts[4]
                    }
    except: pass
    return missions

# --- 資料庫核心操作 ---

def get_today_event():
    seed = int(date.today().strftime("%Y%m%d"))
    random.seed(seed)
    event = random.choice(CITY_EVENTS)
    random.seed()
    return event

def get_admin_data():
    return {
        "password": "x12345678x", "name": "Frank (Admin)", 
        "level": 100, "exp": 999999, "money": 99999999, 
        "bank_deposit": 900000000, "job": "Architect", 
        "inventory": {"Mining GPU": 99}, "completed_missions": []
    }

def get_npc_data(name, job, level, money):
    return {
        "password": "npc", "name": name, "level": level, 
        "exp": level*100, "money": money, "bank_deposit": money*2, 
        "job": job, "inventory": {}, "completed_missions": []
    }

def init_db():
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
        # 確保 admin 存在 (防止舊存檔錯誤)
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

# --- 任務檢查邏輯 (包含隱藏成就解鎖) ---

def check_mission(uid, user, action_type, extra_data=None):
    """
    核心任務檢查函數
    uid: User ID
    user: User Object (Dictionary)
    action_type: 觸發動作
    extra_data: 輔助參數
    """
    missions = load_missions_from_file()
    completed_any = False
    
    # 1. 檢查普通任務 (.txt)
    for mid, m_data in missions.items():
        if m_data["target"] == action_type and mid not in user.get("completed_missions", []):
            user["completed_missions"].append(mid)
            user["money"] += m_data["reward"]
            user["exp"] = user.get("exp", 0) + 100
            st.toast(f"🎉 任務完成：{m_data['title']} (+${m_data['reward']})")
            completed_any = True

    # 2. 檢查隱藏成就 (Easter Eggs)
    
    # 輔助函式：解鎖隱藏成就
    def _unlock(mid):
        nonlocal completed_any
        hm = HIDDEN_MISSIONS[mid]
        user["completed_missions"].append(mid)
        user["money"] += hm["reward"]
        st.toast(f"🏆 隱藏成就解鎖！【{hm['title']}】\n{hm['desc']}", icon="🔥")
        completed_any = True

    # [H_ZERO] 現金歸零
    if "H_ZERO" not in user["completed_missions"] and user["money"] == 0:
        _unlock("H_ZERO")

    # [H_777] 現金 777
    if "H_777" not in user["completed_missions"] and user["money"] == 777:
        _unlock("H_777")

    # [H_SHOP] 背包囤積 > 15
    inv_count = sum(user.get("inventory", {}).values())
    if "H_SHOP" not in user["completed_missions"] and inv_count >= 15:
        _unlock("H_SHOP")
        
    # [H_BANK] 錢都在銀行 (避險大師)
    if "H_BANK" not in user["completed_missions"] and user.get("bank_deposit",0) > 100000 and user["money"] < 100:
        _unlock("H_BANK")

    # [H_HACK] CLI 輸入 sudo su
    if action_type == "cli_input" and extra_data == "sudo su":
        if "H_HACK" not in user["completed_missions"]:
            _unlock("H_HACK")

    # [H_SPAM] CLI 錯誤指令 (需在 app.py 傳入數字)
    if action_type == "cli_error" and isinstance(extra_data, int):
        if "H_SPAM" not in user["completed_missions"] and extra_data >= 5:
             _unlock("H_SPAM")

    # [H_MATH] 輸入 1024
    if action_type == "crypto_input" and str(extra_data) == "1024":
        if "H_MATH" not in user["completed_missions"]:
            _unlock("H_MATH")

    # [H_LOGIC] 全開開關
    if action_type == "logic_state" and extra_data == "11": # A=1, B=1
        if "H_LOGIC" not in user["completed_missions"]:
            _unlock("H_LOGIC")

    # 3. 存檔 (若有變動且非管理員)
    if completed_any and uid != "frank":
        save_db({"users": load_db()["users"] | {uid: user}, "bbs": load_db().get("bbs", [])})
    
    return user
