import streamlit as st
import random
import time
import pandas as pd
import base64
import plotly.graph_objects as go
from datetime import datetime
from config import ITEMS, STOCKS_DATA, SVG_LIB, LEVEL_TITLES
from database import init_db, get_user, save_user, create_user, get_global_stock_state, save_global_stock_state, get_all_users, apply_environmental_hazard, add_exp

# 1. 頁面基礎設定
st.set_page_config(page_title="CityOS: Neon Glitch", layout="wide", page_icon="☣️")

# 2. 基礎駭客風格 CSS
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00ff41; font-family: 'Courier New', monospace; }
    div.stButton > button { background-color: #000; border: 1px solid #00ff41; color: #00ff41; transition: 0.3s; }
    div.stButton > button:hover { background-color: #00ff41; color: #000; box-shadow: 0 0 15px #00ff41; }
    .stTextInput > div > div > input { color: #00ff41; background-color: #111; border-color: #333; }
    code { color: #e6db74; background-color: #222; }
    div[data-baseweb="toast"] { background-color: #111 !important; border: 1px solid #00ff41; }
</style>
""", unsafe_allow_html=True)

init_db()

# --- 🌀 沉浸式特效引擎 (閃爍修正版) ---
def apply_immersion_effects(user):
    styles = []
    inv = user.get("inventory", {})
    
    # 判定觸發條件
    has_shake = inv.get("Stim-Pack", 0) > 0
    has_dizzy = (user.get("toxicity", 0) > 30 or inv.get("Nutri-Paste", 0) > 0)
    has_flash = inv.get("Cyber-Arm", 0) > 0  # 改名為 Flash

    # 1. 定義動畫關鍵影格 (Keyframes)
    styles.append("""
        /* 1. 興奮劑: 物理震動 (Body) */
        @keyframes body-shake {
            0% { transform: translate(0, 0); }
            25% { transform: translate(-2px, 2px); }
            50% { transform: translate(2px, -2px); }
            75% { transform: translate(-2px, -2px); }
            100% { transform: translate(0, 0); }
        }

        /* 2. 營養膏: 迷幻流動 (App Container) */
        @keyframes color-drift {
            0% { filter: hue-rotate(0deg); }
            50% { filter: hue-rotate(180deg) blur(0.5px); }
            100% { filter: hue-rotate(360deg); }
        }

        /* 3. 義肢: 電路閃爍 (Content Layer) - 修正為閃爍效果 */
        @keyframes electric-flash {
            0% { opacity: 1; filter: brightness(1); }
            3% { opacity: 0.8; filter: brightness(1.5) drop-shadow(0 0 5px #00ff41); } /* 瞬間變亮 */
            6% { opacity: 1; filter: brightness(1); }
            20% { opacity: 1; }
            21% { opacity: 0.5; filter: contrast(200%); } /* 瞬間變暗 */
            22% { opacity: 1; filter: contrast(100%); }
            40% { text-shadow: 0 0 0 transparent; }
            41% { text-shadow: 2px 0 red, -2px 0 blue; } /* RGB 分離一瞬間 */
            42% { text-shadow: 0 0 0 transparent; }
            60% { filter: invert(0); }
            61% { filter: invert(1); } /* 負片閃爍 (像雷擊) */
            62% { filter: invert(0); }
            100% { opacity: 1; }
        }
    """)

    # 2. 應用層級分配 (完美疊加)
    
    # 層級 1: Body (震動)
    if has_shake:
        styles.append("""
            body {
                animation: body-shake 0.2s infinite linear !important;
                overflow-x: hidden;
            }
        """)

    # 層級 2: .stApp (背景變色/扭曲)
    if has_dizzy:
        styles.append("""
            .stApp {
                animation: color-drift 8s infinite alternate ease-in-out !important;
            }
        """)

    # 層級 3: section.main (內容閃爍) -> 針對 Cyber-Arm
    if has_flash:
        styles.append("""
            section.main {
                animation: electric-flash 2s infinite steps(10) !important;
            }
            
            /* 加強按鈕的故障感 */
            button {
                animation: electric-flash 0.5s infinite reverse !important;
                border: 1px solid rgba(0, 255, 65, 0.8) !important;
            }
            
            /* 讓圖片偶爾過曝 */
            img {
                 filter: brightness(120%) contrast(120%);
            }
        """)

    if styles:
        css_code = "<style>" + "\n".join(styles) + "</style>"
        st.markdown(css_code, unsafe_allow_html=True)

# --- 輔助邏輯 (股市與K線) ---
def update_stock_market():
    global_state = get_global_stock_state()
    if not global_state: return
    now = time.time()
    if now - global_state.get("last_update", 0) > 0.5:
        new_prices = {}
        for code, data in STOCKS_DATA.items():
            prev = global_state["prices"].get(code, data["base"])
            direction = random.choice([-1, 1])
            change_pct = random.uniform(0.01, 0.1)
            jitter = random.randint(1, 5) * direction
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
    fig.update_layout(title=f"{symbol} 走勢圖", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#00ff41'), xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=30, b=0), height=350)
    st.plotly_chart(fig, use_container_width=True)

# --- 各頁面 ---

def page_dashboard(uid, user):
    st.title(f"🏙️ 儀表板: {user['name']}")
    update_stock_market()
    stock_val = sum([amt * st.session_state.stock_prices.get(c, 0) for c, amt in user.get('stocks',{}).items()])
    total = user['money'] + stock_val
    c1, c2, c3 = st.columns(3)
    c1.metric("總資產", f"${total:,}")
    c2.metric("現金", f"${user['money']:,}")
    c3.metric("股票價值", f"${stock_val:,}")
    if "stock_history" in st.session_state and not st.session_state.stock_history.empty:
        st.subheader("市場指數")
        df = st.session_state.stock_history.drop(columns=["_time"], errors="ignore")
        st.line_chart(df, height=200)

def page_stock(uid, user):
    st.title("📉 交易所")
    auto = st.toggle("⚡ 自動刷新", value=True)
    update_stock_market()
    prices = st.session_state.stock_prices
    cols = st.columns(len(STOCKS_DATA))
    for i, (k, v) in enumerate(prices.items()): cols[i].metric(k, f"${v}")
    c1, c2 = st.columns([2, 1])
    with c2:
        st.subheader("交易操作")
        selected = st.selectbox("標的", list(STOCKS_DATA.keys()))
        curr = prices.get(selected, 0); st.metric(f"現價: {selected}", f"${curr}")
        t1, t2 = st.tabs(["買入", "賣出"])
        with t1:
            q = st.number_input("數量", 1, 1000, 10, key="bq"); cost = curr * q
            if st.button(f"買進 (-${cost})"):
                if user['money']>=cost: user['money']-=cost; user.setdefault('stocks',{})[selected]=user['stocks'].get(selected,0)+q; save_user(uid,user); st.success("OK"); st.rerun()
                else: st.error("沒錢")
        with t2:
            own = user.get('stocks',{}).get(selected,0); st.write(f"持有: {own}")
            sq = st.number_input("數量", 1, max(1,own), 1, key="sq"); inc = curr * sq
            if st.button(f"賣出 (+${inc})"):
                if own>=sq: user['money']+=inc; user['stocks'][selected]-=sq; save_user(uid,user); st.success("OK"); st.rerun()
                else: st.error("不夠賣")
    with c1: render_k_line(selected)
    if auto: time.sleep(1); st.rerun()

def page_shop(uid, user):
    st.title("🛒 地下黑市")
    t1, t2 = st.tabs(["商店", "背包"])
    with t1:
        for k, v in ITEMS.items():
            c1, c2 = st.columns([3, 1])
            c1.markdown(f"**{k}** (${v['price']}) - {v['desc']}")
            if c2.button("購買", key=f"buy_{k}"):
                if user['money']>=v['price']: 
                    user['money']-=v['price']; user.setdefault('inventory',{})[k]=user['inventory'].get(k,0)+1; save_user(uid,user); st.toast(f"已購買 {k}"); st.rerun()
                else: st.error("資金不足")
            st.divider()
    with t2:
        inv = user.get('inventory', {})
        if not inv: st.write("空的")
        for k, v in inv.items():
            if v > 0:
                c1, c2 = st.columns([3, 1])
                c1.write(f"**{k}** x {v}")
                if k == "Anti-Rad Pill":
                    if c2.button("💊 服用"):
                        user["inventory"][k]-=1
                        for bad in ["Nutri-Paste", "Stim-Pack", "Cyber-Arm"]: 
                            if user["inventory"].get(bad,0)>0: user["inventory"][bad]=0
                        user["toxicity"]=0; save_user(uid,user); st.success("解毒完成"); st.rerun()
                elif k in ["Nutri-Paste", "Stim-Pack", "Cyber-Arm"]: c2.caption("⚠️ 已裝備 (特效開啟)")

def page_crypto(uid, user):
    st.title("🔐 密碼學")
    t1, t2, t3 = st.tabs(["凱撒", "Base64", "挑戰"])
    with t1:
        s = st.slider("Key", 1, 25, 3)
        pt = st.text_area("明文", "ATTACK"); st.code("".join([chr((ord(c)-65+s)%26+65) if c.isupper() else c for c in pt]))
    with t2:
        txt = st.text_input("Base64 Encode", "Hello"); st.code(base64.b64encode(txt.encode()).decode())
    with t3:
        if "caesar_ans" not in st.session_state:
            w = random.choice(["LINUX", "JAVA", "PYTHON"]); k = random.randint(1,5)
            st.session_state.caesar_target = w; st.session_state.caesar_shift = k
            st.session_state.caesar_q = "".join([chr(ord(c)+k) for c in w])
        st.write(f"密文: **{st.session_state.caesar_q}**"); ans = st.text_input("答案")
        if st.button("驗證"):
            if ans==st.session_state.caesar_target: add_exp(uid,50); del st.session_state["caesar_ans"]; st.success("Correct!"); st.rerun()
            else: st.error("Wrong")

def page_lab(uid, user):
    st.title("🔌 邏輯閘"); c1, c2 = st.columns(2)
    a = c1.toggle("A", True); b = c2.toggle("B", False); g = st.selectbox("Gate", list(SVG_LIB.keys()))
    st.markdown(SVG_LIB[g], unsafe_allow_html=True)

def page_linux(uid, user):
    st.title("🐧 Terminal"); st.code(f"{uid}@sys:~ $", "bash")
    c = st.text_input("Command"); 
    if st.button("Exec"): st.write("Permission Denied" if c!="ls" and c!="whoami" else "flag.txt" if c=="ls" else uid)

def page_pvp(uid, user):
    st.title("⚔️ PVP")
    ts = [u for u in get_all_users() if u!=uid and u!="frank"]
    if not ts: st.write("無目標"); return
    t = st.selectbox("目標", ts); target = get_user(t)
    if st.button("Hack"):
        if user.get("inventory",{}).get("Trojan Virus",0)>0:
            user["inventory"]["Trojan Virus"]-=1
            if random.random()>0.3: 
                loot=min(100, target['money']); target['money']-=loot; user['money']+=loot; save_user(t,target); save_user(uid,user); st.success(f"搶奪 ${loot}")
            else: st.error("失敗"); save_user(uid,user)
        else: st.error("無病毒")

# --- 主程式 ---
def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    if not st.session_state.logged_in:
        st.title("CITY_OS // LOGIN"); c1, c2 = st.tabs(["登入", "註冊"])
        with c1: 
            u=st.text_input("ID"); p=st.text_input("PW", type="password")
            if st.button("連線"): 
                if get_user(u) and get_user(u)['password']==p: st.session_state.logged_in=True; st.session_state.uid=u; st.rerun()
        with c2:
            nu=st.text_input("新ID"); np=st.text_input("新PW", type="password"); nn=st.text_input("名稱")
            if st.button("建立"): 
                if create_user(nu,np,nn): st.success("OK"); st.rerun()
        return

    uid = st.session_state.uid; user = get_user(uid)
    
    # 🔥 渲染特效
    apply_immersion_effects(user)
    
    # 毒性
    if apply_environmental_hazard(uid, user): st.toast("受到輻射傷害...", icon="☣️")
    if user.get("toxicity",0)>=100: user['money']-=200; user['toxicity']=50; save_user(uid,user); st.error("死亡重置 (-$200)"); time.sleep(2); st.rerun()

    with st.sidebar:
        st.title(f"👤 {user['name']}"); st.caption(f"Lv.{user['level']} {LEVEL_TITLES.get(user['level'],'')}")
        st.progress(user['exp']/(user['level']*100)); st.metric("Money", f"${user['money']}"); st.metric("Tox", f"{user['toxicity']}%")
        nav = st.radio("Menu", ["Dashboard", "Exchange", "Dark Market", "PVP", "Logic Gates", "Crypto", "Linux"])
        if st.button("Logout"): st.session_state.logged_in=False; st.rerun()

    if nav=="Dashboard": page_dashboard(uid, user)
    elif nav=="Exchange": page_stock(uid, user)
    elif nav=="Dark Market": page_shop(uid, user)
    elif nav=="PVP": page_pvp(uid, user)
    elif nav=="Logic Gates": page_lab(uid, user)
    elif nav=="Crypto": page_crypto(uid, user)
    elif nav=="Linux": page_linux(uid, user)

if __name__ == "__main__":
    main()
