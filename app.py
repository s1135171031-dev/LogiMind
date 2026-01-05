# ==========================================
# 檔案名稱: app.py
# 用途: CityOS 主程式 (含動態圖表、美化側欄、完整功能)
# ==========================================
import streamlit as st
import random
import time
import pandas as pd
import numpy as np # 新增：用於生成圖表數據
from config import CITY_EVENTS, MISSIONS, ITEMS, SVG_LIB, MORSE_CODE_DICT
from database import load_db, save_db, init_db, check_mission, get_today_event, get_admin_data, log_intruder, load_quiz_from_file

st.set_page_config(page_title="CityOS V17.0 Ultra", layout="wide", page_icon="🏙️", initial_sidebar_state="expanded")

# --- CSS 美化注入 (讓側欄稍微好看一點) ---
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-color: #1E1E1E;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- 功能頁面模組 ---

def page_dashboard(uid, user):
    st.title("🏙️ CityOS 中央控制台")
    st.caption(f"歡迎回來，{user['name']}。系統運行正常。")

    # 建立分頁
    tab1, tab2, tab3 = st.tabs(["📊 即時監控", "📖 系統介紹", "📘 使用手冊"])

    with tab1:
        st.write("### 📡 系統狀態監控")
        st.info("提示：勾選下方「啟動監控」可檢視即時動態數據 (每秒更新)。")
        
        # 動態圖表區
        run_monitor = st.checkbox("🔴 啟動即時監控 (Live Monitor)")
        
        # 預留圖表位置
        col1, col2, col3 = st.columns(3)
        with col1: chart1 = st.empty()
        with col2: chart2 = st.empty()
        with col3: chart3 = st.empty()
        
        if run_monitor:
            # 模擬即時數據迴圈
            while run_monitor:
                # 產生隨機數據
                data_cpu = pd.DataFrame(np.random.randint(10, 90, size=(20, 1)), columns=["CPU %"])
                data_mem = pd.DataFrame(np.random.randint(30, 70, size=(20, 1)), columns=["RAM %"])
                data_net = pd.DataFrame(np.random.randint(100, 1000, size=(20, 1)), columns=["Net (Kbps)"])
                
                # 更新圖表
                chart1.line_chart(data_cpu, height=200)
                chart2.line_chart(data_mem, height=200)
                chart3.area_chart(data_net, height=200)
                
                time.sleep(1) # 每秒更新
        else:
            # 靜態顯示 (當沒勾選時)
            st.warning("監控已暫停。請勾選上方選項以啟動。")
            chart1.metric("CPU Load", "12%", "Idle")
            chart2.metric("Memory", "4.2 GB", "Stable")
            chart3.metric("Network", "0 Kbps", "Offline")

    with tab2:
        st.markdown("""
        ### 關於 CityOS
        CityOS 是一個模擬賽博龐克風格的城市作業系統。
        結合了 **數位邏輯**、**密碼學**、**經濟系統** 與 **角色扮演**。
        
        **核心特色：**
        * **職業系統**：從市民到駭客，不同職業解鎖不同功能。
        * **經濟循環**：透過銀行生息、測驗賺錢、黑市消費。
        * **教育意義**：內建邏輯閘、卡諾圖、格雷碼等教學工具。
        """)

    with tab3:
        st.markdown("""
        ### 📘 使用者操作手冊
        
        **1. 賺錢方式**
        * 前往 **[📝 每日測驗]** 回答問題。
        * 前往 **[🏦 銀行]** 存錢領利息。
        * 購買 **[Mining GPU]** 每日領取分紅。

        **2. 職業晉升**
        * 累積經驗值 (EXP) 可升級。
        * 特定道具可解鎖新職業權限（開發中）。

        **3. 黑市與道具**
        * **Trojan Virus**: 用於駭客攻擊任務。
        * **Quantum Key**: 收藏品，象徵身分。
        
        **4. 忘記密碼？**
        * 請聯繫系統管理員 (Frank)。
        """)

def page_crypto(uid, user):
    st.title("🔐 密碼學中心")
    st.caption("僅供學術研究，嚴禁非法用途。")
    tab1, tab2, tab3 = st.tabs(["🔢 進位轉換", "📜 凱薩密碼", "📡 摩斯電碼"])

    with tab1:
        val = st.text_input("輸入十進位數字", "255")
        if val.isdigit():
            n = int(val)
            c1, c2, c3 = st.columns(3)
            c1.metric("Binary (2)", f"{n:b}")
            c2.metric("Octal (8)", f"{n:o}")
            c3.metric("Hex (16)", f"{n:X}")

    with tab2:
        text = st.text_input("輸入英文文字", "HELLO").upper()
        shift = st.slider("位移量 (Shift)", 1, 25, 3)
        res = ""
        for char in text:
            if char.isalpha():
                code = ord(char) + shift
                if code > ord('Z'): code -= 26
                res += chr(code)
            else: res += char
        st.success(f"加密結果: {res}")

    with tab3:
        m_text = st.text_input("輸入文字轉摩斯", "SOS").upper()
        if st.button("轉換 & 模擬訊號"):
            morse_res = " ".join([MORSE_CODE_DICT.get(c, c) for c in m_text])
            st.code(morse_res)
            vis = "".join(["🔴" if m=="-" else "🟢" if m=="." else " " for m in morse_res])
            st.write(f"光訊號: {vis}")

def page_quiz(uid, user):
    st.title("📝 每日工程測驗")
    
    if "quiz_today_done" not in st.session_state: st.session_state.quiz_today_done = False
    if st.session_state.quiz_today_done:
        st.info("✅ 您今天已經完成測驗了，請明天再來！")
        return

    if "current_question" not in st.session_state:
        all_qs = load_quiz_from_file() # 從 questions.txt 讀取
        if not all_qs:
            st.error("❌ 題庫檔案 (questions.txt) 讀取失敗或為空。")
            return
        st.session_state.current_question = random.choice(all_qs)

    q = st.session_state.current_question
    st.write(f"### Q: {q['q']}")
    st.caption(f"ID: {q['id']} | 難度: {q['level']}")
    choice = st.radio("選擇答案:", q['options'], key="q_radio")
    
    if st.button("提交答案"):
        if choice == q['ans']:
            st.balloons()
            st.success(f"正確！ 答案是 {q['ans']}")
            user["money"] += 300; user["exp"] += 50
            check_mission(uid, user, "quiz_done")
            if uid != "frank": save_db({"users": load_db()["users"] | {uid: user}, "bbs": []})
            st.session_state.quiz_today_done = True
            del st.session_state.current_question
            st.rerun()
        else:
            st.error("錯誤！系統鎖定。")
            st.session_state.quiz_today_done = True
            del st.session_state.current_question
            st.rerun()

def page_digital_lab(uid, user):
    st.title("🔬 數位邏輯實驗室")
    tab1, tab2, tab3 = st.tabs(["🔌 邏輯閘", "🗺️ 卡諾圖 (K-Map)", "🔄 格雷碼"])
    
    with tab1:
        gate = st.selectbox("選擇元件", list(SVG_LIB.keys()))
        c1, c2 = st.columns(2)
        a = c1.toggle("Input A (1)", False); b = c2.toggle("Input B (1)", False)
        res = 0
        if gate=="AND": res = 1 if (a and b) else 0
        elif gate=="OR": res = 1 if (a or b) else 0
        elif gate=="XOR": res = 1 if (a != b) else 0
        elif gate=="NOT": res = 0 if a else 1
        elif gate=="NAND": res = 0 if (a and b) else 1
        elif gate=="NOR": res = 0 if (a or b) else 1
        st.markdown(SVG_LIB[gate], unsafe_allow_html=True); st.metric("Output", res)
        if gate and (a or b): check_mission(uid, user, "logic_use")

    with tab2:
        st.subheader("2-Var K-Map")
        if "kmap" not in st.session_state: st.session_state.kmap = [0,0,0,0]
        c1, c2 = st.columns(2)
        with c1: 
            st.write("A=0")
            if st.button(f"00: {st.session_state.kmap[0]}", key="k0"): st.session_state.kmap[0]^=1; st.rerun()
            if st.button(f"01: {st.session_state.kmap[1]}", key="k1"): st.session_state.kmap[1]^=1; st.rerun()
        with c2: 
            st.write("A=1")
            if st.button(f"10: {st.session_state.kmap[2]}", key="k2"): st.session_state.kmap[2]^=1; st.rerun()
            if st.button(f"11: {st.session_state.kmap[3]}", key="k3"): st.session_state.kmap[3]^=1; st.rerun()
        ones = [i for i, x in enumerate(st.session_state.kmap) if x == 1]
        st.code(f"Minterms Σm: {ones}", language="text")

    with tab3:
        num = st.slider("Decimal (0-15)", 0, 15, 3)
        st.metric("Gray Code", f"{(num^(num>>1)):04b}")

def page_bank(uid, user):
    st.title("🏦 賽博銀行")
    c1, c2 = st.columns(2)
    c1.metric("存款", f"${user.get('bank_deposit',0):,}"); c2.metric("現金", f"${user['money']:,}")
    with st.expander("存提款操作", expanded=True):
        amt = st.number_input("金額", 0, 1000000, 100)
        b1, b2 = st.columns(2)
        if b1.button("📥 存入") and user['money'] >= amt:
            user['money'] -= amt; user['bank_deposit'] += amt
            check_mission(uid, user, "bank_save")
            if uid!="frank": save_db({"users":load_db()["users"]|{uid:user}, "bbs": []})
            st.rerun()
        if b2.button("📤 提款") and user['bank_deposit'] >= amt:
            user['bank_deposit'] -= amt; user['money'] += amt
            if uid!="frank": save_db({"users":load_db()["users"]|{uid:user}, "bbs": []})
            st.rerun()

def page_shop(uid, user):
    st.title("🛒 地下黑市")
    evt = st.session_state.today_event
    discount = 0.7 if evt["effect"] == "shop_discount" else 1.0
    if discount < 1: st.success("🔥 限時特價中！")
    
    cols = st.columns(3)
    idx = 0
    for item, info in ITEMS.items():
        price = int(info['price'] * discount)
        with cols[idx%3].container(border=True):
            st.subheader(item)
            st.caption(info['desc'])
            st.write(f"**${price:,}**")
            if st.button("購買", key=f"buy_{item}"):
                if user['money'] >= price:
                    user['money'] -= price; user.setdefault("inventory", {})[item] = user.get("inventory", {}).get(item, 0) + 1
                    check_mission(uid, user, "shop_buy")
                    if uid!="frank": save_db({"users":load_db()["users"]|{uid:user}, "bbs": []})
                    st.toast(f"已購買 {item}")
                    time.sleep(0.5); st.rerun()
                else: st.error("現金不足")
        idx+=1

def page_leaderboard(uid, user):
    st.title("🏆 名人堂")
    db = load_db()
    data = []
    for u_id, u_data in db["users"].items():
        data.append({"User": u_data["name"], "Job": u_data["job"], "Total Assets": u_data.get("money",0)+u_data.get("bank_deposit",0)})
    df = pd.DataFrame(data).sort_values(by="Total Assets", ascending=False).reset_index(drop=True)
    df.index += 1
    st.dataframe(df, use_container_width=True)

def page_cli_os(uid, user):
    st.title("💻 駭客終端 (CLI)")
    st.markdown("---")
    if "cli_hist" not in st.session_state: st.session_state.cli_hist = ["System Initialized..."]
    for l in st.session_state.cli_hist[-8:]: st.code(l, language="bash")
    
    cmd = st.chat_input("輸入指令 (help, bal, whoami, clear)...")
    if cmd:
        st.session_state.cli_hist.append(f"user@cityos:~$ {cmd}")
        t = cmd.split()
        res = "Unknown command."
        if t[0]=="help": res = "Available: whoami, bal, scan, clear"
        elif t[0]=="clear": st.session_state.cli_hist=[]; st.rerun()
        elif t[0]=="bal": res = f"Cash: ${user['money']}"
        elif t[0]=="whoami": res = f"User: {user['name']} | Job: {user['job']}"
        st.session_state.cli_hist.append(res); st.rerun()

# --- 主程式 ---
def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    if "today_event" not in st.session_state: st.session_state.today_event = get_today_event()

    if not st.session_state.logged_in:
        st.markdown("<h1 style='text-align: center;'>🏙️ CityOS V17</h1>", unsafe_allow_html=True)
        st.info(f"📅 今日狀態: {st.session_state.today_event['name']}")
        
        t1, t2 = st.tabs(["登入", "註冊"])
        with t1:
            u = st.text_input("帳號"); p = st.text_input("密碼", type="password")
            if st.button("登入"):
                db = load_db()
                if u in db["users"] and db["users"][u]["password"]==p:
                    st.session_state.logged_in=True; st.session_state.user_id=u; st.session_state.user_data=db["users"][u]; st.rerun()
                else: st.error("登入失敗"); log_intruder(u)
        with t2:
            nu = st.text_input("新帳號"); np = st.text_input("新密碼", type="password")
            if st.button("註冊"):
                db = load_db()
                if nu not in db["users"]:
                    db["users"][nu] = {"password": np, "name": nu, "job": "Novice", "money": 1000, "level": 1, "exp": 0, "bank_deposit": 0, "inventory": {}, "completed_missions": []}
                    save_db(db); st.success("成功！請登入")
        return

    uid = st.session_state.user_id
    user = st.session_state.user_data if uid == "frank" else load_db()["users"].get(uid, st.session_state.user_data)

    # --- 側欄美化 ---
    st.sidebar.title(f"🆔 {user['name']}")
    st.sidebar.caption(f"職業: {user['job']} | Lv.{user.get('level',1)}")
    st.sidebar.markdown("---")
    
    # 使用 Emoji 做視覺引導
    menu_map = {
        "✨ 系統大廳": "dashboard",
        "📝 每日測驗": "quiz",
        "🏦 賽博銀行": "bank",
        "🛒 地下黑市": "shop",
        "🔬 邏輯實驗室": "lab",
        "🔐 密碼學中心": "crypto",
        "💻 駭客終端": "cli",
        "🏆 名人堂": "leaderboard",
        "🎯 任務列表": "missions"
    }
    
    selection = st.sidebar.radio("導航選單", list(menu_map.keys()))
    page = menu_map[selection]

    if st.sidebar.button("🚪 安全登出"):
        st.session_state.logged_in=False; st.rerun()

    # 路由
    if page == "dashboard": page_dashboard(uid, user)
    elif page == "quiz": page_quiz(uid, user)
    elif page == "bank": page_bank(uid, user)
    elif page == "shop": page_shop(uid, user)
    elif page == "lab": page_digital_lab(uid, user)
    elif page == "crypto": page_crypto(uid, user)
    elif page == "cli": page_cli_os(uid, user)
    elif page == "leaderboard": page_leaderboard(uid, user)
    elif page == "missions": 
        st.title("🎯 任務列表")
        done = user.get("completed_missions", [])
        st.progress(len(done)/len(MISSIONS), text=f"進度 {len(done)}/{len(MISSIONS)}")
        for mid, m in MISSIONS.items():
            icon = "✅" if mid in done else "⬜"
            st.write(f"### {icon} {m['title']}")
            st.caption(m['desc'] + f" (獎金 ${m['reward']})")

if __name__ == "__main__":
    main()
