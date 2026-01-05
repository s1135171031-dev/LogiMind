# ==========================================
# 檔案: app.py (V31.5 Chaos Market & Visual Patch)
# 修復 1: 圖示文字 (keyboard_arrow_right) 重疊問題 -> CSS 範圍縮小
# 修復 2: 股票死魚問題 -> 引入強制擾動機制 (Drift)
# ==========================================
import streamlit as st
import random
import time
import pandas as pd
import numpy as np
import base64
import json

# --- 0. 防呆引用 ---
try:
    from config import CITY_EVENTS, ITEMS, SVG_LIB, MORSE_CODE_DICT, STOCKS_DATA
    from database import (
        load_db, save_db, check_mission, get_today_event, 
        log_intruder, load_quiz_from_file, 
        get_npc_data, send_mail
    )
except ImportError:
    st.error("⚠️ 系統偵測到缺少 config.py 或 database.py，請確認檔案完整性。")
    st.stop()

# --- 1. 頁面設定 ---
st.set_page_config(page_title="CityOS V31.5", layout="wide", page_icon="📟", initial_sidebar_state="expanded")

# --- 2. CSS 最終修復 (針對重疊問題) ---
st.markdown("""
<style>
    /* 1. 背景與基礎 */
    .stApp {
        background-color: #0e1117;
        /* 這裡不設全局字體，避免污染 Icon */
    }

    /* 2. 精準打擊：只改「文字內容」的字體，放過圖示結構 */
    h1, h2, h3, h4, h5, h6, p, li, label, .stMarkdown p, .stMetricValue, .stMetricLabel, input, textarea, button {
        color: #00ff41 !important;
        font-family: 'Courier New', monospace !important;
        text-shadow: 0 0 2px rgba(0, 255, 65, 0.2);
    }

    /* 3. 特殊修復：強制 Streamlit 的 Icon 使用正確字體 */
    /* 解決 keyboard_arrow_right 顯示出來的問題 */
    .st-emotion-cache-1wbqy5l, .e1b2p2ww0, i, .material-icons {
        font-family: "Material Icons" !important; 
        font-style: normal !important;
    }
    
    /* 4. 按鈕樣式 (加強版) */
    .stButton > button {
        background-color: #0e1117 !important;
        color: #00ff41 !important;
        border: 1px solid #00ff41 !important;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background-color: #00ff41 !important;
        color: #000000 !important;
        box-shadow: 0 0 10px #00ff41;
    }

    /* 5. 表單元件可視化 */
    .stTextInput input, .stNumberInput input, .stSelectbox div, .stTextArea textarea {
        background-color: #1a1a1a !important;
        color: #00ff41 !important;
        border: 1px solid #444 !important;
    }
    
    /* 6. 表格與分隔線 */
    hr { border-color: #00ff41 !important; opacity: 0.3; }
    [data-testid="stDataFrame"] { border: 1px solid #00ff41; }
    
</style>
""", unsafe_allow_html=True)

# --- 3. 系統啟動動畫 ---
def play_boot_sequence():
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("<br><br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            st.markdown("### 🟢 SYSTEM REBOOT V31.5")
            st.write("---")
            bar = st.progress(0, text="Booting...")
            logs = st.empty()
            
            steps = [
                ("Loading Font Engine...", 20),
                ("Fixing Render Overlap...", 50),
                ("Injecting Market Volatility...", 80),
                ("System Online.", 100)
            ]
            for txt, p in steps:
                time.sleep(0.15)
                logs.caption(f">> {txt}")
                bar.progress(p)
            time.sleep(0.5)
    placeholder.empty()

# --- 4. 股市更新邏輯 (V31.5 波動增強版) ---
def update_stock_market():
    now = time.time()
    last_update = st.session_state.get("last_stock_update", 0)
    
    # 初始化：如果沒有資料，先生成歷史數據
    if "stock_prices" not in st.session_state:
        current_sim_prices = {k: v["base"] for k, v in STOCKS_DATA.items()}
        history_list = []
        # 預跑 30 次，讓線圖一開始就有東西
        for _ in range(30):
            next_p = {}
            for code, price in current_sim_prices.items():
                # 波動邏輯：百分比 + 強制微小擾動
                volatility = STOCKS_DATA[code]["volatility"] * 2.0  # 放大波動
                change_pct = random.uniform(-volatility, volatility)
                drift = random.randint(-2, 2) # 強制整數擾動 (-2 到 +2)
                
                new_price = int(price * (1 + change_pct)) + drift
                next_p[code] = max(1, new_price) # 價格不能低於 1
            current_sim_prices = next_p
            history_list.append(current_sim_prices)
            
        st.session_state.stock_prices = current_sim_prices
        st.session_state.stock_history = pd.DataFrame(history_list)
        st.session_state.last_stock_update = now

    # 真實時間更新 (每 10 秒更動一次，讓它看起來比較活潑)
    if now - last_update > 10: 
        prices = {}
        history = st.session_state.get("stock_history", pd.DataFrame())
        evt = st.session_state.get("today_event", {})
        
        for code, data in STOCKS_DATA.items():
            prev = st.session_state.get("stock_prices", {}).get(code, data['base'])
            
            # 1. 基礎波動 (放大 1.5 倍)
            volatility = data['volatility'] * 1.5
            change_pct = random.uniform(-volatility, volatility)
            
            # 2. 事件影響
            if evt.get("effect") == "mining_boost" and code == "CYBR": change_pct += 0.08
            if evt.get("effect") == "hack_nerf" and code == "CYBR": change_pct -= 0.08
            if evt.get("effect") == "tech_boom" and code in ["CYBR", "CHIP"]: change_pct += 0.05
            
            # 3. 計算新價格
            new_price = prev * (1 + change_pct)
            
            # 4. 強制擾動 (確保死魚股也會動)
            # 如果價格沒變，強制 +/- 1~3
            if int(new_price) == prev:
                drift = random.choice([-1, 1, -2, 2])
                new_price += drift
            
            prices[code] = max(1, int(new_price))
            
        st.session_state.stock_prices = prices
        
        # 更新歷史紀錄
        new_row = pd.DataFrame([prices])
        history = pd.concat([history, new_row], ignore_index=True)
        # 保持最近 50 筆，讓線圖看起來比較動態
        if len(history) > 50: history = history.iloc[-50:]
        
        st.session_state.stock_history = history
        st.session_state.last_stock_update = now

# --- 5. 各功能頁面 (保持原樣，僅調整 Dashboard 顯示) ---

def page_dashboard(uid, user):
    st.title("🏙️ CityOS Dashboard")
    evt = st.session_state.today_event
    
    # 事件通知區
    c1, c2 = st.columns([1, 5])
    with c1:
        st.markdown(f"<div style='font-size:50px;text-align:center;color:#00ff41'>{'⚠️' if 'nerf' in str(evt.get('effect','')) else '📢'}</div>", unsafe_allow_html=True)
    with c2:
        st.subheader(f"NEWS: {evt['name']}")
        st.caption(f">> {evt['desc']}")
    
    st.markdown("---")
    
    # 執行股市更新
    update_stock_market()
    
    # 資產監控
    stock_val = sum([amt * st.session_state.stock_prices.get(code,0) for code, amt in user.get("stocks",{}).items()])
    total = user['money'] + user.get('bank_deposit', 0) + stock_val
    
    m1, m2, m3 = st.columns(3)
    m1.metric("TOTAL WEALTH", f"${total:,}", delta=None)
    m2.metric("LIQUID CASH", f"${user['money']:,}")
    m3.metric("STOCK VALUE", f"${stock_val:,}")
    
    # 顯示股市走勢圖 (使用 session_state 中的歷史數據)
    st.markdown("### 📈 MARKET TRENDS (LIVE)")
    if not st.session_state.stock_history.empty:
        # 使用 line_chart 顯示，這裡 Streamlit 會自動分配顏色，但我們背景是黑的，看起來會很清楚
        st.line_chart(st.session_state.stock_history, height=250)
    
    # 任務列表
    st.markdown("---")
    st.subheader("🛠️ ACTIVE MISSIONS")
    if user.get("active_missions"):
        for m in user["active_missions"]:
            if isinstance(m, dict):
                st.info(f"[{m['title']}] {m['desc']}")
    else:
        st.caption("No missions active. Check 'Missions' tab.")

def page_mail(uid, user):
    st.title("📧 MAILBOX")
    mailbox = user.get("mailbox", [])
    unread = len([m for m in mailbox if not m.get("read", False)])
    t1, t2 = st.tabs([f"INBOX ({unread})", "COMPOSE"])
    
    with t1:
        if not mailbox: st.caption("No messages.")
        else:
            for i, m in enumerate(mailbox):
                with st.expander(f"{'[NEW] ' if not m.get('read') else ''}{m['title']} (From: {m['from']})"):
                    st.write(m['msg'])
                    if st.button("Mark Read", key=f"r_{i}"):
                        user["mailbox"][i]["read"] = True
                        save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]}); st.rerun()
                    if st.button("Delete", key=f"d_{i}"):
                        user["mailbox"].pop(i)
                        save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]}); st.rerun()
    with t2:
        db = load_db()
        to = st.selectbox("To:", list(db["users"].keys()))
        sub = st.text_input("Subject")
        content = st.text_area("Message")
        if st.button("Send Encrypted Mail"):
            if send_mail(to, uid, sub, content):
                st.success("Sent.")
                check_mission(uid, user, "send_mail", extra_data=to)
            else: st.error("Failed.")

def page_stock_market(uid, user):
    st.title("💹 STOCK EXCHANGE")
    update_stock_market() # 確保進入頁面時更新
    
    prices = st.session_state.stock_prices
    u_stocks = user.get("stocks", {})
    
    # 上方顯示走勢
    st.line_chart(st.session_state.stock_history, height=200)
    
    # 交易區
    c1, c2 = st.columns([1,1])
    
    with c1.container(border=True):
        st.subheader("BUY")
        sel_buy = st.selectbox("Symbol", list(STOCKS_DATA.keys()), key="sb")
        curr_buy = prices.get(sel_buy, 0)
        st.metric("Current Price", f"${curr_buy}")
        
        q_buy = st.number_input("Qty", 1, 1000, 10, key="nb")
        cost = q_buy * curr_buy
        st.write(f"Cost: ${cost}")
        
        if st.button("Confirm Buy"):
            if user['money'] >= cost:
                user['money'] -= cost
                user.setdefault("stocks", {})[sel_buy] = u_stocks.get(sel_buy, 0) + q_buy
                check_mission(uid, user, "stock_buy", extra_data=sel_buy, extra_val=q_buy)
                save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]})
                st.success("Bought."); st.rerun()
            else: st.error("Not enough cash.")
            
    with c2.container(border=True):
        st.subheader("SELL")
        # 只顯示持有的股票
        my_stocks = list(u_stocks.keys())
        if my_stocks:
            sel_sell = st.selectbox("Symbol", my_stocks, key="ss")
            curr_sell = prices.get(sel_sell, 0)
            owned = u_stocks.get(sel_sell, 0)
            st.metric("Holdings", f"{owned} shares")
            
            q_sell = st.number_input("Qty", 1, owned, 1, key="ns")
            earn = q_sell * curr_sell
            st.write(f"Value: ${earn}")
            
            if st.button("Confirm Sell"):
                user['stocks'][sel_sell] -= q_sell
                user['money'] += earn
                if user['stocks'][sel_sell] == 0: del user['stocks'][sel_sell]
                check_mission(uid, user, "stock_sell")
                save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]})
                st.success("Sold."); st.rerun()
        else:
            st.info("You don't own any stocks.")

# 其他頁面功能保持不變，為節省篇幅直接整合
def page_missions(uid, user):
    st.title("🎯 MISSIONS")
    # 領取獎勵
    pending = user.get("pending_claims", [])
    if pending:
        st.success("Rewards Available!")
        for i, m in enumerate(pending):
            rew = m.get("reward", 100) if isinstance(m, dict) else 100
            t = m.get("title", "Mission") if isinstance(m, dict) else "Unknown"
            if st.button(f"Claim ${rew} - {t}", key=f"cl_{i}"):
                user["money"] += rew
                user["pending_claims"].pop(i)
                user.setdefault("completed_missions", []).append(m.get("id") if isinstance(m, dict) else "old")
                save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]})
                check_mission(uid, user, "none"); st.rerun()
    
    st.write("---")
    if not user.get("active_missions"): check_mission(uid, user, "refresh"); st.rerun()
    
    for m in user.get("active_missions", []):
        if isinstance(m, dict):
            with st.container(border=True):
                st.markdown(f"**{m['title']}** (Reward: ${m['reward']})")
                st.caption(m['desc'])

def page_quiz(uid, user):
    st.title("📝 QUIZ")
    if "quiz_state" not in st.session_state: st.session_state.quiz_state = "start"
    
    if st.session_state.quiz_state == "start":
        if st.button("Start Quiz"):
            qs = load_quiz_from_file()
            st.session_state.q_curr = random.choice(qs)
            st.session_state.quiz_state = "answering"
            st.rerun()
    elif st.session_state.quiz_state == "answering":
        q = st.session_state.q_curr
        st.write(f"**{q['q']}**")
        ans = st.radio("Answer:", q['options'])
        if st.button("Submit"):
            if ans == q['ans']:
                st.balloons()
                user["money"] += 10
                check_mission(uid, user, "quiz_done")
                st.success("Correct! +$10")
            else:
                st.error("Wrong.")
            user["last_quiz_date"] = time.strftime("%Y-%m-%d")
            save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]})
            st.session_state.quiz_state = "start"

def page_shop(uid, user):
    st.title("🛒 BLACK MARKET")
    for k, v in ITEMS.items():
        c1, c2 = st.columns([3,1])
        c1.write(f"**{k}** (${v['price']}) - {v['desc']}")
        if c2.button(f"Buy {k}"):
            if user['money'] >= v['price']:
                user['money'] -= v['price']
                user.setdefault("inventory", {})[k] = user.get("inventory", {}).get(k,0)+1
                check_mission(uid, user, "shop_buy", extra_data=k)
                save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]})
                st.success("Bought."); st.rerun()
            else: st.error("No cash.")

def page_cli(uid, user):
    st.title("💻 TERMINAL")
    history = st.session_state.get("cli_history", ["System Ready."])
    for h in history[-5:]: st.code(h)
    
    cmd = st.chat_input("Input command...")
    if cmd:
        history.append(f"> {cmd}")
        check_mission(uid, user, "cli_input", extra_data=cmd)
        if cmd == "help": history.append("Commands: bal, whoami, clear")
        elif cmd == "bal": history.append(f"Cash: ${user['money']}")
        elif cmd == "clear": history = []
        else: history.append("Command not found.")
        
        st.session_state.cli_history = history
        st.rerun()

# --- 6. 主程式進入點 ---
def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    if "today_event" not in st.session_state: st.session_state.today_event = get_today_event()
    
    # 這裡也要呼叫一次，確保後台有在跑
    update_stock_market()

    if not st.session_state.logged_in:
        st.title("🏙️ CityOS V31.5")
        t1, t2 = st.tabs(["LOGIN", "REGISTER"])
        
        with t1:
            u = st.text_input("User ID")
            p = st.text_input("Password", type="password")
            if st.button("Login"):
                db = load_db()
                if u in db["users"] and db["users"][u]["password"] == p:
                    play_boot_sequence()
                    st.session_state.logged_in = True
                    st.session_state.uid = u
                    st.session_state.user = db["users"][u]
                    st.rerun()
                else: st.error("Invalid credentials.")
        
        with t2:
            nu = st.text_input("New ID"); np = st.text_input("New Password", type="password")
            nn = st.text_input("Nickname")
            if st.button("Register"):
                db = load_db()
                if nu not in db["users"]:
                    db["users"][nu] = get_npc_data(nn, "Rookie", 1, 500)
                    db["users"][nu]["password"] = np
                    save_db(db)
                    st.success("Registered.")
                else: st.error("ID Exists.")
        return

    # 登入後邏輯
    uid = st.session_state.uid
    # 重新讀取確保數據最新
    user = load_db()["users"].get(uid, st.session_state.user)

    st.sidebar.title(f"👤 {user['name']}")
    st.sidebar.metric("FUNDS", f"${user['money']}")
    
    menu = {
        "📊 Dashboard": "dash", "💹 Market": "stock", "📧 Mail": "mail",
        "🎯 Missions": "miss", "📝 Quiz": "quiz", "🛒 Shop": "shop",
        "💻 Terminal": "cli"
    }
    
    sel = st.sidebar.radio("Navigation", list(menu.keys()))
    pg = menu[sel]
    
    if pg == "dash": page_dashboard(uid, user)
    elif pg == "stock": page_stock_market(uid, user)
    elif pg == "mail": page_mail(uid, user)
    elif pg == "miss": page_missions(uid, user)
    elif pg == "quiz": page_quiz(uid, user)
    elif pg == "shop": page_shop(uid, user)
    elif pg == "cli": page_cli(uid, user)
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

if __name__ == "__main__":
    main()
