import streamlit as st
import random
import time
import pandas as pd
import base64
import plotly.graph_objects as go
from datetime import datetime
import os

# 引入本地模組 (確保 database.py 在同一個資料夾)
from database import (
    init_db, get_user, save_user, create_user, 
    get_global_stock_state, save_global_stock_state, 
    get_all_users, apply_environmental_hazard, add_exp,
    add_log, get_logs
)

# 定義常數
SVG_LIB = {
    "AND": '<svg viewBox="0 0 60 40" width="100"><path d="M10,5 L30,5 C45,5 45,35 30,35 L10,35 Z" fill="none" stroke="#00ff41" stroke-width="2"/><path d="M0,10 L10,10 M0,30 L10,30 M45,20 L60,20" stroke="#00ff41" stroke-width="2"/></svg>',
    "OR": '<svg viewBox="0 0 60 40" width="100"><path d="M10,5 C10,5 20,20 10,35 C25,35 50,25 50,20 C50,15 25,5 10,5" fill="none" stroke="#00ff41" stroke-width="2"/><path d="M0,10 L15,10 M0,30 L15,30 M50,20 L60,20" stroke="#00ff41" stroke-width="2"/></svg>'
}
ITEMS = {
    "Nutri-Paste": {"price": 50, "desc": "噁心的營養膏 (飽食度+10)"},
    "Stim-Pack": {"price": 150, "desc": "興奮劑 (短暫提升能力)"},
    "Cyber-Arm": {"price": 2000, "desc": "軍用義肢 (挖礦效率 UP)"},
    "Trojan Virus": {"price": 300, "desc": "木馬程式 (PVP 專用)"},
    "Anti-Rad Pill": {"price": 500, "desc": "抗輻射藥丸 (清除毒素)"}
}
STOCKS_DATA = {"NVID": {"base": 800}, "TSMC": {"base": 600}, "BTC": {"base": 30000}}
LEVEL_TITLES = {1: "菜鳥", 5: "腳本小子", 10: "黑客", 50: "網路幽靈", 100: "數位之神"}

# 1. 頁面設定 (必須是第一行 Streamlit 指令)
st.set_page_config(page_title="CityOS: Final Cut", layout="wide", page_icon="☣️")

# 2. 全域 CSS (駭客風格)
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00ff41; font-family: 'Courier New', monospace; }
    div.stButton > button { background-color: #000; border: 1px solid #00ff41; color: #00ff41; }
    div.stButton > button:hover { background-color: #00ff41; color: #000; box-shadow: 0 0 15px #00ff41; }
    .stTextInput > div > div > input { color: #00ff41; background-color: #111; border-color: #333; }
    code { color: #e6db74; background-color: #222; }
</style>
""", unsafe_allow_html=True)

# 初始化 DB
init_db()

# --- 核心邏輯 ---
def update_stock_market():
    global_state = get_global_stock_state()
    now = time.time()
    if now - global_state.get("last_update", 0) > 0.5:
        new_prices = {}
        for code, data in STOCKS_DATA.items():
            prev = global_state["prices"].get(code, data["base"])
            direction = random.choice([-1, 1])
            new_prices[code] = max(1, int(prev * (1 + (direction * random.uniform(0.01, 0.08)))))
        global_state["prices"] = new_prices
        global_state["last_update"] = now
        hist = new_prices.copy()
        hist["_time"] = datetime.now().strftime("%H:%M:%S")
        global_state["history"].append(hist)
        if len(global_state["history"]) > 60: global_state["history"].pop(0)
        save_global_stock_state(global_state)
    st.session_state.stock_prices = global_state["prices"]
    st.session_state.stock_history = pd.DataFrame(global_state["history"])

def render_k_line(symbol):
    if "stock_history" not in st.session_state or st.session_state.stock_history.empty:
        st.write("NO DATA...")
        return
    df = st.session_state.stock_history.copy()
    if symbol not in df.columns: return
    st.line_chart(df[symbol])

# --- 各個頁面函式 ---
def page_dashboard(uid, user):
    st.title(f"🏙️ 儀表板: {user['name']}")
    update_stock_market()
    stock_val = sum([amt * st.session_state.stock_prices.get(c, 0) for c, amt in user.get('stocks',{}).items()])
    c1, c2, c3 = st.columns(3)
    c1.metric("總資產", f"${user['money'] + stock_val:,}")
    c2.metric("現金", f"${user['money']:,}")
    c3.metric("持股", f"${stock_val:,}")

def page_stock(uid, user):
    st.title("📉 交易所")
    update_stock_market()
    prices = st.session_state.stock_prices
    sel = st.selectbox("選擇股票", list(STOCKS_DATA.keys()))
    curr = prices.get(sel, 0)
    st.metric(f"{sel} 現價", f"${curr}")
    render_k_line(sel)
    
    c1, c2 = st.columns(2)
    with c1:
        q = st.number_input("數量", 1, 1000, 10)
    with c2:
        if st.button("買進"):
            cost = curr * q
            if user['money'] >= cost:
                user['money'] -= cost
                user.setdefault('stocks', {})[sel] = user['stocks'].get(sel, 0) + q
                save_user(uid, user)
                st.success("交易成功")
                st.rerun()
            else:
                st.error("資金不足")

def page_mining(uid, user):
    st.title("⛏️ 數據礦場")
    if st.button("挖掘加密數據"):
        gain = random.randint(10, 100)
        user['money'] += gain
        save_user(uid, user)
        st.success(f"挖到了 ${gain}")
        time.sleep(1)
        st.rerun()

def page_shop(uid, user):
    st.title("🛒 黑市")
    for k, v in ITEMS.items():
        c1, c2 = st.columns([3, 1])
        c1.write(f"**{k}** (${v['price']}) - {v['desc']}")
        if c2.button(f"購買 {k}"):
            if user['money'] >= v['price']:
                user['money'] -= v['price']
                user.setdefault('inventory', {})[k] = user['inventory'].get(k, 0) + 1
                save_user(uid, user)
                st.success("已購買")
                st.rerun()
            else:
                st.error("沒錢滾")

def page_linux(uid, user):
    st.title("🐧 Terminal")
    st.code(f"{uid}@sys:~ $", "bash")
    c = st.text_input("Command")
    if st.button("Exec"):
        if c == "ls": st.write("flag.txt")
        elif c == "whoami": st.write(uid)
        else: st.error("Permission Denied")

def page_lab(uid, user):
    st.title("🔌 邏輯閘實驗室")
    g = st.selectbox("Gate Type", list(SVG_LIB.keys()))
    st.markdown(SVG_LIB[g], unsafe_allow_html=True)

# --- 主程式進入點 ---
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # 登入介面
    if not st.session_state.logged_in:
        st.title("CITY_OS // LOGIN")
        st.caption("Default Admin: frank / x")
        
        tab1, tab2 = st.tabs(["登入", "註冊"])
        with tab1:
            u = st.text_input("ID", key="l_u")
            p = st.text_input("PW", type="password", key="l_p")
            if st.button("連線"):
                user_data = get_user(u)
                if user_data and user_data['password'] == p:
                    st.session_state.logged_in = True
                    st.session_state.uid = u
                    st.success("ACCESS GRANTED")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("ACCESS DENIED")
        with tab2:
            nu = st.text_input("新ID", key="r_u")
            np = st.text_input("新PW", type="password", key="r_p")
            nn = st.text_input("暱稱", key="r_n")
            if st.button("建立身份"):
                if create_user(nu, np, nn):
                    st.success("身份建立完成，請登入")
                else:
                    st.error("ID 已被使用")
        return

    # 登入後的主介面
    uid = st.session_state.uid
    user = get_user(uid)
    
    if not user: # 防止登入後帳號被刪除造成的錯誤
        st.session_state.logged_in = False
        st.rerun()

    with st.sidebar:
        st.title(f"👤 {user['name']}")
        st.metric("Money", f"${user['money']}")
        nav = st.radio("導航", ["儀表板", "交易所", "礦場", "黑市", "終端機", "實驗室"])
        if st.button("登出"):
            st.session_state.logged_in = False
            st.rerun()

    if nav == "儀表板": page_dashboard(uid, user)
    elif nav == "交易所": page_stock(uid, user)
    elif nav == "礦場": page_mining(uid, user)
    elif nav == "黑市": page_shop(uid, user)
    elif nav == "終端機": page_linux(uid, user)
    elif nav == "實驗室": page_lab(uid, user)

# --- 重要：程式執行開關 ---
if __name__ == "__main__":
    main()
