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
# 0. 系統初始化與檔案檢查 (自動修復機制)
# ==================================================
USER_DB_FILE = "users.json"
QUESTIONS_FILE = "questions.txt"

def check_system_files():
    """確保所有必要的系統檔案都存在，若無則自動建立"""
    
    # 1. 檢查題庫，若無則自動生成
    if not os.path.exists(QUESTIONS_FILE):
        default_qs = """1|Easy|Python 中用於輸出的函式是？|print,input,scan,write|print
2|Medium|二進位數字 1010 等於十進位的？|8,9,10,12|10
3|Hard|CityOS 的核心架構基於？|Streamlit,Flask,Django,React|Streamlit
4|Easy|CPU 代表什麼？|中央處理單元,圖形處理單元,記憶體,硬碟|中央處理單元
5|Medium|哪種邏輯閘只有在輸入皆為1時輸出1？|OR,AND,XOR,NOT|AND"""
        with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
            f.write(default_qs)

    # 2. 確保資料庫檔案格式正確
    if not os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "w", encoding="utf-8") as f:
            json.dump({"users": {}}, f)

# ==================================================
# 1. 使用者資料庫管理 (含 Frank 強制植入邏輯)
# ==================================================
def init_user_db():
    """初始化資料庫，並強制確保 'frank' 的超級帳號存在"""
    check_system_files() # 先檢查檔案系統
    
    db = {"users": {}}
    
    # 嘗試讀取現有資料
    if os.path.exists(USER_DB_FILE):
        try:
            with open(USER_DB_FILE, "r", encoding="utf-8") as f:
                content = json.load(f)
                if "users" in content:
                    db = content
        except:
            pass # 檔案損壞時使用預設值

    # 【關鍵】強制植入/更新 Frank 的超級帳號
    frank_history = []
    if "frank" in db["users"]:
        frank_history = db["users"]["frank"].get("history", [])

    db["users"]["frank"] = {
        "password": "12345678x",       # 指定密碼
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

    # 寫回檔案
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

def load_users():
    init_user_db() # 每次讀取前確保 Frank 存在
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
# 2. 系統設定與 UI 元件
# ==================================================
st.set_page_config(page_title="CityOS V180", layout="wide", page_icon="🏙️")

SVG_ICONS = {
    "MUX": '''<svg width="120" height="100" viewBox="0 0 120 100" xmlns="http://www.w3.org/2000/svg"><path d="M30,10 L90,25 L90,75 L30,90 Z" fill="none" stroke="currentColor" stroke-width="3"/><text x="45" y="55" fill="currentColor" font-size="14">MUX</text><path d="M10,25 L30,25 M10,40 L30,40 M10,55 L30,55 M10,70 L30,70 M90,50 L110,50 M60,85 L60,95" stroke="currentColor" stroke-width="2"/></svg>''',
    "AND": '''<svg width="100" height="60" viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg"><path d="M10,10 L40,10 C55,10 65,20 65,30 C65,40 55,50 40,50 L10,50 Z" fill="none" stroke="currentColor" stroke-width="3"/><path d="M0,20 L10,20 M0,40 L10,40 M65,30 L80,30" stroke="currentColor" stroke-width="3"/></svg>''',
    "OR": '''<svg width="100" height="60" viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg"><path d="M10,10 Q40,10 50,30 Q40,50 10,50 Q20,30 10,10 Z" fill="none" stroke="currentColor" stroke-width="3"/><path d="M0,20 L15,20 M0,40 L15,40 M50,30 L65,30" stroke="currentColor" stroke-width="3"/></svg>''',
    "XOR": '''<svg width="100" height="60" viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg"><path d="M20,10 Q50,10 60,30 Q50,50 20,50 Q30,30 20,10 Z" fill="none" stroke="currentColor" stroke-width="3"/><path d="M10,10 Q20,30 10,50" fill="none" stroke="currentColor" stroke-width="3"/><path d="M0,20 L15,20 M0,40 L15,40 M60,30 L75,30" stroke="currentColor" stroke-width="3"/></svg>'''
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

def load_qs_from_txt():
    q = []
    if os.path.exists(QUESTIONS_FILE):
        try:
            with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
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
# 3. 主應用程式 (Main App)
# ==================================================
def main_app():
    user = st.session_state.user_data
    apply_theme()
    t_colors = THEMES[st.session_state.theme_name]["chart"]

    with st.sidebar:
        st.title("🏙️ CityOS V180")
        
        # 顯示使用者資訊
        level_icon = "⭐" if user['level'] == "最高指揮官" else "👤"
        st.markdown(f"""
        <div style="padding:15px; background:rgba(255,255,255,0.05); border-radius:8px; margin-bottom:15px; border-left: 4px solid {user.get('avatar_color', '#888')};">
            <div style="font-size:1.1em; font-weight:bold;">{user['name']}</div>
            <div style="font-size:0.8em; opacity:0.7;">{user['email']}</div>
            <div style="font-size:0.9em; margin-top:8px; color:#FFD700;">{level_icon} {user['level']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 導航選單
        menu = ["🏙️ 城市儀表板", "⚡ 電力設施", "🏦 數據中心", "🎓 市政學院", "📂 人事檔案"]
        page = st.radio("導航", menu)
        
        st.divider()
        
        # 【新增功能】主題切換器
        st.caption("系統外觀")
        selected_theme = st.selectbox("主題風格", list(THEMES.keys()), index=list(THEMES.keys()).index(st.session_state.theme_name), label_visibility="collapsed")
        if selected_theme != st.session_state.theme_name:
            st.session_state.theme_name = selected_theme
            st.rerun()

    # --- 頁面內容路由 ---
    if "城市儀表板" in page:
        st.title(f"👋 指揮官 {user['name']}，系統就緒")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("📡 全域監控 (Live)")
            chart_ph = st.empty()
            metric_ph = st.empty()
            
            # 模擬即時更新
            for _ in range(15): # 增加迴圈次數讓動畫久一點 
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
                time.sleep(0.5) # 加快更新頻率讓視覺更流暢

        with col2:
            st.subheader("📁 核心狀態")
            st.success("Users DB: 連線中")
            
            qs = load_qs_from_txt()
            if len(qs) > 0:
                st.success("Q-Bank: 掛載正常")
            else:
                st.error("Q-Bank: 異常")
                
            st.metric("題目掛載數", len(qs))
            
            # 最高指揮官專屬訊息
            if user['level'] == "最高指揮官":
                st.warning("⚠️ 級別：ROOT ACCESS")
                st.markdown("> 您擁有系統最高裁決權")

    elif "電力設施" in page:
        st.header("⚡ 邏輯閘視覺化")
        col_g1, col_g2 = st.columns([1, 2])
        with col_g1:
            gate = st.selectbox("選擇邏輯閘", ["AND", "OR", "XOR", "MUX"])
            st.info(f"顯示 {gate} 的標準電路符號")
        with col_g2:
            render_svg(SVG_ICONS.get(gate, SVG_ICONS["AND"]))

    elif "數據中心" in page:
        st.header("🏦 運算中心")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            val = st.text_input("輸入十進位數值", "127")
            if val.isdigit(): 
                st.metric("十六進位 (Hex)", hex(int(val))[2:].upper())
                st.metric("二進位 (Bin)", bin(int(val))[2:])
        with col_c2:
            st.info("此區域連線至中央運算單元，提供即時數制轉換服務。")

    elif "市政學院" in page:
        st.header("🎓 市政考評")
        if not st.session_state.exam_active:
            st.write("準備好接受考核了嗎？")
            if st.button("🚀 啟動考核"):
                qs = load_qs_from_txt()
                if len(qs) >= 5:
                    st.session_state.quiz_batch = random.sample(qs, 5)
                    st.session_state.exam_active = True
                    st.rerun()
                else: 
                    st.error(f"題庫不足 (目前 {len(qs)} 題)，請檢查 questions.txt")
        else:
            with st.form("exam_form"):
                ans = {}
                for i, q in enumerate(st.session_state.quiz_batch):
                    st.write(f"**Q{i+1}. {q['q']}**")
                    # 使用 radio 但隱藏 label 避免視覺混亂
                    ans[i] = st.radio(f"選項 {i}", q['o'], key=f"q_{i}", index=None, label_visibility="collapsed")
                    st.divider()
                
                if st.form_submit_button("提交試卷"):
                    if any(a is None for a in ans.values()):
                        st.warning("請完成所有題目後再提交。")
                    else:
                        score = sum([1 for i in range(5) if ans[i]==st.session_state.quiz_batch[i]['a']])
                        new_data = save_score(st.session_state.user_key, f"{score}/5")
                        if new_data: st.session_state.user_data = new_data
                        
                        if score==5: st.balloons()
                        st.success(f"考核結束！得分: {score}/5")
                        st.session_state.exam_active = False
                        time.sleep(2); st.rerun()
            
            if st.button("放棄考核"):
                st.session_state.exam_active = False
                st.rerun()

    elif "人事檔案" in page:
        st.header("📂 檔案管理 (users.json)")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.text_input("Name", user['name'], disabled=True)
            st.text_input("Level", user['level'], disabled=True)
        with col_p2:
            st.text_input("Email", user['email'], disabled=True)
            st.text_input("Avatar Color", user['avatar_color'], disabled=True)
        
        st.subheader("📜 歷史考核紀錄")
        if "history" in user and user["history"]:
            # 將歷史紀錄轉換為 DataFrame 並反向排序(最新的在上面)
            hist_df = pd.DataFrame(user["history"])
            st.dataframe(hist_df.iloc[::-1], use_container_width=True)
        else: 
            st.info("目前尚無考核紀錄")
        
        st.divider()
        if st.button("安全登出"):
            st.session_state.logged_in = False
            st.session_state.user_data = {}
            st.rerun()

# ==================================================
# 4. 登入介面 (Login Page)
# ==================================================
def login_page():
    apply_theme()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🏙️ CityOS V180")
        st.caption("Secure Access System | Taoyuan Node")
        
        # 啟動時自動檢查與修復檔案
        check_system_files()
        init_user_db()

        tab1, tab2 = st.tabs(["身份驗證", "新進人員註冊"])
        
        with tab1:
            with st.form("login"):
                u = st.text_input("帳號", placeholder="e.g. frank")
                p = st.text_input("密碼", type="password")
                if st.form_submit_button("登入系統", use_container_width=True):
                    data = authenticate(u, p)
                    if data:
                        st.session_state.logged_in = True
                        st.session_state.user_key = u
                        st.session_state.user_data = data
                        st.success("驗證成功 - 正在載入使用者設定檔..."); 
                        time.sleep(0.5); st.rerun()
                    else: 
                        st.error("帳號或密碼錯誤，請重試。")
        
        with tab2:
            with st.form("signup"):
                nu = st.text_input("設定帳號")
                np_ = st.text_input("設定密碼", type="password")
                ne = st.text_input("Email")
                if st.form_submit_button("提交申請", use_container_width=True):
                    if nu and np_:
                        ok, msg = register_user(nu, np_, ne)
                        if ok: st.success(msg)
                        else: st.error(msg)
                    else:
                        st.warning("請填寫完整資訊")

# ==================================================
# 5. 程式入口
# ==================================================
if __name__ == "__main__":
    if st.session_state.logged_in: 
        main_app()
    else: 
        login_page()
