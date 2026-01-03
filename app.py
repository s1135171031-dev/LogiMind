import streamlit as st
import pandas as pd
import random
import os
import base64
import time
import json
import hashlib
import numpy as np
from datetime import datetime, date
import matplotlib.pyplot as plt

# ==============================================================================
# 1. 系統核心設定 & 常數
# ==============================================================================
st.set_page_config(
    page_title="CityOS V8.0 Engineer RPG",
    layout="wide",
    page_icon="🏙️",
    initial_sidebar_state="expanded"
)

# 檔案路徑
USER_DB_FILE = "cityos_users.json"
QUESTION_DB_FILE = "questions.txt"

# 職業系統
CLASSES = {
    "Novice": {
        "name": "一般市民", 
        "icon": "👤", 
        "desc": "基礎權限，可使用邏輯閘與歐姆定律工具。",
        "unlocks": []
    },
    "Engineer": {
        "name": "硬體工程師", 
        "icon": "🔧", 
        "desc": "擅長電路設計。解鎖：電阻色碼計算、進階電路。",
        "unlocks": ["Resistor", "AdvancedCircuit"]
    },
    "Programmer": {
        "name": "軟體工程師", 
        "icon": "💻", 
        "desc": "擅長編碼。解鎖：ASCII 查表、進位轉換器。",
        "unlocks": ["ASCII", "BaseConverter"]
    },
    "Architect": {
        "name": "系統架構師", 
        "icon": "⚡", 
        "desc": "精通數位邏輯。解鎖：卡諾圖、格雷碼。",
        "unlocks": ["KMap", "GrayCode"]
    },
    "Hacker": {
        "name": "資安專家", 
        "icon": "🛡️", 
        "desc": "精通加密。解鎖：密碼學工具、留言板特殊字體。",
        "unlocks": ["Crypto", "BoardHighlight"]
    }
}

# SVG 圖示庫 (邏輯閘)
SVG_LIB = {
    "AND": '''<svg width="100" height="60"><path d="M10,5 L40,5 C55,5 65,15 65,25 C65,35 55,45 40,45 L10,45 Z" fill="none" stroke="#CCC" stroke-width="3"/><path d="M0,15 L10,15 M0,35 L10,35 M65,25 L80,25" stroke="#CCC" stroke-width="3"/></svg>''',
    "OR": '''<svg width="100" height="60"><path d="M10,5 L35,5 Q50,25 35,45 L10,45 Q25,25 10,5 Z" fill="none" stroke="#CCC" stroke-width="3"/><path d="M0,15 L15,15 M0,35 L15,35 M45,25 L60,25" stroke="#CCC" stroke-width="3"/></svg>''',
    "NOT": '''<svg width="100" height="60"><path d="M20,5 L20,45 L55,25 Z" fill="none" stroke="#CCC" stroke-width="3"/><circle cx="59" cy="25" r="3" fill="none" stroke="#CCC" stroke-width="2"/><path d="M0,25 L20,25 M63,25 L80,25" stroke="#CCC" stroke-width="3"/></svg>''',
    "XOR": '''<svg width="100" height="60"><path d="M20,5 L45,5 Q60,25 45,45 L20,45 Q35,25 20,5 Z" fill="none" stroke="#CCC" stroke-width="3"/><path d="M10,5 Q25,25 10,45" fill="none" stroke="#CCC" stroke-width="3"/><path d="M0,15 L15,15 M0,35 L15,35 M55,25 L70,25" stroke="#CCC" stroke-width="3"/></svg>''',
    "NAND": '''<svg width="100" height="60"><path d="M10,5 L40,5 C55,5 65,15 65,25 C65,35 55,45 40,45 L10,45 Z" fill="none" stroke="#CCC" stroke-width="3"/><circle cx="69" cy="25" r="3" fill="none" stroke="#CCC" stroke-width="2"/><path d="M0,15 L10,15 M0,35 L10,35 M73,25 L85,25" stroke="#CCC" stroke-width="3"/></svg>'''
}

# ==============================================================================
# 2. 資料管理 (Backend Logic)
# ==============================================================================

def get_admin_data():
    """回傳預設的 Frank 管理員資料"""
    return {
        "password": "x12345678x", 
        "name": "Frank (Admin)", 
        "level": 100, 
        "exp": 99999, 
        "money": 99999, 
        "job": "Architect", 
        "badges": ["GM", "Admin"],
        "last_quiz_date": str(date.today()), 
        "quiz_attempts": 0,
        "history_score": 5,
        "bio": "我是這個系統的創造者。"
    }

def init_db():
    """初始化使用者資料庫"""
    default_data = {
        "users": {
            "frank": get_admin_data()  # 預設寫入 Frank
        },
        "messages": [] 
    }
    if not os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, ensure_ascii=False, indent=4)

def load_db():
    init_db()
    try:
        with open(USER_DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # --- 強制檢查：如果檔案裡沒有 frank，補進去 ---
        # 這是為了防止你已經有舊檔案，導致新帳號無法寫入
        if "frank" not in data["users"]:
            data["users"]["frank"] = get_admin_data()
            save_db(data)
            
        return data
    except Exception as e:
        # 如果檔案壞了，重置
        st.error(f"資料庫讀取錯誤: {e}，已重置資料庫。")
        os.remove(USER_DB_FILE)
        init_db()
        return load_db()

def save_db(data):
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_questions():
    """讀取題目"""
    questions = []
    # 讀取真實檔案
    if os.path.exists(QUESTION_DB_FILE):
        try:
            with open(QUESTION_DB_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) >= 5:
                        questions.append({
                            "id": parts[0],
                            "type": parts[1],
                            "q": parts[2],
                            "opts": parts[3].split(','),
                            "ans": parts[4]
                        })
            return questions
        except:
            pass # 讀取失敗則使用下方模擬題

    # 模擬題 (Fallback)
    for i in range(10):
        a, b = random.randint(0, 1), random.randint(0, 1)
        res = int(not (a and b)) 
        questions.append({
            "id": f"M{i}", "type": "1", 
            "q": f"[邏輯閘測試] 輸入 A={a}, B={b}, 經過 NAND 閘輸出為?", 
            "opts": ["0", "1", "High", "Low"], "ans": str(res)
        })
    return questions

def check_level_up(user):
    current_lvl = user.get("level", 1)
    exp = user.get("exp", 0)
    new_lvl = 1 + (exp // 100)
    if new_lvl > current_lvl:
        user["level"] = new_lvl
        return True, new_lvl
    return False, current_lvl

# ==============================================================================
# 3. 介面模組
# ==============================================================================

def render_sidebar_hud(user):
    st.sidebar.markdown(f"### 🆔 {user['name']}")
    job_key = user.get("job", "Novice")
    job_info = CLASSES.get(job_key, CLASSES["Novice"])
    st.sidebar.markdown(f"**職業**: {job_info['icon']} {job_info['name']}")
    
    lvl = user.get("level", 1)
    xp = user.get("exp", 0)
    
    c1, c2 = st.sidebar.columns([1, 2])
    c1.metric("Lv", lvl)
    c2.metric("💰", user.get("money", 0))
    st.sidebar.progress((xp % 100) / 100.0, text=f"XP: {xp}")
    st.sidebar.markdown("---")

def page_daily_quiz(user_id, user):
    st.header("📝 每日工程師能力測驗")
    
    today_str = str(date.today())
    if user.get("last_quiz_date") != today_str:
        user["last_quiz_date"] = today_str
        user["quiz_attempts"] = 0
        db = load_db()
        db["users"][user_id] = user
        save_db(db)
    
    attempts = user.get("quiz_attempts", 0)
    MAX_ATTEMPTS = 3
    
    st.info(f"今日剩餘次數: **{MAX_ATTEMPTS - attempts} / {MAX_ATTEMPTS}**")

    if "quiz_state" not in st.session_state:
        st.session_state.quiz_state = "IDLE"
        st.session_state.quiz_score = 0
        st.session_state.quiz_index = 0
        st.session_state.quiz_questions = []

    if st.session_state.quiz_state == "IDLE":
        if attempts >= MAX_ATTEMPTS:
            st.error("今日次數已用盡！")
            return
        if st.button("🚀 開始測驗", use_container_width=True):
            all_q = load_questions()
            if not all_q: return
            st.session_state.quiz_questions = random.sample(all_q, min(5, len(all_q)))
            st.session_state.quiz_state = "PLAYING"
            st.session_state.quiz_score = 0
            st.session_state.quiz_index = 0
            st.rerun()

    elif st.session_state.quiz_state == "PLAYING":
        q_idx = st.session_state.quiz_index
        q_data = st.session_state.quiz_questions[q_idx]
        st.progress((q_idx) / 5.0, text=f"Question {q_idx + 1} / 5")
        st.markdown(f"### Q{q_idx+1}: {q_data['q']}")
        
        with st.form(key=f"q_form_{q_idx}"):
            choice = st.radio("請選擇答案:", q_data['opts'])
            if st.form_submit_button("送出答案"):
                if choice == q_data['ans']:
                    st.toast("✅ 正確!", icon="🔥")
                    st.session_state.quiz_score += 1
                else:
                    st.toast(f"❌ 錯誤! 正解: {q_data['ans']}")
                
                if q_idx + 1 >= 5:
                    st.session_state.quiz_state = "FINISHED"
                else:
                    st.session_state.quiz_index += 1
                time.sleep(0.5)
                st.rerun()

    elif st.session_state.quiz_state == "FINISHED":
        score = st.session_state.quiz_score
        xp_gain, money_gain = 0, 0
        rank = "C"
        
        if score == 5: rank, xp_gain, money_gain = "S", 100, 50
        elif score == 4: rank, xp_gain, money_gain = "A", 60, 30
        elif score >= 2: rank, xp_gain, money_gain = "B", 30, 10
        
        st.markdown(f"## 評級: {rank} (答對 {score}/5)")
        st.success(f"獲得: +{xp_gain} XP, +${money_gain}")
        
        if st.button("領取並返回"):
            db = load_db()
            u = db["users"][user_id]
            u["exp"] += xp_gain
            u["money"] += money_gain
            u["quiz_attempts"] += 1
            if score > u.get("history_score", 0): u["history_score"] = score
            check_level_up(u)
            save_db(db)
            st.session_state.quiz_state = "IDLE"
            st.session_state.user_data = u
            st.rerun()

def page_toolbox(user):
    st.title("🧰 工程師工具箱")
    user_job = user.get("job", "Novice")
    user_unlocks = CLASSES[user_job]["unlocks"]
    lvl = user.get("level", 1)
    
    t1, t2, t3, t4, t5 = st.tabs(["邏輯閘", "進位轉換", "電路計算", "格雷碼", "電阻色碼"])
    
    with t1:
        c1, c2 = st.columns([1, 2])
        with c1:
            g = st.selectbox("邏輯閘", list(SVG_LIB.keys()))
            a = st.toggle("Input A")
            b = False if g == "NOT" else st.toggle("Input B")
            res = 0
            if g == "AND": res = int(a and b)
            elif g == "OR": res = int(a or b)
            elif g == "NOT": res = int(not a)
            elif g == "XOR": res = int(a != b)
            elif g == "NAND": res = int(not(a and b))
            st.metric("Output", res)
        with c2:
            svg = SVG_LIB[g].replace('width="100"', 'width="300"').replace('height="60"', 'height="180"')
            if res: svg = svg.replace("#CCC", "#0F0")
            st.markdown(f"<div style='text-align:center'>{svg}</div>", unsafe_allow_html=True)

    with t2:
        if lvl < 1 and "BaseConverter" not in user_unlocks:
            st.warning("🔒 需 Lv.1 或 [軟體工程師]")
        else:
            val = st.number_input("Decimal", value=255)
            st.code(f"BIN: {bin(val)[2:]}\nOCT: {oct(val)[2:]}\nHEX: {hex(val)[2:].upper()}")

    with t3: # 電路
        opt = st.radio("計算", ["V=IR", "I=V/R", "R=V/I"], horizontal=True)
        v, i, r = 5.0, 0.1, 50.0
        if "V=" in opt:
            i = st.number_input("I (A)", 0.1)
            r = st.number_input("R (Ω)", 100.0)
            st.write(f"V = {i*r:.2f} V")
        elif "I=" in opt:
            v = st.number_input("V (V)", 5.0)
            r = st.number_input("R (Ω)", 100.0)
            st.write(f"I = {v/r:.4f} A")

    with t4: # 格雷碼
        if lvl < 5 and "GrayCode" not in user_unlocks:
             st.warning("🔒 需 Lv.5 或 [架構師]")
        else:
            b_in = st.text_input("Binary", "1010")
            try:
                dec = int(b_in, 2)
                gray = dec ^ (dec >> 1)
                st.metric("Gray Code", bin(gray)[2:])
            except: st.error("Invalid Binary")

    with t5: # 色碼
        if lvl < 2 and "Resistor" not in user_unlocks:
            st.warning("🔒 需 Lv.2 或 [工程師]")
        else:
            cols = {"Black":0, "Brown":1, "Red":2, "Orange":3, "Yellow":4, "Green":5, "Blue":6, "Violet":7, "Gray":8, "White":9}
            cc1, cc2, cc3 = st.columns(3)
            c1 = cc1.selectbox("Band 1", list(cols.keys()), index=1)
            c2 = cc2.selectbox("Band 2", list(cols.keys()), index=0)
            c3 = cc3.selectbox("Band 3 (Multiplier)", list(cols.keys()), index=2)
            st.subheader(f"R = {(cols[c1]*10+cols[c2]) * (10**cols[c3])} Ω")

def page_career(user_id, user):
    st.title("🏹 轉職中心")
    curr = user.get("job", "Novice")
    cols = st.columns(2)
    idx = 0
    for k, v in CLASSES.items():
        if k == "Novice": continue
        with cols[idx%2]:
            with st.container(border=True):
                st.subheader(f"{v['icon']} {v['name']}")
                st.write(v['desc'])
                if curr == k:
                    st.button("當前職業", disabled=True, key=k)
                elif user["level"] >= 5:
                    if st.button("轉職", key=k):
                        user["job"] = k
                        db = load_db()
                        db["users"][user_id] = user
                        save_db(db)
                        st.toast("轉職成功!", icon="🎉")
                        st.rerun()
                else:
                    st.button("需 Lv.5", disabled=True, key=k)
        idx+=1

def page_message_board(user_id, user):
    st.title("💬 留言板")
    db = load_db()
    msgs = db.get("messages", [])
    
    with st.form("msg"):
        txt = st.text_input("輸入留言...")
        if st.form_submit_button("發送"):
            msgs.insert(0, {
                "u": user["name"], "lv": user["level"], 
                "job": user.get("job", "Novice"), "txt": txt,
                "t": datetime.now().strftime("%m-%d %H:%M")
            })
            db["messages"] = msgs[:50]
            save_db(db)
            st.rerun()
            
    for m in msgs:
        icon = CLASSES.get(m['job'], CLASSES["Novice"])['icon']
        st.markdown(f"**[{m['t']}] [Lv.{m['lv']}] {icon} {m['u']}**: {m['txt']}")

def page_profile(user_id, user):
    st.title(f"📇 {user['name']}")
    st.write(f"職業: {CLASSES[user.get('job', 'Novice')]['name']} | Lv.{user['level']} | ${user['money']}")
    bio = st.text_area("Bio", user.get("bio", ""))
    if st.button("Save"):
        user["bio"] = bio
        db = load_db()
        db["users"][user_id] = user
        save_db(db)
        st.success("Saved")

# ==============================================================================
# 4. 主流程
# ==============================================================================
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.markdown("<h1 style='text-align:center'>🏙️ CityOS V8.0</h1>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            tab1, tab2 = st.tabs(["登入", "註冊"])
            with tab1:
                u = st.text_input("帳號", "frank")
                p = st.text_input("密碼", type="password")
                if st.button("登入"):
                    db = load_db()
                    if u in db["users"] and db["users"][u]["password"] == p:
                        st.session_state.logged_in = True
                        st.session_state.user_id = u
                        st.session_state.user_data = db["users"][u]
                        st.rerun()
                    else: st.error("帳號或密碼錯誤")
            with tab2:
                nu = st.text_input("新帳號")
                np_ = st.text_input("新密碼", type="password")
                nn = st.text_input("暱稱")
                if st.button("註冊"):
                    db = load_db()
                    if nu in db["users"]: st.error("已存在")
                    else:
                        db["users"][nu] = {
                            "password": np_, "name": nn, "level": 1, "exp": 0, "money": 0,
                            "job": "Novice", "last_quiz_date": "", "quiz_attempts": 0
                        }
                        save_db(db)
                        st.success("成功")
        return

    # Logged In
    user = st.session_state.user_data
    uid = st.session_state.user_id
    render_sidebar_hud(user)
    
    pages = {"主頁": page_daily_quiz, "測驗": page_daily_quiz, "工具": page_toolbox, "轉職": page_career, "社群": page_message_board, "名片": page_profile}
    
    # 修改 Dashboard 顯示內容
    sel = st.sidebar.radio("導航", ["主頁", "每日測驗", "工具箱", "轉職中心", "社群留言", "個人名片", "登出"])
    
    if sel == "主頁":
        st.title("📊 控制中心")
        c1, c2 = st.columns([2,1])
        with c1: 
            st.line_chart(pd.DataFrame(np.random.randn(20, 3), columns=["A","B","C"]))
            st.caption("系統即時負載")
        with c2:
            st.info(f"歡迎, {user['name']}!")
            st.write("今日任務：完成每日測驗")
            
    elif sel == "每日測驗": page_daily_quiz(uid, user)
    elif sel == "工具箱": page_toolbox(user)
    elif sel == "轉職中心": page_career(uid, user)
    elif sel == "社群留言": page_message_board(uid, user)
    elif sel == "個人名片": page_profile(uid, user)
    elif sel == "登出":
        st.session_state.logged_in = False
        st.rerun()

if __name__ == "__main__":
    main()
