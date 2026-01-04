import streamlit as st
import pandas as pd
import random
import os
import time
import json
import numpy as np
from datetime import datetime, date

# ==============================================================================
# 1. 系統設定 & 資料結構
# ==============================================================================
st.set_page_config(page_title="CityOS V16.0 Evolution", layout="wide", page_icon="🏙️", initial_sidebar_state="expanded")

USER_DB_FILE = "cityos_users.json"
LOG_FILE = "intruder_log.txt"

# --- [新增] 每日事件庫 ---
CITY_EVENTS = [
    {"id": "E01", "name": "平靜的一天", "desc": "各項指數正常。", "effect": None},
    {"id": "E02", "name": "牛市來臨", "desc": "加密貨幣飆升，挖礦收益 +50%。", "effect": "mining_boost"},
    {"id": "E03", "name": "黑色星期五", "desc": "黑市大特價，所有道具 7 折。", "effect": "shop_discount"},
    {"id": "E04", "name": "太陽風暴", "desc": "通訊干擾，駭客攻擊成功率與收益下降。", "effect": "hack_nerf"},
    {"id": "E05", "name": "系統漏洞", "desc": "防火牆失效，攻擊收益加倍！", "effect": "hack_boost"},
]

# --- [新增] 任務資料庫 ---
MISSIONS = {
    "M01": {"title": "初入社會", "desc": "前往銀行存入至少 $100。", "reward": 500, "target": "bank_save"},
    "M02": {"title": "裝備升級", "desc": "在黑市購買任意一件物品。", "reward": 800, "target": "shop_buy"},
    "M03": {"title": "邏輯入門", "desc": "在數位實驗室操作一次邏輯閘。", "reward": 600, "target": "logic_use"},
    "M04": {"title": "第一滴血", "desc": "成功執行一次駭客攻擊 (不論成敗)。", "reward": 1000, "target": "attack_try"},
    "M05": {"title": "資安大師", "desc": "將個人防禦代碼修改一次 (重置)。", "reward": 1500, "target": "change_code"}
}

# --- SVG 資源 ---
SVG_LIB = {
    "AND": '''<svg width="150" height="80"><path d="M20,10 L70,10 C95,10 110,30 110,40 C110,50 95,70 70,70 L20,70 Z" fill="none" stroke="#00FF00" stroke-width="3"/><path d="M0,25 L20,25 M0,55 L20,55 M110,40 L140,40" stroke="#00FF00" stroke-width="3"/><text x="40" y="45" fill="white" font-family="monospace">AND</text></svg>''',
    "OR": '''<svg width="150" height="80"><path d="M20,10 L60,10 Q90,40 60,70 L20,70 Q45,40 20,10 Z" fill="none" stroke="#00FF00" stroke-width="3"/><path d="M0,25 L25,25 M0,55 L25,55 M90,40 L120,40" stroke="#00FF00" stroke-width="3"/><text x="35" y="45" fill="white" font-family="monospace">OR</text></svg>''',
    "XOR": '''<svg width="150" height="80"><path d="M35,10 L75,10 Q105,40 75,70 L35,70 Q60,40 35,10 Z" fill="none" stroke="#00FF00" stroke-width="3"/><path d="M15,10 Q40,40 15,70" fill="none" stroke="#00FF00" stroke-width="3"/><path d="M0,25 L25,25 M0,55 L25,55 M105,40 L135,40" stroke="#00FF00" stroke-width="3"/><text x="50" y="45" fill="white" font-family="monospace">XOR</text></svg>''',
    "NOT": '''<svg width="150" height="80"><path d="M30,10 L30,70 L90,40 Z" fill="none" stroke="#00FF00" stroke-width="3"/><circle cx="96" cy="40" r="5" fill="none" stroke="#00FF00" stroke-width="2"/><path d="M0,40 L30,40 M102,40 L130,40" stroke="#00FF00" stroke-width="3"/><text x="40" y="45" fill="white" font-family="monospace">NOT</text></svg>'''
}
MORSE_CODE_DICT = { 'A':'.-', 'B':'-...', 'C':'-.-.', 'D':'-..', 'E':'.', 'F':'..-.', 'G':'--.', 'H':'....', 'I':'..', 'J':'.---', 'K':'-.-', 'L':'.-..', 'M':'--', 'N':'-.', 'O':'---', 'P':'.--.', 'Q':'--.-', 'R':'.-.', 'S':'...', 'T':'-', 'U':'..-', 'V':'...-', 'W':'.--', 'X':'-..-', 'Y':'-.--', 'Z':'--..', '1':'.----', '2':'..---', '3':'...--', '4':'....-', '5':'.....', '6':'-....', '7':'--...', '8':'---..', '9':'----.', '0':'-----'}

CLASSES = {
    "Novice": {"name": "一般市民", "icon": "👤", "desc": "權限受限。請盡快轉職。"},
    "Engineer": {"name": "硬體工程師", "icon": "🔧", "desc": "解鎖：[數位實驗室]、[挖礦加成]。"},
    "Programmer": {"name": "軟體工程師", "icon": "💻", "desc": "解鎖：[密碼學中心]、[CLI模式]。"},
    "Hacker": {"name": "資安專家", "icon": "🛡️", "desc": "解鎖：[駭客終端]、[黑市借貸]。"},
    "Architect": {"name": "系統創造者", "icon": "👑", "desc": "全知全能。"}
}

ITEMS = {
    "Mining GPU": {"price": 2000, "desc": "基礎礦機，每日登入 +$100", "type": "passive"},
    "Trojan Virus": {"price": 500, "desc": "攻擊必備：木馬程式 (消耗品)", "type": "attack"},
    "Firewall": {"price": 800, "desc": "防禦必備：抵擋一次攻擊 (消耗品)", "type": "defense"},
    "Chaos Heart": {"price": 1200, "desc": "混亂之心：被攻擊時，使對方選項 x2 (消耗品)", "type": "trap"},
    "Clarity Necklace": {"price": 1500, "desc": "清醒項鍊：攻擊時，排除一半錯誤選項 (消耗品)", "type": "buff"}
}

# ==============================================================================
# 2. 核心邏輯 (Backend)
# ==============================================================================

def get_today_event():
    """根據日期生成固定隨機事件 (讓所有人當天事件相同)"""
    seed = int(date.today().strftime("%Y%m%d"))
    random.seed(seed)
    event = random.choice(CITY_EVENTS)
    random.seed() # 重置隨機種子以免影響後續
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
        "completed_missions": [] # 新增任務紀錄
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
            # 資料結構遷移 (Migration)
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

# ==============================================================================
# 3. 頁面模組
# ==============================================================================

# --- [模組 A] CLI 終端機模式 (New!) ---
def page_cli_os(uid, user):
    st.markdown("""
    <style>
    .stTextInput > div > div > input {
        background-color: #000; color: #00ff00; font-family: 'Courier New', monospace;
    }
    </style>
    """, unsafe_allow_html=True)
    st.title("💻 Terminal Mode (CLI)")
    st.caption("CityOS Kernel v16.0 | Type 'help' for commands.")

    if "cli_history" not in st.session_state:
        st.session_state.cli_history = ["System initialized..."]

    # 顯示歷史紀錄
    cmd_container = st.container(height=400)
    with cmd_container:
        for line in st.session_state.cli_history:
            st.text(line)

    # 指令解析器
    cmd = st.chat_input("Enter command >>")
    if cmd:
        st.session_state.cli_history.append(f"user@{uid}:~$ {cmd}")
        tokens = cmd.strip().split()
        base_cmd = tokens[0].lower() if tokens else ""
        
        response = ""
        
        if base_cmd == "help":
            response = """
            Available Commands:
            - whoami : 顯示使用者狀態
            - bal    : 顯示餘額
            - scan   : 掃描可攻擊目標
            - buy <item_key> : 快速購買 (virus, firewall)
            - clear  : 清除畫面
            """
        elif base_cmd == "clear":
            st.session_state.cli_history = []
            st.rerun()
        elif base_cmd == "whoami":
            response = f"User: {user['name']}\nRole: {user['job']}\nIP: 192.168.0.{random.randint(2,254)}"
        elif base_cmd == "bal":
            response = f"Cash: ${user['money']:,}\nBank: ${user.get('bank_deposit',0):,}"
        elif base_cmd == "scan":
            db = load_db()
            targets = [u for u in db["users"].keys() if u != uid and u != "frank"]
            response = "Scanning network...\n" + "\n".join([f"[+] Target found: {t}" for t in targets])
        elif base_cmd == "buy":
            if len(tokens) < 2:
                response = "Usage: buy <virus|firewall>"
            else:
                item_map = {"virus": "Trojan Virus", "firewall": "Firewall"}
                item_key = tokens[1].lower()
                if item_key in item_map:
                    real_name = item_map[item_key]
                    price = ITEMS[real_name]["price"]
                    # 應用事件折扣
                    evt = st.session_state.today_event
                    if evt["effect"] == "shop_discount": price = int(price * 0.7)
                    
                    if user["money"] >= price:
                        user["money"] -= price
                        if "inventory" not in user: user["inventory"] = {}
                        user["inventory"][real_name] = user["inventory"].get(real_name, 0) + 1
                        check_mission(uid, user, "shop_buy") # 觸發任務
                        if uid != "frank": save_db({"users": load_db()["users"] | {uid: user}, "bbs": load_db().get("bbs", [])})
                        response = f"Successfully purchased {real_name} for ${price}."
                    else:
                        response = "Error: Insufficient funds."
                else:
                    response = "Error: Item not found in CLI shop."
        else:
            response = f"Command not found: {base_cmd}"

        if response:
            st.session_state.cli_history.append(response)
        st.rerun()

# --- [模組 B] 任務中心 (New!) ---
def page_missions(uid, user):
    st.title("🎯 任務中心 (Mission Control)")
    
    completed = user.get("completed_missions", [])
    
    # 計算進度
    total = len(MISSIONS)
    done = len(completed)
    st.progress(done/total, text=f"完成度: {done}/{total}")
    
    col1, col2 = st.columns(2)
    
    # 進行中
    with col1:
        st.subheader("🚧 待辦事項")
        for mid, m_data in MISSIONS.items():
            if mid not in completed:
                with st.container(border=True):
                    st.write(f"**{m_data['title']}**")
                    st.caption(m_data['desc'])
                    st.write(f"💰 報酬: ${m_data['reward']}")
                    st.info(f"Target: {m_data['target']}")

    # 已完成
    with col2:
        st.subheader("✅ 已完成")
        for mid in completed:
            m_data = MISSIONS[mid]
            with st.container(border=True):
                st.write(f"~~{m_data['title']}~~")
                st.caption("已領取獎勵")

# --- [模組 C] 原有功能 (整合任務觸發) ---

def page_digital_lab(uid, user):
    st.title("🔬 數位邏輯實驗室")
    # ... (原有代碼省略，僅展示整合部分)
    gate = st.selectbox("選擇元件", list(SVG_LIB.keys()))
    col_a, col_b = st.columns(2)
    a = col_a.toggle("Input A"); b = col_b.toggle("Input B")
    st.markdown(SVG_LIB[gate], unsafe_allow_html=True)
    
    # [Hook] 任務觸發
    if gate and (a or b): # 簡單判定有用過
        check_mission(uid, user, "logic_use")

def page_bank(uid, user):
    st.title("🏦 賽博銀行")
    
    # 事件影響
    evt = st.session_state.today_event
    mining_mult = 1.5 if evt["effect"] == "mining_boost" else 1.0
    
    gpu = user.get("inventory", {}).get("Mining GPU", 0)
    income = int(gpu * 100 * mining_mult)
    
    if income > 0: st.toast(f"⛏️ 礦機收益 (+{(mining_mult-1)*100:.0f}% Boost): +${income}")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("存款", f"${user.get('bank_deposit',0):,}")
    c2.metric("現金", f"${user['money']:,}")
    
    with st.expander("💳 存提款", expanded=True):
        amt = st.number_input("金額", 0, 10000, 100)
        if st.button("存入") and user['money'] >= amt:
            user['money'] -= amt; user['bank_deposit'] += amt
            # [Hook] 任務觸發
            if amt >= 100: check_mission(uid, user, "bank_save")
            if uid!="frank": save_db({"users":load_db()["users"]|{uid:user}, "bbs": load_db().get("bbs", [])})
            st.rerun()

def page_shop(uid, user):
    st.title("🛒 地下黑市")
    
    # 事件影響
    evt = st.session_state.today_event
    discount = 0.7 if evt["effect"] == "shop_discount" else 1.0
    if discount < 1.0: st.success("🔥 黑色星期五特賣中！所有商品 7 折！")
    
    cols = st.columns(3)
    idx = 0
    for item, info in ITEMS.items():
        final_price = int(info['price'] * discount)
        with cols[idx % 3].container(border=True):
            st.subheader(item)
            st.write(info['desc'])
            st.write(f"**價格: ${final_price:,}**")
            if discount < 1.0: st.caption(f"原價: ${info['price']}")
            
            if st.button(f"購買 {item}", key=item):
                if user['money'] >= final_price:
                    user['money'] -= final_price
                    if "inventory" not in user: user["inventory"] = {}
                    user["inventory"][item] = user["inventory"].get(item, 0) + 1
                    # [Hook] 任務
                    check_mission(uid, user, "shop_buy")
                    if uid!="frank": save_db({"users": load_db()["users"] | {uid: user}, "bbs": load_db().get("bbs", [])})
                    st.rerun()
                else: st.error("現金不足")
        idx+=1

def page_terminal(uid, user):
    st.title("📟 駭客終端 (GUI)")
    # (保留原有的 GUI 攻擊邏輯，這裡僅示意整合點)
    # ... 省略部分原有代碼以節省篇幅，請保留原有的 page_terminal ...
    # 只要在攻擊成功/失敗的地方加上:
    # check_mission(uid, user, "attack_try") 
    
    # 為了完整性，這裡填入簡化的攻擊邏輯回顧
    if "target_uid" not in st.session_state:
        targets = [u for u in load_db()["users"].keys() if u!=uid and u!="frank"]
        t = st.selectbox("目標", targets)
        if st.button("掃描"): st.session_state.target_uid = t; st.rerun()
    else:
        st.write(f"正在鎖定 {st.session_state.target_uid}...")
        if st.button("發動攻擊 (Demo)"):
            # 這裡應該放原本的複雜邏輯
            # 簡化演示任務觸發
            check_mission(uid, user, "attack_try")
            st.success("攻擊指令已發送")
            del st.session_state.target_uid
            st.rerun()
            
    # 新增按鈕切換防禦碼
    with st.expander("🛡️ 防禦設定"):
        if st.button("重置防禦代碼"):
            user["defense_code"] = random.randint(0, 9)
            check_mission(uid, user, "change_code")
            if uid!="frank": save_db({"users": load_db()["users"] | {uid: user}, "bbs": load_db().get("bbs", [])})
            st.success(f"新代碼: {user['defense_code']}")


# ==============================================================================
# 4. 主程式架構
# ==============================================================================
def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    
    # 生成每日事件
    if "today_event" not in st.session_state:
        st.session_state.today_event = get_today_event()

    # --- 登入頁 ---
    if not st.session_state.logged_in:
        st.markdown("<h1 style='text-align: center;'>🏙️ CityOS V16.0</h1>", unsafe_allow_html=True)
        evt = st.session_state.today_event
        st.info(f"📅 今日城市狀態: **{evt['name']}** - {evt['desc']}")
        
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            tab_l, tab_r = st.tabs(["登入", "註冊"])
            with tab_l:
                u = st.text_input("帳號"); p = st.text_input("密碼", type="password")
                if st.button("登入"):
                    db = load_db()
                    if u=="frank" and p=="x12345678x":
                        st.session_state.logged_in=True; st.session_state.user_id="frank"; st.session_state.user_data=get_admin_data(); st.rerun()
                    elif u in db["users"] and db["users"][u]["password"]==p:
                        st.session_state.logged_in=True; st.session_state.user_id=u; st.session_state.user_data=db["users"][u]; st.rerun()
                    else: st.error("失敗")
            with tab_r:
                nu = st.text_input("新帳號"); np_pass = st.text_input("新密碼", type="password")
                if st.button("註冊"):
                    db = load_db()
                    if nu not in db["users"] and len(nu)>3:
                        db["users"][nu] = get_npc_data(nu, "Novice", 1, 1000)
                        db["users"][nu]["password"] = np_pass
                        save_db(db)
                        st.success("成功")
        return

    # --- 主程式 ---
    uid = st.session_state.user_id
    user = st.session_state.user_data
    if uid != "frank": user = load_db()["users"].get(uid, user)

    # Sidebar 資訊
    st.sidebar.title(f"🆔 {user['name']}")
    evt = st.session_state.today_event
    st.sidebar.warning(f"⚡ {evt['name']}")
    
    # 任務進度微型顯示
    done_cnt = len(user.get("completed_missions", []))
    st.sidebar.caption(f"任務進度: {done_cnt}/{len(MISSIONS)}")
    
    nav_options = ["大廳", "任務中心", "銀行", "黑市", "駭客終端(GUI)", "CMD模式", "數位實驗室"]
    nav = st.sidebar.radio("導航", nav_options)

    if st.sidebar.button("登出"): st.session_state.logged_in=False; st.rerun()

    # 路由
    if nav == "大廳":
        st.title("📊 城市大廳")
        st.write(f"歡迎回來。今日城市氣象：{evt['desc']}")
    elif nav == "任務中心": page_missions(uid, user)
    elif nav == "CMD模式": page_cli_os(uid, user)
    elif nav == "銀行": page_bank(uid, user)
    elif nav == "黑市": page_shop(uid, user)
    elif nav == "數位實驗室": page_digital_lab(uid, user)
    elif nav == "駭客終端(GUI)": page_terminal(uid, user)

if __name__ == "__main__":
    main()
