# app.py
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
st.set_page_config(page_title="CityOS: GPU Failure Edition", layout="wide", page_icon="☣️")

# 2. 基礎駭客風格 CSS (黑底綠字)
st.markdown("""
<style>
    /* 全域字體與背景 */
    .stApp { background-color: #050505; color: #00ff41; font-family: 'Courier New', monospace; }
    
    /* 按鈕樣式 */
    div.stButton > button { 
        background-color: #000; 
        border: 1px solid #00ff41; 
        color: #00ff41; 
        transition: all 0.1s;
    }
    div.stButton > button:hover { 
        background-color: #00ff41; 
        color: #000; 
        box-shadow: 0 0 10px #00ff41;
    }
    
    /* 輸入框與代碼塊 */
    .stTextInput > div > div > input { color: #00ff41; background-color: #111; border-color: #333; }
    code { color: #e6db74; background-color: #222; }
    
    /* 通知視窗 (Toast) */
    div[data-baseweb="toast"] { background-color: #111 !important; border: 1px solid #00ff41; }
</style>
""", unsafe_allow_html=True)

# 初始化資料庫
init_db()

# --- 🌀 沉浸式特效引擎 (HARDCORE GPU DEATH EDITION) ---
def apply_immersion_effects(user):
    styles = []
    inv = user.get("inventory", {})
    
    # 判定觸發條件
    has_shake = inv.get("Stim-Pack", 0) > 0
    has_dizzy = (user.get("toxicity", 0) > 30 or inv.get("Nutri-Paste", 0) > 0)
    has_glitch = inv.get("Cyber-Arm", 0) > 0

    # 1. 定義動畫關鍵影格 (Keyframes)
    styles.append("""
        /* 1. 興奮劑: 暴力震動 (Shake) - 作用於 Body */
        @keyframes violent-shake {
            0% { transform: translate(0, 0); }
            10% { transform: translate(-3px, -3px); }
            20% { transform: translate(3px, 3px); }
            30% { transform: translate(-3px, 3px); }
            40% { transform: translate(3px, -3px); }
            50% { transform: translate(-2px, 0px); }
            60% { transform: translate(2px, 0px); }
            70% { transform: translate(0px, 2px); }
            80% { transform: translate(0px, -2px); }
            100% { transform: translate(0, 0); }
        }

        /* 2. 營養膏: 迷幻熔化 (Acid Trip) - 作用於 App Container */
        @keyframes acid-trip {
            0% { filter: hue-rotate(0deg); transform: scale(1); }
            50% { filter: hue-rotate(180deg) blur(0.5px); transform: scale(1.01) skewY(1deg); }
            100% { filter: hue-rotate(360deg); transform: scale(1); }
        }

        /* 3. 義肢: 顯卡燒毀 (GPU Death) - 作用於 Content Layer */
        @keyframes gpu-death {
            0% { filter: invert(0) saturate(1); transform: translateX(0); }
            2% { filter: invert(1) saturate(5); transform: translateX(-5px); } /* 瞬間反白閃爍 */
            4% { filter: invert(0) saturate(1); transform: translateX(0); }
            20% { text-shadow: 5px 0 red, -5px 0 blue; transform: skewX(5deg); } /* RGB 分離 */
            22% { text-shadow: 0 0 transparent; transform: skewX(0); }
            40% { filter: contrast(200%); }
            60% { transform: scaleY(0.9) scaleX(1.1); filter: invert(1); } /* 畫面撕裂壓扁 */
            62% { transform: scale(1); filter: invert(0); }
            80% { text-shadow: -3px -3px yellow, 3px 3px cyan; }
            100% { transform: translateX(0); }
        }
    """)

    # 2. 應用層級分配 (確保疊加)
    
    # 層級 1: Body (視窗震動)
    if has_shake:
        styles.append("""
            body {
                animation: violent-shake 0.1s infinite linear !important;
                overflow-x: hidden;
            }
        """)

    # 層級 2: .stApp (容器扭曲/變色)
    if has_dizzy:
        styles.append("""
            .stApp {
                animation: acid-trip 6s infinite alternate ease-in-out !important;
            }
        """)

    # 層級 3: section.main (內容炸裂/破圖)
    if has_glitch:
        styles.append("""
            section.main {
                animation: gpu-death 0.4s infinite steps(4) !important; /* Steps 讓動畫看起來像卡頓 */
                background-color: transparent !important;
            }
            
            /* 圖片嚴重損壞 */
            img {
                filter: contrast(300%) sepia(100%) hue-rotate(90deg) !important;
                opacity: 0.9;
            }
            
            /* 按鈕破圖 */
            button {
                border: 2px solid red !important;
                box-shadow: 3px 3px 0px blue !important;
            }
            
            /* 文字背景偶爾變黑塊 */
            h1, h2, h3, p {
                background-color: rgba(0,0,0,0.3);
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
    # 每 0.5 秒更新一次
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
    # 模擬高低點
    df['High'] = df[['Open', 'Close']].max(axis=1) + np.random.randint(0, 3, len(df))
    df['Low'] = df[['Open', 'Close']].min(axis=1) - np.random.randint(0, 3, len(df))
    
    fig = go.Figure(data=[go.Candlestick(x=df['_time'],
                open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                increasing_line_color='#00ff41', decreasing_line_color='#ff3333')])
    
    fig.update_layout(
        title=f"{symbol} 實時走勢",
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#00ff41'), xaxis_rangeslider_visible=False,
        margin=dict(l=0, r=0, t=30, b=0), height=350
    )
    st.plotly_chart(fig, use_container_width=True)

# --- 各個頁面模組 ---

def page_dashboard(uid, user):
    st.title(f"🏙️ 儀表板: {user['name']}")
    update_stock_market()
    stock_val = sum([amt * st.session_state.stock_prices.get(c, 0) for c, amt in user.get('stocks',{}).items()])
    total = user['money'] + stock_val
    
    c1, c2, c3 = st.columns(3)
    c1.metric("總身價", f"${total:,}")
    c2.metric("現金", f"${user['money']:,}")
    c3.metric("持股價值", f"${stock_val:,}")
    
    if "stock_history" in st.session_state and not st.session_state.stock_history.empty:
        st.subheader("市場指數")
        df = st.session_state.stock_history.drop(columns=["_time"], errors="ignore")
        st.line_chart(df, height=200)

def page_stock(uid, user):
    st.title("📉 混亂交易所")
    auto = st.toggle("⚡ 自動刷新", value=True)
    update_stock_market()
    prices = st.session_state.stock_prices
    
    # 顯示所有股價
    cols = st.columns(len(STOCKS_DATA))
    for i, (k, v) in enumerate(prices.items()):
        cols[i].metric(k, f"${v}")
        
    st.divider()
    
    c1, c2 = st.columns([2, 1])
    with c2:
        st.subheader("交易操作")
        selected_stock = st.selectbox("選擇標的", list(STOCKS_DATA.keys()))
        current_price = prices.get(selected_stock, 0)
        st.metric(f"當前價格: {selected_stock}", f"${current_price}")
        
        t1, t2 = st.tabs(["買入 (BUY)", "賣出 (SELL)"])
        with t1:
            qty = st.number_input("買入數量", 1, 1000, 10, key="bq")
            cost = current_price * qty
            if st.button(f"下單買進 (-${cost})"):
                if user['money'] >= cost:
                    user['money'] -= cost
                    user.setdefault('stocks', {})[selected_stock] = user['stocks'].get(selected_stock, 0) + qty
                    save_user(uid, user)
                    st.success("交易成功")
                    st.rerun()
                else:
                    st.error("資金不足")
        with t2:
            own = user.get('stocks', {}).get(selected_stock, 0)
            st.write(f"目前持有: {own} 股")
            sqty = st.number_input("賣出數量", 1, max(1, own), 1, key="sq")
            income = current_price * sqty
            if st.button(f"下單賣出 (+${income})"):
                if own >= sqty:
                    user['money'] += income
                    user['stocks'][selected_stock] -= sqty
                    save_user(uid, user)
                    st.success("交易成功")
                    st.rerun()
                else:
                    st.error("持股不足")
    
    with c1:
        render_k_line(selected_stock)
        
    if auto:
        time.sleep(1)
        st.rerun()

def page_shop(uid, user):
    st.title("🛒 地下黑市 (Dark Market)")
    t1, t2 = st.tabs(["購買物品", "我的背包"])
    
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
                        st.toast(f"已購買 {k}", icon="🛍️")
                        st.rerun()
                    else:
                        st.error("資金不足")
            st.markdown("---")

    with t2:
        inv = user.get('inventory', {})
        if not inv:
            st.write("背包是空的。")
        else:
            for item_name, count in inv.items():
                if count > 0:
                    c1, c2 = st.columns([3, 1])
                    c1.write(f"**{item_name}** x {count}")
                    
                    # 特殊道具邏輯：解毒丸
                    if item_name == "Anti-Rad Pill":
                        if c2.button("💊 吞服 (解毒)", key="use_pill"):
                            user["inventory"]["Anti-Rad Pill"] -= 1
                            
                            # 清除有害物品
                            removed = []
                            for bad_item in ["Nutri-Paste", "Stim-Pack", "Cyber-Arm"]:
                                if user["inventory"].get(bad_item, 0) > 0:
                                    user["inventory"][bad_item] = 0
                                    removed.append(bad_item)
                            
                            user["toxicity"] = 0
                            save_user(uid, user)
                            msg = "系統重置完成。"
                            if removed: msg += f" 已移除汙染源: {', '.join(removed)}"
                            st.success(msg)
                            time.sleep(1.5)
                            st.rerun()
                    elif item_name in ["Nutri-Paste", "Stim-Pack", "Cyber-Arm"]:
                        c2.caption("⚠️ 帶在身上即觸發詛咒")

def page_crypto(uid, user):
    st.title("🔐 密碼學終端機")
    tab1, tab2, tab3 = st.tabs(["🏛️ 凱撒密碼", "📦 Base64", "🧩 每日挑戰"])
    
    with tab1:
        shift = st.slider("偏移量 (Key)", 1, 25, 3)
        c1, c2 = st.columns(2)
        with c1:
            pt = st.text_area("輸入明文", "ATTACK AT DAWN")
            if pt:
                res = "".join([chr((ord(c)-65+shift)%26+65) if c.isupper() else chr((ord(c)-97+shift)%26+97) if c.islower() else c for c in pt])
                st.code(res)
        with c2:
            ct = st.text_area("輸入密文", "")
            if ct:
                res = "".join([chr((ord(c)-65-shift)%26+65) if c.isupper() else chr((ord(c)-97-shift)%26+97) if c.islower() else c for c in ct])
                st.success(res)
                
    with tab2:
        c1, c2 = st.columns(2)
        with c1: 
            txt = st.text_input("文字 -> Base64", "Hello World")
            if txt: st.code(base64.b64encode(txt.encode()).decode())
        with c2:
            b64 = st.text_input("Base64 -> 文字", "")
            if b64:
                try: st.success(base64.b64decode(b64).decode())
                except: st.error("無效的 Base64")
                
    with tab3:
        if "caesar_ans" not in st.session_state:
            w = random.choice(["LINUX", "PYTHON", "JAVA", "RUBY", "DOCKER"])
            s = random.randint(1, 5)
            st.session_state.caesar_target = w
            st.session_state.caesar_shift = s
            st.session_state.caesar_q = "".join([chr(ord(c)+s) for c in w])
            st.session_state.caesar_ans = w # 標記已生成
            
        st.write("攔截到加密封包:")
        st.markdown(f"## `{st.session_state.caesar_q}`")
        st.caption(f"提示: 偏移量可能是 {st.session_state.caesar_shift}")
        
        ans = st.text_input("請輸入解密後的單字 (大寫)", key="cg_in")
        if st.button("提交驗證"):
            if ans == st.session_state.caesar_target:
                add_exp(uid, 50)
                del st.session_state["caesar_ans"]
                st.balloons()
                st.success("✅ 解密成功! 獲得 +50 EXP")
                time.sleep(2)
                st.rerun()
            else:
                st.error("❌ 密碼錯誤")

def page_lab(uid, user):
    st.title("🔌 邏輯電路實驗室")
    c1, c2 = st.columns(2)
    with c1: a = st.toggle("Input A (1)", True)
    with c2: b = st.toggle("Input B (0)", False)
    
    gate = st.selectbox("選擇邏輯閘", list(SVG_LIB.keys()))
    
    # 簡單的邏輯計算
    val_a = 1 if a else 0
    val_b = 1 if b else 0
    res = 0
    if gate == "AND": res = val_a & val_b
    elif gate == "OR": res = val_a | val_b
    elif gate == "NOT": res = not val_a
    elif gate == "XOR": res = val_a ^ val_b
    elif gate == "NAND": res = not (val_a & val_b)
    elif gate == "NOR": res = not (val_a | val_b)
    elif gate == "XNOR": res = not (val_a ^ val_b)
    
    st.markdown(SVG_LIB[gate], unsafe_allow_html=True)
    st.metric("Output", str(int(res)))

def page_linux(uid, user):
    st.title("🐧 遠端終端機 (SSH)")
    st.code(f"{uid}@cityos-mainframe:~$", language="bash")
    
    cmd = st.text_input("Command Input", placeholder="ls, pwd, whoami...")
    if st.button("Execute"):
        if cmd == "ls":
            st.write("system32  secrets.txt  mining_script.py  wallet.dat")
        elif cmd == "pwd":
            st.write(f"/home/users/{uid}")
        elif cmd == "whoami":
            st.write(uid)
        elif cmd == "cat secrets.txt":
            st.error("Permission Denied: You need Level 5 access.")
        elif cmd.startswith("sudo"):
            st.write("user is not in the sudoers file. This incident will be reported.")
        else:
            st.write(f"bash: {cmd}: command not found")

def page_pvp(uid, user):
    st.title("⚔️ 網路攻防 (PVP)")
    targets = [u for u in get_all_users() if u != uid and u != "frank"]
    
    if not targets:
        st.write("目前網路上沒有其他可攻擊的目標。")
        return
        
    t = st.selectbox("選擇入侵目標", targets)
    target_user = get_user(t)
    
    col1, col2 = st.columns(2)
    col1.metric("目標等級", target_user['level'])
    col2.metric("預估獲利", "???")
    
    if st.button("執行注入攻擊 (需消耗 Trojan Virus)"):
        if user.get("inventory", {}).get("Trojan Virus", 0) > 0:
            user["inventory"]["Trojan Virus"] -= 1
            
            # 攻擊邏輯
            success_rate = 0.7 # 70% 成功率
            if random.random() < success_rate:
                steal_amount = random.randint(50, 200)
                if target_user['money'] < steal_amount:
                    steal_amount = target_user['money']
                
                target_user['money'] -= steal_amount
                user['money'] += steal_amount
                
                save_user(t, target_user)
                save_user(uid, user)
                st.success(f"入侵成功！竊取了 ${steal_amount}")
                st.balloons()
            else:
                st.error("入侵失敗！防火牆攔截了你的連線。")
                save_user(uid, user) # 還是要扣道具
        else:
            st.error("錯誤：缺少攻擊工具 (Trojan Virus)")

# --- 主程式入口 ---
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # 登入介面
    if not st.session_state.logged_in:
        st.title("CITY_OS // ACCESS PORT")
        c1, c2 = st.tabs(["LOGIN", "REGISTER"])
        
        with c1:
            u = st.text_input("使用者 ID")
            p = st.text_input("密碼", type="password")
            if st.button("連線"):
                user = get_user(u)
                if user and user['password'] == p:
                    st.session_state.logged_in = True
                    st.session_state.uid = u
                    st.rerun()
                else:
                    st.error("存取被拒。")
        
        with c2:
            nu = st.text_input("設定新 ID")
            np = st.text_input("設定新密碼", type="password")
            nn = st.text_input("暱稱")
            if st.button("註冊身份"):
                if create_user(nu, np, nn):
                    st.success("身分建立成功。請登入。")
                else:
                    st.error("該 ID 已存在。")
        return

    # 登入後邏輯
    uid = st.session_state.uid
    user = get_user(uid)
    
    # 🔥 1. 優先執行：特效渲染 (Hardcore CSS)
    apply_immersion_effects(user)

    # 2. 環境檢測 (毒氣傷害)
    is_poisoned = apply_environmental_hazard(uid, user)
    if is_poisoned:
        st.toast("⚠️ 警告：偵測到環境輻射，生命值下降...", icon="☣️")
    
    # 死亡判定
    if user.get("toxicity", 0) >= 100:
        st.error("☠️ 生命訊號中斷... 重構中...")
        st.warning("支付 $200 重生費。")
        user["money"] = max(0, user["money"] - 200)
        user["toxicity"] = 50
        save_user(uid, user)
        time.sleep(3)
        st.rerun()

    # 3. 側邊欄導航
    with st.sidebar:
        st.title(f"👤 {user['name']}")
        st.caption(f"等級 {user['level']}: {LEVEL_TITLES.get(user['level'], 'Unknown')}")
        
        # 經驗值條
        exp_req = user['level'] * 100
        st.progress(min(1.0, user['exp'] / exp_req))
        
        st.metric("Credits", f"${user['money']}")
        st.metric("Toxicity", f"{user['toxicity']}%", delta_color="inverse")
        
        st.divider()
        nav = st.radio("導航系統", 
            ["Dashboard", "Exchange", "Dark Market", "PVP", "Logic Gates", "Crypto", "Linux"])
        
        st.divider()
        if st.button("中斷連線 (Logout)"):
            st.session_state.logged_in = False
            st.rerun()

    # 4. 頁面路由
    if nav == "Dashboard": page_dashboard(uid, user)
    elif nav == "Exchange": page_stock(uid, user)
    elif nav == "Dark Market": page_shop(uid, user)
    elif nav == "PVP": page_pvp(uid, user)
    elif nav == "Logic Gates": page_lab(uid, user)
    elif nav == "Crypto": page_crypto(uid, user)
    elif nav == "Linux": page_linux(uid, user)

if __name__ == "__main__":
    main()
