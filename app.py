# ==========================================
# 檔案: app.py (V31.3 Stable Matrix)
# 修復: 按鈕文字看不見的問題、文字重疊排版崩壞的問題
# 保留: 所有功能 + 駭客風格配色
# ==========================================
import streamlit as st
import random
import time
import pandas as pd
import numpy as np
import base64
import json
from config import CITY_EVENTS, ITEMS, SVG_LIB, MORSE_CODE_DICT, STOCKS_DATA
from database import (
    load_db, save_db, check_mission, get_today_event, 
    log_intruder, load_quiz_from_file, 
    get_npc_data, send_mail
)

# --- 1. 頁面基礎設定 ---
st.set_page_config(page_title="CityOS V31.3", layout="wide", page_icon="📟", initial_sidebar_state="expanded")

# --- 2. CSS 美化 (修復版) ---
st.markdown("""
<style>
    /* 1. 基礎字體與背景 - 針對內容層級設定，不破壞佈局 div */
    .stApp {
        background-color: #0e1117;
        font-family: 'Courier New', monospace;
    }
    
    /* 2. 強制文字顏色為螢光綠，但排除輸入框內部以免看不見 */
    h1, h2, h3, h4, h5, h6, p, li, span, .stMarkdown, label, .stMetricValue, .stMetricLabel {
        color: #00ff41 !important;
        font-family: 'Courier New', monospace !important;
        text-shadow: 0 0 2px rgba(0, 255, 65, 0.2); /* 微微發光 */
    }

    /* 3. 按鈕修復：預設黑底綠框，懸停變綠底黑字 */
    .stButton > button {
        background-color: #0e1117 !important;
        color: #00ff41 !important;
        border: 1px solid #00ff41 !important;
        border-radius: 4px;
        font-family: 'Courier New', monospace !important;
        font-weight: bold;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #00ff41 !important;
        color: #000000 !important;
        box-shadow: 0 0 10px #00ff41;
    }
    .stButton > button:active {
        color: #000000 !important;
    }

    /* 4. 輸入框修復：確保輸入時文字看得到 */
    .stTextInput > div > div > input, 
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div,
    .stTextArea > div > div > textarea {
        background-color: #1a1a1a !important;
        color: #00ff41 !important;
        border: 1px solid #333 !important;
        font-family: 'Courier New', monospace !important;
    }
    
    /* 5. 側邊欄與分隔線 */
    [data-testid="stSidebar"] {
        background-color: #000000;
        border-right: 1px solid #00ff41;
    }
    hr { border-color: #00ff41 !important; opacity: 0.3; }
    
    /* 6. 表格修復 */
    [data-testid="stDataFrame"] { border: 1px solid #00ff41; }
    
    /* 7. 進度條 */
    .stProgress > div > div > div > div { background-color: #00ff41; }

    /* 8. 修正文字重疊：增加行高 */
    p, .stMarkdown { line-height: 1.6 !important; }

</style>
""", unsafe_allow_html=True)

# --- 3. 系統啟動特效 ---
def play_boot_sequence():
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown("### 🟢 SYSTEM REBOOT")
            st.markdown("---")
            msg_spot = st.empty()
            bar = st.progress(0, text="Initializing...")
            
            steps = [
                ("Fixing CSS Grid...", 20),
                ("Restoring Visual Cortex...", 40),
                ("Decrypting User Data...", 60),
                ("Simulating Market (30 ticks)...", 80),
                ("System Stable.", 100)
            ]
            
            for text, percent in steps:
                time.sleep(random.uniform(0.1, 0.25))
                msg_spot.markdown(f"<p style='color:#00ff41;'>> {text}</p>", unsafe_allow_html=True)
                bar.progress(percent, text=text)
            
            time.sleep(0.5)
    placeholder.empty()

# --- 4. 股市更新邏輯 (含預跑 30 次) ---
def update_stock_market():
    now = time.time()
    last_update = st.session_state.get("last_stock_update", 0)
    
    if "stock_prices" not in st.session_state:
        current_sim_prices = {k: v["base"] for k, v in STOCKS_DATA.items()}
        history_list = []
        for _ in range(30):
            next_p = {}
            for code, price in current_sim_prices.items():
                volatility = STOCKS_DATA[code]["volatility"]
                change = random.uniform(-volatility, volatility)
                next_p[code] = max(1, int(price * (1 + change)))
            current_sim_prices = next_p
            history_list.append(current_sim_prices)
        st.session_state.stock_prices = current_sim_prices
        st.session_state.stock_history = pd.DataFrame(history_list)
        st.session_state.last_stock_update = now

    if now - last_update > 60:
        prices = {}
        history = st.session_state.get("stock_history", pd.DataFrame())
        evt = st.session_state.get("today_event", {})
        
        for code, data in STOCKS_DATA.items():
            prev = st.session_state.get("stock_prices", {}).get(code, data['base'])
            change = random.uniform(-data['volatility'], data['volatility'])
            if evt.get("effect") == "mining_boost" and code == "CYBR": change += 0.08
            if evt.get("effect") == "hack_nerf" and code == "CYBR": change -= 0.08
            if evt.get("effect") == "tech_boom" and code in ["CYBR", "CHIP"]: change += 0.05
            prices[code] = max(1, int(prev * (1 + change)))
            
        st.session_state.stock_prices = prices
        new_row = pd.DataFrame([prices])
        history = pd.concat([history, new_row], ignore_index=True)
        if len(history) > 50: history = history.iloc[-50:]
        st.session_state.stock_history = history
        st.session_state.last_stock_update = now

# --- 5. 各功能頁面 ---

def page_dashboard(uid, user):
    st.title("🏙️ CityOS Dashboard")
    evt = st.session_state.today_event
    
    c1, c2 = st.columns([1, 5])
    with c1:
        st.markdown(f"<div style='font-size:50px;text-align:center;color:#00ff41'>{'📉' if 'nerf' in str(evt.get('effect','')) else '📈'}</div>", unsafe_allow_html=True)
    with c2:
        st.subheader(f"HEADLINE: {evt['name']}")
        st.write(f">> {evt['desc']}")
        if evt['effect']: st.code(f"EFFECT: {evt['effect']}")
    
    update_stock_market()
    
    st.markdown("---")
    st.subheader("📊 ASSETS MONITOR")
    stock_val = sum([amt * st.session_state.stock_prices.get(code,0) for code, amt in user.get("stocks",{}).items()])
    total = user['money'] + user.get('bank_deposit', 0) + stock_val
    
    m1, m2, m3 = st.columns(3)
    m1.metric("NET WORTH", f"${total:,}")
    m2.metric("BANK", f"${user.get('bank_deposit', 0):,}")
    m3.metric("STOCKS", f"${stock_val:,}")
    
    if not st.session_state.stock_history.empty:
        st.line_chart(st.session_state.stock_history, height=200)

    st.markdown("---")
    st.subheader("🎯 ACTIVE CONTRACTS")
    if user.get("active_missions"):
        for m in user["active_missions"]:
            if isinstance(m, dict):
                st.info(f"[{m['title']}] {m['desc']} (Reward: ${m['reward']})")
    else:
        st.caption("No active missions.")

def page_mail(uid, user):
    st.title("📧 ENCRYPTED MAIL")
    mailbox = user.get("mailbox", [])
    unread = len([m for m in mailbox if not m.get("read", False)])
    t1, t2 = st.tabs([f"INBOX ({unread})", "COMPOSE"])
    
    with t1:
        if not mailbox: st.caption("Mailbox empty.")
        else:
            for i, m in enumerate(mailbox):
                st.text(f"{'[NEW]' if not m.get('read') else '[READ]'} {m['title']} (from: {m['from']})")
                with st.expander("DECRYPT MESSAGE"):
                    st.write(m['msg'])
                    if st.button("MARK READ", key=f"r_{i}"):
                        user["mailbox"][i]["read"] = True
                        save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]}); st.rerun()
                    if st.button("DELETE", key=f"d_{i}"):
                        user["mailbox"].pop(i)
                        save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]}); st.rerun()
    with t2:
        db = load_db()
        to = st.selectbox("RECIPIENT", list(db["users"].keys()))
        sub = st.text_input("SUBJECT"); content = st.text_area("CONTENT")
        if st.button("SEND"):
            if send_mail(to, uid, sub, content):
                st.success("Message Sent."); check_mission(uid, user, "send_mail", extra_data=to)
            else: st.error("Delivery Failed.")

def page_stock_market(uid, user):
    st.title("💹 BLACK MARKET EXCHANGE")
    update_stock_market()
    prices = st.session_state.stock_prices
    u_stocks = user.get("stocks", {})
    
    st.line_chart(st.session_state.stock_history)
    
    c1, c2 = st.columns(2)
    sel = st.selectbox("SYMBOL", list(STOCKS_DATA.keys()))
    curr = prices.get(sel, 0)
    owned = u_stocks.get(sel, 0)
    
    st.metric(f"{STOCKS_DATA[sel]['name']}", f"${curr}")
    st.write(f"OWNED: {owned} SHARES")
    
    with c1.container(border=True):
        qb = st.number_input("BUY QTY", 1, 1000, 10)
        if st.button("EXECUTE BUY"):
            cost = qb * curr
            if user['money'] >= cost:
                user['money'] -= cost
                user.setdefault("stocks", {})[sel] = owned + qb
                check_mission(uid, user, "stock_buy", extra_data=sel, extra_val=qb)
                save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]}); st.success("ORDER FILLED"); st.rerun()
            else: st.error("INSUFFICIENT FUNDS")
            
    with c2.container(border=True):
        qs = st.number_input("SELL QTY", 1, max(1, owned), 1)
        if st.button("EXECUTE SELL"):
            if owned >= qs:
                user['stocks'][sel] -= qs
                user['money'] += qs * curr
                if user['stocks'][sel] == 0: del user['stocks'][sel]
                check_mission(uid, user, "stock_sell")
                save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]}); st.success("ORDER FILLED"); st.rerun()
            else: st.error("INSUFFICIENT ASSETS")

def page_missions(uid, user):
    st.title("🎯 OPS CENTER")
    pending = user.get("pending_claims", [])
    if pending:
        st.success(f"🎁 {len(pending)} REWARDS AVAILABLE")
        for i, m in enumerate(pending):
            title = m.get("title", "Unknown") if isinstance(m, dict) else "Achievement"
            reward = m.get("reward", 0) if isinstance(m, dict) else 100
            with st.container(border=True):
                c1, c2 = st.columns([4,1])
                c1.write(f"**{title}** (${reward})")
                if c2.button("CLAIM", key=f"mc_{i}"):
                    user["money"] += reward
                    user["pending_claims"].pop(i)
                    mid = m.get("id","") if isinstance(m, dict) else m
                    user.setdefault("completed_missions", []).append(mid)
                    save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]})
                    check_mission(uid, user, "none"); st.rerun()
    
    st.markdown("---")
    if not user.get("active_missions"):
        check_mission(uid, user, "refresh"); st.rerun()
        
    st.subheader("📋 CURRENT OPERATIONS")
    cols = st.columns(3)
    for i, m in enumerate(user.get("active_missions", [])):
        if isinstance(m, dict):
            with cols[i%3].container(border=True):
                st.info(f"OP-{i+1}")
                st.markdown(f"#### {m['title']}")
                st.write(m['desc'])
                st.metric("BOUNTY", f"${m['reward']}")

def page_quiz(uid, user):
    st.title("📝 KNOWLEDGE CHECK")
    today = time.strftime("%Y-%m-%d")
    if user.get("last_quiz_date") == today:
        st.warning("Daily limit reached.")
        return
    
    if "quiz_state" not in st.session_state: st.session_state.quiz_state = "intro"
    
    if st.session_state.quiz_state == "intro":
        if st.button("INITIATE TEST"):
            qs = load_quiz_from_file()
            st.session_state.q_curr = random.choice(qs)
            st.session_state.quiz_state = "play"
            st.rerun()
    elif st.session_state.quiz_state == "play":
        q = st.session_state.q_curr
        st.write(f"**QUERY: {q['q']}**")
        ans = st.radio("SELECT ANSWER", q['options'])
        if st.button("SUBMIT"):
            if ans == q['ans']:
                st.success("CORRECT. +$10")
                user["money"] += 10
                check_mission(uid, user, "quiz_done")
            else:
                st.error("INCORRECT.")
            user["last_quiz_date"] = today
            save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]})
            del st.session_state.quiz_state
            time.sleep(1); st.rerun()

def page_lab(uid, user):
    st.title("🔬 LOGIC LAB")
    g = st.selectbox("LOGIC GATE", ["AND", "OR", "NOT", "XOR", "NAND"])
    c1, c2 = st.columns(2)
    a = c1.toggle("INPUT A"); b = False
    if g!="NOT": b = c2.toggle("INPUT B")
    
    st.html(f"<div style='width:150px;margin:auto;filter: invert(1) hue-rotate(90deg);'>{SVG_LIB.get(g,'')}</div>")
    res = 0
    if g=="AND": res = 1 if a and b else 0
    elif g=="OR": res = 1 if a or b else 0
    elif g=="NOT": res = 1 if not a else 0
    elif g=="XOR": res = 1 if a!=b else 0
    elif g=="NAND": res = 0 if a and b else 1
    
    st.metric("OUTPUT SIGNAL", res)
    if res==1: check_mission(uid, user, "logic_use")

def page_crypto(uid, user):
    st.title("🔐 CRYPTOGRAPHY")
    m = st.selectbox("ALGORITHM", ["Caesar", "Morse", "Base64"])
    txt = st.text_input("INPUT DATA", "HELLO")
    check_mission(uid, user, "crypto_input", extra_data=txt)
    
    res = ""
    if m=="Caesar":
        s = st.slider("SHIFT KEY", 1, 25, 3)
        res = "".join([chr((ord(c)-65+s)%26+65) if c.isupper() else chr((ord(c)-97+s)%26+97) if c.islower() else c for c in txt])
    elif m=="Morse":
        res = " ".join([MORSE_CODE_DICT.get(c.upper(),c) for c in txt])
    elif m=="Base64":
        try: res = base64.b64encode(txt.encode()).decode()
        except: res = "Error"
    st.code(res)

def page_shop(uid, user):
    st.title("🛒 DARK WEB STORE")
    disc = 0.7 if st.session_state.today_event['effect']=="shop_discount" else 1.0
    for k, v in ITEMS.items():
        with st.container(border=True):
            c1, c2 = st.columns([3,1])
            c1.write(f"**{k}**"); c1.caption(v['desc'])
            price = int(v['price']*disc)
            if c2.button(f"BUY ${price}", key=f"b_{k}"):
                if user['money'] >= price:
                    user['money'] -= price
                    user.setdefault("inventory", {})[k] = user.get("inventory", {}).get(k,0)+1
                    check_mission(uid, user, "shop_buy", extra_data=k)
                    save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]})
                    st.success("TRANSACTION COMPLETE"); st.rerun()
                else: st.error("INSUFFICIENT FUNDS")

def page_bank(uid, user):
    st.title("🏦 OFFSHORE BANK")
    st.metric("DEPOSIT", f"${user.get('bank_deposit',0)}")
    amt = st.number_input("AMOUNT", 1, 100000)
    c1, c2 = st.columns(2)
    if c1.button("DEPOSIT"):
        if user['money']>=amt:
            user['money']-=amt; user['bank_deposit'] = user.get('bank_deposit',0)+amt
            check_mission(uid, user, "bank_save", extra_val=amt)
            save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]}); st.rerun()
    if c2.button("WITHDRAW"):
        if user.get('bank_deposit',0)>=amt:
            user['bank_deposit']-=amt; user['money']+=amt
            save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]}); st.rerun()

def page_pvp(uid, user):
    st.title("⚔️ NETRUNNER PVP")
    db = load_db()
    targets = [u for u in db["users"] if u != uid and u != "frank"]
    if not targets: st.warning("No reachable targets."); return
    
    tid = st.selectbox("SELECT TARGET", targets)
    t_user = db["users"][tid]
    
    script_cnt = user.get("inventory",{}).get("Brute Force Script", 0)
    st.write(f"SCRIPTS AVAILABLE: {script_cnt}")
    
    if script_cnt <= 0: st.error("SCRIPT REQUIRED."); return
    
    if st.button("🚀 EXECUTE ATTACK"):
        user["inventory"]["Brute Force Script"] -= 1
        if user["inventory"]["Brute Force Script"]==0: del user["inventory"]["Brute Force Script"]
        
        if random.random() < 0.3:
            loot = int(t_user["money"] * 0.1)
            t_user["money"] -= loot
            user["money"] += loot
            check_mission(uid, user, "pvp_win", extra_val=1)
            st.success(f"BREACH SUCCESSFUL. STOLEN: ${loot}")
        else:
            st.error("BREACH FAILED. TRACE DETECTED.")
            log_intruder(uid)
            
        db["users"][uid] = user; db["users"][tid] = t_user
        save_db(db); st.rerun()

def page_cli(uid, user):
    st.title("💻 TERMINAL")
    sarcastic = [
        "SYNTAX ERROR. PEBKAC detected.", "Permission Denied. Nice try.", 
        "404 Brain Not Found.", "I'm calling the cyber-police.", "Go touch grass."
    ]
    
    if "cli_h" not in st.session_state: st.session_state.cli_h = ["Kernel v31.3 loaded..."]
    for l in st.session_state.cli_h[-6:]: st.code(l)
    
    cmd = st.chat_input("user@cityos:~$")
    if cmd:
        st.session_state.cli_h.append(f"$ {cmd}")
        check_mission(uid, user, "cli_input", extra_data=cmd)
        
        if cmd == "help": res = "CMDS: bal, whoami, scan, sudo, clear"
        elif cmd == "bal": res = f"Cash: ${user['money']} (Poor)" if user['money']<100 else f"${user['money']}"
        elif cmd == "whoami": res = f"{user['name']} (Lv.{user['level']})"
        elif cmd == "clear": st.session_state.cli_h=[]; st.rerun()
        elif cmd == "sudo": res = "UID 0 required."
        elif cmd == "sudo su": res = "Achievement Unlocked: 'Keep Dreaming'"; check_mission(uid, user, "cli_input", extra_data="sudo su")
        else:
            res = f"Error: {random.choice(sarcastic)}"
            check_mission(uid, user, "cli_error", extra_val=st.session_state.get("cli_err",0)+1)
        
        st.session_state.cli_h.append(res)
        st.rerun()

def page_leaderboard(uid, user):
    st.title("🏆 HALL OF FAME")
    db = load_db()
    data = []
    prices = st.session_state.get("stock_prices", {})
    for u in db['users'].values():
        val = u['money'] + u.get('bank_deposit',0) + sum([q*prices.get(c,10) for c,q in u.get('stocks',{}).items()])
        data.append({"User":u['name'], "Total":val})
    st.dataframe(pd.DataFrame(data).sort_values("Total", ascending=False))

def page_admin(uid, user):
    st.title("💀 ROOT ACCESS")
    with st.expander("WORLD STATE"):
        evt = st.selectbox("Force Event", [e['name'] for e in CITY_EVENTS])
        if st.button("EXECUTE"):
            for e in CITY_EVENTS:
                if e['name'] == evt: st.session_state.today_event = e; st.rerun()

# --- 6. 主程式 ---
def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    if "today_event" not in st.session_state: st.session_state.today_event = get_today_event()
    update_stock_market()
    
    if not st.session_state.logged_in:
        st.title("🏙️ CityOS V31.3")
        
        with st.expander("💾 DATA MANAGEMENT"):
            c1, c2 = st.columns(2)
            try:
                with open("cityos_users.json", "r", encoding="utf-8") as f:
                    c1.download_button("BACKUP SAVE", f, "save.json")
            except: c1.warning("NO DATA")
            
            up = c2.file_uploader("RESTORE SAVE", type=["json"])
            if up:
                with open("cityos_users.json", "w", encoding="utf-8") as f:
                    json.dump(json.load(up), f, ensure_ascii=False, indent=4)
                st.success("RESTORED"); st.rerun()
        
        t1, t2 = st.tabs(["LOGIN", "REGISTER"])
        with t1:
            u = st.text_input("USER ID"); p = st.text_input("PASSWORD", type="password")
            if st.button("CONNECT"):
                db = load_db()
                if u in db["users"] and db["users"][u]["password"]==p:
                    play_boot_sequence() 
                    st.session_state.logged_in=True; st.session_state.uid=u; st.session_state.user=db["users"][u]
                    st.rerun()
                else: st.error("ACCESS DENIED"); log_intruder(u)
        with t2:
            nu = st.text_input("NEW ID"); np = st.text_input("NEW PW", type="password"); nn = st.text_input("CODENAME")
            if st.button("CREATE ID"):
                if len(np)>4 and nu and nn:
                    db = load_db()
                    if nu not in db["users"]:
                        db["users"][nu] = get_npc_data(nn, "Novice", 1, 500)
                        db["users"][nu]["password"] = np
                        save_db(db); st.success("ID CREATED")
                    else: st.error("ID TAKEN")
        return

    uid = st.session_state.uid
    user = st.session_state.user if uid=="frank" else load_db()["users"].get(uid, st.session_state.user)
    
    st.sidebar.title(f"> {user['name']}")
    st.sidebar.metric("CASH", f"${user['money']}")
    
    menu = {
        "📊 DASHBOARD": "dash", "📧 MAIL": "mail", "💹 MARKET": "stock", 
        "🎯 MISSIONS": "miss", "📝 TEST": "quiz", "🔬 LAB": "lab", 
        "🔐 CRYPTO": "cryp", "🛒 SHOP": "shop", "🏦 BANK": "bank", 
        "⚔️ PVP": "pvp", "💻 CLI": "cli", "🏆 RANK": "rank"
    }
    if uid == "frank": menu["💀 ROOT"] = "admin"
    
    pg = menu[st.sidebar.radio("SYSTEM", list(menu.keys()))]
    
    if pg=="dash": page_dashboard(uid, user)
    elif pg=="mail": page_mail(uid, user)
    elif pg=="stock": page_stock_market(uid, user)
    elif pg=="miss": page_missions(uid, user)
    elif pg=="quiz": page_quiz(uid, user)
    elif pg=="lab": page_lab(uid, user)
    elif pg=="cryp": page_crypto(uid, user)
    elif pg=="shop": page_shop(uid, user)
    elif pg=="bank": page_bank(uid, user)
    elif pg=="pvp": page_pvp(uid, user)
    elif pg=="cli": page_cli(uid, user)
    elif pg=="rank": page_leaderboard(uid, user)
    elif pg=="admin": page_admin(uid, user)
    
    if st.sidebar.button("DISCONNECT"):
        st.session_state.logged_in=False; st.rerun()

if __name__ == "__main__":
    main()
