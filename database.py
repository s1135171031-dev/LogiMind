# ==========================================
# 檔案: database.py (動態任務版)
# ==========================================
import json
import os
import random
import streamlit as st
from datetime import datetime, date

# --- 檔案路徑 ---
USER_DB_FILE = "cityos_users.json"
QUIZ_FILE = "questions.txt"
LOG_FILE = "intruder_log.txt"

# --- 隱藏成就 (固定不變) ---
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

# --- 預設測驗 ---
DEFAULT_QUIZ = [
    {"id":"Q1", "level":"1", "q":"Python 定義函式用什麼？", "options":["def","func","var"], "ans":"def"},
    {"id":"Q2", "level":"1", "q":"二進位 101 是多少？", "options":["3","5","7"], "ans":"5"},
    {"id":"Q3", "level":"2", "q":"HTTP 成功狀態碼？", "options":["200","404","500"], "ans":"200"}
]

# --- [核心] 動態任務生成器 ---
def generate_dynamic_missions(user_level, existing_ids):
    """根據等級生成隨機任務，並確保不與現有ID重複"""
    
    # 任務模版 (Templates)
    # {target} 是行動類型, {val} 是數值要求, {sub} 是次要要求(如股票代碼)
    templates = [
        # 股市類
        {"type": "stock_buy", "base_reward": 150, "text": "投資眼光", "desc": "買入 {sub} 股票 {val} 股", "codes": ["CYBR", "NETW", "DARK", "CHIP"]},
        {"type": "stock_val", "base_reward": 200, "text": "資產增值", "desc": "持有 {sub} 股票總值達 ${val}", "codes": ["CYBR", "NETW"]},
        
        # 駭客類
        {"type": "cli_input", "base_reward": 100, "text": "指令練習", "desc": "在 CLI 輸入 '{sub}' 指令", "cmds": ["whoami", "bal", "scan", "help"]},
        {"type": "pvp_win",   "base_reward": 300, "text": "賞金獵人", "desc": "在 PVP 入侵成功 {val} 次", "range": (1, 3)},
        {"type": "crypto_input", "base_reward": 120, "text": "解碼員", "desc": "在密碼學輸入 '{sub}'"},

        # 生活類
        {"type": "bank_save", "base_reward": 100, "text": "儲蓄習慣", "desc": "單筆存入銀行 ${val}", "range": (500, 5000)},
        {"type": "shop_buy",  "base_reward": 150, "text": "軍備競賽", "desc": "在黑市購買 {sub}", "items": ["Firewall", "Brute Force Script"]},
        {"type": "quiz_done", "base_reward": 80,  "text": "知識份子", "desc": "完成每日測驗", "fixed": True},
        {"type": "send_mail", "base_reward": 50,  "text": "社交活躍", "desc": "發送一封郵件給 {sub}", "npcs": ["Alice", "Bob"]}
    ]

    new_missions = []
    # 根據等級調整難度係數
    multiplier = 1 + (user_level * 0.1) 

    while len(new_missions) < 4: # 每次產生 4 個新任務
        tmpl = random.choice(templates)
        m_id = f"M_{int(datetime.now().timestamp())}_{random.randint(1000,9999)}"
        
        # 產生具體參數
        val = 0
        sub = ""
        
        if "range" in tmpl:
            base_val = random.randint(tmpl["range"][0], tmpl["range"][1])
            val = int(base_val * multiplier)
        elif "fixed" not in tmpl: # 預設數值
             val = int(10 * multiplier)

        if "codes" in tmpl: sub = random.choice(tmpl["codes"])
        if "cmds" in tmpl: sub = random.choice(tmpl["cmds"])
        if "items" in tmpl: sub = random.choice(tmpl["items"])
        if "npcs" in tmpl: sub = random.choice(tmpl["npcs"])
        if tmpl["type"] == "crypto_input": sub = str(random.randint(100, 999))

        # 組合描述
        desc = tmpl["desc"].replace("{val}", str(val)).replace("{sub}", sub)
        reward = int(tmpl["base_reward"] * multiplier * random.uniform(0.8, 1.2))

        mission = {
            "id": m_id,
            "title": tmpl["text"],
            "desc": desc,
            "reward": reward,
            "target": tmpl["type"],
            "req_val": val,   # 需求數值
            "req_sub": sub    # 需求字串 (股票代碼/物品名)
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
        "active_missions": [], "mailbox": [] # active_missions 現在存放完整任務物件，不只是 ID
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
    from config import CITY_EVENTS # 避免循環引用
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

# --- [核心] 任務檢查與刷新邏輯 ---
def refresh_active_missions(user):
    """如果沒有任務或日期變更(可選)，則生成新任務"""
    # 這裡的邏輯是：如果身上的任務少於 3 個，就補滿
    # 為了讓任務多樣化，我們直接生成完整的任務物件存入 active_missions
    
    current_missions = user.get("active_missions", [])
    
    # 簡單過濾掉格式錯誤的舊資料 (如果之前存的是字串ID)
    current_missions = [m for m in current_missions if isinstance(m, dict)]
    
    if len(current_missions) < 3:
        # 生成新任務
        existing_ids = [m["id"] for m in current_missions]
        new_batch = generate_dynamic_missions(user.get("level", 1), existing_ids)
        
        for m in new_batch:
            if len(current_missions) >= 3: break
            current_missions.append(m)
            
        user["active_missions"] = current_missions
        return True # 表示有更新
    return False

def check_mission(uid, user, action_type, extra_data=None, extra_val=0):
    """
    action_type: 觸發動作類型 (如 stock_buy)
    extra_data: 輔助數據 (如 股票代碼 'CYBR' 或 CLI 指令 'help')
    extra_val: 數值數據 (如 買入股數 50)
    """
    if "completed_missions" not in user: user["completed_missions"] = []
    if "pending_claims" not in user: user["pending_claims"] = []
    
    # 1. 檢查並補貨任務
    if refresh_active_missions(user):
        save_db({"users": load_db()["users"]|{uid:user}, "bbs":[]})

    triggered = False
    
    # 2. 遍歷當前任務
    # 我們需要倒序遍歷，因為可能會從列表中移除項目
    for i in range(len(user["active_missions"]) - 1, -1, -1):
        mission = user["active_missions"][i]
        
        # 判斷類型是否匹配
        if mission["target"] == action_type:
            is_match = True
            
            # 判斷細節條件 (req_sub)
            if "req_sub" in mission and mission["req_sub"]:
                # 如果任務要求特定股票/指令，但玩家做的動作不符
                if str(extra_data) != str(mission["req_sub"]):
                    is_match = False
            
            # 判斷數值條件 (req_val) -> 這裡簡化為單次觸發大於等於即可
            # 進階寫法可以用進度條，這裡先做單次判定
            if "req_val" in mission and mission["req_val"] > 0:
                if extra_val < mission["req_val"]:
                    is_match = False

            if is_match:
                # 任務完成！
                user["pending_claims"].append(mission) # 移入待領取
                user["active_missions"].pop(i)         # 從進行中移除
                st.toast(f"🚩 達成：{mission['title']}！", icon="🎁")
                triggered = True

    # 3. 隱藏成就檢查 (保持原樣)
    def _t_hidden(mid, title):
        nonlocal triggered
        if mid not in user["completed_missions"] and mid not in [m.get("id","") if isinstance(m, dict) else m for m in user["pending_claims"]]:
            # 隱藏成就還是用簡單 ID 格式
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
    
    if triggered and uid != "frank":
        # 再次補貨
        refresh_active_missions(user)
        save_db({"users": load_db()["users"]|{uid:user}, "bbs":[]})
    
    return user
