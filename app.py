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
# 0. 資料庫核心與 Frank 帳號初始化
# ==================================================
USER_DB_FILE = "users.json"

def init_user_db():
    """初始化使用者資料庫，確保最高指揮官存在"""
    should_init = False
    if not os.path.exists(USER_DB_FILE) or os.path.getsize(USER_DB_FILE) == 0:
        should_init = True
            
    if should_init:
        default_data = {
            "users": {
                # --- ☢️ 最高指揮官 (God Mode) ---
                "frank": {
                    "password": "x12345678x",
                    "name": "Frank (Supreme Commander)",
                    "email": "frank@cityos.gov",
                    "level": "最高指揮官",
                    "avatar_color": "#000000", # 黑色帝王感
                    "history": []
                },
                # --- 🟠 系統管理員 ---
                "admin": {
                    "password": "admin",
                    "name": "Admin (System)",
                    "email": "admin@cityos.gov",
                    "level": "系統管理員",
                    "avatar_color": "#EA4335",
                    "history": []
                },
                # --- 🔵 一般操作員 ---
                "user": {
                    "password": "123",
                    "name": "Site Operator",
                    "email": "op@cityos.gov",
                    "level": "區域管理員",
                    "avatar_color": "#4285F4",
                    "history": []
                }
            }
        }
        with open(USER_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=4, ensure_ascii=False)

def load_users():
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
# 1. 系統視覺與工具
# ==================================================
st.set_page_config(page_title="CityOS V180", layout="wide", page_icon="🏙️")

SVG_ICONS = {
    "MUX": '''<svg width="120" height="100" viewBox="0 0 120 100" xmlns="http://www.w3.org/2000/svg"><path d="M30,10 L90,25 L90,75 L30,90 Z" fill="none" stroke="currentColor" stroke-width="3"/><text x="45" y="55" fill="currentColor" font-size="14">MUX</text><path d="M10,25 L30,25 M10,40 L30,40 M10,55 L30,55 M10,70 L30,70 M90,50 L110,50 M60,85 L60,95" stroke="currentColor" stroke-width="2"/></svg>''',
    "AND": '''<svg width="100" height="60" viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg"><path d="M10,10 L40,10 C55,10 65,20 65,30 C65,40 55,50 40,50 L10,50 Z" fill="none" stroke="currentColor" stroke-width="3"/><path d="M0,20 L10,20 M0,40 L10,40 M65,30 L80,30" stroke="currentColor" stroke-width="3"/></svg>''',
    "OR": '''<svg width="100" height="60" viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg"><path d="M10,10 L35,10 Q50,30 35,50 L10,50 Q25,30 10,10 Z" fill="none" stroke="currentColor" stroke-width="3"/><path d="M0,20 L15,20 M0,40 L15,40 M45,30 L60,30" stroke="currentColor" stroke-width="3"/></svg>''',
    "XOR": '''<svg width="100" height="60" viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg"><path d="M20,10 L45,10 Q60,30 45,50 L20,50 Q35,30 20,10 Z" fill="none" stroke="currentColor" stroke-width="3"/><path d="M10,10 Q25,30 10,50" fill="none" stroke="currentColor" stroke-width="3"/><path d="M0,20 L15,20 M0,40 L15,40 M55,30 L70,30" stroke="currentColor" stroke-width="3"/></svg>'''
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
    
    /* Commander Exclusive Style */
    .commander-card {{ border: 2px solid gold !important; box-shadow: 0 0 15px rgba(255, 215, 0, 0.2); background: linear-gradient(135deg, rgba(0,0,0,0.8), rgba(50,50,50,0.9)); }}
    .commander-badge {{ color: gold; font-weight: bold; font-size: 0.8em; border: 1px solid gold; padding: 2px 6px; border-radius: 4px; display: inline-block; margin-top:5px;}}
    </style>
    """, unsafe_allow_html=True)

def render_svg(svg_code):
    svg_black = svg_code.replace('stroke="currentColor"', 'stroke="#888888"').replace('fill="currentColor"', 'fill="#888888"')
    b64 = base64.b64encode(svg_black.encode('utf-8')).decode("utf-8")
    st.markdown(f'''<div style="background-color: rgba(255,255,255,0.05); border-radius: 8px; padding: 20px; margin-bottom: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"><img src="data:image/svg+xml;base64,{b64}" width="200"/></div>''', unsafe_allow_html=True)

# [升級] 讀取題目並進行防呆檢測
def load_qs_from_txt():
    q = []
    errors = [] # 記錄格式錯誤的行
    if os.path.exists("questions.txt"):
        try:
            with open("questions.txt", "r", encoding="utf-8") as f:
                for idx, l in enumerate(f):
                    line_content = l.strip()
                    if not line_content: continue # 跳過空行
                    
                    p = line_content.split("|")
                    if len(p) == 5: 
                        q.append({"id":p[0],"diff":p[1],"q":p[2],"o":p[3].split(","),"a":p[4]})
                    else:
                        errors.append(f"Line {idx+1}: 格式錯誤 (欄位數 {len(p)}/5)")
        except Exception as e:
            errors.append(str(e))
    return q, errors

def update_data_random_walk():
    last_row = st.session_state.monitor_data.iloc[-1]
    new_vals = [max(0, min(100, last_row[col] + random.randint(-5, 5))) for col in ['CPU', 'NET', 'SEC']]
    new_row = pd.DataFrame([new_vals], columns=['CPU', 'NET', 'SEC'])
    updated_df = pd.concat([st.session_state.monitor_data, new_row], ignore_index=True)
    if len(updated_df) > 30: updated_df = updated_df.iloc[1:]
    st.session_state.monitor_data = updated_df
    return updated_df

# ==================================================
# 3. 主應用程式邏輯
# ==================================================
def main_app():
    user = st.session_state.user_data
    apply_theme()
    t_colors = THEMES[st.session_state.theme_name]["chart"]
    
    # 判斷是否為最高指揮官
    is_commander = user.get("level") == "最高指揮官"

    with st.sidebar:
        st.title("🏙️ CityOS V180")
        st.caption("Dual File Architecture")
        
        # 指揮官專屬卡片設計
        card_class = "commander-card" if is_commander else ""
        badge_html = "<div class='commander-badge'>SUPREME ACCESS</div>" if is_commander else ""
        
        st.markdown(f"""
        <div class="{card_class}" style="padding:15px; background:rgba(255,255,255,0.05); border-radius:8px; margin-bottom:15px; border-left: 4px solid {user.get('avatar_color', '#888')};">
            <div style="font-size:1.1em; font-weight:bold;">{user['name']}</div>
            <div style="font-size:0.8em; opacity:0.7;">{user['email']}</div>
            <div style="font-size:0.8em; margin-top:5px; color:{user.get('avatar_color', '#888')};">Lv: {user['level']}</div>
            {badge_html}
        </div>
        """, unsafe_allow_html=True)
        
        menu = ["🏙️ 城市儀表板", "⚡ 電力設施", "🏦 數據中心", "🎓 市政學院", "📂 人事檔案"]
        
        # [升級] 指揮官專屬選單
        if is_commander:
            menu.append("☢️ 核心控制")
            
        page = st.radio("導航", menu)

    if "城市儀表板" in page:
        st.title(f"👋 歡迎，{user['name']}")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("📡 即時監控 (Real-time)")
            chart_ph = st.empty()
            metric_ph = st.empty()
            
            for _ in range(8): # 輕量化動畫
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
                time.sleep(0.5)

        with col2:
            st.subheader("📁 系統狀態")
            st.success("✅ Users DB")
            
            # [升級] 題庫健康度檢查
            qs, errs = load_qs_from_txt()
            if os.path.exists("questions.txt"):
                if not errs:
                    st.info("✅ Q-Bank (Healthy)")
                else:
                    st.warning(f"⚠️ Q-Bank ({len(errs)} Errors)")
                    with st.expander("查看錯誤"):
                        for e in errs: st.write(e)
            else:
                st.error("❌ Q-Bank Missing")
            
            st.metric("題庫總數", len(qs))
            db = load_users()
            st.metric("註冊用戶", len(db.get("users", [])))

    elif "電力設施" in page:
        st.header("⚡ 邏輯閘視覺化")
        col1, col2 = st.columns([1, 2])
        with col1:
            gate = st.selectbox("選擇邏輯閘", ["AND", "OR", "XOR"])
            st.caption("SVG 動態渲染")
        with col2:
            render_svg(SVG_ICONS.get(gate, SVG_ICONS["AND"]))

    elif "數據中心" in page:
        st.header("🏦 運算轉換中心")
        val = st.text_input("輸入十進位 (Decimal)", "255")
        if val.isdigit(): 
            c1, c2 = st.columns(2)
            c1.metric("十六進位 (Hex)", hex(int(val))[2:].upper())
            c2.metric("二進位 (Binary)", bin(int(val))[2:])

    elif "市政學院" in page:
        st.header("🎓 市政考評 (Batch-5)")
        qs, errs = load_qs_from_txt() # 取得題目
        
        if errs:
            st.warning(f"題庫檔案檢測到 {len(errs)} 行格式錯誤，請通知管理員修正。")
        
        if not st.session_state.exam_active:
            if st.button("🚀 啟動考核"):
                if len(qs) >= 5:
                    st.session_state.quiz_batch = random.sample(qs, 5)
                    st.session_state.exam_active = True
                    st.rerun()
                else: st.error(f"題庫不足 (目前有效: {len(qs)} 題)，需要至少 5 題。")
        else:
            with st.form("exam_form"):
                ans = {}
                for i, q in enumerate(st.session_state.quiz_batch):
                    st.write(f"**{i+1}. {q['q']}**")
                    ans[i] = st.radio("Select", q['o'], key=f"q{i}", index=None, label_visibility="collapsed")
                    st.divider()
                
                if st.form_submit_button("提交考卷"):
                    if any(a is None for a in ans.values()):
                        st.warning("請作答所有題目")
                    else:
                        score = sum([1 for i in range(5) if ans[i]==st.session_state.quiz_batch[i]['a']])
                        new_data = save_score(st.session_state.user_key, f"{score}/5")
                        st.session_state.user_data = new_data # 更新 Session 資料
                        
                        if score==5: st.balloons()
                        st.success(f"成績已存檔！得分: {score}")
                        st.session_state.exam_active = False
                        time.sleep(2); st.rerun()

    elif "人事檔案" in page:
        st.header("📂 檔案管理中心")
        st.text_input("當前用戶", user['name'], disabled=True)
        st.selectbox("介面主題", list(THEMES.keys()), key="theme_name")
        
        st.subheader("📊 考核績效分析")
        if "history" in user and user["history"]:
            # [升級] 數據視覺化 - 將成績字串轉為數字並繪圖
            hist_df = pd.DataFrame(user["history"])
            
            # 資料清理: "4/5" -> 4
            try:
                hist_df["numeric_score"] = hist_df["score"].apply(lambda x: int(str(x).split('/')[0]))
                
                # 繪製折線圖
                st.line_chart(hist_df[["date", "numeric_score"]].set_index("date"))
                
                # 顯示詳細表格 (最新的在上面)
                with st.expander("查看詳細列表"):
                    st.dataframe(hist_df.iloc[::-1])
            except:
                st.error("成績資料格式異常，無法繪製圖表。")
                st.dataframe(hist_df)
        else: 
            st.info("尚無考核紀錄，請前往「市政學院」進行測試。")
        
        st.divider()
        if st.button("登出系統"):
            st.session_state.logged_in = False
            st.session_state.user_data = {}
            st.rerun()

    # [升級] 指揮官專屬 - 核心控制頁面
    elif "核心控制" in page and is_commander:
        st.title("☢️ 核心控制台 (Commander Only)")
        st.warning("⚠️ 此區域擁有最高權限，請謹慎操作。")
        
        all_db = load_users()
        all_users = all_db.get("users", {})
        
        # 1. 檢視所有用戶表格
        st.subheader("👥 全域用戶監控")
        user_list = []
        for u_key, u_val in all_users.items():
            user_list.append({
                "ID": u_key,
                "Name": u_val["name"],
                "Level": u_val["level"],
                "History Count": len(u_val.get("history", []))
            })
        st.dataframe(pd.DataFrame(user_list), use_container_width=True)
        
        # 2. 權力操作區
        st.subheader("🛠️ 權限操作")
        col_admin1, col_admin2 = st.columns(2)
        
        with col_admin1:
            target_user = st.selectbox("選擇目標用戶", list(all_users.keys()))
            
        with col_admin2:
            if st.button("🔄 重置該用戶密碼 (Default: 1234)"):
                if target_user == "frank":
                    st.error("❌ 無法重置指揮官密碼！")
                else:
                    all_db["users"][target_user]["password"] = "1234"
                    save_users(all_db)
                    st.success(f"用戶 {target_user} 密碼已重置為 1234")
            
            if st.button("🗑️ 清空該用戶歷史紀錄"):
                all_db["users"][target_user]["history"] = []
                save_users(all_db)
                st.success(f"用戶 {target_user} 歷史紀錄已清空")

# ==================================================
# 4. 登入頁面
# ==================================================
def login_page():
    apply_theme()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("CityOS V180")
        st.caption("Secure Access System | user.json")
        
        # 登入頁面的題庫檢查
        if not os.path.exists("questions.txt"):
            st.error("⚠️ 嚴重錯誤：題庫 questions.txt 遺失。")
        else:
            _, errs = load_qs_from_txt()
            if errs: st.warning(f"⚠️ 警告：題庫包含 {len(errs)} 個格式錯誤。")

        tab1, tab2 = st.tabs(["🔒 登入", "📝 註冊"])
        with tab1:
            with st.form("login"):
                u = st.text_input("帳號")
                p = st.text_input("密碼", type="password")
                if st.form_submit_button("登入系統"):
                    data = authenticate(u, p)
                    if data:
                        st.session_state.logged_in = True
                        st.session_state.user_key = u
                        st.session_state.user_data = data
                        st.success("身份驗證成功"); time.sleep(0.5); st.rerun()
                    else: st.error("帳號或密碼錯誤")
        with tab2:
            with st.form("signup"):
                nu = st.text_input("設定新帳號")
                np_ = st.text_input("設定新密碼", type="password")
                ne = st.text_input("Email")
                if st.form_submit_button("建立檔案"):
                    ok, msg = register_user(nu, np_, ne)
                    if ok: st.success(msg)
                    else: st.error(msg)

if st.session_state.logged_in: main_app()
else: login_page()
