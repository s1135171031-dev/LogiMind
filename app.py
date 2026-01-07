# app.py
import streamlit as st
import random
import time
import pandas as pd
import base64
import hashlib
import plotly.graph_objects as go
from datetime import datetime
from config import ITEMS, STOCKS_DATA, SVG_LIB, LEVEL_TITLES

# 🔥 修正引用語法，避免 SyntaxError
from database import init_db, get_user, save_user, create_user, get_global_stock_state, save_global_stock_state, rebuild_market, check_mission, send_mail, get_all_users, apply_environmental_hazard, add_exp

st.set_page_config(page_title="CityOS Edu-Core", layout="wide", page_icon="☣️")
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00ff41; font-family: monospace; }
    div.stButton > button { background-color: #000; border: 1px solid #00ff41; color: #00ff41; }
    div.stButton > button:hover { background-color: #00ff41; color: #000; }
    .js-plotly-plot .plotly .main-svg { background: rgba(0,0,0,0) !important; }
    .stProgress > div > div > div > div { background-color: #ff3333; }
    code { color: #e6db74; }
</style>
""", unsafe_allow_html=True)

init_db()

# --- 輔助函數 ---
def update_stock_market():
    global_state = get_global_stock_state()
    if not global_state: return
    now = time.time()
    if now - global_state.get("last_update", 0) > 0.5:
        new_prices = {}
        for code, data in STOCKS_DATA.items():
            prev = global_state["prices"].get(code, data["base"])
            direction = random.choice([-1, 1])
            change_pct = random.uniform(0.05, 0.2)
            jitter = random.randint(2, 10) * direction
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

def render_k_line(symbol):
    if "stock_history" not in st.session_state or st.session_state.stock_history.empty:
        st.write("等待市場數據..."); return
    df = st.session_state.stock_history.copy()
    if symbol not in df.columns: return
    df['Close'] = df[symbol]
    df['Open'] = df[symbol].shift(1).fillna(df[symbol])
    import numpy as np
    df['High'] = df[['Open', 'Close']].max(axis=1) + np.random.randint(0, 3, len(df))
    df['Low'] = df[['Open', 'Close']].min(axis=1) - np.random.randint(0, 3, len(df))
    fig = go.Figure(data=[go.Candlestick(x=df['_time'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], increasing_line_color='#00ff41', decreasing_line_color='#ff3333')])
    fig.update_layout(title=f"{symbol} K-Line", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#00ff41'), xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=30, b=0), height=350)
    st.plotly_chart(fig, use_container_width=True)

# --- 功能模組 ---

def page_dashboard(uid, user):
    st.title(f"🏙️ 儀表板: {user['name']}")
    update_stock_market()
    stock_val = sum([amt * st.session_state.stock_prices.get(c, 0) for c, amt in user.get('stocks',{}).items()])
    total = user['money'] + stock_val
    c1, c2, c3 = st.columns(3)
    c1.metric("總身價", f"${total:,}")
    c2.metric("現金", f"${user['money']:,}")
    c3.metric("持股", f"${stock_val:,}")
    if "stock_history" in st.session_state and not st.session_state.stock_history.empty:
        st.subheader("市場總覽")
        df = st.session_state.stock_history.drop(columns=["_time"], errors="ignore")
        st.line_chart(df, height=200)

def page_stock(uid, user):
    st.title("📉 交易所"); auto = st.toggle("⚡ 自動刷新", value=True); update_stock_market(); prices = st.session_state.stock_prices
    cols = st.columns(len(STOCKS_DATA)); 
    for i, (k, v) in enumerate(prices.items()): cols[i].metric(k, f"${v}")
    c1, c2 = st.columns([2, 1])
    with c2:
        st.subheader("交易面板"); selected_stock = st.selectbox("標的", list(STOCKS_DATA.keys()))
        current_price = prices.get(selected_stock, 0); st.metric(f"現價: {selected_stock}", f"${current_price}")
        t1, t2 = st.tabs(["買", "賣"])
        with t1:
            qty = st.number_input("股數", 1, 1000, 10, key="bq"); cost = current_price * qty
            if st.button(f"買進 (-${cost})"): 
                if user['money']>=cost: 
                    user['money']-=cost; user.setdefault('stocks',{})[selected_stock]=user['stocks'].get(selected_stock,0)+qty
                    save_user(uid,user); st.success("OK"); st.rerun()
                else: st.error("資金不足")
        with t2:
            own = user.get('stocks',{}).get(selected_stock,0); st.write(f"持有: {own}"); sqty = st.number_input("股數", 1, max(1,own), 1, key="sq")
            income = current_price * sqty
            if st.button(f"賣出 (+${income})"):
                if own>=sqty: user['money']+=income; user['stocks'][selected_stock]-=sqty; save_user(uid,user); st.success("OK"); st.rerun()
    with c1: render_k_line(selected_stock)
    if auto: time.sleep(1); st.rerun()

def page_lab(uid, user):
    st.title("🔌 邏輯電路 (Logic Gates)")
    st.caption("硬體教育：學習 AND/OR/NOT 邏輯閘運作原理。")
    col_i1, col_i2 = st.columns(2)
    with col_i1: in_A = st.toggle("Input A", True)
    with col_i2: in_B = st.toggle("Input B", False)
    st.markdown("---")
    gate = st.selectbox("選擇邏輯閘", list(SVG_LIB.keys()))
    res = False
    if gate == "AND": res = in_A and in_B
    elif gate == "OR": res = in_A or in_B
    elif gate == "XOR": res = in_A != in_B
    elif gate == "NOT": res = not in_A
    elif gate == "NAND": res = not (in_A and in_B)
    elif gate == "NOR": res = not (in_A or in_B)
    st.markdown(SVG_LIB[gate], unsafe_allow_html=True)
    st.info(f"Output: {int(res)}")
    if st.button("提交測試"): 
        leveled, _ = add_exp(uid, 10); st.toast("測試成功 (+10 XP)")
        if leveled: st.balloons()

# 🔐 雙向密碼學模組
def page_crypto(uid, user):
    st.title("🔐 密碼學終端機 (Crypto)")
    st.caption("雙向轉換：加密與解密工具箱。")
    tab1, tab2, tab3 = st.tabs(["🏛️ 凱撒密碼", "📦 Base64", "🧩 每日挑戰"])

    with tab1:
        st.info("Shift Cipher: 將字母依照位移量搬移。")
        shift = st.slider("位移量 (Key)", 1, 25, 3)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🔒 加密")
            pt = st.text_area("明文", "ATTACK", height=70)
            if pt:
                et = "".join([chr((ord(c)-65+shift)%26+65) if c.isupper() else chr((ord(c)-97+shift)%26+97) if c.islower() else c for c in pt])
                st.code(et)
        with c2:
            st.markdown("### 🔓 解密")
            ct = st.text_area("密文", "", height=70)
            if ct:
                dt = "".join([chr((ord(c)-65-shift)%26+65) if c.isupper() else chr((ord(c)-97-shift)%26+97) if c.islower() else c for c in ct])
                st.success(dt)

    with tab2:
        st.info("Base64: 二進位轉文字編碼。")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### ➡️ 編碼")
            txt = st.text_input("輸入文字", "Hello")
            if txt: st.code(base64.b64encode(txt.encode()).decode())
        with c2:
            st.markdown("### ⬅️ 解碼")
            b64 = st.text_input("輸入Base64", "")
            if b64:
                try: st.success(base64.b64decode(b64).decode())
                except: st.error("無效格式")

    with tab3:
        if "caesar_ans" not in st.session_state:
            w = random.choice(["LINUX", "CODE", "JAVA", "RUBY"]); s = random.randint(1,5)
            st.session_state.caesar_target = w; st.session_state.caesar_shift = s
            st.session_state.caesar_q = "".join([chr(ord(c)+s) for c in w])
        st.write(f"攔截訊息: **{st.session_state.caesar_q}** (Shift: {st.session_state.caesar_shift})")
        ans = st.text_input("答案 (大寫)", key="cg_in")
        if st.button("驗證"):
            if ans == st.session_state.caesar_target:
                add_exp(uid, 20); del st.session_state["caesar_ans"]; st.success("✅ 成功!"); st.rerun()
            else: st.error("❌ 錯誤")

# 🛡️ 雜湊實驗室
def page_hashing(uid, user):
    st.title("🛡️ 雜湊實驗室 (Hash)")
    st.caption("單向函數演示：為什麼密碼不能雙向還原？")
    col1, col2 = st.columns(2)
    with col1:
        pwd = st.text_input("輸入任意文字", "password123")
    with col2:
        sha = hashlib.sha256(pwd.encode()).hexdigest()
        st.markdown("**SHA-256 (單向指紋):**"); st.code(sha)
    
    st.markdown("---")
    check = st.text_input("嘗試撞庫 (猜密碼):")
    if check:
        if hashlib.sha256(check.encode()).hexdigest() == sha: st.success("✅ 匹配成功")
        else: st.error("❌ 指紋不符")

def page_binary(uid, user):
    st.title("🔢 進制駭客")
    if "bin_target" not in st.session_state: st.session_state.bin_target = random.randint(1, 64)
    target = st.session_state.bin_target
    mode = st.radio("模式", ["二進位 (Binary)", "十六進位 (Hex)"])
    st.metric("目標 (十進位)", target)
    ans = st.text_input("輸入答案")
    if st.button("提交"):
        correct = bin(target)[2:] if "Binary" in mode else hex(target)[2:].upper()
        if ans.lower() == correct.lower():
            add_exp(uid, 15); st.session_state.bin_target = random.randint(1, 100); st.success("✅ 正確!"); st.rerun()
        else: st.error(f"❌ 錯誤，答案是 {correct}")

def page_linux(uid, user):
    st.title("🐧 Linux Terminal")
    st.caption("指令：ls, cd, cat, pwd")
    if "fs" not in st.session_state:
        st.session_state.fs = {"pwd": "/home/user", "files": {"/home/user": ["flag.txt"], "/": ["home", "var"]}, "data": {"flag.txt": "CTF{LINUX_OP}"}}
    st.code(f"{uid}@cityos:{st.session_state.fs['pwd']}$", language="bash")
    cmd = st.text_input("Command", key="lin_cmd")
    if st.button("Run"):
        args = cmd.split(); pwd = st.session_state.fs['pwd']
        if not args: return
        if args[0]=="ls": st.write(st.session_state.fs['files'].get(pwd, []))
        elif args[0]=="pwd": st.info(pwd)
        elif args[0]=="cat" and len(args)>1: st.code(st.session_state.fs['data'].get(args[1], "No such file"))
        elif args[0]=="cd" and len(args)>1: st.session_state.fs['pwd'] = args[1] # 簡化版

def page_debug(uid, user):
    st.title("🐍 Python Debugger")
    q = {"q": "print('Hello", "a": "print('Hello')", "hint": "缺少右括號"}
    st.code(q["q"], language="python"); st.info(q["hint"])
    ans = st.text_input("修正程式碼")
    if st.button("Fix"):
        if ans.replace(" ","") == q["a"].replace(" ",""): add_exp(uid, 20); st.success("✅ Fixed!"); st.rerun()
        else: st.error("Still broken")

def page_shop(uid, user):
    st.title("🛒 黑市"); t1, t2 = st.tabs(["買", "背包"])
    with t1:
        for k, v in ITEMS.items():
            if st.button(f"買 {k} (${v['price']})"):
                if user['money'] >= v['price']:
                    user['money'] -= v['price']; user.setdefault('inventory', {})[k] = user['inventory'].get(k, 0) + 1; save_user(uid, user); st.success(f"已購買 {k}"); st.rerun()
                else: st.error("沒錢")
    with t2:
        st.write(user.get('inventory', {}))
        if user.get("inventory", {}).get("Anti-Rad Pill", 0) > 0:
            if st.button("💊 服用輻射藥丸"):
                user["inventory"]["Anti-Rad Pill"] -= 1; user["toxicity"] = max(0, user.get("toxicity",0)-30); save_user(uid, user); st.rerun()

def page_pvp(uid, user):
    st.title("⚔️ PVP"); targets = [u for u in get_all_users() if u!=uid and u!="frank"]
    if not targets: st.write("無人可打"); return
    t = st.selectbox("目標", targets)
    if st.button("駭入攻擊 (需病毒)"):
        if user.get("inventory",{}).get("Trojan Virus",0) > 0:
            user["inventory"]["Trojan Virus"]-=1; vic = get_user(t); loot = 100
            vic["money"] -= loot; user["money"] += loot; save_user(t, vic); save_user(uid, user)
            st.success(f"攻擊成功！搶奪 ${loot}"); st.rerun()
        else: st.error("缺少 Trojan Virus")

# --- 主程式 ---
def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    if not st.session_state.logged_in:
        st.title("CITY_OS // EDU_CORE"); c1,c2=st.tabs(["登入","註冊"]); 
        with c1: 
            u=st.text_input("ID"); p=st.text_input("PW",type="password")
            if st.button("LOGIN"): 
                if get_user(u) and get_user(u)['password']==p: st.session_state.logged_in=True; st.session_state.uid=u; st.rerun()
        with c2:
            nu=st.text_input("NID"); np=st.text_input("NPW",type="password"); nn=st.text_input("Name")
            if st.button("REG"): 
                if create_user(nu,np,nn): st.success("OK"); st.rerun()
        return

    uid = st.session_state.uid; user = get_user(uid)
    
    # 環境災害判定
    if apply_environmental_hazard(uid, user): st.toast("⚠️ 警告：吸入有毒氣體！", icon="☣️")
    if user.get("toxicity", 0) >= 100: st.error("☠️ 毒發身亡... 緊急重生 (-$200)"); user["money"]-=200; user["toxicity"]=50; save_user(uid,user); time.sleep(2); st.rerun()

    with st.sidebar:
        st.title(f"👤 {user['name']}")
        st.caption(f"🆔 {LEVEL_TITLES.get(user['level'], 'Unknown')}")
        st.progress(user['exp'] / (user['level']*100)); st.write(f"Lv.{user['level']} (XP: {user['exp']})")
        st.metric("Credits", f"${user['money']}")
        st.metric("Toxicity", f"{user['toxicity']}%", delta_color="inverse")
        
        nav = st.radio("導航", [
            "儀表板", "交易所", "黑市", "PVP", 
            "--- 教育模組 ---",
            "邏輯電路 (Logic)", "密碼學 (Crypto)", "雜湊實驗室 (Hash)",
            "進制駭客 (Binary)", "Linux 終端機", "Python 除錯室"
        ])
        if st.button("登出"): st.session_state.logged_in=False; st.rerun()

    if nav == "儀表板": page_dashboard(uid, user)
    elif nav == "交易所": page_stock(uid, user)
    elif nav == "黑市": page_shop(uid, user)
    elif nav == "PVP": page_pvp(uid, user)
    elif nav == "邏輯電路 (Logic)": page_lab(uid, user)
    elif nav == "密碼學 (Crypto)": page_crypto(uid, user)
    elif nav == "雜湊實驗室 (Hash)": page_hashing(uid, user)
    elif nav == "進制駭客 (Binary)": page_binary(uid, user)
    elif nav == "Linux 終端機": page_linux(uid, user)
    elif nav == "Python 除錯室": page_debug(uid, user)

if __name__ == "__main__":
    main()
