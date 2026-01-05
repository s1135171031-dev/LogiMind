# ==========================================
# 檔案: database.py (V29.0 Sarcastic Mode)
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

# --- 隱藏成就 (獎勵大幅下修) ---
HIDDEN_MISSIONS = {
    "H_ZERO": {"title": "💸 乞丐超人", "desc": "現金歸零。現在你跟我一樣窮了。", "reward": 10},
    "H_777":  {"title": "🎰 777", "desc": "現金剛好 $777。去買樂透吧，別當駭客了。", "reward": 77},
    "H_SHOP": {"title": "🛍️ 敗家子", "desc": "背包物品 > 15。你是有囤積症嗎？", "reward": 50},
    "H_HACK": {"title": "💀 腳本小子", "desc": "CLI 輸入 sudo su。還真的以為這樣就有權限喔？", "reward": 50},
    "H_MATH": {"title": "🤓 1024", "desc": "輸入 1024。好啦，知道你是理組的。", "reward": 32},
    "H_SPAM": {"title": "🤬 鍵盤殺手", "desc": "連續打錯指令 5 次。鍵盤壞了還是腦袋壞了？", "reward": 10},
    "H_BANK": {"title": "🏦 守財奴", "desc": "存款>10萬且現金<100。有錢不花，等著通膨吃掉嗎？", "reward": 100},
    "H_PVP_W": {"title": "⚔️ 暴力狂", "desc": "PVP 獲勝。搶別人的錢很開心是吧？", "reward": 50},
    "H_WOLF": {"title": "🐺 華爾街之狼", "desc": "股票市值 > $50,000。分一點給我會死喔？", "reward": 200}
}

# --- 預設測驗 (獎金變少) ---
DEFAULT_QUIZ = [
    {"id":"Q1", "level":"1", "q":"Python 定義函式用什麼？", "options":["def","func","var"], "ans":"def"},
    {"id":"Q2", "level":"1", "q":"二進位 101 是多少？", "options":["3","5","7"], "ans":"5"},
    {"id":"Q3", "level":"2", "q":"HTTP 成功狀態碼？", "options":["200","404","500"], "ans":"200"}
]

# --- [核心] 毒舌動態任務生成器 ---
def generate_dynamic_missions(user_level, existing_ids):
    """生成充滿吐槽的隨機任務，獎勵微薄"""
    
    templates = [
        # 股市類
        {
            "type": "stock_buy", "base_reward": 30, # 原 150 -> 30
            "text": "護盤俠", 
            "desc": "老闆說 {sub} 股價太難看，去買 {val} 股撐一下。快點，別讓韭菜跑了。", 
            "codes": ["CYBR", "NETW", "DARK", "CHIP"]
        },
        {
            "type": "stock_val", "base_reward": 40, # 原 200 -> 40
            "text": "資產證明", 
            "desc": "持有 {sub} 股票總值達 ${val}。讓我看看你是不是真大戶，還是只是在裝B。", 
            "codes": ["CYBR", "NETW"]
        },
        
        # 駭客類
        {
            "type": "cli_input", "base_reward": 15, # 原 100 -> 15
            "text": "手指復健", 
            "desc": "鍵盤生灰塵了嗎？去 CLI 輸入 '{sub}' 假裝你在工作。", 
            "cmds": ["whoami", "bal", "scan", "help"]
        },
        {
            "type": "pvp_win",   "base_reward": 50, # 原 300 -> 50
            "text": "合法搶劫", 
            "desc": "我看大家過太爽，去 PVP 入侵成功 {val} 次。記得把錢轉過來，這才是重點。", 
            "range": (1, 3)
        },
        {
            "type": "crypto_input", "base_reward": 25, # 原 120 -> 25
            "text": "猜謎時間", 
            "desc": "去密碼學頁面輸入 '{sub}'。別問為什麼，照做就對了。", 
        },

        # 生活類
        {
            "type": "bank_save", "base_reward": 20, # 原 100 -> 20
            "text": "存錢買棺材", 
            "desc": "把 ${val} 存進銀行。雖然利息連買茶葉蛋都不夠。", 
            "range": (100, 1000)
        },
        {
            "type": "shop_buy",  "base_reward": 20, # 原 150 -> 20 (買東西還只給20塊，虧爆)
            "text": "促進經濟", 
            "desc": "去黑市買個 {sub}。我知道很貴，但為了組織的榮耀（和我的業績），你必須買。", 
            "items": ["Firewall", "Brute Force Script", "Engineer Heart"]
        },
        {
            "type": "quiz_done", "base_reward": 10, # 原 80 -> 10 (買不起咖啡)
            "text": "腦力激盪", 
            "desc": "去完成每日測驗。證明你的腦袋不只是裝飾品。", 
            "fixed": True
        },
        {
            "type": "send_mail", "base_reward": 5,  # 原 50 -> 5 (發信要錢喔?)
            "text": "騷擾信件", 
            "desc": "發一封信給 {sub}。內容隨便，反正他們也不會回。", 
            "npcs": ["Alice", "Bob", "Frank"]
        }
    ]

    new_missions = []
    # 難度係數 (雖然變難了，但獎勵增加幅度很小)
    multiplier = 1 + (user_level * 0.05) 

    while len(new_missions) < 4:
        tmpl = random.choice(templates)
        m_id = f"M_{int(datetime.now().timestamp())}_{random.randint(1000,9999)}"
        
        val = 0
        sub = ""
        
        if "range" in tmpl:
            base_val = random.randint(tmpl["range"][0], tmpl["range"][1])
            val = int(base_val * multiplier)
        elif "fixed" not in tmpl:
             val = int(5 * multiplier) # 數量要求

        if "codes" in tmpl: sub = random.choice(tmpl["codes"])
        if "cmds" in tmpl: sub = random.choice(tmpl["cmds"])
        if "items" in tmpl: sub = random.choice(tmpl["items"])
        if "npcs" in tmpl: sub = random.choice(tmpl["npcs"])
        if tmpl["type"] == "crypto_input": sub = str(random.randint(100, 999))

        desc = tmpl["desc"].replace("{val}", str(val)).replace("{sub}", sub)
        reward = int(tmpl["base_reward"] * multiplier)

        mission = {
            "id": m_id,
            "title": tmpl["text"],
            "desc": desc,
            "reward": reward,
            "target": tmpl["type"],
            "req_val": val,
            "req_sub": sub
        }
        
        new_missions.append(mission)

    return new_missions

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

# --- DB 操作 ---
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
            "alice": get_npc_data("Alice", "Hacker", 15, 800, "1357"),
            "bob": get_npc_data("Bob", "Engineer", 10, 350, "2468"),
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

def get_today_event():
    from config import CITY_EVENTS
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

# --- 任務檢查 ---
def refresh_active_missions(user):
    current_missions = user.get("active_missions", [])
    current_missions = [m for m in current_missions if isinstance(m, dict)]
    
    if len(current_missions) < 3:
        existing_ids = [m["id"] for m in current_missions]
        new_batch = generate_dynamic_missions(user.get("level", 1), existing_ids)
        
        for m in new_batch:
            if len(current_missions) >= 3: break
            current_missions.append(m)
            
        user["active_missions"] = current_missions
        return True
    return False

def check_mission(uid, user, action_type, extra_data=None, extra_val=0):
    if "completed_missions" not in user: user["completed_missions"] = []
    if "pending_claims" not in user: user["pending_claims"] = []
    
    if refresh_active_missions(user):
        save_db({"users": load_db()["users"]|{uid:user}, "bbs":[]})

    triggered = False
    
    for i in range(len(user["active_missions"]) - 1, -1, -1):
        mission = user["active_missions"][i]
        
        if mission["target"] == action_type:
            is_match = True
            
            if "req_sub" in mission and mission["req_sub"]:
                if str(extra_data) != str(mission["req_sub"]): is_match = False
            
            if "req_val" in mission and mission["req_val"] > 0:
                if extra_val < mission["req_val"]: is_match = False

            if is_match:
                user["pending_claims"].append(mission)
                user["active_missions"].pop(i)
                st.toast(f"🚩 達成：{mission['title']}！ (+$ {mission['reward']})", icon="🎁")
                triggered = True

    def _t_hidden(mid, title):
        nonlocal triggered
        if mid not in user["completed_missions"] and mid not in [m.get("id","") if isinstance(m, dict) else m for m in user["pending_claims"]]:
            user["pending_claims"].append({"id": mid, "title": title, "reward": HIDDEN_MISSIONS[mid]["reward"], "desc": HIDDEN_MISSIONS[mid]["desc"]})
            st.toast(f"🕵️ 隱藏成就：{title}！", icon="🔥")
            triggered = True

    if user["money"] == 0: _t_hidden("H_ZERO", HIDDEN_MISSIONS["H_ZERO"]["title"])
    if user["money"] == 777: _t_hidden("H_777", HIDDEN_MISSIONS["H_777"]["title"])
    if sum(user.get("inventory", {}).values()) >= 15: _t_hidden("H_SHOP", HIDDEN_MISSIONS["H_SHOP"]["title"])
    if user.get("bank_deposit",0)>100000 and user["money"]<100: _t_hidden("H_BANK", HIDDEN_MISSIONS["H_BANK"]["title"])
    if action_type == "cli_input" and extra_data == "sudo su": _t_hidden("H_HACK", HIDDEN_MISSIONS["H_HACK"]["title"])
    if action_type == "crypto_input" and str(extra_data) == "1024": _t_hidden("H_MATH", HIDDEN_MISSIONS["H_MATH"]["title"])
    if action_type == "pvp_win": _t_hidden("H_PVP_W", HIDDEN_MISSIONS["H_PVP_W"]["title"])
    
    if "stock_prices" in st.session_state:
        val = sum([amt * st.session_state.stock_prices.get(code,0) for code, amt in user.get("stocks",{}).items()])
        if val >= 50000: _t_hidden("H_WOLF", HIDDEN_MISSIONS["H_WOLF"]["title"])

    if triggered and uid != "frank":
        refresh_active_missions(user)
        save_db({"users": load_db()["users"]|{uid:user}, "bbs":[]})
    
    return user
