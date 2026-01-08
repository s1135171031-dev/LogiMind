import streamlit as st
import random
import time
import pandas as pd
import base64
import plotly.graph_objects as go
from datetime import datetime
import os

# --- 核心連結：匯入 database.py 的功能 ---
from database import (
    init_db, get_user, save_user, create_user, 
    get_global_stock_state, save_global_stock_state, 
    get_all_users, apply_environmental_hazard, add_exp,
    add_log, get_logs
)

# --- 1. 遊戲資料設定 ---
SVG_LIB = {
    "AND": '<svg viewBox="0 0 60 40" width="100"><path d="M10,5 L30,5 C45,5 45,35 30,35 L10,35 Z" fill="none" stroke="#00ff41" stroke-width="2"/><path d="M0,10 L10,10 M0,30 L10,30 M45,20 L60,20" stroke="#00ff41" stroke-width="2"/></svg>',
    "OR": '<svg viewBox="0 0 60 40" width="100"><path d="M10,5 C10,5 20,20 10,35 C25,35 50,25 50,20 C50,15 25,5 10,5" fill="none" stroke="#00ff41" stroke-width="2"/><path d="M0,10 L15,10 M0,30 L15,30 M50,20 L60,20" stroke="#00ff41" stroke-width="2"/></svg>',
    "NOT": '<svg viewBox="0 0 60 40" width="100"><path d="M10,5 L40,20 L10,35 Z" fill="none" stroke="#00ff41" stroke-width="2"/><circle cx="45" cy="20" r="3" stroke="#00ff41" stroke-width="2" fill="none"/><path d="M0,20 L10,20 M48,20 L60,20" stroke="#00ff41" stroke-width="2"/></svg>'
}

ITEMS = {
    "Nutri-Paste": {"price": 50, "desc": "噁心的營養膏 (飽食度+10)"},
    "Stim-Pack": {"price": 150, "desc": "興奮劑 (短暫提升能力)"},
    "Cyber-Arm": {"price": 2000, "desc": "軍用義肢 (挖礦效率 UP)"},
    "Trojan Virus": {"price": 300, "desc": "木馬程式 (PVP 專用)"},
    "Anti-Rad Pill": {"price": 500, "desc": "抗輻射藥丸 (清除毒素)"}
}

STOCKS_DATA = {
    "NVID": {"base": 800}, 
    "TSMC": {"base": 600}, 
    "BTC": {"base": 30000}
}

# --- 2. 頁面初始化 ---
st.set_page_config(page_title="CityOS: Final Cut", layout="wide", page_icon="☣️")

# 駭客風格 CSS
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00ff41; font-family: 'Courier New', monospace; }
    div.stButton > button { background-color: #000; border: 1px solid #00ff41; color: #00ff41; }
    div.stButton > button:hover { background-color: #00ff41; color: #000; box-shadow: 0 0 15px #00ff41; }
    .stTextInput > div > div > input { color: #00ff41; background-color: #111; border-color: #333; }
    code { color: #e6db74; background-color: #222; }
    h1, h2, h3 { color: #00ff41 !important; text-shadow: 0 0 5px #003300; }
</style>
""", unsafe_allow_html=True)

# 啟動資料庫連接
init_db()

# --- 3. 系統核心邏輯 ---
def update_stock_market():
    """更新全伺服器股市"""
    global_state = get_global_stock_state()
    now = time.time()
    
    # 每 2 秒更新一次價格，避免刷新太快
    if now - global_state.get("last_update", 0) > 2.0:
        new_prices = {}
        for code, data in STOCKS_DATA.items():
            prev = global_state["prices"].get(code, data["base"])
            # 隨機漲跌 -5% ~ +5%
            change = random.uniform(-0.05, 0.05)
            new_prices[code] = max(1, int(prev * (1 + change)))
        
        global_state["prices"] = new_prices
        global_state["last_update"] = now
        
        # 紀錄歷史供 K 線圖使用
        hist = new_prices.copy()
        hist["_time"] = datetime.now().strftime("%H:%M:%S")
        global_state["history"].append(hist)
        if len(global_state["history"]) > 50: global_state["history"].pop(0)
        
        save_global_stock_state(global_state)
        
    st.session_state.stock_prices = global_state["prices"]
    st.session_state.stock_history = pd.DataFrame(global_state["history"])

def render_k_line(symbol):
    """繪製簡易 K 線趨勢圖"""
    if "stock_history" not in st.session_state or st.session_state.stock_history.empty:
        st.write("等待市場數據...")
        return
    df = st.session_state.stock_history
    if symbol in df.columns:
        st.line_chart(df[symbol])

# --- 4. 各功能頁面 ---

def page_dashboard(uid, user):
    st.title(f"🏙️ 儀表板: {user['name']}")
    
    # 環境危害判定
    if apply_environmental_hazard(uid, user):
        st.toast("⚠️ 警告：偵測到環境輻射傷害！", icon="☢️")

    update_stock_market()
    
    # 計算資產
    stock_val = sum([amt * st.session_state.stock_prices.get(c, 0) for c, amt in user.get('stocks',{}).items()])
    total_asset = user['money'] + stock_val
    
    # 顯示數據
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("等級 (Level)", f"Lv.{user['level']}")
    c2.metric("現金 (Cash)", f"${user['money']:,}")
    c3.metric("股票資產 (Stocks)", f"${stock_val:,}")
    c4.metric("總身價 (Net Worth)", f"${total_asset:,}")
    
    st.divider()
    st.subheader("📡 城市廣播 (Logs)")
    logs = get_logs()
    for log in logs[:5]:
        st.text(log)

def page_stock(uid, user):
    st.title("📉 紐約證券交易所 (NY-EX)")
    update_stock_market()
    
    c1, c2 = st.columns([2, 1])
    
    with c1:
        sel = st.selectbox("選擇股票代碼", list(STOCKS_DATA.keys()))
        render_k_line(sel)
    
    with c2:
        curr_price = st.session_state.stock_prices.get(sel, 0)
        st.metric(f"{sel} 目前價格", f"${curr_price}")
        
        my_stock = user.get('stocks', {}).get(sel, 0)
        st.write(f"持有數量: {my_stock}")
        
        amount = st.number_input("交易數量", 1, 1000, 10)
        
        col_buy, col_sell = st.columns(2)
        if col_buy.button("🟢 買進"):
            cost = curr_price * amount
            if user['money'] >= cost:
                user['money'] -= cost
                user.setdefault('stocks', {})[sel] = user['stocks'].get(sel, 0) + amount
                save_user(uid, user)
                add_log(f"💰 {user['name']} 買入了 {amount} 股 {sel}")
                st.success("交易成功")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("資金不足！")
                
        if col_sell.button("🔴 賣出"):
            if my_stock >= amount:
                gain = curr_price * amount
                user['money'] += gain
                user['stocks'][sel] -= amount
                save_user(uid, user)
                add_log(f"💸 {user['name']} 賣出了 {amount} 股 {sel}")
                st.success("交易成功")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("持股不足！")

def page_mining(uid, user):
    st.title("⛏️ 數據礦場 (Data Mine)")
    st.write("點擊按鈕挖掘加密數據碎片...")
    
    # 根據裝備計算效率
    efficiency = 1
    if "Cyber-Arm" in user.get('inventory', {}):
        efficiency = 5
        st.info("⚡ 裝備加成：Cyber-Arm 已啟動 (效率 x5)")
        
    if st.button("⛏️ 開始挖掘", use_container_width=True):
        with st.spinner("解析區塊鏈中..."):
            time.sleep(0.5) # 模擬延遲
            base_reward = random.randint(10, 50)
            final_reward = base_reward * efficiency
            
            user['money'] += final_reward
            add_exp(uid, 5) # 增加經驗值
            save_user(uid, user)
            
            st.balloons()
            st.success(f"挖掘完成！獲得 ${final_reward} (經驗 +5)")
            time.sleep(1)
            st.rerun()

def page_shop(uid, user):
    st.title("🛒 地下黑市 (Black Market)")
    st.write("有些東西，光有錢是不夠的...")
    
    for item_name, info in ITEMS.items():
        with st.container():
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.markdown(f"**{item_name}**")
            c1.caption(info['desc'])
            c2.write(f"${info['price']}")
            
            if c3.button(f"購買", key=f"buy_{item_name}"):
                if user['money'] >= info['price']:
                    user['money'] -= info['price']
                    user.setdefault('inventory', {})[item_name] = user['inventory'].get(item_name, 0) + 1
                    save_user(uid, user)
                    st.success(f"已購買 {item_name}")
                    st.rerun()
                else:
                    st.error("資金不足")
            st.divider()

def page_linux(uid, user):
    st.title("🐧 系統終端機 (Terminal)")
    st.markdown("連線至: `root@cityos_core:~`")
    
    history = st.session_state.get('term_history', [])
    for h in history:
        st.text(h)
        
    cmd = st.text_input("輸入指令 (try: ls, whoami, help)", key="cmd_input")
    
    if st.button("Execute"):
        response = ""
        if cmd == "help": response = "可用指令: ls, whoami, date, clear, hack"
        elif cmd == "ls": response = "user_data.db  wallet.dat  secret_plans.txt"
        elif cmd == "whoami": response = f"{uid} (Level {user['level']})"
        elif cmd == "date": response = str(datetime.now())
        elif cmd == "clear": 
            st.session_state.term_history = []
            st.rerun()
        elif cmd == "hack": response = "ACCESS DENIED. 防火牆等級過高。"
        else: response = f"bash: {cmd}: command not found"
        
        if cmd != "clear":
            st.session_state.setdefault('term_history', []).append(f"{uid}@cityos:~$ {cmd}")
            st.session_state.term_history.append(response)
            st.rerun()

def page_lab(uid, user):
    st.title("🔌 邏輯閘實驗室 (Logic Lab)")
    st.write("學習數位邏輯的基礎。")
    
    gate_type = st.selectbox("選擇邏輯閘", list(SVG_LIB.keys()))
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div style='background:#222; padding:20px; border-radius:10px;'>{SVG_LIB[gate_type]}</div>", unsafe_allow_html=True)
    with col2:
        if gate_type == "AND":
            st.info("AND 閘：兩個輸入都為 1，輸出才為 1。")
            st.code("Input A: 1, Input B: 1 => Output: 1\nOther cases => Output: 0")
        elif gate_type == "OR":
            st.info("OR 閘：只要有一個輸入為 1，輸出就為 1。")
            st.code("Input A: 0, Input B: 0 => Output: 0\nOther cases => Output: 1")
        elif gate_type == "NOT":
            st.info("NOT 閘：反轉輸入訊號。")
            st.code("Input: 1 => Output: 0\nInput: 0 => Output: 1")

# --- 5. 主程式流程 ---
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # A. 登入畫面
    if not st.session_state.logged_in:
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            st.title("CITY_OS // ACCESS")
            st.markdown("---")
            
            tab_login, tab_reg = st.tabs(["🔒 登入", "📝 註冊"])
            
            with tab_login:
                u = st.text_input("用戶名 (ID)", key="login_u")
                p = st.text_input("密碼 (PW)", type="password", key="login_p")
                if st.button("連線系統", use_container_width=True):
                    user_data = get_user(u)
                    if user_data and user_data['password'] == p:
                        st.session_state.logged_in = True
                        st.session_state.uid = u
                        st.toast("連線成功！", icon="✅")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("拒絕存取：帳號或密碼錯誤")
            
            with tab_reg:
                new_u = st.text_input("設定 ID")
                new_p = st.text_input("設定密碼", type="password")
                new_n = st.text_input("顯示暱稱")
                if st.button("建立新身份", use_container_width=True):
                    if create_user(new_u, new_p, new_n):
                        st.success("身份建立完成，請切換至登入頁面")
                    else:
                        st.error("錯誤：ID 已被佔用")
        return

    # B. 遊戲主畫面
    uid = st.session_state.uid
    user = get_user(uid)
    
    # 防呆：如果登入後資料庫被清空
    if not user:
        st.session_state.logged_in = False
        st.rerun()

    # 側邊欄導航
    with st.sidebar:
        st.image("https://img.icons8.com/nolan/96/matrix-desktop.png", width=80)
        st.title(f"{user['name']}")
        st.caption(f"ID: {user['id']}")
        st.progress(user['exp'] / (user['level']*100), text=f"EXP: {user['exp']}/{user['level']*100}")
        
        st.divider()
        nav = st.radio("導航模組", 
            ["📊 儀表板", "📉 交易所", "⛏️ 礦場", "🛒 黑市", "🐧 終端機", "🔌 實驗室"]
        )
        
        st.divider()
        st.write("🎒 背包:")
        for k, v in user.get('inventory', {}).items():
            st.caption(f"- {k} x{v}")
            
        if st.button("🔴 登出系統"):
            st.session_state.logged_in = False
            st.rerun()

    # 頁面路由
    if nav == "📊 儀表板": page_dashboard(uid, user)
    elif nav == "📉 交易所": page_stock(uid, user)
    elif nav == "⛏️ 礦場": page_mining(uid, user)
    elif nav == "🛒 黑市": page_shop(uid, user)
    elif nav == "🐧 終端機": page_linux(uid, user)
    elif nav == "🔌 實驗室": page_lab(uid, user)

# --- 啟動點 ---
if __name__ == "__main__":
    main()
