import streamlit as st
import random
import time
import json
import os
import pandas as pd
from datetime import datetime, timedelta

# ==========================================
# 1. 設定區
# ==========================================

ITEMS = {
    "Nutri-Paste": {"price": 20, "desc": "像是嘔吐物的營養膏。"},
    "Stim-Pack": {"price": 150, "desc": "非法興奮劑，手會抖。"},
    "Data Chip": {"price": 300, "desc": "從垃圾堆撿來的晶片。"},
    "GPU (Mining)": {"price": 5000, "desc": "現在比人命還值錢。"},
    "Firewall Key": {"price": 10000, "desc": "駭客夢寐以求的玩具。"}
}

STOCKS_DATA = {
    "CYBR": {"name": "CyberCorp", "base": 1200, "volatility": 0.2},
    "NEO":  {"name": "Neo-Tokyo", "base": 5000, "volatility": 0.1},
    "SLUM": {"name": "Slum Ind.", "base": 50, "volatility": 0.4},
    "AI":   {"name": "Skynet", "base": 3000, "volatility": 0.3},
    "BOND": {"name": "City Bond", "base": 100, "volatility": 0.05},
    "DOGE": {"name": "MemeCoin", "base": 10, "volatility": 0.8}
}

# ==========================================
# 2. 資料庫邏輯
# ==========================================

USER_DB_FILE = "cityos_users.json"
STOCK_DB_FILE = "cityos_chaos_market.json"

def init_db():
    # 初始化使用者
    if not os.path.exists(USER_DB_FILE):
        users = {
            "admin": { "password": "admin", "name": "System OVERLORD", "money": 99999, "job": "Admin", "stocks": {}, "inventory": {}, "mailbox": [] },
            "frank": { "password": "x", "name": "Frank (Dev)", "money": 50000, "job": "Hacker", "stocks": {"CYBR": 100}, "inventory": {}, "mailbox": [] }
        }
        with open(USER_DB_FILE, "w", encoding="utf-8") as f: 
            json.dump(users, f, indent=4, ensure_ascii=False)
    
    # 初始化股市
    if not os.path.exists(STOCK_DB_FILE):
        rebuild_market()

def rebuild_market():
    """ 生成 50 筆絕對混亂的歷史數據 """
    current_prices = {k: v["base"] for k, v in STOCKS_DATA.items()}
    history = []
    
    for i in range(50):
        row = {}
        for code, price in current_prices.items():
            change_pct = random.uniform(-0.2, 0.2)
            force_jitter = random.randint(-5, 5) 
            if force_jitter == 0: force_jitter = 1
            
            new_price = int(price * (1 + change_pct) + force_jitter)
            new_price = max(1, new_price)
            
            current_prices[code] = new_price
            row[code] = new_price
        
        past_time = datetime.now() - timedelta(seconds=(50-i)*2)
        row["_time"] = past_time.strftime("%H:%M:%S")
        history.append(row)

    state = { "last_update": time.time(), "prices": current_prices, "history": history }
    with open(STOCK_DB_FILE, "w", encoding="utf-8") as f: 
        json.dump(state, f, indent=4)
    return True

# --- 修正後的讀寫函數 (分行寫) ---

def get_all_users():
    try:
        with open(USER_DB_FILE, "r", encoding="utf-8") as f: 
            return json.load(f)
    except: 
        return {}

def get_user(uid): 
    return get_all_users().get(uid)

def save_user(uid, data):
    users = get_all_users()
    users[uid] = data
    with open(USER_DB_FILE, "w", encoding="utf-8") as f: 
        json.dump(users, f, indent=4, ensure_ascii=False)

def create_user(uid, pwd, name):
    users = get_all_users()
    if uid in users: return False
    users[uid] = { "password": pwd, "name": name, "money": 1000, "job": "Citizen", "stocks": {}, "inventory": {}, "mailbox": [] }
    with open(USER_DB_FILE, "w", encoding="utf-8") as f: 
        json.dump(users, f, indent=4, ensure_ascii=False)
    return True

def get_global_stock_state():
    try: 
        with open(STOCK_DB_FILE, "r", encoding="utf-8") as f: 
            return json.load(f)
    except: 
        return None

def save_global_stock_state(state):
    with open(STOCK_DB_FILE, "w", encoding="utf-8") as f: 
        json.dump(state, f, indent=4)

# ==========================================
# 3. 前端介面
# ==========================================

st.set_page_config(page_title="CityOS Chaos", layout="wide", page_icon="⚡")
st.markdown("""<style>.stApp { background-color: #050505; color: #00ff41; font-family: monospace; }</style>""", unsafe_allow_html=True)

# 初始化
init_db()

def update_stock_market():
    global_state = get_global_stock_state()
    if not global_state: return

    now = time.time()
    # 0.5 秒刷新一次
    if now - global_state.get("last_update", 0) > 0.5:
        new_prices = {}
        for code, data in STOCKS_DATA.items():
            prev = global_state["prices"].get(code, data["base"])
            
            # 🔥 波動演算法
            pct = random.uniform(-0.15, 0.15)
            jitter = random.randint(-10, 10)
            if jitter == 0: jitter = random.choice([-2, 2]) 

            new_p = int(prev * (1 + pct) + jitter)
            new_p = max(1, new_p) 
            
            new_prices[code] = new_p

        global_state["prices"] = new_prices
        global_state["last_update"] = now
        
        hist = new_prices.copy()
        hist["_time"] = datetime.now().strftime("%H:%M:%S")
        global_state["history"].append(hist)
        if len(global_state["history"]) > 60: global_state["history"].pop(0)
        
        save_global_stock_state(global_state)

    st.session_state.stock_prices = global_state["prices"]
    st.session_state.stock_history = pd.DataFrame(global_state["history"])

def page_stock_market(uid, user):
    st.title("📈 混亂交易所")
    
    # 自動刷新開關
    auto_refresh = st.toggle("⚡ 啟用即時連線 (AUTO-REFRESH)", value=True)
    
    update_stock_market()
    
    # 圖表
    if "stock_history" in st.session_state and not st.session_state.stock_history.empty:
        chart_data = st.session_state.stock_history.drop(columns=["_time"], errors="ignore")
        st.line_chart(chart_data, height=300)
        
    # 報價
    cols = st.columns(len(STOCKS_DATA))
    prices = st.session_state.stock_prices
    for i, (code, val) in enumerate(prices.items()):
        cols[i].metric(code, f"${val}", delta=random.choice(["↑", "↓", "⚡"]))

    # 交易介面
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        buy_code = st.selectbox("買進標的", list(STOCKS_DATA.keys()))
        if st.button("BUY (10股)"):
            cost = prices[buy_code] * 10
            if user['money'] >= cost:
                user['money'] -= cost
                user.setdefault('stocks', {})[buy_code] = user['stocks'].get(buy_code, 0) + 10
                save_user(uid, user)
                st.success("交易成功")
                st.rerun()
    with c2:
        st.write(f"持有股份: {user.get('stocks', {})}")
        st.write(f"剩餘資金: ${user['money']}")

    # 自動刷新
    if auto_refresh:
        time.sleep(1)
        st.rerun()

def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    
    # 登入頁面
    if not st.session_state.logged_in:
        st.title("CITY_OS // LOGIN")
        c1, c2 = st.tabs(["登入", "註冊"])
        with c1:
            u = st.text_input("ID", key="login_u"); p = st.text_input("PWD", type="password", key="login_p")
            if st.button("LOGIN"):
                user = get_user(u)
                if user and user['password'] == p:
                    st.session_state.logged_in = True; st.session_state.uid = u; st.rerun()
                else: st.error("帳號密碼錯誤")
        with c2:
            nu = st.text_input("New ID"); np = st.text_input("New PWD", type="password"); nn = st.text_input("Name")
            if st.button("REGISTER"):
                if create_user(nu, np, nn): st.success("註冊成功，請登入")
                else: st.error("ID 已被使用")
        return

    # 登入後頁面
    uid = st.session_state.uid; user = get_user(uid)
    
    with st.sidebar:
        st.title(f"User: {user['name']}")
        st.metric("Cash", f"${user['money']}")
        if st.button("登出"): st.session_state.logged_in = False; st.rerun()
        st.divider()
        if st.button("💥 重置股市 (Admin)"): 
            rebuild_market()
            st.toast("股市已重置為混沌狀態")
            time.sleep(1)
            st.rerun()

    page_stock_market(uid, user)

if __name__ == "__main__":
    main()
