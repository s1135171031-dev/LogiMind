# app.py
# 用途: 系統核心 UI 與業務邏輯

import streamlit as st
import random
import time
import pandas as pd
from datetime import datetime, date
import os 

# --- 引用自訂模組 ---
try:
    from config import ITEMS, STOCKS_DATA, CITY_EVENTS, SVG_LIB 
    from database import (init_db, get_user, save_user, create_user, check_mission, 
                          send_mail, get_all_users, get_global_stock_state, save_global_stock_state)
except ImportError:
    st.error("⚠️ 檔案遺失！請確保 app.py, config.py, database.py 都在同目錄下。")
    st.stop()

# --- 讀取/生成 題庫函數 ---
def load_quiz_from_file():
    questions = []
    default_q = [{"q": "系統錯誤: 找不到 questions.txt", "options": ["重試", "略過"], "ans": "重試"}]
    
    if not os.path.exists("questions.txt"):
        with open("questions.txt", "w", encoding="utf-8") as f:
            f.write("Python是什麼?|程式語言,蛇,咖啡|程式語言\n")
            f.write("CityOS的核心是?|數據,金錢,控制|數據\n")
    
    try:
        with open("questions.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or "|" not in line: continue
                parts = line.split("|")
                if len(parts) >= 3:
                    questions.append({"q": parts[0], "options": parts[1].split(","), "ans": parts[2]})
        return questions if questions else default_q
    except: return default_q

# --- 頁面設定 ---
st.set_page_config(page_title="CityOS V32.0 Multi", layout="wide", page_icon="📟", initial_sidebar_state="expanded")

# --- CSS ---
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00ff41; }
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stButton button, input, textarea, .stSelectbox div, .stRadio div {
        font-family: 'Courier New', monospace !important;
        text-shadow: 0 0 2px rgba(0, 255, 65, 0.3);
    }
    .stButton > button {
        background-color: #000 !important; color: #00ff41 !important;
        border: 1px solid #00ff41 !important;
    }
    .stButton > button:hover { box-shadow: 0 0 15px #00ff41; background-color: #001a05 !important; }
    .stTextInput > div > div > input { background-color: #111 !important; color: #00ff41 !important; }
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #00ff41; }
</style>
""", unsafe_allow_html=True)

# --- 系統初始化 ---
init_db()

# --- 每日事件 ---
def get_today_event():
    seed = int(date.today().strftime("%Y%m%d"))
    random.seed(seed)
    evt = random.choice(CITY_EVENTS)
    random.seed()
    return evt

if "today_event" not in st.session_state:
    st.session_state.today_event = get_today_event()

# --- 🔥 核心股市邏輯 (多人同步版) ---
def update_stock_market():
    # 1. 讀取全域檔案
    global_state = get_global_stock_state()
    if not global_state: return # Error handling

    now = time.time()
    last_update = global_state.get("last_update", 0)
    
    # 2. 如果超過 5 秒沒人更新，由我來計算並寫入 (成為 Host)
    if now - last_update > 5:
        evt = st.session_state.today_event
        new_prices = {}
        
        for code, data in STOCKS_DATA.items():
            prev = global_state["prices"].get(code, data["base"])
            vol = data["volatility"] * 2.0 # 加大波動
            
            # 事件影響
            if evt["effect"] == "crash": change = random.uniform(-0.3, -0.05)
            elif evt["effect"] == "tech_boom" and code in ["CYBR", "AI"]: change = random.uniform(0.05, 0.2)
            else: change = random.uniform(-vol, vol)
            
            new_p = int(prev * (1 + change))
            new_p = max(5, min(3000, new_p)) # 限制價格區間
            new_prices[code] = new_p
            
        global_state["prices"] = new_prices
        global_state["last_update"] = now
        
        # 存歷史紀錄 (只留最後 30 筆以省空間)
        hist_entry = new_prices.copy()
        hist_entry["_time"] = datetime.now().strftime("%H:%M:%S")
        global_state["history"].append(hist_entry)
        if len(global_state["history"]) > 30: global_state["history"].pop(0)
        
        save_global_stock_state(global_state)

    # 3. 將全域資料載入 Session 供顯示
    st.session_state.stock_prices = global_state["prices"]
    st.session_state.stock_history = pd.DataFrame(global_state["history"])

# --- 功能頁面 ---

def page_dashboard(uid, user):
    st.title("🏙️ DASHBOARD")
    evt = st.session_state.today_event
    st.info(f"📢 今日狀態: {evt['name']} | {evt['desc']}")
    
    update_stock_market() # 同步股市
    
    # 計算資產
    stock_val = sum([amt * st.session_state.stock_prices.get(c, 0) for c, amt in user.get('stocks',{}).items()])
    total = user['money'] + stock_val
    
    c1, c2, c3 = st.columns(3)
    c1.metric("總資產", f"${total:,}")
    c2.metric("現金", f"${user['money']:,}")
    c3.metric("股票市值", f"${stock_val:,}")
    
    if not st.session_state.stock_history.empty:
        st.subheader("📉 市場走勢 (Global)")
        chart_data = st.session_state.stock_history.drop(columns=["_time"], errors="ignore")
        st.line_chart(chart_data, height=300)

def page_stock(uid, user):
    st.title("💹 證券交易所")
    update_stock_market() # 同步
    prices = st.session_state.stock_prices
    
    t1, t2 = st.tabs(["買入", "賣出"])
    
    with t1:
        code = st.selectbox("選擇股票", list(STOCKS_DATA.keys()))
        curr = prices.get(code, 0)
        st.metric(f"{STOCKS_DATA[code]['name']}", f"${curr}")
        qty = st.number_input("數量", 1, 1000, 10, key="buy_qty")
        cost = qty * curr
        
        if st.button(f"買進 (花費 ${cost:,})"):
            if user['money'] >= cost:
                user['money'] -= cost
                user.setdefault('stocks', {})[code] = user['stocks'].get(code, 0) + qty
                check_mission(uid, user, "stock_buy")
                save_user(uid, user)
                st.success("交易成功！")
                time.sleep(0.5); st.rerun()
            else: st.error("資金不足")
            
    with t2:
        my_stocks = user.get('stocks', {})
        if my_stocks:
            s_code = st.selectbox("賣出股票", list(my_stocks.keys()))
            owned = my_stocks[s_code]
            curr = prices.get(s_code, 0)
            st.write(f"持有: {owned} 股 | 現價: ${curr}")
            s_qty = st.number_input("賣出數量", 1, owned, 1, key="sell_qty")
            income = s_qty * curr
            
            if st.button(f"賣出 (獲得 ${income:,})"):
                user['stocks'][s_code] -= s_qty
                user['money'] += income
                if user['stocks'][s_code] == 0: del user['stocks'][s_code]
                save_user(uid, user)
                st.success("交易成功！")
                time.sleep(0.5); st.rerun()
        else: st.info("無持倉股票")

def page_pvp(uid, user):
    st.title("⚔️ 網路攻防戰 (PVP)")
    
    # 計算冷卻時間
    last_hack = user.get("last_hack", 0)
    cooldown = 60 # 60秒冷卻
    remaining = int(cooldown - (time.time() - last_hack))
    
    if remaining > 0:
        st.warning(f"⚠️ 系統追蹤中，請等待冷卻結束: {remaining} 秒")
        return

    # 顯示目標列表
    all_users = get_all_users()
    targets = [u for u in all_users.keys() if u != uid and u != "admin"]
    
    if not targets:
        st.info("附近沒有可攻擊的目標 IP。")
        return
        
    target_uid = st.selectbox("鎖定目標 IP", targets)
    
    # 檢查道具
    has_virus = user.get("inventory", {}).get("Trojan Virus", 0) > 0
    st.write(f"木馬病毒狀態: {'✅ 就緒' if has_virus else '❌ 未持有 (請至黑市購買)'}")
    
    if st.button("🔴 執行攻擊 (EXECUTE)", disabled=not has_virus):
        # 1. 消耗道具
        user["inventory"]["Trojan Virus"] -= 1
        if user["inventory"]["Trojan Virus"] <= 0: del user["inventory"]["Trojan Virus"]
        
        # 2. 計算成功率
        success_rate = 0.5
        if user.get("inventory", {}).get("Brute Force Script", 0) > 0: success_rate = 0.8
        
        # 3. 判定結果
        if random.random() < success_rate:
            # 🔥 重點：重新讀取受害者資料以避免衝突
            victim = get_user(target_uid)
            loot = random.randint(100, 500)
            
            # 檢查受害者是否有防火牆
            if victim.get("inventory", {}).get("Firewall", 0) > 0:
                victim["inventory"]["Firewall"] -= 1
                if victim["inventory"]["Firewall"] <= 0: del victim["inventory"]["Firewall"]
                save_user(target_uid, victim) # 儲存消耗
                save_user(uid, user)          # 儲存自己消耗
                st.error("🚫 攻擊被對方的 [Firewall] 攔截！")
                send_mail(target_uid, "System", "🛡️ 防禦通知", f"{uid} 試圖攻擊你，但被防火牆擋下了。")
            else:
                actual_loot = min(victim['money'], loot)
                victim['money'] -= actual_loot
                user['money'] += actual_loot
                user['last_hack'] = time.time() # 設定冷卻
                
                # 雙方存檔
                save_user(target_uid, victim)
                save_user(uid, user)
                
                # 發送通知
                send_mail(target_uid, "System", "🚨 入侵警報", f"你遭到 {uid} 攻擊，損失資金 ${actual_loot}")
                st.balloons()
                st.success(f"攻擊成功！竊取資金 ${actual_loot}")
        else:
            # 失敗懲罰
            penalty = 100
            user['money'] = max(0, user['money'] - penalty)
            user['last_hack'] = time.time()
            save_user(uid, user)
            st.error(f"⚠️ 攻擊失敗！反向追蹤導致罰款 ${penalty}")

def page_shop(uid, user):
    st.title("🛒 地下黑市")
    
    # 檢查是否打折
    discount = 0.7 if st.session_state.today_event['effect'] == "shop_discount" else 1.0
    if discount < 1.0: st.success("🔥 黑色星期五特賣中！")
    
    cols = st.columns(3)
    for i, (k, v) in enumerate(ITEMS.items()):
        price = int(v['price'] * discount)
        with cols[i % 3].container(border=True):
            st.subheader(k)
            st.caption(v['desc'])
            st.write(f"**${price:,}**")
            
            if st.button("購買", key=f"buy_{i}"):
                if user['money'] >= price:
                    user['money'] -= price
                    user.setdefault("inventory", {})[k] = user.get("inventory", {}).get(k, 0) + 1
                    check_mission(uid, user, "shop_buy")
                    save_user(uid, user)
                    st.toast(f"已購買 {k}")
                    time.sleep(0.5); st.rerun()
                else: st.error("資金不足")

def page_missions(uid, user):
    st.title("🎯 任務中心")
    
    # 領獎區
    if user.get("pending_claims"):
        st.success("🎁 有可領取的獎勵！")
        for i, m in enumerate(user["pending_claims"]):
            if st.button(f"領取 ${m['reward']} - {m['title']}", key=f"claim_{i}"):
                user['money'] += m['reward']
                user['pending_claims'].pop(i)
                save_user(uid, user)
                st.rerun()
    
    st.divider()
    
    # 任務列表
    st.subheader("進行中任務")
    if not user.get("active_missions"):
        st.info("目前沒有新任務。")
    for m in user.get('active_missions', []):
        st.write(f"- **{m['title']}**: {m['desc']} (獎勵: ${m['reward']})")

def page_cli(uid, user):
    st.title("💻 終端機 (CLI)")
    if "cli_log" not in st.session_state: st.session_state.cli_log = ["System connected..."]
    
    # 顯示 Log
    with st.container(height=300):
        for l in st.session_state.cli_log: st.text(l)
    
    cmd = st.chat_input(f"{uid}@cityos:~$")
    if cmd:
        st.session_state.cli_log.append(f"{uid}@cityos:~$ {cmd}")
        parts = cmd.strip().split()
        base = parts[0].lower()
        resp = ""
        
        if base == "help": resp = "指令: bal, whoami, scan, date, clear"
        elif base == "bal": resp = f"Cash: ${user['money']}"
        elif base == "whoami": resp = f"User: {user['name']} | Role: User"
        elif base == "clear": st.session_state.cli_log = []; st.rerun()
        elif base == "date": resp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elif base == "scan":
             users = get_all_users()
             count = len(users) - 1
             resp = f"Network Scan Complete. {count} active nodes found."
        else: resp = f"Command not found: {base}"
        
        if resp: st.session_state.cli_log.append(resp)
        check_mission(uid, user, "cli_input") # 觸發隱藏任務
        st.rerun()

# --- 主程式 ---
def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        st.title("🏙️ CityOS V32.0 Access")
        st.caption(f"Server Event: {st.session_state.today_event['name']}")
        
        t1, t2 = st.tabs(["登入", "註冊公民ID"])
        with t1:
            u = st.text_input("帳號")
            p = st.text_input("密碼", type="password")
            if st.button("連線"):
                user_data = get_user(u)
                if user_data and user_data['password'] == p:
                    st.session_state.logged_in = True
                    st.session_state.uid = u
                    st.rerun()
                else: st.error("認證失敗")
        with t2:
            nu = st.text_input("新帳號")
            np = st.text_input("新密碼", type="password")
            nn = st.text_input("暱稱")
            if st.button("建立身份"):
                if create_user(nu, np, nn): st.success("註冊成功！請登入")
                else: st.error("帳號已存在")
        return

    # 已登入狀態
    uid = st.session_state.uid
    user = get_user(uid) # 每次重繪都讀取最新資料
    
    with st.sidebar:
        st.title(f"👤 {user['name']}")
        st.metric("現金", f"${user['money']:,}")
        
        nav = st.radio("導航系統", ["儀表板", "股市", "任務", "黑市", "PVP", "CLI"])
        if st.button("斷開連線"):
            st.session_state.logged_in = False
            st.rerun()

    if nav == "儀表板": page_dashboard(uid, user)
    elif nav == "股市": page_stock(uid, user)
    elif nav == "任務": page_missions(uid, user)
    elif nav == "黑市": page_shop(uid, user)
    elif nav == "PVP": page_pvp(uid, user)
    elif nav == "CLI": page_cli(uid, user)

if __name__ == "__main__":
    main()
