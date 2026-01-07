# app.py
import streamlit as st
import random
import time
import pandas as pd
from datetime import datetime
from config import ITEMS, STOCKS_DATA
from database import (init_db, get_user, save_user, create_user, 
                      get_global_stock_state, save_global_stock_state, rebuild_market)

st.set_page_config(page_title="CityOS Chaos", layout="wide", page_icon="⚡")
st.markdown("""<style>.stApp { background-color: #050505; color: #00ff41; font-family: monospace; }</style>""", unsafe_allow_html=True)

init_db()

# 🔥 核心修正：強制暴走邏輯
def update_stock_market():
    global_state = get_global_stock_state()
    if not global_state: return

    # 0.5 秒就更新一次
    now = time.time()
    if now - global_state.get("last_update", 0) > 0.5:
        new_prices = {}
        for code, data in STOCKS_DATA.items():
            prev = global_state["prices"].get(code, data["base"])
            
            # ⚡⚡⚡ 絕對暴力算法 ⚡⚡⚡
            # 1. 基礎波動 (-15% ~ +15%)
            pct = random.uniform(-0.15, 0.15)
            
            # 2. 強制位移 (Force Jitter)：不管原本多少錢，強迫加減 2~10 塊
            # 這能保證就算股價是 10 塊錢，也會變成 12 或 8，而不是死魚般的 10
            jitter = random.randint(-10, 10)
            if jitter == 0: jitter = random.choice([-2, 2]) 

            new_p = int(prev * (1 + pct) + jitter)
            new_p = max(1, new_p) # 到底了
            
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

# --- 頁面 ---

def page_stock_market(uid, user):
    st.title("📈 混亂交易所")
    
    # 🔥 自動刷新開關：打開這個，網頁才會自己動！
    auto_refresh = st.toggle("⚡ 啟用即時連線 (AUTO-REFRESH)", value=True)
    
    update_stock_market()
    
    # 圖表區
    if "stock_history" in st.session_state and not st.session_state.stock_history.empty:
        chart_data = st.session_state.stock_history.drop(columns=["_time"], errors="ignore")
        st.line_chart(chart_data, height=300)
        
    # 報價區
    cols = st.columns(len(STOCKS_DATA))
    prices = st.session_state.stock_prices
    for i, (code, val) in enumerate(prices.items()):
        cols[i].metric(code, f"${val}", delta=random.choice(["↑", "↓", "⚡"]))

    # 交易區 (簡單版)
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        buy_code = st.selectbox("買進", list(STOCKS_DATA.keys()))
        if st.button("BUY (10股)"):
            cost = prices[buy_code] * 10
            if user['money'] >= cost:
                user['money'] -= cost
                user.setdefault('stocks', {})[buy_code] = user['stocks'].get(buy_code, 0) + 10
                save_user(uid, user)
                st.success("成交")
    with c2:
        st.write(f"持有: {user.get('stocks', {})}")
        st.write(f"現金: ${user['money']}")

    # 🔥 強制重跑：這行代碼讓網頁每秒自己按一下 F5
    if auto_refresh:
        time.sleep(1) # 等待 1 秒
        st.rerun()    # 重新執行整個頁面

def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        st.title("CITY_OS LOGIN")
        u = st.text_input("ID"); p = st.text_input("PWD", type="password")
        if st.button("LOGIN"):
            user = get_user(u)
            if user and user['password'] == p:
                st.session_state.logged_in = True; st.session_state.uid = u; st.rerun()
            else: st.error("錯誤")
        if st.button("註冊新公民"):
            create_user(u, p, "Citizen")
        return

    uid = st.session_state.uid; user = get_user(uid)
    
    with st.sidebar:
        st.title(f"User: {user['name']}")
        if st.button("登出"): st.session_state.logged_in = False; st.rerun()
        if st.button("💥 重置股市"): rebuild_market(); st.rerun()

    page_stock_market(uid, user)

if __name__ == "__main__":
    main()
