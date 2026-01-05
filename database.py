# ==========================================
# 檔案: database.py
# ==========================================
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

# --- 隱藏成就定義 ---
HIDDEN_MISSIONS = {
    "H_ZERO": {"title": "💸 破產俱樂部", "desc": "現金歸零。", "reward": 1000},
    "H_777":  {"title": "🎰 幸運七七七", "desc": "現金剛好 $777。", "reward": 7777},
    "H_SHOP": {"title": "🛍️ 囤積症", "desc": "背包擁有超過 15 個物品。", "reward": 2000},
    "H_HACK": {"title": "💀 ROOT", "desc": "CLI 發現管理者指令。", "reward": 5000},
    "H_MATH": {"title": "🤓 1024", "desc": "密碼學輸入 1024。", "reward": 1024},
    "H_SPAM": {"title": "🤬 暴怒駭客", "desc": "CLI 連續錯誤 5 次。", "reward": 500},
    "H_BANK": {"title": "🏦 避險大師", "desc": "存款 > 10萬 且 現金 < 100。", "reward": 3000},
    "H_PVP_W": {"title": "⚔️ 戰爭之王", "desc": "PVP 獲勝一次。", "reward": 1500},
    "H_WOLF": {"title": "🐺 華爾街之狼", "desc": "股票市值超過 $50,000。", "reward": 5000}
}

# --- 讀取外部檔案 ---
def load_quiz_from_file():
    qs = []
    if os.path.exists(QUIZ_FILE):
        try:
            with open(QUIZ_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    p = line.strip().split("|")
                    if len(p)>=5: qs.append({"id":p[0], "level":p[1], "q":p[2], "options":p[3].split(","), "ans":p[4]})
        except: pass
    return qs

def load_missions_from_file():
    ms = {}
    if os.path.exists(MISSION_FILE):
        try:
            with open(MISSION_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    p = line.strip().split("|")
                    if len(p)>=5: ms[p[0]] = {"title":p[1], "desc":p[2], "reward":int(p[3]), "target":p[4]}
        except: pass
    return ms

# --- 資料庫初始化 ---
def get_npc_data(name, job, level, money):
    return {
        "password": "npc", "defense_code": "1234", "name": name, 
        "level": level, "exp": level*100, "money": money, "bank_deposit": money*2, 
        "job": job, "inventory": {"Firewall": 1, "Chaos Heart": 1}, 
        "completed_missions": [], "pending_claims": [], "stocks": {}
    }

def init_db():
    if not os.path.exists(USER_DB_FILE):
        users = {
            "alice": get_npc_data("Alice", "Hacker", 15, 8000),
            "bob": get_npc_data("Bob", "Engineer", 10, 3500),
            "frank": {
                "password": "x", "defense_code": "9999", "name": "Frank (Admin)", 
                "level": 100, "exp": 999999, "money": 9999999, "bank_deposit": 900000000, 
                "job": "Architect", "inventory": {"Mining GPU": 99}, 
                "completed_missions": [], "pending_claims": [], "stocks": {}
            }
        }
        with open(USER_DB_FILE, "w", encoding="utf-8") as f:
            json.dump({"users": users, "bbs": []}, f, ensure_ascii=False, indent=4)
    else:
        # 自動遷移舊資料
        try:
            with open(USER_DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            changed = False
            for u in data["users"].values():
                if "stocks" not in u: u["stocks"] = {}; changed = True
                if "pending_claims" not in u: u["pending_claims"] = []; changed = True
                if "defense_code" not in u: u["defense_code"] = "0000"; changed = True
            if changed:
                with open(USER_DB_FILE, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
        except: pass

def load_db():
    init_db()
    try:
        with open(USER_DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {"users":{}, "bbs":[]}

def save_db(data):
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_today_event():
    random.seed(int(date.today().strftime("%Y%m%d")))
    evt = random.choice(CITY_EVENTS)
    random.seed()
    return evt

def log_intruder(u):
    with open(LOG_FILE, "a", encoding="utf-8") as f: f.write(f"[{datetime.now()}] Fail: {u}\n")

# --- 任務檢查邏輯 (含股市市值計算) ---
def check_mission(uid, user, action_type, extra_data=None):
    ms = load_missions_from_file()
    if "completed_missions" not in user: user["completed_missions"] = []
    if "pending_claims" not in user: user["pending_claims"] = []
    
    trig = False
    def _t(mid, title):
        nonlocal trig
        if mid not in user["completed_missions"] and mid not in user["pending_claims"]:
            user["pending_claims"].append(mid)
            st.toast(f"🚩 達成：【{title}】！請領獎。", icon="🎁")
            trig = True

    # 一般任務
    for mid, m in ms.items():
        if m["target"] == action_type: _t(mid, m['title'])

    # 隱藏與特殊條件
    if user["money"] == 0: _t("H_ZERO", HIDDEN_MISSIONS["H_ZERO"]["title"])
    if user["money"] == 777: _t("H_777", HIDDEN_MISSIONS["H_777"]["title"])
    if sum(user.get("inventory", {}).values()) >= 15: _t("H_SHOP", HIDDEN_MISSIONS["H_SHOP"]["title"])
    if user.get("bank_deposit",0) > 100000 and user["money"] < 100: _t("H_BANK", HIDDEN_MISSIONS["H_BANK"]["title"])
    
    if action_type == "cli_input" and extra_data == "sudo su": _t("H_HACK", HIDDEN_MISSIONS["H_HACK"]["title"])
    if action_type == "crypto_input" and str(extra_data) == "1024": _t("H_MATH", HIDDEN_MISSIONS["H_MATH"]["title"])
    if action_type == "pvp_win": _t("H_PVP_W", HIDDEN_MISSIONS["H_PVP_W"]["title"])
    if action_type == "cli_error" and isinstance(extra_data, int) and extra_data >= 5: _t("H_SPAM", HIDDEN_MISSIONS["H_SPAM"]["title"])
    
    # 股市成就 (華爾街之狼)
    if "stock_prices" in st.session_state:
        val = sum([amt * st.session_state.stock_prices.get(code,0) for code, amt in user.get("stocks",{}).items()])
        if val >= 50000: _t("H_WOLF", HIDDEN_MISSIONS["H_WOLF"]["title"])

    if trig and uid != "frank":
        save_db({"users": load_db()["users"]|{uid:user}, "bbs": load_db().get("bbs",[])})
    return user
