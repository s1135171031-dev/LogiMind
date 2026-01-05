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

# --- 備用資料 (防止空白) ---
DEFAULT_MISSIONS = {
    "M_DEF_1": {"title": "新手上路", "desc": "在邏輯實驗室完成一次運算", "reward": 100, "target": "logic_use"},
    "M_DEF_2": {"title": "股海羅盤", "desc": "在股市買入股票", "reward": 200, "target": "stock_buy"},
    "M_DEF_3": {"title": "駭客入門", "desc": "在 CLI 輸入任意指令", "reward": 150, "target": "cli_input"},
    "M_DEF_4": {"title": "儲蓄習慣", "desc": "存錢進銀行", "reward": 150, "target": "bank_save"},
    "M_DEF_5": {"title": "社交達人", "desc": "發送一封郵件", "reward": 100, "target": "send_mail"}
}

DEFAULT_QUIZ = [
    {"id":"Q1", "level":"1", "q":"Python 定義函式用什麼？", "options":["def","func","var"], "ans":"def"},
    {"id":"Q2", "level":"1", "q":"二進位 101 是多少？", "options":["3","5","7"], "ans":"5"},
    {"id":"Q3", "level":"2", "q":"HTTP 成功狀態碼？", "options":["200","404","500"], "ans":"200"}
]

# --- 隱藏成就 ---
HIDDEN_MISSIONS = {
    "H_ZERO": {"title": "💸 破產俱樂部", "desc": "現金歸零。", "reward": 100},
    "H_777":  {"title": "🎰 幸運七七七", "desc": "現金剛好 $777。", "reward": 777},
    "H_SHOP": {"title": "🛍️ 囤積症", "desc": "背包物品 > 15。", "reward": 200},
    "H_HACK": {"title": "💀 ROOT", "desc": "CLI 輸入 sudo su。", "reward": 500},
    "H_MATH": {"title": "🤓 1024", "desc": "密碼學輸入 1024。", "reward": 128},
    "H_SPAM": {"title": "🤬 暴怒駭客", "desc": "CLI 連續錯誤 5 次。", "reward": 50},
    "H_BANK": {"title": "🏦 避險大師", "desc": "存款>10萬且現金<100。", "reward": 300},
    "H_PVP_W": {"title": "⚔️ 戰爭之王", "desc": "PVP 獲勝。", "reward": 150},
    "H_WOLF": {"title": "🐺 華爾街之狼", "desc": "股票市值 > $50,000。", "reward": 1000}
}

# --- 讀取外部檔案 ---
def load_quiz_from_file():
    qs = []
    if os.path.exists(QUIZ_FILE):
        try:
            with open(QUIZ_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    p = line.strip().split("|")
                    if len(p) >= 5:
                        qs.append({"id": p[0], "level": p[1], "q": p[2], "options": p[3].split(","), "ans": p[4]})
        except: pass
    return qs if qs else DEFAULT_QUIZ

def load_missions_from_file():
    ms = {}
    if os.path.exists(MISSION_FILE):
        try:
            with open(MISSION_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    p = line.strip().split("|")
                    if len(p) >= 5:
                        ms[p[0]] = {"title":p[1], "desc":p[2], "reward":int(p[3]), "target":p[4]}
        except: pass
    if not ms: return DEFAULT_MISSIONS
    return ms

# --- DB 初始化 (設定固定密碼) ---
def get_npc_data(name, job, level, money, fixed_code="1234"):
    return {
        "password": "npc", "defense_code": fixed_code, "name": name, 
        "level": level, "exp": level*100, "money": money, "bank_deposit": money*2, 
        "job": job, "inventory": {"Firewall": 1, "Chaos Heart": 1}, 
        "completed_missions": [], "pending_claims": [], "stocks": {},
        "active_missions": [], "mailbox": []
    }

def init_db():
    if not os.path.exists(USER_DB_FILE):
        users = {
            "alice": get_npc_data("Alice", "Hacker", 15, 800, "1357"), # Alice 固定密碼
            "bob": get_npc_data("Bob", "Engineer", 10, 350, "2468"),   # Bob 固定密碼
            "frank": {
                "password": "x12345678x", "defense_code": "9999", "name": "Frank", 
                "level": 100, "exp": 999999, "money": 9999999, "bank_deposit": 900000000, 
                "job": "Architect", "inventory": {"Mining GPU": 99}, 
                "completed_missions": [], "pending_claims": [], "stocks": {}, 
                "active_missions": [], "mailbox": []
            }
        }
        with open(USER_DB_FILE, "w", encoding="utf-8") as f:
            json.dump({"users": users, "bbs": []}, f, ensure_ascii=False, indent=4)

def load_db():
    init_db()
    try:
        with open(USER_DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {"users":{}, "bbs":[]}

def save_db(data):
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 核心邏輯 ---
def get_today_event():
    random.seed(int(date.today().strftime("%Y%m%d")))
    evt = random.choice(CITY_EVENTS)
    random.seed()
    return evt

def log_intruder(u):
    with open(LOG_FILE, "a", encoding="utf-8") as f: f.write(f"[{datetime.now()}] Fail: {u}\n")

def send_mail(to_uid, from_uid, title, msg):
    db = load_db()
    if to_uid in db["users"]:
        mail = {"from": from_uid, "title": title, "msg": msg, "time": datetime.now().strftime("%Y-%m-%d %H:%M"), "read": False}
        db["users"][to_uid].setdefault("mailbox", []).insert(0, mail)
        save_db(db)
        return True
    return False

def refresh_active_missions(user):
    ms = load_missions_from_file()
    all_ids = list(ms.keys())
    exclude = set(user.get("completed_missions", []) + user.get("pending_claims", []) + user.get("active_missions", []))
    available = [mid for mid in all_ids if mid not in exclude]
    if not available and not user["active_missions"]: available = all_ids
    
    changed = False
    while len(user["active_missions"]) < 3 and available:
        new_mid = random.choice(available)
        user["active_missions"].append(new_mid)
        available.remove(new_mid)
        changed = True
    return changed

def check_mission(uid, user, action_type, extra_data=None):
    ms = load_missions_from_file()
    if "completed_missions" not in user: user["completed_missions"] = []
    if "pending_claims" not in user: user["pending_claims"] = []
    if "active_missions" not in user: user["active_missions"] = []
    
    if refresh_active_missions(user): save_db({"users": load_db()["users"]|{uid:user}, "bbs":[]})

    triggered = False
    active_copy = user["active_missions"][:]
    for mid in active_copy:
        if mid in ms:
            m_data = ms[mid]
            if m_data["target"] == action_type:
                user["pending_claims"].append(mid)
                user["active_missions"].remove(mid)
                st.toast(f"🚩 達成：{m_data['title']}！", icon="🎁")
                triggered = True

    def _t_hidden(mid, title):
        nonlocal triggered
        if mid not in user["completed_missions"] and mid not in user["pending_claims"]:
            user["pending_claims"].append(mid)
            st.toast(f"🕵️ 隱藏成就：{title}！", icon="🔥")
            triggered = True

    if user["money"] == 0: _t_hidden("H_ZERO", HIDDEN_MISSIONS["H_ZERO"]["title"])
    if user["money"] == 777: _t_hidden("H_777", HIDDEN_MISSIONS["H_777"]["title"])
    if sum(user.get("inventory", {}).values()) >= 15: _t_hidden("H_SHOP", HIDDEN_MISSIONS["H_SHOP"]["title"])
    if user.get("bank_deposit",0)>100000 and user["money"]<100: _t_hidden("H_BANK", HIDDEN_MISSIONS["H_BANK"]["title"])
    if action_type == "cli_input" and extra_data == "sudo su": _t_hidden("H_HACK", HIDDEN_MISSIONS["H_HACK"]["title"])
    if action_type == "crypto_input" and str(extra_data) == "1024": _t_hidden("H_MATH", HIDDEN_MISSIONS["H_MATH"]["title"])
    if action_type == "pvp_win": _t_hidden("H_PVP_W", HIDDEN_MISSIONS["H_PVP_W"]["title"])
    if action_type == "cli_error" and isinstance(extra_data, int) and extra_data >= 5: _t_hidden("H_SPAM", HIDDEN_MISSIONS["H_SPAM"]["title"])
    
    if "stock_prices" in st.session_state:
        val = sum([amt * st.session_state.stock_prices.get(code,0) for code, amt in user.get("stocks",{}).items()])
        if val >= 50000: _t_hidden("H_WOLF", HIDDEN_MISSIONS["H_WOLF"]["title"])

    if triggered and uid != "frank":
        refresh_active_missions(user)
        save_db({"users": load_db()["users"]|{uid:user}, "bbs":[]})
    
    return user
