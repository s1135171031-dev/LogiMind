import streamlit as st
import pandas as pd
import random
import os
import base64
import time
import json
import numpy as np 
from datetime import datetime

# ==================================================
# 0. 使用者資料庫 (users.json) 管理 - 強制植入版
# ==================================================
USER_DB_FILE = "users.json"

def init_user_db():
    """
    初始化資料庫，並強制確保 'frank' 的超級帳號存在。
    """
    db = {"users": {}}
    
    # 1. 嘗試讀取現有資料 (避免覆蓋其他人的註冊資料)
    if os.path.exists(USER_DB_FILE):
        try:
            with open(USER_DB_FILE, "r", encoding="utf-8") as f:
                content = json.load(f)
                if "users" in content:
                    db = content
        except:
            pass # 如果檔案壞掉，就用新的

    # 2. 【關鍵】強制植入/更新 Frank 的超級帳號
    # 先保留舊的歷史紀錄 (如果有的話)
    frank_history = []
    if "frank" in db["users"]:
        frank_history = db["users"]["frank"].get("history", [])

    db["users"]["frank"] = {
        "password": "x12345678x",       # 指定密碼
        "name": "Frank",               # 顯示名稱
        "email": "frank@cityos.gov",
        "level": "最高指揮官",          # 全部權限
        "avatar_color": "#EA4335",     # 紅色 (指揮官色)
        "history": frank_history       # 繼承歷史紀錄
    }
    
    # 確保還有一個預設的一般 user 供測試
    if "user" not in db["users"]:
        db["users"]["user"] = {
            "password": "123", "name": "Site Operator", "email": "op@cityos.gov",
            "level": "區域管理員", "avatar_color": "#4285F4", "history": []
        }

    # 3. 寫回檔案
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

def load_users():
    # 每次讀取前都執行 init，確保 Frank 帳號永遠有效
    init_user_db()
    try:
        with open(USER_DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"users": {}}

def save_users(data):
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def authenticate(u, p):
    db = load_users()
    users = db.get("users", {})
    # 直接比對
    if u in users and users[u]["password"] == p:
        return users[u]
    return None

def register_user(u, p, email):
    db = load_users()
    if u in db["users"]:
        return False, "帳號已存在"
    
    db["users"][u] = {
        "password": p, "name": u, "email": email, "level": "區域管理員",
        "avatar_color": random.choice(["#4285F4", "#34A853", "#FBBC05"]), "history": []
    }
    save_users(db)
    return True, "註冊成功"

def save_score(username, score_str):
    db = load_users()
    if username in db["users"]:
        if "history" not in db["users"][username]:
            db["users"][username]["history"] = []
        
        db["users"][username]["history"].append({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "score": score_str
        })
        save_users(db)
        return db["users"][username]
    return None

# ==================================================
# 1. 系統設定
# ==================================================
st.set_page_config(page_title="CityOS V180", layout="wide", page_icon="🏙️")

# SVG 圖標資源
SVG_ICONS = {
    "MUX": '''<svg width="120" height="100" viewBox="0 0 120 100" xmlns="http://www.w3.org/2000/svg"><path d="M30,10 L90,25 L90,75 L30,90 Z" fill="none" stroke="currentColor" stroke-width="3"/><text x="45" y="55" fill="currentColor" font-size="14">MUX</text><path d="M10,25 L30,25 M10,40 L30,40 M10,55 L30,55 M10,70 L30,70 M90,50 L110,50 M60,85 L60,95" stroke="currentColor" stroke-width="2"/></svg>''',
    "AND": '''<svg width="100" height="60" viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg"><path d="M10,10 L40,10 C55,10 65,20 65,30 C65,40 55,50 40,50 L10,50 Z" fill="none" stroke="currentColor" stroke-width="3"/><path d="M0,20 L10,20 M0,40 L10,40 M65,30 L80,30" stroke="currentColor" stroke-width="3"/></svg>''',
}

THEMES = {
    "專業暗色 (Night City)": {"bg": "#212529", "txt": "#E9ECEF", "btn": "#495057", "btn_txt": "#FFFFFF", "card": "#343A40", "chart": ["#00ADB5", "#EEEEEE", "#FF2E63"]},
    "舒適亮色 (Day City)": {"bg": "#F8F9FA", "txt": "#343A40", "btn": "#6C757D", "btn_txt": "#FFFFFF", "card": "#FFFFFF", "chart": ["#343A40", "#6C757D", "#ADB5BD"]}
}

if "user_data" not in st.session_state:
    init_df = pd.DataFrame(np.random.randint(40, 60, size=(30, 3)), columns=['CPU', 'NET', 'SEC'])
    st.session_state.update({
        "logged_in": False, 
        "user_key": "",
        "user_data": {}, 
        "theme_name": "專業暗色 (Night City)",
        "monitor_data": init_df, 
        "exam_active": False, 
        "quiz_batch": []
    })

def apply_theme():
    t = THEMES[st.session_state.theme_name]
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {t['bg']} !important; }}
    h1, h2, h3, h4, p, span, div, label, li, .stMarkdown, .stExpander, .stTabs {{ color: {t['txt']} !important; font-family: 'Segoe UI', sans-serif; }}
    .stButton>button {{ background-color: {t['btn']} !important; color: {t['btn_txt']} !important; border: none !important; border-radius: 6px !important; padding: 0.5rem 1rem; }}
    div[data-testid="stDataFrame"], div[data-testid="stExpander"] {{ background-color: {t['card']} !important; border: 1px solid rgba(128,128,128,0.2); border-radius: 8px; }}
    [data-testid="stSidebar"] {{ background-color: {t['card']}; border-right: 1px solid rgba(128,128,128,0.1); }}
    </style>
    """, unsafe_allow_html=True)

def render_svg(svg_code):
    svg_black = svg_code.replace('stroke="currentColor"', 'stroke="#000000"').replace('fill="currentColor"', 'fill="#000000"')
    b64 = base64.b64encode(svg_black.encode('utf-8')).decode("utf-8")
    st.markdown(f'''<div style="background-color: #FFFFFF; border-radius: 8px; padding: 20px; margin-bottom: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"><img src="data:image/svg+xml;base64,{b64}" width="200"/></div>''', unsafe_allow_html=True)

# 讀取題目 (questions.txt)
def load_qs_from_txt():
    q = []
    if os.path.exists("questions.txt"):
        try:
            with open("questions.txt", "r", encoding="utf-8") as f:
                for l in f:
                    p = l.strip().split("|")
                    if len(p)==5: q.append({"id":p[0],"diff":p[1],"q":p[2],"o":p[3].split(","),"a":p[4]})
        except: pass
    return q

def update_data_random_walk():
    last_row = st.session_state.monitor_data.iloc[-1]
    new_vals = [max(0, min(100, last_row[col] + random.randint(-5, 5))) for col in ['CPU', 'NET', 'SEC']]
    new_row = pd.DataFrame([new_vals], columns=['CPU', 'NET', 'SEC'])
    updated_df = pd.concat([st.session_state.monitor_data, new_row], ignore_index=True)
    if len(updated_df) > 30: updated_df = updated_df.iloc[1:]
    st.session_state.monitor_data = updated_df
    return updated_df

# ==================================================
# 3. 主應用程式
# ==================================================
def main_app():
    user = st.session_state.user_data
    apply_theme()
    t_colors = THEMES[st.session_state.theme_name]["chart"]

    with st.sidebar:
        st.title("🏙️ CityOS V180")
        
        # 根據權限顯示不同標記
        level_icon = "⭐" if user['level'] == "最高指揮官" else "👤"
        
        st.markdown(f"""
        <div style="padding:15px; background:rgba(255,255,255,0.05); border-radius:8px; margin-bottom:15px; border-left: 4px solid {user.get('avatar_color', '#888')};">
            <div style="font-size:1.1em; font-weight:bold;">{user['name']}</div>
            <div style="font-size:0.8em; opacity:0.7;">{user['email']}</div>
            <div style="font-size:0.9em; margin-top:8px; color:#FFD700;">{level_icon} {user['level']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        menu = ["🏙️ 城市儀表板", "⚡ 電力設施", "🏦 數據中心", "🎓 市政學院", "📂 人事檔案"]
        page = st.radio("導航", menu)

    if "城市儀表板" in page:
        st.title(f"👋 指揮官 {user['name']}，系統就緒")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("📡 全域監控 (Live)")
            chart_ph = st.empty()
            metric_ph = st.empty()
            
            for _ in range(10): 
                df = update_data_random_walk()
                chart_ph.area_chart(df, color=t_colors, height=280)
                last = df.iloc[-1]
                metric_ph.markdown(f"""
                <div style="display:flex; justify-content:space-around; background:rgba(255,255,255,0.1); padding:10px; border-radius:5px;">
                    <div>CPU: <b>{int(last['CPU'])}%</b></div>
                    <div>NET: <b>{int(last['NET'])} Mbps</b></div>
                    <div>SEC: <b>{int(last['SEC'])} Lvl</b></div>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(1)

        with col2:
            st.subheader("📁 核心狀態")
            st.success("Users DB: 連線中")
            st.info("Questions DB: 連線中")
            qs = load_qs_from_txt()
            st.metric("題目掛載數", len(qs))
            
            # 只有最高指揮官看得到這個秘密訊息
            if user['level'] == "最高指揮官":
                st.warning("⚠️ 權限級別：ROOT ACCESS")
                st.markdown("> 您擁有系統最高裁決權")

    elif "電力設施" in page:
        st.header("⚡ 邏輯閘")
        gate = st.selectbox("Gate", ["AND", "OR", "XOR"])
        render_svg(SVG_ICONS.get(gate, SVG_ICONS["AND"]))

    elif "數據中心" in page:
        st.header("🏦 運算中心")
        val = st.text_input("輸入數值", "127")
        if val.isdigit(): st.metric("Hex", hex(int(val))[2:].upper())

    elif "市政學院" in page:
        st.header("🎓 市政考評")
        if not st.session_state.exam_active:
            if st.button("🚀 啟動考核"):
                qs = load_qs_from_txt()
                if len(qs) >= 5:
                    st.session_state.quiz_batch = random.sample(qs, 5)
                    st.session_state.exam_active = True
                    st.rerun()
                else: st.error("題庫 questions.txt 不足或遺失！")
        else:
            with st.form("exam_form"):
                ans = {}
                for i, q in enumerate(st.session_state.quiz_batch):
                    st.write(f"**{i+1}. {q['q']}**")
                    ans[i] = st.radio("Select", q['o'], key=f"q{i}", index=None, label_visibility="collapsed")
                    st.divider()
                
                if st.form_submit_button("提交"):
                    if any(a is None for a in ans.values()):
                        st.warning("請作答")
                    else:
                        score = sum([1 for i in range(5) if ans[i]==st.session_state.quiz_batch[i]['a']])
                        new_data = save_score(st.session_state.user_key, f"{score}/5")
                        if new_data: st.session_state.user_data = new_data
                        
                        if score==5: st.balloons()
                        st.success(f"成績已存檔！得分: {score}")
                        st.session_state.exam_active = False
                        time.sleep(1.5); st.rerun()

    elif "人事檔案" in page:
        st.header("📂 檔案管理 (users.json)")
        st.text_input("Name", user['name'], disabled=True)
        st.text_input("Level", user['level'], disabled=True)
        
        st.subheader("📜 歷史紀錄")
        if "history" in user and user["history"]:
            st.dataframe(pd.DataFrame(user["history"]))
        else: st.info("無紀錄")
        
        if st.button("登出"):
            st.session_state.logged_in = False
            st.session_state.user_data = {}
            st.rerun()

# ==================================================
# 4. 登入介面
# ==================================================
def login_page():
    apply_theme()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("CityOS V180")
        st.caption("Secure Access System")
        
        if not os.path.exists("questions.txt"):
            st.warning("⚠️ 警告：題庫 questions.txt 遺失。")

        # 這裡會自動執行初始化，確保 Frank 存在
        init_user_db()

        tab1, tab2 = st.tabs(["登入", "註冊"])
        with tab1:
            with st.form("login"):
                u = st.text_input("帳號 (frank)")
                p = st.text_input("密碼", type="password")
                if st.form_submit_button("登入"):
                    data = authenticate(u, p)
                    if data:
                        st.session_state.logged_in = True
                        st.session_state.user_key = u
                        st.session_state.user_data = data
                        st.success("驗證成功 - 最高權限已授權"); time.sleep(0.5); st.rerun()
                    else: st.error("帳號或密碼錯誤")
        with tab2:
            with st.form("signup"):
                nu = st.text_input("新帳號")
                np_ = st.text_input("新密碼", type="password")
                ne = st.text_input("Email")
                if st.form_submit_button("註冊"):
                    ok, msg = register_user(nu, np_, ne)
                    if ok: st.success(msg)
                    else: st.error(msg)

if st.session_state.logged_in: main_app()
else: login_page()
