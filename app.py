# app.py
# CityOS Ultimate: 全功能整合版 (股市 + 任務 + PVP + 邏輯 + 測驗 + 黑市)

import streamlit as st
import random
import time
import pandas as pd
from datetime import datetime, date
from config import ITEMS, STOCKS_DATA, CITY_EVENTS, SVG_LIB
from database import (init_db, get_user, save_user, create_user, 
                      get_global_stock_state, save_global_stock_state, 
                      rebuild_market, check_mission, send_mail, get_all_users)

st.set_page_config(page_title="CityOS Full", layout="wide", page_icon="☣️")
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00ff41; font-family: monospace; }
    div.stButton > button { background-color: #000; border: 1px solid #00ff41; color: #00ff41; }
    div.stButton > button:hover { background-color: #00ff41; color: #000; }
</style>
""", unsafe_allow_html=True)

init_db()

# --- 題庫 (寫死在代碼裡以免遺失) ---
QUIZ_DB = [
    {"q": "AND 閘：輸入 1, 1 輸出什麼？", "options": ["0", "1"], "ans": "1"},
    {"q": "二進位 1010 是多少？", "options": ["8", "10", "12"], "ans": "10"},
    {"q": "Python 中列表用什麼符號？", "options": ["{}", "[]", "()"], "ans": "[]"},
    {"q": "哪個是強密碼？", "options": ["123456", "password", "X#9v!m2"], "ans": "X#9v!m2"}
]

# --- 核心：綠線風格股市刷新 ---
def update_stock_market():
    global_state = get_global_stock_state()
    if not global_state: return

    now = time.time()
    if now - global_state.get("last_update", 0) > 0.5:
        new_prices = {}
        for code, data in STOCKS_DATA.items():
            prev = global_state["prices"].get(code, data["base"])
            
            # 🔥 綠線演算法
            pct = random.uniform(-0.3, 0.4)
            jitter = random.randint(-40, 40)
            if jitter == 0: jitter = random.choice([-10, 10]) 

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

# --- 各個頁面功能 ---

def page_dashboard(uid, user):
    st.title(f"🏙️ 儀表板: {user['name']}")
    
    update_stock_market() # 背景刷新股市
    
    # 資產計算
    stock_val = sum([amt * st.session_state.stock_prices.get(c, 0) for c, amt in user.get('stocks',{}).items()])
    total = user['money'] + stock_val
    
    c1, c2, c3 = st.columns(3)
    c1.metric("身價", f"${total:,}")
    c2.metric("現金", f"${user['money']:,}")
    c3.metric("股票市值", f"${stock_val:,}")
    
    if "stock_history" in st.session_state and not st.session_state.stock_history.empty:
        chart = st.session_state.stock_history.drop(columns=["_time"], errors="ignore")
        st.line_chart(chart, height=300)
    
    # 郵件通知
    if user.get("mailbox"):
        with st.expander(f"📩 收件匣 ({len(user['mailbox'])})"):
            for mail in user['mailbox'][::-1]:
                st.info(f"[{mail['time']}] {mail['from']}: {mail['title']}\n\n{mail['msg']}")

def page_stock(uid, user):
    st.title("📈 綠線交易所")
    auto = st.toggle("⚡ 自動刷新", value=True)
    update_stock_market()
    
    prices = st.session_state.stock_prices
    cols = st.columns(len(STOCKS_DATA))
    for i, (k, v) in enumerate(prices.items()):
        cols[i].metric(k, f"${v}", delta=random.choice(["▲", "▼"]))
        
    t1, t2 = st.tabs(["買進", "賣出"])
    with t1:
        b_code = st.selectbox("買入代碼", list(STOCKS_DATA.keys()))
        qty = st.number_input("數量", 1, 1000, 10)
        cost = prices.get(b_code, 0) * qty
        if st.button(f"下單 (-${cost})"):
            if user['money'] >= cost:
                user['money'] -= cost
                user.setdefault('stocks', {})[b_code] = user['stocks'].get(b_code, 0) + qty
                check_mission(uid, user, "stock_buy")
                save_user(uid, user)
                st.success("成交")
                st.rerun()
            else: st.error("資金不足")
    with t2:
        if user.get('stocks'):
            s_code = st.selectbox("賣出代碼", list(user['stocks'].keys()))
            own = user['stocks'][s_code]
            st.write(f"持有: {own}")
            s_qty = st.number_input("賣出量", 1, own, own)
            income = prices.get(s_code, 0) * s_qty
            if st.button(f"拋售 (+${income})"):
                user['money'] += income
                user['stocks'][s_code] -= s_qty
                if user['stocks'][s_code] <= 0: del user['stocks'][s_code]
                save_user(uid, user)
                st.success("成交")
                st.rerun()
                
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
                else: st.error("錢不夠")
    st.divider()
    st.write(f"🎒 背包: {user.get('inventory', {})}")

def page_missions(uid, user):
    st.title("🎯 任務中心")
    
    # 領獎
    if user.get("pending_claims"):
        st.success("有完成的任務！")
        for i, m in enumerate(user["pending_claims"]):
            if st.button(f"領取賞金 ${m['reward']} ({m['title']})", key=f"clm_{i}"):
                user['money'] += m['reward']
                user["pending_claims"].pop(i)
                save_user(uid, user)
                st.rerun()
    
    st.subheader("進行中")
    for m in user.get("active_missions", []):
        st.info(f"🔸 {m['title']}: {m['desc']} (賞金 ${m['reward']})")

def page_pvp(uid, user):
    st.title("⚔️ 互害 (PVP)")
    
    # 冷卻檢查
    if time.time() - user.get("last_hack", 0) < 60:
        st.warning(f"冷卻中... 剩餘 {int(60 - (time.time() - user['last_hack']))} 秒")
        return

    targets = [u for u in get_all_users() if u != uid and u != "admin"]
    if not targets:
        st.info("沒人可以攻擊")
        return
        
    target = st.selectbox("選擇受害者", targets)
    has_virus = user.get("inventory", {}).get("Trojan Virus", 0) > 0
    st.write(f"工具: {'✅ 病毒' if has_virus else '❌ 無 (去黑市買)'}")
    
    if st.button("執行攻擊", disabled=not has_virus):
        user["inventory"]["Trojan Virus"] -= 1
        if user["inventory"]["Trojan Virus"] <= 0: del user["inventory"]["Trojan Virus"]
        
        # 判定
        victim = get_user(target)
        if victim.get("inventory", {}).get("Firewall", 0) > 0:
            victim["inventory"]["Firewall"] -= 1
            if victim["inventory"]["Firewall"] <= 0: del victim["inventory"]["Firewall"]
            send_mail(target, "System", "攔截通知", f"{uid} 攻擊你失敗了！消耗了你一個防火牆。")
            st.error("攻擊失敗！對方有防火牆。")
        else:
            loot = random.randint(100, 500)
            loot = min(loot, victim['money'])
            victim['money'] -= loot
            user['money'] += loot
            send_mail(target, "System", "警報", f"你被 {uid} 駭入，損失 ${loot}。")
            st.success(f"攻擊成功！搶奪了 ${loot}")
        
        user["last_hack"] = time.time()
        save_user(target, victim)
        save_user(uid, user)
        st.rerun()

def page_cli(uid, user):
    st.title("💻 終端機 (CLI)")
    cmd = st.text_input(f"{uid}@cityos:~$")
    if cmd:
        check_mission(uid, user, "cli_input")
        if cmd == "help": st.code("Commands: bal, whoami, date, scan")
        elif cmd == "bal": st.code(f"Balance: ${user['money']}")
        elif cmd == "whoami": st.code(f"User: {uid} | Job: {user['job']}")
        elif cmd == "scan": st.code(f"Online: {list(get_all_users().keys())}")
        elif cmd == "date": st.code(str(datetime.now()))
        else: st.code("Unknown command.")

def page_lab(uid, user):
    st.title("🔬 邏輯實驗室")
    gate = st.selectbox("元件", list(SVG_LIB.keys()))
    c1, c2 = st.columns(2)
    i1 = c1.checkbox("Input A (1)")
    i2 = c2.checkbox("Input B (1)", disabled=(gate=="NOT"))
    
    st.markdown(SVG_LIB[gate], unsafe_allow_html=True)
    
    out = False
    if gate == "AND": out = i1 and i2
    elif gate == "OR": out = i1 or i2
    elif gate == "NOT": out = not i1
    elif gate == "XOR": out = i1 != i2
    
    st.metric("Output", "1 (High)" if out else "0 (Low)")

def page_quiz(uid, user):
    st.title("📝 智力測驗")
    if "q_idx" not in st.session_state: st.session_state.q_idx = 0
    
    q = QUIZ_DB[st.session_state.q_idx]
    st.markdown(f"**Q: {q['q']}**")
    
    ans = st.radio("選項", q['options'], key=f"q_{st.session_state.q_idx}")
    if st.button("送出答案"):
        if ans == q['ans']:
            st.balloons()
            st.success("正確！獲得 $50")
            user['money'] += 50
            save_user(uid, user)
        else:
            st.error("錯誤！扣除 $10")
            user['money'] = max(0, user['money'] - 10)
            save_user(uid, user)
        
        st.session_state.q_idx = (st.session_state.q_idx + 1) % len(QUIZ_DB)
        time.sleep(1)
        st.rerun()

# --- 主程式 ---

def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        st.title("CITY_OS // ACCESS")
        c1, c2 = st.tabs(["登入", "註冊"])
        with c1:
            u = st.text_input("ID"); p = st.text_input("Password", type="password")
            if st.button("LOGIN"):
                user = get_user(u)
                if user and user['password'] == p:
                    st.session_state.logged_in = True; st.session_state.uid = u; st.rerun()
                else: st.error("錯誤")
        with c2:
            nu = st.text_input("New ID"); np = st.text_input("New PWD", type="password"); nn = st.text_input("Name")
            if st.button("REGISTER"):
                if create_user(nu, np, nn): st.success("註冊成功"); st.rerun()
                else: st.error("ID 已存在")
        return

    uid = st.session_state.uid; user = get_user(uid)
    
    with st.sidebar:
        st.title(f"👤 {user['name']}")
        st.caption(f"ID: {uid} | ${user['money']:,}")
        
        nav = st.radio("導航", ["儀表板", "交易所", "任務", "黑市", "PVP", "CLI", "邏輯", "測驗"])
        
        st.divider()
        if st.button("登出"): st.session_state.logged_in = False; st.rerun()
        
        if user.get("job") == "Gamemaster":
            if st.button("💥 重置股市"): rebuild_market(); st.rerun()

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
