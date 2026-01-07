# app.py
# CityOS 主程式：使用者介面與即時邏輯

import streamlit as st
import random
import time
import pandas as pd
from datetime import datetime
from config import ITEMS, STOCKS_DATA, CITY_EVENTS
from database import (init_db, get_user, save_user, create_user, 
                      get_global_stock_state, save_global_stock_state, rebuild_market)

# 1. 頁面設定與 CSS (駭客風格)
st.set_page_config(page_title="CityOS v9.0", layout="wide", page_icon="☣️")
st.markdown("""
<style>
    .stApp { background-color: #000000; color: #00ff41; font-family: 'Courier New', monospace; }
    div.stButton > button { background-color: #000; border: 1px solid #00ff41; color: #00ff41; border-radius: 0; }
    div.stButton > button:hover { background-color: #00ff41; color: #000; }
    .metric-container { border: 1px solid #333; padding: 10px; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# 2. 初始化資料庫
init_db()

# 3. 核心函數：即時股市刷新 (每秒都在狂暴)
def update_stock_market():
    global_state = get_global_stock_state()
    if not global_state: return

    # 檢查是否需要更新 (每 0.8 秒)
    now = time.time()
    if now - global_state.get("last_update", 0) > 0.8:
        new_prices = {}
        
        for code, data in STOCKS_DATA.items():
            prev = global_state["prices"].get(code, data["base"])
            
            # 🔥 絕對暴力：每一秒都在 ±15% 之間亂跳
            change = random.uniform(-0.15, 0.15)
            
            # 偶爾暴擊 (讓它更像賭博)
            if random.random() < 0.1: change *= 2.5
            
            new_p = int(prev * (1 + change))
            new_p = max(5, new_p) # 最低 5 元
            new_prices[code] = new_p

        global_state["prices"] = new_prices
        global_state["last_update"] = now
        
        # 記錄歷史
        hist_entry = new_prices.copy()
        hist_entry["_time"] = datetime.now().strftime("%H:%M:%S")
        global_state["history"].append(hist_entry)
        if len(global_state["history"]) > 60: global_state["history"].pop(0) # 保持60點
        
        save_global_stock_state(global_state)

    # 同步到 Session State
    st.session_state.stock_prices = global_state["prices"]
    st.session_state.stock_history = pd.DataFrame(global_state["history"])

# 4. 子頁面功能

def page_dashboard(uid, user):
    st.title(f"🏙️ CityOS: {user['name']}")
    st.write("身份: 公民 | 狀態: 存活 | 信用: 極低")
    
    col1, col2, col3 = st.columns(3)
    
    # 計算總資產
    stock_val = sum([amt * st.session_state.stock_prices.get(c, 0) for c, amt in user.get('stocks',{}).items()])
    total_asset = user['money'] + stock_val
    
    col1.metric("現金 (CASH)", f"${user['money']:,}")
    col2.metric("股票市值 (STOCKS)", f"${stock_val:,}")
    col3.metric("總資產 (NET WORTH)", f"${total_asset:,}")

    # 顯示走勢圖
    st.subheader("📊 市場監控")
    update_stock_market()
    if not st.session_state.stock_history.empty:
        chart_data = st.session_state.stock_history.drop(columns=["_time"], errors="ignore")
        st.line_chart(chart_data, height=350)

def page_stock_market(uid, user):
    st.title("💹 賭場 (證交所)")
    st.caption("警告：投資有賺有賠，更多時候是直接歸零。")
    
    # 自動刷新開關
    if st.toggle("開啟即時報價 (AUTO-REFRESH)", value=True):
        time.sleep(1)
        st.rerun()
    
    update_stock_market()
    prices = st.session_state.stock_prices
    
    # 顯示所有股價
    cols = st.columns(len(STOCKS_DATA))
    for i, (code, data) in enumerate(STOCKS_DATA.items()):
        curr = prices.get(code, data['base'])
        cols[i].metric(code, f"${curr}", delta_color="off")

    # 交易介面
    tab1, tab2 = st.tabs(["🔴 買入 (BUY)", "🟢 賣出 (SELL)"])
    
    with tab1:
        b_code = st.selectbox("選擇標的", list(STOCKS_DATA.keys()), key="buy_sel")
        curr_p = prices.get(b_code, 0)
        st.info(f"當前價格: ${curr_p}")
        
        b_qty = st.number_input("數量", 1, 1000, 10, key="buy_qty")
        cost = b_qty * curr_p
        
        if st.button(f"下單 (花費 ${cost})"):
            if user['money'] >= cost:
                user['money'] -= cost
                user.setdefault('stocks', {})[b_code] = user['stocks'].get(b_code, 0) + b_qty
                save_user(uid, user)
                st.success("交易成功")
                st.rerun()
            else:
                st.error("資金不足。去打工吧，窮鬼。")

    with tab2:
        if not user.get('stocks'):
            st.warning("你沒有任何股票。")
        else:
            s_code = st.selectbox("選擇持股", list(user['stocks'].keys()), key="sell_sel")
            own = user['stocks'][s_code]
            curr_p = prices.get(s_code, 0)
            st.info(f"持有: {own} 股 | 現價: ${curr_p} | 價值: ${own*curr_p}")
            
            s_qty = st.number_input("賣出數量", 1, own, own if own > 0 else 1, key="sell_qty")
            
            if st.button("拋售"):
                gain = s_qty * curr_p
                user['money'] += gain
                user['stocks'][s_code] -= s_qty
                if user['stocks'][s_code] <= 0: del user['stocks'][s_code]
                save_user(uid, user)
                st.success(f"已賣出，獲得 ${gain}")
                st.rerun()

def page_job_center(uid, user):
    st.title("🔨 奴隸中心 (工作)")
    st.write("用時間換取微薄的薪水。")
    
    jobs = [
        {"name": "數據輸入員", "wage": 100, "energy": "低"},
        {"name": "人體試藥員", "wage": 500, "energy": "高風險"},
        {"name": "電子廢料回收", "wage": 200, "energy": "中"},
    ]
    
    for job in jobs:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{job['name']}** - 薪資: ${job['wage']}")
        with col2:
            if st.button(f"上工 ({job['name']})"):
                with st.spinner("工作中..."):
                    time.sleep(1.5)
                user['money'] += job['wage']
                save_user(uid, user)
                st.success(f"工作完成。入帳 ${job['wage']}")
                st.rerun()

def page_black_market(uid, user):
    st.title("🛒 黑市")
    st.write("只要有錢，什麼都買得到。")
    
    for item_name, info in ITEMS.items():
        with st.expander(f"{item_name} - ${info['price']}"):
            st.write(info['desc'])
            if st.button(f"購買 {item_name}"):
                if user['money'] >= info['price']:
                    user['money'] -= info['price']
                    user.setdefault('inventory', {})[item_name] = user['inventory'].get(item_name, 0) + 1
                    save_user(uid, user)
                    st.success(f"已購買 {item_name}")
                    st.rerun()
                else:
                    st.error("錢不夠。")
    
    st.divider()
    st.subheader("🎒 我的背包")
    if user.get('inventory'):
        for i, q in user['inventory'].items():
            st.write(f"- {i}: {q} 個")
    else:
        st.write("空空如也。")

# 5. 主程式入口
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # --- 登入畫面 ---
    if not st.session_state.logged_in:
        st.title("CITY_OS // ACCESS_CONTROL")
        c1, c2 = st.tabs(["登入", "註冊公民ID"])
        
        with c1:
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("LOGIN"):
                user = get_user(u)
                if user and user['password'] == p:
                    st.session_state.logged_in = True
                    st.session_state.uid = u
                    st.rerun()
                else:
                    st.error("拒絕存取。")
        
        with c2:
            new_u = st.text_input("New ID")
            new_p = st.text_input("New Pass", type="password")
            new_n = st.text_input("Display Name")
            if st.button("REGISTER"):
                if create_user(new_u, new_p, new_n):
                    st.success("註冊成功。請登入。")
                else:
                    st.error("ID 已被佔用。")
        return

    # --- 登入後畫面 ---
    uid = st.session_state.uid
    user = get_user(uid)
    
    # 側邊導航欄
    with st.sidebar:
        st.title("功能選單")
        st.write(f"User: **{user['name']}**")
        st.write(f"Cash: **${user['money']:,}**")
        
        page = st.radio("導航", ["儀表板", "股市", "工作", "黑市"])
        
        st.divider()
        if st.button("登出"):
            st.session_state.logged_in = False
            st.rerun()

        # 🔥 Frank 的專屬按鈕 🔥
        if user.get("job") == "Gamemaster":
            st.warning("⚠️ ADMIN TOOLS")
            if st.button("💥 重置股市 (CHAOS)", help="引發金融海嘯"):
                rebuild_market()
                st.toast("股市已重置！")
                time.sleep(1)
                st.rerun()

    # 頁面路由
    if page == "儀表板": page_dashboard(uid, user)
    elif page == "股市": page_stock_market(uid, user)
    elif page == "工作": page_job_center(uid, user)
    elif page == "黑市": page_black_market(uid, user)

if __name__ == "__main__":
    main()
