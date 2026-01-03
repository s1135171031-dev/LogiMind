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
# 0. 資料庫核心 (User DB)
# ==================================================
USER_DB_FILE = "users.json"

def init_user_db():
    should_init = False
    if not os.path.exists(USER_DB_FILE) or os.path.getsize(USER_DB_FILE) == 0:
        should_init = True
            
    if should_init:
        default_data = {
            "users": {
                # --- Frank (指揮官) ---
                "frank": {
                    "password": "x12345678x",
                    "name": "Frank (Supreme Commander)",
                    "email": "frank@cityos.gov",
                    "level": "最高指揮官",
                    "avatar_color": "#000000",
                    "history": []
                },
                # --- 一般用戶 ---
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
st.set_page_config(page_title="CityOS V215", layout="wide", page_icon="🏙️")

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
    
    .commander-card {{ border: 2px solid gold !important; box-shadow: 0 0 15px rgba(255, 215, 0, 0.2); background: linear-gradient(135deg, rgba(0,0,0,0.8), rgba(50,50,50,0.9)); }}
    .commander-badge {{ color: gold; font-weight: bold; font-size: 0.8em; border: 1px solid gold; padding: 2px 6px; border-radius: 4px; display: inline-block; margin-top:5px;}}
    
    .manual-box {{ background-color: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; border-left: 4px solid #00ADB5; margin-bottom: 20px; }}
    </style>
    """, unsafe_allow_html=True)

def render_svg(svg_code):
    svg_black = svg_code.replace('stroke="currentColor"', 'stroke="#888888"').replace('fill="currentColor"', 'fill="#888888"')
    b64 = base64.b64encode(svg_black.encode('utf-8')).decode("utf-8")
    st.markdown(f'''<div style="background-color: rgba(255,255,255,0.05); border-radius: 8px; padding: 20px; margin-bottom: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"><img src="data:image/svg+xml;base64,{b64}" width="200"/></div>''', unsafe_allow_html=True)

def load_qs_from_txt():
    q = []
    errors = []
    if os.path.exists("questions.txt"):
        try:
            with open("questions.txt", "r", encoding="utf-8") as f:
                for idx, l in enumerate(f):
                    line_content = l.strip()
                    if not line_content: continue
                    p = line_content.split("|")
                    if len(p) == 5: 
                        q.append({"id":p[0],"diff":p[1],"q":p[2],"o":p[3].split(","),"a":p[4]})
                    else:
                        errors.append(f"Line {idx+1}: 格式錯誤")
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
    
    is_commander = (user.get("level") == "最高指揮官")

    with st.sidebar:
        st.title("🏙️ CityOS V215")
        st.caption("Central Command Unit")
        
        # --- 個人卡片 ---
        card_bg = "rgba(255,255,255,0.05)"
        border_color = user.get('avatar_color', '#888')
        card_class = "commander-card" if is_commander else ""
        badge_html = "<div class='commander-badge'>SUPREME ACCESS</div>" if is_commander else ""
        
        # [修復點] 這裡原本少了結尾引號，現在已經加上了
        style_str = f"padding:15px; background:{card_bg}; border-radius:8px; margin-bottom:15px; border-left:4px solid {border_color};
        
        st.markdown(f"""
        <div class="{card_class}" style="{style_str}">
            <div style="font-size:1.1em; font-weight:bold;">{user['name']}</div>
            <div style="font-size:0.8em; opacity:0.7;">{user['email']}</div>
            <div style="font-size:0.8em; margin-top:5px; color:{border_color};">{user['level']}</div>
            {badge_html}
        </div>
        """, unsafe_allow_html=True)
        # ---------------
        
        menu = ["🏙️ 城市儀表板", "⚡ 電力設施", "🏦 數據中心", "🎓 市政學院", "📂 人事檔案"]
        if is_commander:
            menu.append("☢️ 核心控制")
        page = st.radio("導航", menu)

    # -------------------------------------------
    # 頁面 1: 城市儀表板 (資訊全開)
    # -------------------------------------------
    if "城市儀表板" in page:
        # [標題區] 
        col_h1, col_h2 = st.columns([3, 1])
        with col_h1: 
            st.title(f"👋 歡迎，{user['name']}")
        with col_h2: 
            st.write("")
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            st.caption(f"📅 更新至: {now_str}")

        # [介紹區] 這裡直接顯示
        st.markdown("""
        <div class="manual-box">
            <h4>📖 城市作業系統操作指南 (System Manual)</h4>
            <ul>
                <li><b>城市儀表板 (Dashboard)</b>: 監控 CPU/NET/SEC 系統即時數據。</li>
                <li><b>電力設施 (Electricity)</b>: 邏輯閘運作視覺化 (AND/OR/XOR/MUX)。</li>
                <li><b>數據中心 (Data Center)</b>: 提供 進制轉換 與 格雷碼 (Gray Code) 計算。</li>
                <li><b>市政學院 (Academy)</b>: 進行人員考核，記錄成績。</li>
                <li><b>核心控制 (Commander)</b>: Frank 專屬權限管理後台。</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("📡 即時監控 (Real-time)")
            chart_ph = st.empty()
            metric_ph = st.empty()
            
            for _ in range(5): 
                df = update_data_random_walk()
                chart_ph.area_chart(df, color=t_colors, height=250)
                last = df.iloc[-1]
                metric_ph.markdown(f"""
                <div style="display:flex; justify-content:space-around; background:rgba(255,255,255,0.1); padding:10px; border-radius:5px;">
                    <div>CPU: <b>{int(last['CPU'])}%</b></div>
                    <div>NET: <b>{int(last['NET'])} Mbps</b></div>
                    <div>SEC: <b>{int(last['SEC'])} Lvl</b></div>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(0.3)

        with col2:
            st.subheader("📁 系統狀態")
            qs, errs = load_qs_from_txt()
            if os.path.exists("questions.txt") and not errs:
                st.info("✅ Q-Bank Ready")
            else:
                st.warning(f"⚠️ Errors: {len(errs)}")
            
            st.metric("題庫總數", len(qs))
            db = load_users()
            st.metric("總用戶數", len(db.get("users", [])))

    # -------------------------------------------
    # 頁面 2: 電力設施 (直接可用)
    # -------------------------------------------
    elif "電力設施" in page:
        st.header("⚡ 邏輯閘視覺化")
        st.caption("Logic Gate Simulator")
        col1, col2 = st.columns([1, 2])
        with col1:
            gate = st.selectbox("選擇邏輯閘", ["AND", "OR", "XOR", "MUX"])
            st.info("選擇不同的邏輯閘以觀察電路符號。")
        with col2:
            render_svg(SVG_ICONS.get(gate, SVG_ICONS["AND"]))

    # -------------------------------------------
    # 頁面 3: 數據中心 (含格雷碼，直接可用)
    # -------------------------------------------
    elif "數據中心" in page:
        st.header("🏦 運算轉換中心")
        st.caption("Advanced Computing & Gray Code Unit")
        
        val_str = st.text_input("輸入十進位數值 (Decimal)", "127")
        
        if val_str.isdigit():
            val = int(val_str)
            # 格雷碼計算
            gray_val = val ^ (val >> 1)
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("十六進位 (Hex)", hex(val)[2:].upper())
            with c2:
                st.metric("二進位 (Binary)", bin(val)[2:])
            with c3:
                st.metric("格雷碼 (Gray Code)", bin(gray_val)[2:])
                
            st.markdown("---")
            st.write(f"**詳細轉換資訊**: Decimal `{val}` -> Binary `{bin(val)[2:]}` -> Gray `{bin(gray_val)[2:]}`")
        else:
            st.error("請輸入有效的整數")

    # -------------------------------------------
    # 頁面 4: 市政學院
    # -------------------------------------------
    elif "市政學院" in page:
        st.header("🎓 市政考評")
        qs, errs = load_qs_from_txt()
        
        if errs: st.warning(f"題庫錯誤: {len(errs)} 行")
        
        if not st.session_state.exam_active:
            if st.button("🚀 啟動考核"):
                if len(qs) >= 5:
                    st.session_state.quiz_batch = random.sample(qs, 5)
                    st.session_state.exam_active = True
                    st.rerun()
                else: st.error("題庫不足 5 題")
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
                        st.session_state.user_data = new_data
                        
                        if score==5: st.balloons()
                        st.success(f"成績存檔完成！得分: {score}")
                        st.session_state.exam_active = False
                        time.sleep(2); st.rerun()

    # -------------------------------------------
    # 頁面 5: 人事檔案 (含圖表)
    # -------------------------------------------
    elif "人事檔案" in page:
        st.header("📂 檔案管理中心")
        st.text_input("當前用戶", user['name'], disabled=True)
        st.selectbox("介面主題", list(THEMES.keys()), key="theme_name")
        
        st.subheader("📊 考核績效趨勢")
        if "history" in user and user["history"]:
            hist_df = pd.DataFrame(user["history"])
            try:
                hist_df["numeric_score"] = hist_df["score"].apply(lambda x: int(str(x).split('/')[0]))
                st.line_chart(hist_df[["date", "numeric_score"]].set_index("date"))
                with st.expander("查看詳細列表"):
                    st.dataframe(hist_df.iloc[::-1], use_container_width=True)
            except:
                st.dataframe(hist_df)
        else: st.info("尚無考核紀錄")
        
        st.divider()
        if st.button("登出系統"):
            st.session_state.logged_in = False
            st.session_state.user_data = {}
            st.rerun()

    # -------------------------------------------
    # 頁面 6: 核心控制 (Frank Only)
    # -------------------------------------------
    elif "核心控制" in page and is_commander:
        st.title("☢️ 核心控制台")
        st.warning("Commander Access Granted")
        
        all_db = load_users()
        users_list = [{"ID":k, "Name":v["name"], "Level":v["level"]} for k,v in all_db["users"].items()]
        st.dataframe(pd.DataFrame(users_list), use_container_width=True)
        
        col_adm1, col_adm2 = st.columns(2)
        with col_adm1:
            target = st.selectbox("選擇目標用戶", list(all_db["users"].keys()))
        with col_adm2:
            if st.button("重置密碼 (預設: 1234)"):
                if target == "frank": st.error("不可重置指揮官")
                else:
                    all_db["users"][target]["password"] = "1234"
                    save_users(all_db)
                    st.success("密碼已重置")
            if st.button("清空該用戶紀錄"):
                all_db["users"][target]["history"] = []
                save_users(all_db)
                st.success("紀錄已清空")

# ==================================================
# 4. 登入頁面
# ==================================================
def login_page():
    apply_theme()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("CityOS V215")
        st.caption("Full Access Restoration")
        
        if not os.path.exists("questions.txt"):
            st.error("⚠️ 嚴重錯誤：題庫 questions.txt 遺失。")

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
                        st.rerun()
                    else: st.error("帳號或密碼錯誤")
        with tab2:
            with st.form("signup"):
                nu = st.text_input("新帳號")
                np_ = st.text_input("新密碼", type="password")
                ne = st.text_input("Email")
                if st.form_submit_button("建立檔案"):
                    ok, msg = register_user(nu, np_, ne)
                    if ok: st.success(msg)
                    else: st.error(msg)

if st.session_state.logged_in: main_app()
else: login_page()
