
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
from database import init_db, get_user, save_user, create_user, get_global_stock_state, save_global_stock_state, rebuild_market, get_all_users, apply_environmental_hazard, add_exp

st.set_page_config(page_title="CityOS Edu-Core", layout="wide", page_icon="☣️")

# CSS: 駭客風格 + 特效基礎
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00ff41; font-family: monospace; }
    div.stButton > button { background-color: #000; border: 1px solid #00ff41; color: #00ff41; }
    div.stButton > button:hover { background-color: #00ff41; color: #000; }
    .js-plotly-plot .plotly .main-svg { background: rgba(0,0,0,0) !important; }
    code { color: #e6db74; }
    /* 讓吐司訊息也黑化 */
    div[data-baseweb="toast"] { background-color: #333 !important; }
</style>
""", unsafe_allow_html=True)

init_db()

# --- 🌀 沉浸式特效引擎 (Immersive Engine) ---
def apply_immersion_effects(user):
    styles = []
    inv = user.get("inventory", {})
    
    # 1. 💉 Stim-Pack 副作用：手抖 (畫面劇烈高頻震動)
    # 只要背包裡有，就會因為「藥物洩漏」導致手抖
    if inv.get("Stim-Pack", 0) > 0:
        styles.append("""
            @keyframes shake {
                0% { transform: translate(1px, 1px) rotate(0deg); }
                10% { transform: translate(-1px, -2px) rotate(-1deg); }
                20% { transform: translate(-3px, 0px) rotate(1deg); }
                30% { transform: translate(3px, 2px) rotate(0deg); }
                40% { transform: translate(1px, -1px) rotate(1deg); }
                50% { transform: translate(-1px, 2px) rotate(-1deg); }
                60% { transform: translate(-3px, 1px) rotate(0deg); }
                70% { transform: translate(3px, 1px) rotate(-1deg); }
                80% { transform: translate(-1px, -1px) rotate(1deg); }
                90% { transform: translate(1px, 2px) rotate(0deg); }
                100% { transform: translate(1px, -2px) rotate(-1deg); }
            }
            .stApp { animation: shake 0.5s infinite; }
        """)

    # 2. 🤢 Nutri-Paste / 毒氣中毒：暈眩 (畫面流體扭曲 + 變色)
    # 持有營養膏 或 中毒指數高
    is_dizzy = user.get("toxicity", 0) > 30 or inv.get("Nutri-Paste", 0) > 0
    if is_dizzy:
        styles.append("""
            @keyframes dizzy {
                0% { filter: hue-rotate(0deg) blur(0px); transform: scale(1); }
                25% { filter: hue-rotate(45deg) blur(1px); transform: scale(1.02) skewX(2deg); }
                50% { filter: hue-rotate(0deg) blur(2px); transform: scale(1) skewY(-2deg); }
                75% { filter: hue-rotate(-45deg) blur(1px); transform: scale(1.02) skewX(-2deg); }
                100% { filter: hue-rotate(0deg) blur(0px); transform: scale(1); }
            }
            .stApp { animation: dizzy 8s infinite ease-in-out; }
            h1, h2, h3, p { text-shadow: 2px 2px 5px #ff00ff; }
        """)

    # 3. 🤖 Cyber-Arm：機械故障 (CRT 掃描線)
    if inv.get("Cyber-Arm", 0) > 0:
        styles.append("""
            .stApp::before {
                content: " "; display: block; position: fixed;
                top: 0; left: 0; bottom: 0; right: 0;
                background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
                z-index: 9999; background-size: 100% 2px, 3px 100%; pointer-events: none;
            }
        """)

    if styles:
        css_code = "<style>" + "\n".join(styles) + "</style>"
        st.markdown(css_code, unsafe_allow_html=True)

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

# --- 頁面模組 ---

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

def page_shop(uid, user):
    st.title("🛒 地下黑市 (Dark Market)")
    st.caption("副作用警告：部分商品可能導致視覺神經失調。")
    t1, t2 = st.tabs(["購買", "背包"])
    
    with t1:
        for k, v in ITEMS.items():
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.markdown(f"**{k}** (${v['price']})")
                st.caption(v['desc'])
            with col_b:
                if st.button(f"購買", key=f"buy_{k}"):
                    if user['money'] >= v['price']:
                        user['money'] -= v['price']
                        user.setdefault('inventory', {})[k] = user['inventory'].get(k, 0) + 1
                        save_user(uid, user)
                        st.toast(f"已購買 {k}！小心副作用...", icon="🛍️")
                        st.rerun()
                    else: st.error("資金不足")
            st.markdown("---")

    with t2:
        st.subheader("背包內容")
        inv = user.get('inventory', {})
        if not inv: st.write("背包是空的。")
        
        for item_name, count in inv.items():
            if count > 0:
                c1, c2 = st.columns([3, 1])
                c1.write(f"📦 **{item_name}** x {count}")
                
                # 特殊道具的使用邏輯
                if item_name == "Anti-Rad Pill":
                    if c2.button("💊 服用 (解毒+清除副作用)", key="use_pill"):
                        user["inventory"]["Anti-Rad Pill"] -= 1
                        user["toxicity"] = 0
                        # 強制清除導致副作用的道具
                        if user["inventory"].get("Nutri-Paste", 0) > 0:
                            user["inventory"]["Nutri-Paste"] -= 1
                            st.toast("已清除體內殘留的營養膏毒素。", icon="🤮")
                        if user["inventory"].get("Stim-Pack", 0) > 0:
                            user["inventory"]["Stim-Pack"] -= 1
                            st.toast("已中和血液中的興奮劑。", icon="💉")
                        save_user(uid, user)
                        st.success("身體狀態已重置！")
                        time.sleep(1)
                        st.rerun()
                elif item_name in ["Nutri-Paste", "Stim-Pack"]:
                    c2.caption("持有即觸發被動效果")

def page_crypto(uid, user):
    st.title("🔐 密碼學終端機")
    tab1, tab2, tab3 = st.tabs(["🏛️ 凱撒密碼", "📦 Base64", "🧩 每日挑戰"])
    with tab1:
        shift = st.slider("Key (Shift)", 1, 25, 3)
        c1, c2 = st.columns(2)
        with c1:
            pt = st.text_area("明文", "ATTACK")
            if pt: st.code("".join([chr((ord(c)-65+shift)%26+65) if c.isupper() else chr((ord(c)-97+shift)%26+97) if c.islower() else c for c in pt]))
        with c2:
            ct = st.text_area("密文", "")
            if ct: st.success("".join([chr((ord(c)-65-shift)%26+65) if c.isupper() else chr((ord(c)-97-shift)%26+97) if c.islower() else c for c in ct]))
    with tab2:
        c1, c2 = st.columns(2)
        with c1: 
            txt = st.text_input("文字->Base64", "Hello")
            if txt: st.code(base64.b64encode(txt.encode()).decode())
        with c2:
            b64 = st.text_input("Base64->文字", "")
            if b64:
                try: st.success(base64.b64decode(b64).decode())
                except: st.error("Invalid")
    with tab3:
        if "caesar_ans" not in st.session_state:
            w = random.choice(["LINUX", "CODE", "JAVA", "RUBY"]); s = random.randint(1,5)
            st.session_state.caesar_target = w; st.session_state.caesar_shift = s
            st.session_state.caesar_q = "".join([chr(ord(c)+s) for c in w])
        st.write(f"攔截訊息: **{st.session_state.caesar_q}** (Key: {st.session_state.caesar_shift})")
        ans = st.text_input("答案 (大寫)", key="cg_in")
        if st.button("驗證"):
            if ans == st.session_state.caesar_target:
                add_exp(uid, 20); del st.session_state["caesar_ans"]; st.success("✅ Success (+20XP)"); st.rerun()
            else: st.error("❌ Fail")

def page_hashing(uid, user):
    st.title("🛡️ 雜湊實驗室")
    c1, c2 = st.columns(2)
    with c1: pwd = st.text_input("明文輸入", "123456")
    with c2: st.markdown("SHA-256:"); st.code(hashlib.sha256(pwd.encode()).hexdigest())

def page_lab(uid, user):
    st.title("🔌 邏輯電路")
    c1, c2 = st.columns(2)
    with c1: a = st.toggle("A", True)
    with c2: b = st.toggle("B", False)
    gate = st.selectbox("Gate", list(SVG_LIB.keys()))
    st.markdown(SVG_LIB[gate], unsafe_allow_html=True)

def page_linux(uid, user):
    st.title("🐧 Linux Terminal")
    st.code(f"{uid}@cityos:~ $", language="bash")
    cmd = st.text_input("Command")
    if st.button("Exec"):
        if cmd == "ls": st.write("flag.txt  secrets  bin")
        elif cmd == "pwd": st.write("/home/runner")
        else: st.write("Permission Denied.")

def page_binary(uid, user):
    st.title("🔢 Binary Hacker")
    t = random.randint(1, 32)
    st.metric("Target", t)
    ans = st.text_input("Binary (e.g. 1010)")
    if st.button("Submit"):
        if ans == bin(t)[2:]: add_exp(uid, 15); st.success("Correct!")
        else: st.error(f"Wrong. Ans: {bin(t)[2:]}")

def page_debug(uid, user):
    st.title("🐍 Python Debug")
    st.code("print('Hello World'", language="python")
    st.info("Error: SyntaxError")
    ans = st.text_input("Fix it:")
    if st.button("Run Fix"):
        if ans.replace(" ","") == "print('HelloWorld')": add_exp(uid, 15); st.success("Fixed!")

def page_pvp(uid, user):
    st.title("⚔️ PVP")
    targets = [u for u in get_all_users() if u!=uid and u!="frank"]
    if not targets: st.write("No targets."); return
    t = st.selectbox("Target", targets)
    if st.button("Hack"):
        if user.get("inventory",{}).get("Trojan Virus",0) > 0:
            user["inventory"]["Trojan Virus"]-=1; vic = get_user(t); loot = 100
            vic["money"] -= loot; user["money"] += loot
            save_user(t, vic); save_user(uid, user)
            st.success(f"Stole ${loot}"); st.rerun()
        else: st.error("Need Virus")

# --- 主程式 ---
def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    if not st.session_state.logged_in:
        st.title("CITY_OS // LOGIN"); c1,c2=st.tabs(["Login","Register"])
        with c1: 
            u=st.text_input("ID"); p=st.text_input("PW",type="password")
            if st.button("ENTER"): 
                if get_user(u) and get_user(u)['password']==p: st.session_state.logged_in=True; st.session_state.uid=u; st.rerun()
        with c2:
            nu=st.text_input("New ID"); np=st.text_input("New PW",type="password"); nn=st.text_input("Name")
            if st.button("JOIN"): 
                if create_user(nu,np,nn): st.success("Created"); st.rerun()
        return

    uid = st.session_state.uid; user = get_user(uid)
    
    # 🔥 啟動特效 (在所有UI渲染前)
    apply_immersion_effects(user)

    if apply_environmental_hazard(uid, user): st.toast("⚠️ 吸入毒氣...", icon="☣️")
    if user.get("toxicity", 0) >= 100: 
        st.error("☠️ 毒發身亡... 重生扣除 $200"); user["money"]-=200; user["toxicity"]=50; save_user(uid,user); time.sleep(2); st.rerun()

    with st.sidebar:
        st.title(f"👤 {user['name']}")
        st.caption(f"🆔 {LEVEL_TITLES.get(user['level'], 'Unknown')}")
        st.progress(user['exp'] / (user['level']*100))
        st.metric("Credits", f"${user['money']}")
        st.metric("Toxicity", f"{user['toxicity']}%", delta_color="inverse")
        nav = st.radio("System", ["Dashboard", "Exchange", "Dark Market", "PVP", "Logic Gates", "Crypto", "Hash Lab", "Binary", "Linux", "Python Debug"])
        if st.button("Logout"): st.session_state.logged_in=False; st.rerun()

    if nav == "Dashboard": page_dashboard(uid, user)
    elif nav == "Exchange": page_stock(uid, user)
    elif nav == "Dark Market": page_shop(uid, user)
    elif nav == "PVP": page_pvp(uid, user)
    elif nav == "Logic Gates": page_lab(uid, user)
    elif nav == "Crypto": page_crypto(uid, user)
    elif nav == "Hash Lab": page_hashing(uid, user)
    elif nav == "Binary": page_binary(uid, user)
    elif nav == "Linux": page_linux(uid, user)
    elif nav == "Python Debug": page_debug(uid, user)

if __name__ == "__main__":
    main()

