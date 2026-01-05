# database.py
import json
import os
import random
import streamlit as st
from datetime import datetime, date
from config import CITY_EVENTS

USER_DB_FILE = "cityos_users.json"
QUIZ_FILE = "questions.txt"
MISSION_FILE = "missions.txt"
LOG_FILE = "intruder_log.txt"

# --- 隱藏任務定義 (代碼寫死在程式裡，不寫在 txt) ---
HIDDEN_MISSIONS = {
    "H_ZERO": {"title": "💸 破產俱樂部", "desc": "身無分文也是一種藝術 (現金歸零)。", "reward": 1000},
    "H_777":  {"title": "🎰 幸運七七七", "desc": "現金剛好等於 $777。", "reward": 7777},
    "H_HACK": {"title": "👨‍💻 真正的駭客", "desc": "在 CLI 終端機輸入特定密技指令。", "reward": 5000},
    "H_SHOP": {"title": "🛍️ 購物狂", "desc": "背包內擁有超過 10 個道具。", "reward": 2000},
    "H_RICH": {"title": "💎 賽博首富", "desc": "總資產超過 $1,000,000。", "reward": 10000}
}

# ... (load_quiz_from_file, load_missions_from_file 等讀取函數保持不變) ...
def load_quiz_from_file():
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
    missions = {}
    if not os.path.exists(MISSION_FILE): return {}
    try:
        with open(MISSION_FILE, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) >= 5:
                    missions[parts[0]] = {"title": parts[1], "desc": parts[2], "reward": int(parts[3]), "target": parts[4]}
    except: pass
    return missions

# ... (init_db, load_db, save_db, get_today_event 等函數保持不變) ...
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

def log_intruder(username):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f: f.write(f"[{timestamp}] Failed Login: {username}\n")

# --- 🔥 重點修改：任務檢查邏輯 (含隱藏任務) ---

def check_mission(uid, user, action_type, extra_data=None):
    """
    uid: 使用者 ID
    user: 使用者資料物件
    action_type: 觸發動作類型 (bank_save, cli_input, etc.)
    extra_data: 額外參數 (例如 CLI 輸入的文字)
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

    # 2. 檢查隱藏任務 (Hardcoded)
    # 邏輯：如果該隱藏任務未完成，且符合奇怪條件 -> 解鎖
    
    # 條件 A: 現金歸零 (Action: any)
    if "H_ZERO" not in user["completed_missions"] and user["money"] == 0:
        hm = HIDDEN_MISSIONS["H_ZERO"]
        user["completed_missions"].append("H_ZERO")
        user["money"] += hm["reward"]
        st.toast(f"⚠️ 異常訊號：隱藏成就解鎖！【{hm['title']}】", icon="🕵️")
        completed_any = True

    # 條件 B: 現金 777 (Action: any)
    if "H_777" not in user["completed_missions"] and user["money"] == 777:
        hm = HIDDEN_MISSIONS["H_777"]
        user["completed_missions"].append("H_777")
        user["money"] += hm["reward"]
        st.toast(f"⚠️ 幸運女神：隱藏成就解鎖！【{hm['title']}】", icon="🎰")
        completed_any = True

    # 條件 C: 購物狂 (Inventory > 10 items)
    inv_count = sum(user.get("inventory", {}).values())
    if "H_SHOP" not in user["completed_missions"] and inv_count >= 10:
        hm = HIDDEN_MISSIONS["H_SHOP"]
        user["completed_missions"].append("H_SHOP")
        user["money"] += hm["reward"]
        st.toast(f"⚠️ 暴發戶：隱藏成就解鎖！【{hm['title']}】", icon="🛍️")
        completed_any = True
        
    # 條件 D: CLI 輸入特定指令 (Action: cli_input)
    if action_type == "cli_input" and extra_data == "sudo su":
        if "H_HACK" not in user["completed_missions"]:
            hm = HIDDEN_MISSIONS["H_HACK"]
            user["completed_missions"].append("H_HACK")
            user["money"] += hm["reward"]
            st.toast(f"⚠️ ROOT ACCESS：隱藏成就解鎖！【{hm['title']}】", icon="💀")
            completed_any = True

    # 條件 E: 資產百萬
    total_asset = user["money"] + user.get("bank_deposit", 0)
    if "H_RICH" not in user["completed_missions"] and total_asset >= 1000000:
        hm = HIDDEN_MISSIONS["H_RICH"]
        user["completed_missions"].append("H_RICH")
        user["money"] += hm["reward"]
        st.toast(f"⚠️ 財富自由：隱藏成就解鎖！【{hm['title']}】", icon="💎")
        completed_any = True

    # 存檔
    if completed_any and uid != "frank":
        save_db({"users": load_db()["users"] | {uid: user}, "bbs": load_db().get("bbs", [])})
    
    return user
