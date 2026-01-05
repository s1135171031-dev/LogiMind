# ==========================================
# 檔案名稱: app.py
# 用途: CityOS 主程式 (V18.0 Ultimate)
# 功能: 動態儀表板、外部任務/題庫、隱藏成就、CLI 駭客系統
# ==========================================

import streamlit as st
import random
import time
import pandas as pd
import numpy as np  # 需安裝: pip install numpy
from config import CITY_EVENTS, ITEMS, SVG_LIB, MORSE_CODE_DICT
# 注意：這裡多引入了 HIDDEN_MISSIONS 以便在介面上顯示成就
from database import (
    load_db, save_db, check_mission, get_today_event, 
    log_intruder, load_quiz_from_file, load_missions_from_file, 
    HIDDEN_MISSIONS
)

# --- 頁面設定 ---
st.set_page_config(
    page_title="CityOS V18.0 Ultimate", 
    layout="wide", 
    page_icon="🏙️", 
    initial_sidebar_state="expanded"
)

# --- CSS 美化注入 ---
st.markdown("""
<style>
    /* 側欄背景微調 */
    [data-testid="stSidebar"] { background-color: #0E1117; }
    
    /* 按鈕樣式 */
    .stButton>button { 
        border-radius: 8px; 
        border: 1px solid #333; 
        transition: all 0.3s;
    }
    .stButton>button:hover {
        border-color: #00FF00;
        color: #00FF00;
    }
    
    /* 進度條顏色 */
    .stProgress > div > div > div > div { background-color: #00FF00; }
    
    /* 標題樣式 */
    h1, h2, h3 { font-family: 'Courier New', monospace; }
</style>
""", unsafe_allow_html=True)

# --- 功能模組 ---

def page_dashboard(uid, user):
    st.title("🏙️ CityOS 中央控制台")
    st.caption(f"User: {user['name']} | Status: Online | Role: {user['job']}")

    # 分頁設計
    tab1, tab2, tab3 = st.tabs(["📊 系統監控", "📖 系統介紹", "📘 使用手冊"])

    with tab1:
        st.subheader("📡 即時數據監控")
        run_monitor = st.checkbox("🔴 啟動即時數據串流 (Live Stream)")
        
        col1, col2, col3 = st.columns(3)
        with col1: chart1 = st.empty()
        with col2: chart2 = st.empty()
        with col3: chart3 = st.empty()
        
        if run_monitor:
            # 模擬動態數據
            while run_monitor:
                cpu_data = pd.DataFrame(np.random.randint(10, 60, size=(20, 1)), columns=["CPU Usage %"])
                ram_data = pd.DataFrame(np.random.randint(40, 80, size=(20, 1)), columns=["RAM Usage %"])
                net_data = pd.DataFrame(np.random.randint(200, 900, size=(20, 1)), columns=["Network (Kbps)"])
                
                chart1.line_chart(cpu_data, height=200)
                chart2.area_chart(ram_data, height=200, color="#00FF00")
                chart3.bar_chart(net_data, height=200, color="#FF0000")
                time.sleep(0.8) # 更新頻率
        else:
            st.info("監控已待命。請勾選上方選項啟動。")
            chart1.metric("CPU", "Idle", "0%")
            chart2.metric("RAM", "Stable", "4.2GB")
            chart3.metric("Network", "Connected", "1Gbps")

    with tab2:
        st.markdown("""
        ### 關於 CityOS
        這是一個模擬 **賽博龐克 (Cyberpunk)** 風格的城市作業系統。
        結合了 **數位邏輯教育**、**經濟模擬** 與 **駭客任務**。
        
        #### 核心模組
        * **數位實驗室**：學習 AND/OR/XOR 閘與卡諾圖化簡。
        * **密碼學中心**：體驗凱薩加密與摩斯電碼傳輸。
        * **經濟體系**：包含銀行利息、黑市交易與挖礦系統。
        """)

    with tab3:
        st.markdown("""
        ### 📘 操作指南
        
        **1. 賺錢攻略**
        * 購買 **[Mining GPU]** 每日登入領取收益。
        * 完成 **[📝 每日測驗]**，答對賺 $300。
        * 完成 **[🎯 任務]**，獎金豐厚。

        **2. 隱藏要素 (Easter Eggs)**
        * 系統中藏有隱藏成就，試著達成特殊的金錢數字、擁有特定數量的物品，或在 CLI 輸入駭客指令。
        
        **3. CLI 指令**
        * `bal`: 查詢餘額
        * `scan`: 掃描區域網路
        * `sudo su`: 嘗試獲取管理員權限 (?)
        """)

def page_missions(uid, user):
    st.title("🎯 任務中心")
    
    # 讀取普通任務
    missions = load_missions_from_file()
    if not missions:
        st.error("❌ 無法讀取 missions.txt，請確認檔案存在。")
        return

    done = user.get("completed_missions", [])
    
    # 計算進度 (僅計算普通任務)
    valid_done = [m for m in done if m in missions]
    total = len(missions)
    progress = len(valid_done)/total if total > 0 else 0
    st.progress(progress, text=f"普通任務進度: {len(valid_done)}/{total}")
    
    # 建立分頁：普通任務 vs 隱藏成就
    tab_n, tab_h = st.tabs(["📋 一般任務", "🏆 隱藏成就"])
    
    with tab_n:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🚧 待執行")
            count = 0
            for mid, m in missions.items():
                if mid not in done and count < 10: # 限制顯示數量避免洗版
                    with st.container(border=True):
                        st.write(f"**{m['title']}**")
                        st.caption(m['desc'])
                        st.write(f"💰 報酬: ${m['reward']}")
                    count += 1
            if count == 10:
                st.info("... 完成上方任務以顯示更多")
        
        with col2:
            st.subheader("✅ 已完成")
            for mid in reversed(done): # 顯示最新的在上面
                if mid in missions:
                    m = missions[mid]
                    with st.container(border=True):
                        st.write(f"~~{m['title']}~~")
                        st.caption("已領取獎勵")
    
    with tab_h:
        st.subheader("🕵️ 傳奇隱藏成就")
        hidden_done = [mid for mid in done if mid.startswith("H_")]
        
        if not hidden_done:
            st.info("尚無隱藏成就。提示：嘗試讓錢歸零、變成 777，或在 CLI 輸入特定指令。")
        else:
            for mid in hidden_done:
                if mid in HIDDEN_MISSIONS:
                    m = HIDDEN_MISSIONS[mid]
                    st.success(f"【{m['title']}】 {m['desc']} (獎金 ${m['reward']})")

def page_quiz(uid, user):
    st.title("📝 每日工程測驗")
    if "quiz_today_done" not in st.session_state: st.session_state.quiz_today_done = False
    
    if st.session_state.quiz_today_done:
        st.info("✅ 今日測驗已完成，請明日再來。")
        return

    if "current_question" not in st.session_state:
        qs = load_quiz_from_file()
        if not qs:
            st.error("找不到題庫 (questions.txt)。"); return
        st.session_state.current_question = random.choice(qs)

    q = st.session_state.current_question
    st.write(f"### Q: {q['q']}")
    st.caption(f"Level: {q['level']} | ID: {q['id']}")
    choice = st.radio("Answer:", q['options'], key="quiz_opt")
    
    if st.button("提交"):
        if choice == q['ans']:
            st.balloons(); st.success("正確！ +$300"); user["money"]+=300; user["exp"]+=50
            check_mission(uid, user, "quiz_done")
            if uid!="frank": save_db({"users": load_db()["users"]|{uid:user}, "bbs":[]})
            st.session_state.quiz_today_done=True; del st.session_state.current_question; st.rerun()
        else:
            st.error("錯誤！系統鎖定。"); st.session_state.quiz_today_done=True; del st.session_state.current_question; st.rerun()

def page_digital_lab(uid, user):
    st.title("🔬 數位邏輯實驗室")
    t1, t2, t3 = st.tabs(["邏輯閘", "K-Map", "格雷碼"])
    with t1:
        g = st.selectbox("Gate", list(SVG_LIB.keys()))
        c1, c2 = st.columns(2)
        a = c1.toggle("Input A", False); b = c2.toggle("Input B", False)
        st.markdown(SVG_LIB[g], unsafe_allow_html=True)
        if g and (a or b): check_mission(uid, user, "logic_use")
    with t2:
        st.write("2-Var K-Map")
        if "kmap" not in st.session_state: st.session_state.kmap=[0,0,0,0]
        c1, c2 = st.columns(2)
        c1.write("A=0"); c2.write("A=1")
        if c1.button(f"00: {st.session_state.kmap[0]}", key="k0"): st.session_state.kmap[0]^=1; st.rerun()
        if c1.button(f"01: {st.session_state.kmap[1]}", key="k1"): st.session_state.kmap[1]^=1; st.rerun()
        if c2.button(f"10: {st.session_state.kmap[2]}", key="k2"): st.session_state.kmap[2]^=1; st.rerun()
        if c2.button(f"11: {st.session_state.kmap[3]}", key="k3"): st.session_state.kmap[3]^=1; st.rerun()
    with t3:
        n = st.slider("Num", 0, 15, 5)
        st.metric("Gray Code", f"{(n^(n>>1)):04b}")

def page_bank(uid, user):
    st.title("🏦 賽博銀行")
    c1, c2 = st.columns(2)
    c1.metric("存款", f"${user.get('bank_deposit',0):,}")
    c2.metric("現金", f"${user['money']:,}")
    
    with st.expander("ATM 操作", expanded=True):
        amt = st.number_input("金額", 0, 1000000, 100)
        b1, b2 = st.columns(2)
        if b1.button("📥 存入") and user['money']>=amt:
            user['money']-=amt; user['bank_deposit']+=amt
            # 觸發任務檢查：普通存錢 & 隱藏777檢查
            check_mission(uid, user, "bank_save")
            st.rerun()
        if b2.button("📤 提款") and user['bank_deposit']>=amt:
            user['bank_deposit']-=amt; user['money']+=amt
            # 觸發任務檢查：隱藏破產/777檢查 (即使提款不是主要任務目標，也會檢查隱藏條件)
            check_mission(uid, user, "bank_withdraw") 
            st.rerun()

def page_shop(uid, user):
    st.title("🛒 地下黑市")
    evt = st.session_state.today_event
    discount = 0.7 if evt["effect"] == "shop_discount" else 1.0
    if discount < 1: st.success("🔥 限時特價中！")

    cols = st.columns(3)
    idx = 0
    for k, v in ITEMS.items():
        price = int(v['price'] * discount)
        with cols[idx%3].container(border=True):
            st.subheader(k)
            st.caption(v['desc'])
            st.write(f"**${price:,}**")
            if st.button("購買", key=f"buy_{k}"):
                if user['money']>=price:
                    user['money']-=price
                    user.setdefault("inventory", {})[k] = user.get("inventory", {}).get(k, 0) + 1
                    # 觸發任務檢查
                    check_mission(uid, user, "shop_buy")
                    st.toast(f"已購買 {k}")
                    time.sleep(0.5); st.rerun()
                else: st.error("現金不足")
        idx+=1

def page_crypto(uid, user):
    st.title("🔐 密碼學中心")
    t1, t2 = st.tabs(["凱薩密碼", "摩斯電碼"])
    with t1:
        txt = st.text_input("輸入文字", "HELLO"); s = st.slider("偏移量", 1, 10, 3)
        res = "".join([chr(ord(c)+s) if c.isalpha() else c for c in txt.upper()])
        st.success(f"加密結果: {res}")
    with t2:
        mt = st.text_input("輸入英文", "SOS").upper()
        res = " ".join([MORSE_CODE_DICT.get(c,c) for c in mt])
        st.code(res)

def page_leaderboard(uid, user):
    st.title("🏆 名人堂")
    db = load_db()
    data = []
    for u_id, u_data in db["users"].items():
        total = u_data.get("money",0) + u_data.get("bank_deposit",0)
        data.append({"User": u_data["name"], "Job": u_data["job"], "Total Assets": total})
    df = pd.DataFrame(data).sort_values(by="Total Assets", ascending=False).reset_index(drop=True)
    df.index += 1
    st.dataframe(df, use_container_width=True)

def page_cli_os(uid, user):
    st.title("💻 駭客終端 (CLI)")
    st.markdown("---")
    
    if "cli_hist" not in st.session_state: st.session_state.cli_hist = ["System Initialized...", "Type 'help' for commands."]
    for l in st.session_state.cli_hist[-8:]: st.code(l, language="bash")
    
    cmd = st.chat_input("輸入指令...")
    if cmd:
        st.session_state.cli_hist.append(f"user@cityos:~$ {cmd}")
        t = cmd.split()
        res = "Unknown command."
        
        # 關鍵：觸發任務檢查 (檢查是否輸入了 sudo su)
        check_mission(uid, user, "cli_input", extra_data=cmd)

        if t[0]=="help": res = "Available: whoami, bal, scan, clear, sudo"
        elif t[0]=="clear": st.session_state.cli_hist=[]; st.rerun()
        elif t[0]=="bal": res = f"Cash: ${user['money']} | Bank: ${user.get('bank_deposit',0)}"
        elif t[0]=="whoami": res = f"User: {user['name']} | Job: {user['job']} | Level: {user['level']}"
        elif t[0]=="scan": res = "Scanning network... Found: Alice, Bob, Frank(Admin)"
        elif t[0]=="sudo" and len(t)>1 and t[1]=="su": res = "ACCESS DENIED. (But... did something unlock?)"
        
        st.session_state.cli_hist.append(res); st.rerun()

# --- 主程式 ---
def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    if "today_event" not in st.session_state: st.session_state.today_event = get_today_event()

    # --- 登入頁面 ---
    if not st.session_state.logged_in:
        st.markdown("<h1 style='text-align: center;'>🏙️ CityOS V18</h1>", unsafe_allow_html=True)
        st.info(f"📅 今日狀態: {st.session_state.today_event['name']} ({st.session_state.today_event['desc']})")
        
        t1, t2 = st.tabs(["登入", "註冊"])
        with t1:
            u = st.text_input("帳號"); p = st.text_input("密碼", type="password")
            if st.button("登入"):
                db = load_db()
                if u in db["users"] and db["users"][u]["password"]==p:
                    st.session_state.logged_in=True
                    st.session_state.user_id=u
                    st.session_state.user_data=db["users"][u]
                    
                    # 登入獎勵 (Mining GPU)
                    if "Mining GPU" in st.session_state.user_data.get("inventory", {}):
                        gpu_count = st.session_state.user_data["inventory"]["Mining GPU"]
                        bonus = gpu_count * 100
                        st.session_state.user_data["money"] += bonus
                        st.toast(f"⛏️ 挖礦收益: +${bonus}")
                        save_db(db)
                    
                    st.rerun()
                else: st.error("登入失敗"); log_intruder(u)
        with t2:
            nu = st.text_input("新帳號"); np = st.text_input("新密碼", type="password")
            if st.button("註冊"):
                db = load_db()
                if nu not in db["users"]:
                    db["users"][nu] = {"password": np, "name": nu, "job": "Novice", "money": 1000, "level": 1, "exp": 0, "bank_deposit": 0, "inventory": {}, "completed_missions": []}
                    save_db(db); st.success("成功！請登入")
                else: st.error("帳號已存在")
        return

    # --- 登入後邏輯 ---
    uid = st.session_state.user_id
    # 強制從 DB 重新讀取最新資料 (避免數據不同步)
    user = st.session_state.user_data if uid == "frank" else load_db()["users"].get(uid, st.session_state.user_data)

    # 側欄導航
    st.sidebar.title(f"🆔 {user['name']}")
    st.sidebar.caption(f"職業: {user['job']} | Lv.{user.get('level',1)}")
    st.sidebar.markdown("---")
    
    menu = {
        "✨ 系統大廳": "dashboard",
        "🎯 任務中心": "missions",
        "📝 每日測驗": "quiz",
        "🏦 賽博銀行": "bank",
        "🛒 地下黑市": "shop",
        "🔬 邏輯實驗": "lab",
        "🔐 密碼學": "crypto",
        "💻 駭客終端": "cli",
        "🏆 名人堂": "leaderboard"
    }
    
    selection = st.sidebar.radio("導航選單", list(menu.keys()))
    page = menu[selection]

    if st.sidebar.button("🚪 安全登出"):
        st.session_state.logged_in=False; st.rerun()

    # 頁面路由
    if page == "dashboard": page_dashboard(uid, user)
    elif page == "missions": page_missions(uid, user)
    elif page == "quiz": page_quiz(uid, user)
    elif page == "bank": page_bank(uid, user)
    elif page == "shop": page_shop(uid, user)
    elif page == "lab": page_digital_lab(uid, user)
    elif page == "crypto": page_crypto(uid, user)
    elif page == "cli": page_cli_os(uid, user)
    elif page == "leaderboard": page_leaderboard(uid, user)

if __name__ == "__main__":
    main()
