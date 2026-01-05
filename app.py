# ==========================================
# 檔案: app.py
# 用途: CityOS 主介面
# ==========================================
import streamlit as st
import random
import time
import pandas as pd
import numpy as np # 用於圖表
from config import CITY_EVENTS, ITEMS, SVG_LIB, MORSE_CODE_DICT
from database import load_db, save_db, check_mission, get_today_event, log_intruder, load_quiz_from_file, load_missions_from_file

st.set_page_config(page_title="CityOS V17.5 Ultra", layout="wide", page_icon="🏙️", initial_sidebar_state="expanded")

# --- CSS 美化 ---
st.markdown("""
<style>
    /* 側欄背景色微調 */
    [data-testid="stSidebar"] { background-color: #121212; }
    /* 按鈕樣式 */
    .stButton>button { border-radius: 8px; border: 1px solid #333; }
    /* 進度條顏色 */
    .stProgress > div > div > div > div { background-color: #00FF00; }
</style>
""", unsafe_allow_html=True)

# --- 頁面模組 ---

def page_dashboard(uid, user):
    st.title("🏙️ CityOS 中央控制台")
    st.caption(f"User: {user['name']} | Status: Online")

    # 分頁設計
    tab1, tab2, tab3 = st.tabs(["📊 系統監控", "📖 系統介紹", "📘 使用手冊"])

    with tab1:
        st.subheader("📡 即時數據監控")
        run = st.checkbox("🔴 啟動即時數據串流 (Live Stream)")
        
        # 預留三個圖表位置
        col1, col2, col3 = st.columns(3)
        with col1: chart1 = st.empty()
        with col2: chart2 = st.empty()
        with col3: chart3 = st.empty()
        
        if run:
            while run:
                # 模擬監控數據
                cpu_data = pd.DataFrame(np.random.randint(10, 60, size=(20, 1)), columns=["CPU Usage %"])
                ram_data = pd.DataFrame(np.random.randint(40, 80, size=(20, 1)), columns=["RAM Usage %"])
                net_data = pd.DataFrame(np.random.randint(200, 800, size=(20, 1)), columns=["Network (Kbps)"])
                
                chart1.line_chart(cpu_data, height=200)
                chart2.area_chart(ram_data, height=200, color="#00FF00")
                chart3.bar_chart(net_data, height=200, color="#FF0000")
                time.sleep(0.8)
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
        * 每天登入領取挖礦收益 (需購買 GPU)。
        * 完成 **[📝 每日測驗]**，答對賺 $300。
        * 完成 **[🎯 任務]**，獎金豐厚。

        **2. 職業與權限**
        * **市民 (Novice)**: 基礎權限。
        * **駭客 (Hacker)**: 可進入 CLI 模式與使用病毒。
        * **工程師 (Engineer)**: 數位實驗室專家。

        **3. 常見指令 (CLI)**
        * `bal`: 查詢餘額
        * `scan`: 掃描區域網路使用者
        * `buy virus`: 快速購買病毒
        """)

def page_missions(uid, user):
    st.title("🎯 任務列表 (外部載入)")
    
    # 從檔案讀取任務
    missions = load_missions_from_file()
    if not missions:
        st.error("❌ 無法讀取 missions.txt，請確認檔案存在。")
        return

    done = user.get("completed_missions", [])
    total = len(missions)
    completed_count = len([m for m in done if m in missions]) # 只計算有效任務
    
    st.progress(completed_count/total if total>0 else 0, text=f"進度: {completed_count}/{total}")
    
    # 顯示任務
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🚧 未完成任務")
        for mid, m in missions.items():
            if mid not in done:
                with st.container(border=True):
                    st.write(f"**{m['title']}**")
                    st.caption(m['desc'])
                    st.write(f"💰 報酬: ${m['reward']}")
    
    with col2:
        st.subheader("✅ 已完成")
        for mid in done:
            if mid in missions:
                m = missions[mid]
                with st.container(border=True):
                    st.write(f"~~{m['title']}~~")
                    st.caption("已領取獎勵")

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
            st.error("錯誤！"); st.session_state.quiz_today_done=True; del st.session_state.current_question; st.rerun()

def page_digital_lab(uid, user):
    st.title("🔬 數位實驗室")
    t1, t2, t3 = st.tabs(["邏輯閘", "K-Map", "格雷碼"])
    with t1:
        g = st.selectbox("Gate", list(SVG_LIB.keys()))
        c1, c2 = st.columns(2)
        a = c1.toggle("A", False); b = c2.toggle("B", False)
        st.markdown(SVG_LIB[g], unsafe_allow_html=True)
        if g and (a or b): check_mission(uid, user, "logic_use")
    with t2:
        st.write("2-Var K-Map")
        if "kmap" not in st.session_state: st.session_state.kmap=[0,0,0,0]
        c1, c2 = st.columns(2)
        c1.write("A=0"); c2.write("A=1")
        if c1.button(f"00: {st.session_state.kmap[0]}"): st.session_state.kmap[0]^=1; st.rerun()
        if c1.button(f"01: {st.session_state.kmap[1]}"): st.session_state.kmap[1]^=1; st.rerun()
        if c2.button(f"10: {st.session_state.kmap[2]}"): st.session_state.kmap[2]^=1; st.rerun()
        if c2.button(f"11: {st.session_state.kmap[3]}"): st.session_state.kmap[3]^=1; st.rerun()
    with t3:
        n = st.slider("Num", 0, 15, 5)
        st.metric("Gray", f"{(n^(n>>1)):04b}")

def page_bank(uid, user):
    st.title("🏦 銀行"); c1, c2 = st.columns(2)
    c1.metric("存款", user.get('bank_deposit',0)); c2.metric("現金", user['money'])
    amt = st.number_input("Amount", 0, 100000)
    if st.button("存入") and user['money']>=amt:
        user['money']-=amt; user['bank_deposit']+=amt; check_mission(uid, user, "bank_save"); st.rerun()

def page_shop(uid, user):
    st.title("🛒 黑市"); cols = st.columns(3); i=0
    for k, v in ITEMS.items():
        with cols[i%3].container(border=True):
            st.write(f"**{k}** (${v['price']})"); st.caption(v['desc'])
            if st.button("Buy", key=k) and user['money']>=v['price']:
                user['money']-=v['price']; check_mission(uid, user, "shop_buy"); st.toast("Bought!"); st.rerun()
        i+=1

def page_crypto(uid, user):
    st.title("🔐 密碼學"); t1, t2 = st.tabs(["凱薩", "摩斯"])
    with t1:
        txt = st.text_input("Text", "ABC"); s = st.slider("Shift", 1, 10, 1)
        res = "".join([chr(ord(c)+s) if c.isalpha() else c for c in txt])
        st.success(res)
    with t2:
        mt = st.text_input("Morse", "SOS").upper()
        st.code(" ".join([MORSE_CODE_DICT.get(c,c) for c in mt]))

def page_leaderboard(uid, user):
    st.title("🏆 排行榜"); db=load_db()
    data = [{"Name": v['name'], "Money": v['money']} for v in db["users"].values()]
    st.dataframe(pd.DataFrame(data).sort_values("Money", ascending=False), use_container_width=True)

def page_cli_os(uid, user):
    st.title("💻 CLI"); cmd=st.chat_input("cmd...")
    if "hist" not in st.session_state: st.session_state.hist=[]
    if cmd: st.session_state.hist.append(f"$ {cmd}"); st.rerun()
    for l in st.session_state.hist: st.text(l)

# --- 主程式 ---
def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    if "today_event" not in st.session_state: st.session_state.today_event = get_today_event()

    if not st.session_state.logged_in:
        st.markdown("<h1 style='text-align: center;'>🏙️ CityOS V17.5</h1>", unsafe_allow_html=True)
        st.info(f"📅 Status: {st.session_state.today_event['name']}")
        u = st.text_input("User"); p = st.text_input("Pass", type="password")
        if st.button("Login"):
            db = load_db()
            if u in db["users"] and db["users"][u]["password"]==p:
                st.session_state.logged_in=True; st.session_state.user_id=u; st.session_state.user_data=db["users"][u]; st.rerun()
            else: st.error("Error")
        return

    uid = st.session_state.user_id
    user = st.session_state.user_data if uid == "frank" else load_db()["users"].get(uid, st.session_state.user_data)

    # 側欄美化導航
    st.sidebar.title(f"🆔 {user['name']}")
    st.sidebar.success(f"{user['job']}")
    
    pages = {
        "✨ 大廳": "dash", "🎯 任務": "miss", "📝 測驗": "quiz", 
        "🏦 銀行": "bank", "🛒 黑市": "shop", "🔬 實驗": "lab", 
        "🔐 密碼": "cryp", "🏆 排行": "lead", "💻 CLI": "cli"
    }
    
    sel = st.sidebar.radio("Navigation", list(pages.keys()))
    
    if st.sidebar.button("登出"): st.session_state.logged_in=False; st.rerun()

    p = pages[sel]
    if p=="dash": page_dashboard(uid, user)
    elif p=="miss": page_missions(uid, user)
    elif p=="quiz": page_quiz(uid, user)
    elif p=="bank": page_bank(uid, user)
    elif p=="shop": page_shop(uid, user)
    elif p=="lab": page_digital_lab(uid, user)
    elif p=="cryp": page_crypto(uid, user)
    elif p=="lead": page_leaderboard(uid, user)
    elif p=="cli": page_cli_os(uid, user)

if __name__ == "__main__":
    main()
