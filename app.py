# app.py
import streamlit as st
import random
import time
import pandas as pd
import plotly.graph_objects as go # 引入 K 線圖套件
from datetime import datetime
from config import ITEMS, STOCKS_DATA, SVG_LIB
from database import (init_db, get_user, save_user, create_user, 
                      get_global_stock_state, save_global_stock_state, 
                      rebuild_market, check_mission, send_mail, get_all_users)

st.set_page_config(page_title="CityOS Ultimate", layout="wide", page_icon="☣️")
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00ff41; font-family: monospace; }
    div.stButton > button { background-color: #000; border: 1px solid #00ff41; color: #00ff41; }
    div.stButton > button:hover { background-color: #00ff41; color: #000; }
    .js-plotly-plot .plotly .main-svg { background: rgba(0,0,0,0) !important; }
</style>
""", unsafe_allow_html=True)

init_db()

QUIZ_DB = [
    {"q": "AND 閘：輸入 1, 1 輸出？", "options": ["0", "1"], "ans": "1"},
    {"q": "二進位 1010 是？", "options": ["8", "10", "12"], "ans": "10"},
    {"q": "Python 列表符號？", "options": ["{}", "[]", "()"], "ans": "[]"},
    {"q": "最強的密碼？", "options": ["123456", "password", "X#9v!m2"], "ans": "X#9v!m2"}
]

# --- 核心股市邏輯 ---
def update_stock_market():
    global_state = get_global_stock_state()
    if not global_state: return

    now = time.time()
    # 0.5 秒刷新
    if now - global_state.get("last_update", 0) > 0.5:
        new_prices = {}
        for code, data in STOCKS_DATA.items():
            prev = global_state["prices"].get(code, data["base"])
            
            # 🔥 暴動演算法 (Green Line Chaos)
            direction = random.choice([-1, 1])
            change_pct = random.uniform(0.05, 0.2) # 5%~20% 波動
            jitter = random.randint(2, 10) * direction # 強制跳動
            
            new_p = int(prev * (1 + (direction * change_pct))) + jitter
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

# --- K 線圖引擎 ---
def render_k_line(symbol):
    if "stock_history" not in st.session_state or st.session_state.stock_history.empty:
        st.write("等待市場數據...")
        return

    df = st.session_state.stock_history.copy()
    if symbol not in df.columns: return

    # 模擬 OHLC
    df['Close'] = df[symbol]
    df['Open'] = df[symbol].shift(1).fillna(df[symbol])
    import numpy as np
    df['High'] = df[['Open', 'Close']].max(axis=1) + np.random.randint(0, 3, len(df))
    df['Low'] = df[['Open', 'Close']].min(axis=1) - np.random.randint(0, 3, len(df))
    
    fig = go.Figure(data=[go.Candlestick(
        x=df['_time'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        increasing_line_color='#00ff41', decreasing_line_color='#ff3333'
    )])

    fig.update_layout(
        title=f"{symbol} 實時 K 線",
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#00ff41'), xaxis_rangeslider_visible=False,
        margin=dict(l=0, r=0, t=30, b=0), height=350
    )
    st.plotly_chart(fig, use_container_width=True)

# --- 功能頁面 ---

def page_dashboard(uid, user):
    st.title(f"🏙️ 儀表板: {user['name']}")
    update_stock_market()
    
    stock_val = sum([amt * st.session_state.stock_prices.get(c, 0) for c, amt in user.get('stocks',{}).items()])
    total = user['money'] + stock_val
    
    c1, c2, c3 = st.columns(3)
    c1.metric("總身價", f"${total:,}")
    c2.metric("現金", f"${user['money']:,}")
    c3.metric("持股價值", f"${stock_val:,}")
    
    # 總覽只顯示線圖
    if "stock_history" in st.session_state and not st.session_state.stock_history.empty:
        st.subheader("市場總覽")
        df = st.session_state.stock_history.drop(columns=["_time"], errors="ignore")
        st.line_chart(df, height=200)

    if user.get("mailbox"):
        with st.expander(f"📩 訊息 ({len(user['mailbox'])})"):
            for mail in user['mailbox'][::-1]:
                st.info(f"[{mail['time']}] {mail['from']}: {mail['title']} - {mail['msg']}")

def page_stock(uid, user):
    st.title("📉 專業交易所")
    auto = st.toggle("⚡ 自動刷新", value=True)
    update_stock_market()
    
    prices = st.session_state.stock_prices
    cols = st.columns(len(STOCKS_DATA))
    for i, (k, v) in enumerate(prices.items()):
        cols[i].metric(k, f"${v}")

    # 左圖右單
    c1, c2 = st.columns([2, 1])
    with c2:
        st.subheader("交易面板")
        selected_stock = st.selectbox("標的", list(STOCKS_DATA.keys()))
        current_price = prices.get(selected_stock, 0)
        st.metric(f"現價: {selected_stock}", f"${current_price}")
        
        t1, t2 = st.tabs(["買", "賣"])
        with t1:
            qty = st.number_input("股數", 1, 1000, 10, key="buy_q")
            cost = current_price * qty
            if st.button(f"買進 (-${cost})"):
                if user['money'] >= cost:
                    user['money'] -= cost
                    user.setdefault('stocks', {})[selected_stock] = user['stocks'].get(selected_stock, 0) + qty
                    check_mission(uid, user, "stock_buy")
                    save_user(uid, user)
                    st.success("成交")
                    st.rerun()
                else: st.error("沒錢")
        with t2:
            own = user.get('stocks', {}).get(selected_stock, 0)
            st.write(f"持有: {own}")
            sqty = st.number_input("股數", 1, max(1, own), 1, key="sell_q")
            income = current_price * sqty
            if st.button(f"賣出 (+${income})"):
                if own >= sqty:
                    user['money'] += income
                    user['stocks'][selected_stock] -= sqty
                    if user['stocks'][selected_stock] <= 0: del user['stocks'][selected_stock]
                    save_user(uid, user)
                    st.success("成交")
                    st.rerun()
    with c1:
        render_k_line(selected_stock)

    if auto: time.sleep(1); st.rerun()

def page_shop(uid, user):
    st.title("🛒 黑市")
    for k, v in ITEMS.items():
        with st.expander(f"{k} (${v['price']})"):
            st.write(v['desc'])
            if st.button(f"購買 {k}"):
                if user['money'] >= v['price']:
                    user['money'] -= v['price']
                    user.setdefault('inventory', {})[k] = user['inventory'].get(k, 0) + 1
                    check_mission(uid, user, "shop_buy")
                    save_user(uid, user)
                    st.success("購買成功")
                    st.rerun()
                else: st.error("資金不足")
    st.divider()
    st.write(f"🎒 背包: {user.get('inventory', {})}")

def page_missions(uid, user):
    st.title("🎯 任務板")
    if user.get("pending_claims"):
        for i, m in enumerate(user["pending_claims"]):
            if st.button(f"領取 ${m['reward']} ({m['title']})", key=f"clm_{i}"):
                user['money'] += m['reward']
                user["pending_claims"].pop(i)
                save_user(uid, user)
                st.rerun()
    st.subheader("進行中")
    for m in user.get("active_missions", []):
        st.warning(f"🔸 {m['title']}: {m['desc']} (賞金 ${m['reward']})")

def page_pvp(uid, user):
    st.title("⚔️ 互害模式")
    if time.time() - user.get("last_hack", 0) < 30:
        st.info(f"冷卻中... {int(30 - (time.time() - user['last_hack']))}s")
        return

    targets = [u for u in get_all_users() if u != uid and u != "admin"]
    if not targets: st.write("無目標"); return
        
    target = st.selectbox("目標", targets)
    has_virus = user.get("inventory", {}).get("Trojan Virus", 0) > 0
    st.write(f"病毒: {'✅' if has_virus else '❌'}")
    
    if st.button("攻擊", disabled=not has_virus):
        user["inventory"]["Trojan Virus"] -= 1
        if user["inventory"]["Trojan Virus"] <= 0: del user["inventory"]["Trojan Virus"]
        
        victim = get_user(target)
        if victim.get("inventory", {}).get("Firewall", 0) > 0:
            victim["inventory"]["Firewall"] -= 1
            if victim["inventory"]["Firewall"] <= 0: del victim["inventory"]["Firewall"]
            send_mail(target, "System", "防禦", f"{uid} 攻擊失敗。")
            st.error("被防火牆擋下")
        else:
            loot = min(random.randint(50, 150), victim['money'])
            victim['money'] -= loot
            user['money'] += loot
            send_mail(target, "System", "警報", f"被 {uid} 搶走 ${loot}")
            st.success(f"搶奪 ${loot}")
        
        user["last_hack"] = time.time()
        save_user(target, victim)
        save_user(uid, user)
        st.rerun()

def page_cli(uid, user):
    st.title("💻 終端機")
    cmd = st.text_input(f"{uid}@cityos:~$")
    if cmd:
        check_mission(uid, user, "cli_input")
        if cmd == "bal": st.code(f"${user['money']}")
        elif cmd == "date": st.code(str(datetime.now()))
        elif cmd == "help": st.code("bal, date, ls")
        else: st.code("Error")

def page_lab(uid, user):
    st.title("🔬 邏輯閘")
    gate = st.selectbox("元件", list(SVG_LIB.keys()))
    c1, c2 = st.columns(2)
    i1 = c1.checkbox("A")
    i2 = c2.checkbox("B", disabled=(gate=="NOT"))
    st.markdown(SVG_LIB[gate], unsafe_allow_html=True)
    out = False
    if gate == "AND": out = i1 and i2
    elif gate == "OR": out = i1 or i2
    elif gate == "NOT": out = not i1
    elif gate == "XOR": out = i1 != i2
    st.metric("Output", "1" if out else "0")

def page_quiz(uid, user):
    st.title("📝 測驗")
    if "q_idx" not in st.session_state: st.session_state.q_idx = 0
    q = QUIZ_DB[st.session_state.q_idx]
    st.write(f"Q: {q['q']}")
    ans = st.radio("選", q['options'], key=f"q_{st.session_state.q_idx}")
    if st.button("送出"):
        if ans == q['ans']:
            st.success("正確 (+$20)"); user['money'] += 20
        else:
            st.error("錯誤 (-$5)"); user['money'] = max(0, user['money'] - 5)
        save_user(uid, user)
        st.session_state.q_idx = (st.session_state.q_idx + 1) % len(QUIZ_DB)
        time.sleep(0.5); st.rerun()

def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        st.title("CITY_OS // FINAL")
        c1, c2 = st.tabs(["Login", "Reg"])
        with c1:
            u = st.text_input("ID"); p = st.text_input("PWD", type="password")
            if st.button("LOGIN"):
                user = get_user(u)
                if user and user['password'] == p:
                    st.session_state.logged_in = True; st.session_state.uid = u; st.rerun()
                else: st.error("Fail")
        with c2:
            nu = st.text_input("N_ID"); np = st.text_input("N_PWD", type="password"); nn = st.text_input("Name")
            if st.button("REG"):
                if create_user(nu, np, nn): st.success("OK"); st.rerun()
                else: st.error("Used")
        return

    uid = st.session_state.uid; user = get_user(uid)
    
    with st.sidebar:
        st.title(f"{user['name']}")
        st.write(f"💵 ${user['money']}")
        nav = st.radio("MENU", ["儀表板", "交易所", "任務", "黑市", "PVP", "CLI", "邏輯", "測驗"])
        st.divider()
        if st.button("LOGOUT"): st.session_state.logged_in = False; st.rerun()
        if user.get("job") == "Gamemaster":
            if st.button("💥 RESET"): rebuild_market(); st.rerun()

    if nav == "儀表板": page_dashboard(uid, user)
    elif nav == "交易所": page_stock(uid, user)
    elif nav == "任務": page_missions(uid, user)
    elif nav == "黑市": page_shop(uid, user)
    elif nav == "PVP": page_pvp(uid, user)
    elif nav == "CLI": page_cli(uid, user)
    elif nav == "邏輯": page_lab(uid, user)
    elif nav == "測驗": page_quiz(uid, user)

if __name__ == "__main__":
    main()
