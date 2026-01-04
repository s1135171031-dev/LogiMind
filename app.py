import streamlit as st
import pandas as pd
import random
import os
import time
import json
import numpy as np
from datetime import datetime, date

# ==============================================================================
# 1. 系統設定 & 資源庫
# ==============================================================================
st.set_page_config(
    page_title="CityOS V14.0 Renaissance",
    layout="wide",
    page_icon="🏙️",
    initial_sidebar_state="expanded"
)

USER_DB_FILE = "cityos_users.json"
LOG_FILE = "intruder_log.txt"

# --- SVG 資源 (邏輯閘) ---
SVG_LIB = {
    "AND": '''<svg width="150" height="80"><path d="M20,10 L70,10 C95,10 110,30 110,40 C110,50 95,70 70,70 L20,70 Z" fill="none" stroke="#00FF00" stroke-width="3"/><path d="M0,25 L20,25 M0,55 L20,55 M110,40 L140,40" stroke="#00FF00" stroke-width="3"/><text x="40" y="45" fill="white" font-family="monospace">AND</text></svg>''',
    "OR": '''<svg width="150" height="80"><path d="M20,10 L60,10 Q90,40 60,70 L20,70 Q45,40 20,10 Z" fill="none" stroke="#00FF00" stroke-width="3"/><path d="M0,25 L25,25 M0,55 L25,55 M90,40 L120,40" stroke="#00FF00" stroke-width="3"/><text x="35" y="45" fill="white" font-family="monospace">OR</text></svg>''',
    "XOR": '''<svg width="150" height="80"><path d="M35,10 L75,10 Q105,40 75,70 L35,70 Q60,40 35,10 Z" fill="none" stroke="#00FF00" stroke-width="3"/><path d="M15,10 Q40,40 15,70" fill="none" stroke="#00FF00" stroke-width="3"/><path d="M0,25 L25,25 M0,55 L25,55 M105,40 L135,40" stroke="#00FF00" stroke-width="3"/><text x="50" y="45" fill="white" font-family="monospace">XOR</text></svg>''',
    "NOT": '''<svg width="150" height="80"><path d="M30,10 L30,70 L90,40 Z" fill="none" stroke="#00FF00" stroke-width="3"/><circle cx="96" cy="40" r="5" fill="none" stroke="#00FF00" stroke-width="2"/><path d="M0,40 L30,40 M102,40 L130,40" stroke="#00FF00" stroke-width="3"/><text x="40" y="45" fill="white" font-family="monospace">NOT</text></svg>'''
}

# --- 摩斯密碼表 ---
MORSE_CODE_DICT = { 'A':'.-', 'B':'-...', 'C':'-.-.', 'D':'-..', 'E':'.', 'F':'..-.', 'G':'--.', 'H':'....', 'I':'..', 'J':'.---', 'K':'-.-', 'L':'.-..', 'M':'--', 'N':'-.', 'O':'---', 'P':'.--.', 'Q':'--.-', 'R':'.-.', 'S':'...', 'T':'-', 'U':'..-', 'V':'...-', 'W':'.--', 'X':'-..-', 'Y':'-.--', 'Z':'--..', '1':'.----', '2':'..---', '3':'...--', '4':'....-', '5':'.....', '6':'-....', '7':'--...', '8':'---..', '9':'----.', '0':'-----', ', ':'--..--', '.':'.-.-.-', '?':'..--..', '/':'-..-.', '-':'-....-', '(':'-.--.', ')':'-.--.-'}

# --- 職業與權限 ---
CLASSES = {
    "Novice": {"name": "一般市民", "icon": "👤", "desc": "權限受限。請盡快轉職。", "unlocks": []},
    "Engineer": {"name": "硬體工程師", "icon": "🔧", "desc": "解鎖：[數位實驗室-邏輯/格雷碼/卡諾圖]、[挖礦加成]。", "unlocks": ["DigitalLab", "MiningBonus"]},
    "Programmer": {"name": "軟體工程師", "icon": "💻", "desc": "解鎖：[密碼學中心-凱薩/摩斯]、[進位轉換]。", "unlocks": ["CryptoLab", "BaseConverter"]},
    "Hacker": {"name": "資安專家", "icon": "🛡️", "desc": "解鎖：[駭客終端]、[黑市借貸]。", "unlocks": ["Terminal"]},
    "Architect": {"name": "系統創造者", "icon": "👑", "desc": "全知全能。", "unlocks": ["All"]}
}

# ==============================================================================
# 2. 資料庫邏輯 (Backend)
# ==============================================================================

def get_admin_data():
    """ 生成最高指揮官 Frank 的資料 (記憶體中生成，不一定依賴檔案) """
    return {
        "password": "x", # 實際登入用 x12345678x 判斷，這裡僅為佔位符
        "name": "Frank (Supreme Commander)", 
        "level": 100, "exp": 999999, "money": 9999999, "bank_deposit": 50000000,
        "job": "Architect", "inventory": ["RTX 4090", "Quantum CPU"], "mining_balance": 100.0,
        "last_quiz_date": "", "quiz_attempts": 0, "bio": "The Architect of CityOS.", "debt": 0,
        "mails": [{"sender":"System", "title":"Root Access Granted", "content":"Welcome back, Commander."}]
    }

def get_npc_data(name, job, level, money):
    return {
        "password": "npc", "name": name, 
        "level": level, "exp": level*100, "money": money, "bank_deposit": money*2,
        "job": job, "inventory": [], "mining_balance": 0.0, "debt": 0, "bio": "City Resident", "mails": []
    }

def init_db():
    if not os.path.exists(USER_DB_FILE):
        users = {
            "alice": get_npc_data("Alice", "Hacker", 15, 8000),
            "bob": get_npc_data("Bob", "Engineer", 10, 3500),
            "charlie": get_npc_data("Charlie", "Programmer", 22, 15000)
        }
        with open(USER_DB_FILE, "w", encoding="utf-8") as f:
            json.dump({"users": users}, f, ensure_ascii=False, indent=4)

def load_db():
    init_db()
    try:
        with open(USER_DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"users": {}}

def save_db(data):
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def check_level_up(user):
    cur, exp = user.get("level", 1), user.get("exp", 0)
    new_lvl = 1 + (exp // 200) # 經驗值曲線
    if new_lvl > cur: user["level"] = new_lvl; return True, new_lvl
    return False, cur

def log_intruder(username):
    """將失敗的登入嘗試寫入一般文檔"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] Unauthorized Access Attempt - User: {username}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Log Error: {e}")

# ==============================================================================
# 3. 核心功能模組
# ==============================================================================

# --- [模組 A] 數位實驗室 (Logic, Gray, K-Map) ---
def page_digital_lab():
    st.title("🔬 數位邏輯實驗室")
    st.caption("硬體工程師的聖地：探索電路與邏輯的奧秘")
    
    tab1, tab2, tab3 = st.tabs(["🔌 邏輯閘視覺化", "🧬 格雷碼 (Gray Code)", "🗺️ 卡諾圖 (K-Map)"])
    
    with tab1: # Logic Gates
        c1, c2 = st.columns([1, 2])
        with c1:
            gate = st.selectbox("選擇元件", list(SVG_LIB.keys()))
            st.write("輸入訊號:")
            col_a, col_b = st.columns(2)
            a = col_a.toggle("Input A", value=False)
            b = False
            if gate != "NOT": b = col_b.toggle("Input B", value=False)
            
            res = 0
            if gate=="AND": res=1 if a and b else 0
            elif gate=="OR": res=1 if a or b else 0
            elif gate=="XOR": res=1 if a!=b else 0
            elif gate=="NOT": res=0 if a else 1
            
            st.metric("Output", res)
        with c2:
            st.markdown(SVG_LIB[gate], unsafe_allow_html=True)
            # 真值表生成
            st.caption("即時真值表")
            if gate=="NOT": df=pd.DataFrame({"A":[0,1],"Out":[1,0]})
            elif gate=="AND": df=pd.DataFrame({"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,0,0,1]})
            elif gate=="OR": df=pd.DataFrame({"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,1,1,1]})
            elif gate=="XOR": df=pd.DataFrame({"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,1,1,0]})
            
            def highlight(row):
                match = False
                if gate=="NOT": match = (row['A']==int(a))
                else: match = (row['A']==int(a) and row['B']==int(b))
                return ['background-color: #333300' if match else '' for _ in row]
            st.dataframe(df.style.apply(highlight, axis=1), use_container_width=True, hide_index=True)

    with tab2: # Gray Code
        st.subheader("格雷碼轉換器")
        st.write("格雷碼特性：相鄰兩個數值之間，只有一個 Bit 發生變化。")
        val = st.number_input("輸入十進位整數", 0, 255, 0)
        
        gray = val ^ (val >> 1)
        bin_str = format(val, '08b')
        gray_str = format(gray, '08b')
        
        c1, c2 = st.columns(2)
        c1.metric("二進位 (Binary)", bin_str)
        c2.metric("格雷碼 (Gray)", gray_str)
        
        # 視覺化比較
        st.write("Bit 變化視覺化:")
        viz_data = pd.DataFrame({"Bit Index":[7,6,5,4,3,2,1,0], "Binary":list(bin_str), "Gray":list(gray_str)})
        st.dataframe(viz_data.T)

    with tab3: # Karnaugh Map (2 Variables Simplified)
        st.subheader("卡諾圖 (2變數範例)")
        st.write("設定真值表輸出 (F)：")
        
        col_k1, col_k2, col_k3, col_k4 = st.columns(4)
        out_00 = col_k1.checkbox("A=0, B=0", False)
        out_01 = col_k2.checkbox("A=0, B=1", False)
        out_10 = col_k3.checkbox("A=1, B=0", False)
        out_11 = col_k4.checkbox("A=1, B=1", False)
        
        # 建構 K-Map Dataframe
        kmap_data = pd.DataFrame(
            [[int(out_00), int(out_10)], [int(out_01), int(out_11)]],
            columns=["A=0", "A=1"],
            index=["B=0", "B=1"]
        )
        st.write("### K-Map Grid")
        st.table(kmap_data)
        
        # 簡單的 SOP (Sum of Products) 分析
        terms = []
        if out_00: terms.append("A'B'")
        if out_01: terms.append("A'B")
        if out_10: terms.append("AB'")
        if out_11: terms.append("AB")
        
        sop = " + ".join(terms) if terms else "0"
        st.info(f"布林代數表示式 (SOP): F = {sop}")

# --- [模組 B] 密碼學與運算中心 (Caesar, Morse, Base) ---
def page_crypto_lab():
    st.title("🔐 密碼學與運算中心")
    st.caption("軟體工程師的武器：數據加密、解密與進位轉換")
    
    tab1, tab2, tab3 = st.tabs(["🔢 進位轉換", "🏛️ 凱薩密碼", "📻 摩斯密碼"])
    
    with tab1: # Base Converter
        val = st.number_input("輸入十進位 (Decimal)", value=255)
        c1, c2, c3 = st.columns(3)
        c1.code(f"HEX: {hex(val).upper().replace('0X','')}")
        c2.code(f"BIN: {bin(val).replace('0b','')}")
        c3.code(f"OCT: {oct(val).replace('0o','')}")

    with tab2: # Caesar Cipher
        st.subheader("凱薩密碼 (Caesar Cipher)")
        mode = st.radio("模式", ["加密 (Encrypt)", "解密 (Decrypt)"], horizontal=True)
        text = st.text_input("輸入文字 (限英文字母)", "HELLO CITYOS")
        shift = st.slider("位移量 (Shift)", 1, 25, 3)
        
        result = ""
        for char in text.upper():
            if char.isalpha():
                start = ord('A')
                offset = shift if "加密" in mode else -shift
                result += chr((ord(char) - start + offset) % 26 + start)
            else:
                result += char
        st.success(f"結果: {result}")

    with tab3: # Morse Code
        st.subheader("摩斯密碼 (Morse Code)")
        m_mode = st.radio("功能", ["文字轉摩斯", "摩斯轉文字"], horizontal=True)
        m_input = st.text_input("輸入內容", "SOS" if "文字" in m_mode else "... --- ...")
        
        m_res = ""
        if "文字轉摩斯" in m_mode:
            for char in m_input.upper():
                m_res += MORSE_CODE_DICT.get(char, '?') + " "
        else:
            # 簡單的反向查找
            rev_dict = {v: k for k, v in MORSE_CODE_DICT.items()}
            for code in m_input.split(" "):
                m_res += rev_dict.get(code, '?')
        
        st.code(m_res, language="text")
        if st.button("🔊 發送訊號 (模擬)"):
            st.toast("正在透過無線電發送...", icon="📡")

# --- [模組 C] 生活與經濟 (Bank, Mail, Mining) ---
def page_bank(uid, user):
    st.title("🏦 賽博銀行 (Cyber Bank)")
    balance = user.get("bank_deposit", 0)
    debt = user.get("debt", 0)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("存款餘額", f"${balance:,}", delta="年利率 1.5%")
    c2.metric("現金", f"${user['money']:,}")
    c3.metric("負債", f"${debt:,}", delta_color="inverse")
    
    with st.expander("💳 存提款服務", expanded=True):
        c_in, c_out = st.columns(2)
        with c_in:
            amt_in = st.number_input("存款金額", 0, user['money'], 0, step=100)
            if st.button("存入"):
                user['money']-=amt_in; user['bank_deposit']+=amt_in; 
                if uid != "frank": save_db({"users":load_db()["users"]|{uid:user}})
                st.rerun()
        with c_out:
            amt_out = st.number_input("提款金額", 0, balance, 0, step=100)
            if st.button("提領"):
                user['bank_deposit']-=amt_out; user['money']+=amt_out;
                if uid != "frank": save_db({"users":load_db()["users"]|{uid:user}})
                st.rerun()
    
    if user["job"] in ["Hacker", "Architect"]:
        st.markdown("### 🕶️ 地下錢莊 (Black Market)")
        if st.button("借款 $5,000 (利息20%)"):
            user['money']+=5000; user['debt']+=6000
            if uid != "frank": save_db({"users":load_db()["users"]|{uid:user}})
            st.warning("款項已匯入。別想跑路。"); st.rerun()
        if debt > 0 and st.button("還清債務"):
            if user['money'] >= debt:
                user['money']-=debt; user['debt']=0
                if uid != "frank": save_db({"users":load_db()["users"]|{uid:user}})
                st.success("算你識相。"); st.rerun()
            else: st.error("錢不夠！")

def page_mail_system(uid, user):
    st.title("📩 系統信箱")
    if not user.get("mails"): st.info("目前沒有新郵件。")
    
    for i, mail in enumerate(user.get("mails", [])):
        with st.chat_message("assistant" if mail['sender']=="System" else "user"):
            st.write(f"**From: {mail['sender']}** | {mail['title']}")
            st.write(mail['content'])
            if st.button(f"刪除 #{i}", key=f"m_{i}"):
                del user["mails"][i]
                if uid != "frank": save_db({"users":load_db()["users"]|{uid:user}})
                st.rerun()

def page_leaderboard(uid):
    st.title("🏆 CityOS 名人堂")
    db = load_db()
    data = []
    # 如果 Frank 在線，手動加入 Frank 到排行榜展示
    if uid == "frank":
        f_data = get_admin_data()
        data.append({"User": "👑 Frank", "Level": 100, "Net Worth": f_data['money'] + f_data['bank_deposit']})
        
    for u_id, u in db["users"].items():
        total = u.get("money",0) + u.get("bank_deposit",0) - u.get("debt",0)
        data.append({"User": f"{CLASSES.get(u.get('job'),CLASSES['Novice'])['icon']} {u['name']}", "Level": u.get('level',1), "Net Worth": total})
    
    df = pd.DataFrame(data).sort_values("Net Worth", ascending=False).reset_index(drop=True)
    df.index += 1
    st.dataframe(df, use_container_width=True)

# --- [模組 D] 日常 (Mining, Quiz, Career) ---
def page_daily_quiz(uid, user):
    st.header("📝 每日工程師測驗")
    today = str(date.today())
    if user.get("last_quiz_date") != today:
        user["last_quiz_date"]=today; user["quiz_attempts"]=0
        if uid != "frank": save_db({"users":load_db()["users"]|{uid:user}})
    
    left = 3 - user.get("quiz_attempts", 0)
    if "quiz_st" not in st.session_state: st.session_state.quiz_st = "LOBBY"

    if st.session_state.quiz_st == "LOBBY":
        st.metric("今日剩餘機會", left)
        if left > 0:
            if st.button("🚀 開始測驗", type="primary"):
                st.session_state.qs = [
                    {"q":"ASCII Code 中，'A' 的十進位是多少?", "o":["65","97","64","32"], "a":"65"},
                    {"q":"摩斯密碼 '...' 代表什麼字母?", "o":["S","O","H","E"], "a":"S"},
                    {"q":"格雷碼的主要應用是?", "o":["減少誤差","加密","壓縮","傳輸"], "a":"減少誤差"}
                ]
                st.session_state.q_idx=0; st.session_state.score=0; st.session_state.quiz_st="PLAY"; st.rerun()
        else: st.warning("明日請早。")

    elif st.session_state.quiz_st == "PLAY":
        q = st.session_state.qs[st.session_state.q_idx]
        st.subheader(f"Q: {q['q']}")
        ans = st.radio("Ans", q['o'], key=f"q{st.session_state.q_idx}")
        if st.button("送出"):
            if ans==q['a']: st.session_state.score+=1; st.toast("✅ 正確")
            else: st.toast("❌ 錯誤")
            time.sleep(0.5)
            if st.session_state.q_idx < 2: st.session_state.q_idx+=1; st.rerun()
            else: st.session_state.quiz_st="END"; st.rerun()

    elif st.session_state.quiz_st == "END":
        reward = st.session_state.score * 50
        st.success(f"測驗結束！獲得 ${reward}")
        if st.button("領取"):
            user["money"]+=reward; user["exp"]+=reward; user["quiz_attempts"]+=1
            check_level_up(user)
            if uid != "frank": save_db({"users":load_db()["users"]|{uid:user}})
            st.session_state.quiz_st="LOBBY"; st.rerun()

def page_career(uid, user):
    st.title("🏹 轉職中心")
    curr = user.get("job","Novice")
    
    cols = st.columns(2)
    idx = 0
    for k, v in CLASSES.items():
        if k == "Novice": continue
        if k == "Architect" and uid != "frank": continue # Hide God Mode
        
        with cols[idx%2]:
            with st.container(border=True):
                st.markdown(f"### {v['icon']} {v['name']}")
                st.caption(v['desc'])
                if curr == k: st.button("當前職業", disabled=True, key=k)
                elif user["level"] >= 5 or uid == "frank":
                    if st.button("轉職", key=k):
                        user["job"]=k
                        if uid != "frank": save_db({"users":load_db()["users"]|{uid:user}})
                        st.balloons(); st.rerun()
                else: st.button("Lv.5 解鎖", disabled=True, key=k)
        idx+=1

# ==============================================================================
# 4. 主程式架構 - (含後門判斷與註冊限制)
# ==============================================================================
def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False

    # --- 登入/註冊 畫面 ---
    if not st.session_state.logged_in:
        st.markdown("<h1 style='text-align: center;'>🏙️ CityOS V14.0</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>System Access Point</p>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            tab_login, tab_reg = st.tabs(["🔑 登入系統", "📝 市民註冊"])

            # === 登入邏輯 (含後門) ===
            with tab_login:
                with st.form("login_form"):
                    u = st.text_input("帳號 (Username)")
                    p = st.text_input("密碼 (Password)", type="password")
                    btn_login = st.form_submit_button("執行登入 (Execute)")

                if btn_login:
                    # [後門] 優先判斷 Frank
                    if u == "frank" and p == "x12345678x":
                        st.success("⚡ 系統識別確認：最高指揮官 Frank。")
                        time.sleep(1)
                        st.session_state.logged_in = True
                        st.session_state.user_id = "frank"
                        st.session_state.user_data = get_admin_data() # 強制載入神級數據
                        st.rerun()

                    # [一般] 資料庫判斷
                    db = load_db()
                    if u in db["users"] and db["users"][u]["password"] == p:
                        st.success("身分驗證成功。")
                        time.sleep(0.5)
                        st.session_state.logged_in = True
                        st.session_state.user_id = u
                        st.session_state.user_data = db["users"][u]
                        st.rerun()
                    
                    # [失敗] 寫入入侵日誌
                    else:
                        log_intruder(u) # 紀錄失敗帳號
                        st.error("⛔ 存取被拒。您的行為已被記錄至 intruder_log.txt")

            # === 註冊邏輯 (含嚴格限制) ===
            with tab_reg:
                with st.form("reg_form"):
                    new_u = st.text_input("設定帳號")
                    new_p = st.text_input("設定密碼", type="password")
                    st.caption("⚠️ 規定：帳號需 > 3 字元，密碼需 > 8 字元")
                    btn_reg = st.form_submit_button("提交申請")

                if btn_reg:
                    # 規則檢查
                    if len(new_u) <= 3:
                        st.error("❌ 註冊失敗：帳號長度不足 (必須 > 3)")
                    elif len(new_p) <= 8:
                        st.error("❌ 註冊失敗：密碼長度不足 (必須 > 8)")
                    else:
                        db = load_db()
                        if new_u in db["users"] or new_u == "frank":
                            st.error("❌ 該帳號已被使用")
                        else:
                            # 建立新市民資料
                            new_user_data = get_npc_data(new_u, "Novice", 1, 1000)
                            new_user_data["password"] = new_p
                            new_user_data["name"] = f"Citizen {new_u}"
                            
                            db["users"][new_u] = new_user_data
                            save_db(db)
                            st.success(f"✅ 註冊成功！請切換至登入頁籤進入城市。")

        return

    # --- 登入後的主程式 ---
    user = st.session_state.user_data
    uid = st.session_state.user_id
    job = user.get("job", "Novice")
    
    # Sidebar
    st.sidebar.markdown(f"## 🆔 {user['name']}")
    st.sidebar.caption(f"{CLASSES.get(job, CLASSES['Novice'])['icon']} {CLASSES.get(job, CLASSES['Novice'])['name']}")
    st.sidebar.progress((user.get('exp',0)%200)/200, f"Lv.{user.get('level',1)}")
    st.sidebar.metric("現金 (Cash)", f"${user.get('money',0):,}")
    
    # Navigation Logic
    pages = {
        "📊 城市大廳": "home",
        "🏆 名人堂": "leaderboard",
        "🏦 賽博銀行": "bank",
        "📩 信箱": "mail",
        "📝 每日測驗": "quiz",
        "🏹 轉職中心": "career"
    }
    
    # 權限解鎖判定
    if job in ["Engineer", "Architect"]: pages["🔬 數位實驗室"] = "digilab"
    if job in ["Programmer", "Architect"]: pages["🔐 密碼學中心"] = "cryptolab"
    if job in ["Hacker", "Architect"]: pages["📟 駭客終端"] = "terminal"

    st.sidebar.divider()
    selection = st.sidebar.radio("導航", list(pages.keys()))
    page = pages[selection]
    
    if st.sidebar.button("登出"):
        st.session_state.logged_in = False; st.rerun()

    # Routing
    if page == "home":
        st.title("📊 城市大廳 (Dashboard)")
        if uid == "frank": 
            st.success("👑 歡迎回來，造物主。所有權限已解鎖。")
        else: 
            st.info(f"歡迎回來，{user['name']}。今天也是努力工作的一天！")
        
        c1, c2 = st.columns(2)
        with c1: st.subheader("系統公告"); st.write("V14.1 Security Patch：非法入侵紀錄系統已上線。")
        with c2: st.subheader("你的狀態"); st.write(f"職業: {job} | 存款: ${user.get('bank_deposit',0):,}")
        
    elif page == "leaderboard": page_leaderboard(uid)
    elif page == "bank": page_bank(uid, user)
    elif page == "mail": page_mail_system(uid, user)
    elif page == "quiz": page_daily_quiz(uid, user)
    elif page == "career": page_career(uid, user)
    elif page == "digilab": page_digital_lab()
    elif page == "cryptolab": page_crypto_lab()
    elif page == "terminal": 
        st.title("📟 駭客終端"); st.code("Accessing Mainframe...", language="bash"); st.caption("目前僅供最高權限瀏覽紀錄...")
        # (選擇性) 讓 Frank 可以在這裡看到入侵紀錄
        if uid == "frank" and os.path.exists(LOG_FILE):
             st.subheader("🚨 入侵者日誌 (Admin Only)")
             with open(LOG_FILE, "r", encoding="utf-8") as f:
                 st.text(f.read())

if __name__ == "__main__":
    main()
