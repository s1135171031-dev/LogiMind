# ==========================================
# 檔案: app.py
# 用途: 系統核心 (包含瘋狂股市邏輯)
# ==========================================
import streamlit as st
import random
import time
import pandas as pd
from datetime import datetime
import os 

# --- 引用模組 ---
try:
    from config import ITEMS, STOCKS_DATA, CITY_EVENTS, SVG_LIB 
    from database import init_db, get_user, save_user, create_user, check_mission, send_mail
except ImportError:
    st.error("⚠️ 檔案遺失！請確保 app.py, config.py, database.py 都在同目錄下。")
    st.stop()

# --- 讀取題庫函數 ---
def load_quiz_from_file():
    questions = []
    default_q = [{"q": "系統錯誤: 找不到 questions.txt", "options": ["重試", "略過"], "ans": "重試"}]
    
    if not os.path.exists("questions.txt"):
        # 如果檔案不存在，生成一個範例檔案
        with open("questions.txt", "w", encoding="utf-8") as f:
            f.write("Python是什麼?|程式語言,蛇,咖啡|程式語言\n")
            f.write("CityOS的核心是?|數據,金錢,控制|數據\n")
        st.toast("⚠️ 已自動建立範例 questions.txt")
    
    try:
        with open("questions.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or "|" not in line: continue
                
                parts = line.split("|")
                if len(parts) == 3:
                    q_text = parts[0].strip()
                    options = [o.strip() for o in parts[1].split(",")]
                    ans = parts[2].strip()
                    if len(options) >= 2:
                        questions.append({"q": q_text, "options": options, "ans": ans})
        
        if not questions: return default_q
        return questions

    except Exception as e:
        st.error(f"讀取題庫失敗: {e}")
        return default_q

# --- 頁面設定 ---
st.set_page_config(page_title="CityOS V31.9", layout="wide", page_icon="📟", initial_sidebar_state="expanded")

# --- CSS ---
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00ff41; }
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stButton button, input, textarea, .stSelectbox div, .stRadio div {
        font-family: 'Courier New', monospace !important;
        text-shadow: 0 0 2px rgba(0, 255, 65, 0.3);
    }
    [data-testid="stIcon"], .material-icons {
        font-family: 'Material Icons' !important;
    }
    .stButton > button {
        background-color: #000 !important; color: #00ff41 !important;
        border: 1px solid #00ff41 !important;
    }
    .stButton > button:hover { box-shadow: 0 0 15px #00ff41; background-color: #001a05 !important; }
    .stTextInput > div > div > input, .stNumberInput input {
        background-color: #111 !important; color: #00ff41 !important; border: 1px solid #333 !important;
    }
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #00ff41; }
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 系統初始化 ---
init_db()

# --- 股市運算引擎 (🔥超暴力波動版) ---
def update_stock_market():
    now = time.time()
    last_update = st.session_state.get("last_stock_update", 0)
    
    # 初始化
    if "stock_prices" not in st.session_state:
        current_sim_prices = {k: v["base"] for k, v in STOCKS_DATA.items()}
        history_list = []
        for _ in range(30):
            next_p = {}
            for code, price in current_sim_prices.items():
                vol = STOCKS_DATA[code]["volatility"] * 5.0 
                change = random.uniform(-vol, vol)
                next_p[code] = max(10, int(price * (1 + change)))
            current_sim_prices = next_p
            history_list.append(current_sim_prices)
        st.session_state.stock_prices = current_sim_prices
        st.session_state.stock_history = pd.DataFrame(history_list)
        st.session_state.last_stock_update = now

    # 每 5 秒更新一次
    if now - last_update > 5:
        prices = {}
        history = st.session_state.get("stock_history", pd.DataFrame())
        evt = st.session_state.get("today_event", {})
        
        for code, data in STOCKS_DATA.items():
            prev = st.session_state.stock_prices.get(code, data['base'])
            
            # 🔥 波動係數 15.0 (劇烈)
            volatility = data['volatility'] * 15.0 
            
            # 🔥 事件影響力加倍
            if evt.get("effect") == "crash": 
                change_pct = random.uniform(-0.60, -0.20)
            elif evt.get("effect") == "tech_boom" and code in ["CYBR", "ROBO", "AI"]: 
                change_pct = random.uniform(0.30, 0.80)
            elif evt.get("effect") == "whale" and random.random() > 0.5: 
                change_pct = random.uniform(-0.8, 0.8)
            else: 
                change_pct = random.uniform(-volatility, volatility)
            
            new_price = prev * (1 + change_pct)
            
            # 🔥 隨機雜訊 ±50
            random_jump = random.randint(-50, 50)
            new_price += random_jump
            
            if new_price > 2000: new_price -= random.uniform(50, 150) 
            elif new_price < 5: new_price = random.uniform(5, 15)     
            
            prices[code] = max(1, int(new_price))
            
        st.session_state.stock_prices = prices
        new_row = pd.DataFrame([prices])
        history = pd.concat([history, new_row], ignore_index=True)
        if len(history) > 50: history = history.iloc[-50:]
        st.session_state.stock_history = history
        st.session_state.last_stock_update = now

if "today_event" not in st.session_state:
    st.session_state.today_event = random.choice(CITY_EVENTS)

# --- 功能頁面函數 ---

def page_dashboard(uid, user):
    st.title("🏙️ DASHBOARD")
    evt = st.session_state.today_event
    c1, c2 = st.columns([1, 2])
    c1.metric("Status", evt['name'], delta_color="off")
    c2.info(f"News: {evt['desc']}")
    
    update_stock_market()
    
    stocks_val = sum([amt * st.session_state.stock_prices.get(c, 0) for c, amt in user['stocks'].items()])
    total = user['money'] + stocks_val
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Net Worth", f"${total:,}")
    m2.metric("Cash", f"${user['money']:,}")
    m3.metric("Stock Value", f"${stocks_val:,}")
    
    st.subheader("📉 Market Trends (Live)")
    st.line_chart(st.session_state.stock_history, height=300)

def page_stock(uid, user):
    st.title("💹 EXCHANGE")
    update_stock_market()
    prices = st.session_state.stock_prices
    
    t1, t2 = st.tabs(["BUY", "SELL"])
    
    with t1:
        code = st.selectbox("Select Stock", list(STOCKS_DATA.keys()))
        curr = prices[code]
        st.metric(f"{STOCKS_DATA[code]['name']}", f"${curr}")
        qty = st.number_input("Buy Amount", 1, 1000, 10, key="buy_qty")
        cost = qty * curr
        if st.button("BUY NOW"):
            if user['money'] >= cost:
                user['money'] -= cost
                user['stocks'][code] = user['stocks'].get(code, 0) + qty
                check_mission(uid, user, "stock_buy")
                save_user(uid, user)
                st.success("Bought!"); time.sleep(0.5); st.rerun()
            else: st.error("No Money.")
            
    with t2:
        if user['stocks']:
            s_code = st.selectbox("Sell Stock", list(user['stocks'].keys()))
            owned = user['stocks'][s_code]
            st.write(f"Owned: {owned} | Current: ${prices[s_code]}")
            s_qty = st.number_input("Sell Amount", 1, owned, 1, key="sell_qty")
            if st.button("SELL NOW"):
                user['stocks'][s_code] -= s_qty
                user['money'] += s_qty * prices[s_code]
                if user['stocks'][s_code] == 0: del user['stocks'][s_code]
                save_user(uid, user)
                st.success("Sold!"); time.sleep(0.5); st.rerun()
        else: st.info("Empty Portfolio.")

def page_missions(uid, user):
    st.title("🎯 OPS CENTER")
    if user.get("pending_claims"):
        st.success("🎁 Reward Available!")
        for i, m in enumerate(user["pending_claims"]):
            if st.button(f"CLAIM ${m['reward']} - {m['title']}", key=f"c_{i}"):
                user['money'] += m['reward']
                user['pending_claims'].pop(i)
                save_user(uid, user); st.rerun()
    st.markdown("---")
    if not user['active_missions']: check_mission(uid, user, "refresh"); st.rerun()
    for m in user['active_missions']:
        with st.container(border=True):
            st.markdown(f"**{m['title']}** (+${m['reward']})")
            st.caption(m['desc'])

def page_mail(uid, user):
    st.title("📧 ENCRYPTED MAIL")
    tab1, tab2 = st.tabs(["INBOX", "COMPOSE"])
    with tab1:
        if not user["mailbox"]: st.caption("No messages.")
        for msg in user["mailbox"]:
            with st.expander(f"[{msg['time']}] {msg['title']} (From: {msg['from']})"):
                st.write(msg['msg'])
    with tab2:
        all_users = list(st.session_state.db["users"].keys())
        to = st.selectbox("To", all_users)
        sub = st.text_input("Subject")
        body = st.text_area("Message")
        if st.button("SEND"):
            if send_mail(to, uid, sub, body):
                st.success("Sent.")
                check_mission(uid, user, "send_mail")
            else: st.error("User not found.")

def page_shop(uid, user):
    st.title("🛒 BLACK MARKET")
    cols = st.columns(2)
    for i, (k, v) in enumerate(ITEMS.items()):
        with cols[i % 2].container(border=True):
            st.subheader(k)
            st.caption(v['desc'])
            if st.button(f"${v['price']}", key=f"shop_{i}"):
                if user['money'] >= v['price']:
                    user['money'] -= v['price']
                    user.setdefault("inventory", {})[k] = user.get("inventory", {}).get(k, 0) + 1
                    check_mission(uid, user, "shop_buy")
                    save_user(uid, user)
                    st.success(f"Bought {k}"); time.sleep(0.5); st.rerun()
                else: st.error("Insufficient Funds")

def page_cli(uid, user):
    st.title("💻 TERMINAL")
    if "cli_log" not in st.session_state: st.session_state.cli_log = ["System connected..."]
    for l in st.session_state.cli_log[-5:]: st.code(l, language="bash")
    cmd = st.chat_input("root@cityos:~#")
    if cmd:
        st.session_state.cli_log.append(f"# {cmd}")
        check_mission(uid, user, "cli_input")
        resp = "Unknown command."
        if cmd == "help": resp = "bal, whoami, clear, date, ls"
        elif cmd == "bal": resp = f"Cash: ${user['money']}"
        elif cmd == "whoami": resp = f"User: {user['name']}"
        elif cmd == "clear": st.session_state.cli_log = []; st.rerun()
        elif cmd == "ls": resp = "config.sys  user.dat  wallet.key questions.txt"
        elif cmd == "date": resp = datetime.now().strftime("%Y-%m-%d")
        st.session_state.cli_log.append(f"> {resp}")
        st.rerun()

def page_lab(uid, user):
    st.title("🔬 LOGIC LAB")
    gate = st.selectbox("Gate Type", list(SVG_LIB.keys()))
    c1, c2 = st.columns(2)
    i1 = c1.toggle("Input A")
    i2 = c2.toggle("Input B", disabled=(gate=="NOT"))
    
    st.markdown(SVG_LIB.get(gate, "SVG Error"), unsafe_allow_html=True)
    out = False
    if gate == "AND": out = i1 and i2
    elif gate == "OR": out = i1 or i2
    elif gate == "NOT": out = not i1
    st.metric("Output", "HIGH (1)" if out else "LOW (0)")

def page_pvp(uid, user):
    st.title("⚔️ NETRUNNER PVP")
    users = [u for u in st.session_state.db['users'] if u != uid]
    if not users: st.warning("No targets."); return
    target = st.selectbox("Target IP", users)
    
    has_tool = user.get("inventory", {}).get("Brute Force Script", 0) > 0
    st.write(f"Tool Available: {'✅' if has_tool else '❌ (Need Brute Force Script)'}")
    
    if st.button("EXECUTE HACK", disabled=not has_tool):
        user["inventory"]["Brute Force Script"] -= 1
        if user["inventory"]["Brute Force Script"] == 0: del user["inventory"]["Brute Force Script"]
        
        success_rate = 0.4
        if "Zero Day" in st.session_state.today_event['name']: success_rate = 0.7
        
        if random.random() > (1 - success_rate):
            loot = random.randint(50, 300)
            t_user = get_user(target)
            t_user['money'] = max(0, t_user['money'] - loot)
            user['money'] += loot
            save_user(uid, user); save_user(target, t_user)
            st.success(f"Success! Stole ${loot}")
        else:
            st.error("Failed! Trace detected. (-$50)")
            user['money'] -= 50
            save_user(uid, user)
        st.rerun()

def page_quiz(uid, user):
    st.title("📝 KNOWLEDGE BASE")
    
    questions = load_quiz_from_file()
    
    if "q_idx" not in st.session_state or st.session_state.q_idx >= len(questions):
        st.session_state.q_idx = random.randint(0, len(questions)-1)
    
    q = questions[st.session_state.q_idx]
    st.subheader(q['q'])
    
    ans = st.radio("Select Answer:", q['options'], key="quiz_radio")
    
    if st.button("SUBMIT ANSWER"):
        if ans == q['ans']:
            st.balloons()
            user['money'] += 50
            check_mission(uid, user, "quiz_done")
            save_user(uid, user)
            st.success("Correct! +$50")
            time.sleep(1)
            st.session_state.q_idx = random.randint(0, len(questions)-1)
            st.rerun()
        else:
            st.error("Incorrect.")

# --- 主程式進入點 ---
def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    update_stock_market()
    
    if not st.session_state.logged_in:
        st.title("🏙️ CityOS V31.9 Login")
        tab1, tab2 = st.tabs(["LOGIN", "REGISTER"])
        with tab1:
            uid = st.text_input("Username")
            pwd = st.text_input("Password", type="password")
            if st.button("CONNECT"):
                u = get_user(uid)
                if u and u['password'] == pwd:
                    st.session_state.logged_in = True; st.session_state.uid = uid; st.rerun()
                else: st.error("Access Denied")
        with tab2:
            n_uid = st.text_input("New User ID"); n_pwd = st.text_input("New Password", type="password")
            n_name = st.text_input("Display Name")
            if st.button("CREATE IDENTITY"):
                if create_user(n_uid, n_pwd, n_name): st.success("Identity Created.")
                else: st.error("ID Taken")
        return

    uid = st.session_state.uid
    user = get_user(uid)
    with st.sidebar:
        st.title(f"👤 {user['name']}")
        st.metric("CASH", f"${user['money']}")
        menu = st.radio("SYSTEM NAV", ["Dashboard", "Market", "Missions", "Mail", "Shop", "Terminal", "Lab", "PVP", "Quiz"])
        if st.button("LOGOUT"): st.session_state.logged_in = False; st.rerun()

    if menu == "Dashboard": page_dashboard(uid, user)
    elif menu == "Market": page_stock(uid, user)
    elif menu == "Missions": page_missions(uid, user)
    elif menu == "Mail": page_mail(uid, user)
    elif menu == "Terminal": page_cli(uid, user)
    elif menu == "Shop": page_shop(uid, user)
    elif menu == "Lab": page_lab(uid, user)
    elif menu == "PVP": page_pvp(uid, user)
    elif menu == "Quiz": page_quiz(uid, user)

if __name__ == "__main__":
    main()
