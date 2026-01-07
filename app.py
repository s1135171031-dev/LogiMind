# app.py (完整版，包含重置按鈕)

import streamlit as st
import random
import time
import pandas as pd
from datetime import datetime, date
import os 

try:
    from config import ITEMS, STOCKS_DATA, CITY_EVENTS, SVG_LIB 
    # 🔥 引入新函數 rebuild_market
    from database import (init_db, get_user, save_user, create_user, check_mission, 
                          send_mail, get_all_users, get_global_stock_state, save_global_stock_state, rebuild_market)
except ImportError:
    st.error("⚠️ 檔案遺失！請確保 app.py, config.py, database.py 都在同目錄下。")
    st.stop()

# ... (中間的 load_quiz_from_file, CSS, update_stock_market 等函數保持不變，直接沿用即可) ...
# ... (如果不確定，請使用上一版給你的程式碼，只需改最後 main 的部分) ...

# 為了方便，這裡提供完整的 main 函數，請覆蓋原本的 main

# --- 重複的函數省略，請確保上方有 get_today_event, update_stock_market 等 ---
# (這些函數不用改，直接看下面的 main)

def load_quiz_from_file():
    # ... (保持原樣) ...
    questions = []
    default_q = [{"q": "系統錯誤: 題庫損毀", "options": ["...", "???"], "ans": "..."}]
    file_path = "questions.txt"
    if not os.path.exists(file_path): return default_q
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f: lines = f.readlines()
    except: return default_q
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"): continue
        parts = line.split("|")
        if len(parts) >= 5:
            q_text, options, ans = parts[2].strip(), [o.strip() for o in parts[3].split(",")], parts[4].strip()
            if ans not in options: options.append(ans); random.shuffle(options)
            questions.append({"q": q_text, "options": options, "ans": ans})
    return questions if questions else default_q

st.set_page_config(page_title="CityOS Toxic", layout="wide", page_icon="☣️")
st.markdown("""<style>.stApp { background-color: #050505; color: #00ff41; } 
    .stButton>button { border: 1px solid #00ff41; background: black; color: #00ff41; }
    </style>""", unsafe_allow_html=True)

init_db()

def get_today_event():
    seed = int(date.today().strftime("%Y%m%d"))
    random.seed(seed); evt = random.choice(CITY_EVENTS); random.seed()
    return evt

if "today_event" not in st.session_state: st.session_state.today_event = get_today_event()

def update_stock_market():
    global_state = get_global_stock_state()
    if not global_state: return
    now = time.time()
    if now - global_state.get("last_update", 0) > 1: # 1秒刷新
        evt = st.session_state.today_event
        new_prices = {}
        for code, data in STOCKS_DATA.items():
            prev = global_state["prices"].get(code, data["base"])
            vol = data["volatility"] * 2.0
            change = random.uniform(-vol, vol)
            if evt["effect"] == "crash": change -= 0.1
            new_p = max(5, int(prev * (1 + change)))
            new_prices[code] = new_p
        global_state["prices"] = new_prices
        global_state["last_update"] = now
        hist_entry = new_prices.copy(); hist_entry["_time"] = datetime.now().strftime("%H:%M:%S")
        global_state["history"].append(hist_entry)
        if len(global_state["history"]) > 30: global_state["history"].pop(0)
        save_global_stock_state(global_state)
    st.session_state.stock_prices = global_state["prices"]
    st.session_state.stock_history = pd.DataFrame(global_state["history"])

# 頁面函數 (Dashboard, Stock, etc.) 請保持上一版原樣，這裡不重複貼以免混淆
# ... (省略 page_dashboard, page_stock 等) ...
# 只需要把下面的 main() 替換掉原本的即可

def page_dashboard(uid, user):
    st.title("🏙️ DASHBOARD")
    update_stock_market()
    stock_val = sum([amt * st.session_state.stock_prices.get(c, 0) for c, amt in user.get('stocks',{}).items()])
    st.metric("總資產", f"${user['money'] + stock_val:,}")
    if not st.session_state.stock_history.empty:
        st.line_chart(st.session_state.stock_history.drop(columns=["_time"], errors="ignore"), height=300)

def page_stock(uid, user):
    st.title("💹 股市")
    auto_refresh = st.toggle("自動刷新 (焦慮模式)")
    update_stock_market()
    prices = st.session_state.stock_prices
    
    t1, t2 = st.tabs(["買進", "賣出"])
    with t1:
        code = st.selectbox("股票", list(STOCKS_DATA.keys()))
        curr = prices.get(code, 0)
        st.metric(STOCKS_DATA[code]['name'], f"${curr}")
        qty = st.number_input("數量", 1, 100, 10)
        if st.button("買"):
            if user['money'] >= qty*curr:
                user['money'] -= qty*curr
                user.setdefault('stocks', {})[code] = user['stocks'].get(code, 0) + qty
                save_user(uid, user); st.success("已買入"); st.rerun()
            else: st.error("沒錢")
    with t2:
        if user.get('stocks'):
            s_code = st.selectbox("賣出", list(user['stocks'].keys()))
            curr = prices.get(s_code, 0)
            if st.button("賣"):
                user['money'] += user['stocks'][s_code] * curr
                del user['stocks'][s_code]
                save_user(uid, user); st.success("已賣出"); st.rerun()
                
    if auto_refresh: time.sleep(1); st.rerun()

# --- 主要修正區：main 函數 ---
def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        st.title("Login")
        u = st.text_input("User"); p = st.text_input("Pass", type="password")
        if st.button("Login"):
            user = get_user(u)
            if user and user['password'] == p:
                st.session_state.logged_in = True; st.session_state.uid = u; st.rerun()
            else: st.error("Error")
        return

    uid = st.session_state.uid
    user = get_user(uid)
    
    with st.sidebar:
        st.title(f"👤 {user['name']}")
        st.metric("Cash", f"${user['money']:,}")
        
        # 🔥🔥🔥 Frank 專屬按鈕 🔥🔥🔥
        if user.get("job") == "Gamemaster":
            st.warning("⚠️ 開發者權限")
            if st.button("💥 重置股市 (引發崩盤)", help="強制刪除舊數據，重新生成狂暴歷史"):
                rebuild_market()
                st.toast("股市已重置！快去看看有多慘。")
                time.sleep(1)
                st.rerun()
                
        nav = st.radio("前往", ["儀表板", "股市"]) # 簡化選單，你的版本可能有更多

    if nav == "儀表板": page_dashboard(uid, user)
    elif nav == "股市": page_stock(uid, user)
    # ... 其他頁面保持原樣

if __name__ == "__main__":
    main()
