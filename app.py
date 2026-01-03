import streamlit as st
import pandas as pd
import random
import os
import base64
import time
import json
import hashlib # 新增雜湊函式庫
import numpy as np 
from datetime import datetime

# ==================================================
# 0. 資料庫與權限核心
# ==================================================
USER_DB_FILE = "users.json"

# 定義權限等級分數
LEVEL_MAP = {
    "實習生": 0,
    "初級管理員": 1,
    "中級管理員": 2,
    "高級管理員": 3,
    "最高指揮官": 99
}

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
                # --- 預設用戶 ---
                "user": {
                    "password": "123",
                    "name": "Site Operator",
                    "email": "op@cityos.gov",
                    "level": "初級管理員", 
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
    # 新註冊預設為 初級管理員
    db["users"][u] = {
        "password": p, "name": u, "email": email, "level": "初級管理員",
        "avatar_color": random.choice(["#4285F4", "#34A853", "#FBBC05"]), "history": []
    }
    save_users(db)
    return True, "註冊成功"

def check_access(user_level_str, required_level_str):
    """檢查用戶等級是否 >= 需求等級"""
    u_score = LEVEL_MAP.get(user_level_str, 0)
    r_score = LEVEL_MAP.get(required_level_str, 0)
    return u_score >= r_score

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
st.set_page_config(page_title="CityOS V3.2", layout="wide", page_icon="🏙️")

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
        "quiz_batch": [],
        "kmap_data": [0]*8 
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
    .intro-box {{ background-color: rgba(0, 173, 181, 0.1); border-left: 5px solid #00ADB5; padding: 15px; border-radius: 5px; margin-bottom: 20px; line-height: 1.6;}}
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
    user_lvl = user.get("level", "實習生")
    apply_theme()
    t_colors = THEMES[st.session_state.theme_name]["chart"]
    
    is_commander = (user_lvl == "最高指揮官")

    with st.sidebar:
        st.title("🏙️ CityOS V3.2")
        st.caption("Secured Infrastructure")
        
        # --- 個人卡片 ---
        card_bg = "rgba(255,255,255,0.05)"
        border_color = user.get('avatar_color', '#888')
        card_class = "commander-card" if is_commander else ""
        badge_html = "<div class='commander-badge'>SUPREME ACCESS</div>" if is_commander else ""
        
        style_str = f"padding:15px; background:{card_bg}; border-radius:8px; margin-bottom:15px; border-left:4px solid {border_color};"
        
        st.markdown(f"""
        <div class="{card_class}" style="{style_str}">
            <div style="font-size:1.1em; font-weight:bold;">{user['name']}</div>
            <div style="font-size:0.8em; opacity:0.7;">{user['email']}</div>
            <div style="font-size:0.8em; margin-top:5px; color:{border_color};">{user_lvl}</div>
            {badge_html}
        </div>
        """, unsafe_allow_html=True)
        # ---------------
        
        # 動態選單生成
        st.markdown("### 導航選單")
        menu_options = {
            "Dashboard": "🏙️ 城市儀表板",
            "Electricity": "⚡ 電力設施 (Logic)",
            "Boolean": "🧩 布林轉換器 (Lv1+)",
            "GrayCode": "🏦 格雷碼核心 (Lv2+)",
            "BaseConv": "🔢 進制轉換 (Lv2+)",
            "InfoSec": "🛡️ 資訊安全局 (Lv2+)", # NEW
            "KMap": "🗺️ 卡諾圖 (Lv3+)",
            "Academy": "🎓 市政學院",
            "UpdateLog": "📜 更新日誌",
            "Profile": "📂 人事檔案"
        }
        
        if is_commander:
            menu_options["Commander"] = "☢️ 核心控制"

        selection = st.radio("前往", list(menu_options.values()), label_visibility="collapsed")

    # -------------------------------------------
    # 頁面: 城市儀表板 (All)
    # -------------------------------------------
    if selection == "🏙️ 城市儀表板":
        col_h1, col_h2 = st.columns([3, 1])
        with col_h1: st.title(f"👋 歡迎，{user['name']}")
        with col_h2: st.caption(datetime.now().strftime("%Y-%m-%d %H:%M"))

        # 系統簡介
        st.markdown("""
        <div class="intro-box">
            <b>CityOS (Urban Operation System) V3.2</b> 是一套專為現代智慧城市設計的中央控制中樞。
            整合底層邏輯運算、多進制數據處理以及高階權限管理，並新增了<b>資訊安全局</b>以強化數據加密傳輸監控。
            <br><br>
            系統採用嚴格的分級授權機制（Level 1 至 Level 3），確保只有經過考核的合格人員能操作關鍵設施。
            透過即時數據儀表板與市政學院的持續考核，我們致力於構建一個安全、高效且可持續發展的運算城市生態系統。
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("📡 即時監控")
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
            st.subheader("📁 狀態")
            qs, errs = load_qs_from_txt()
            st.metric("題庫總數", len(qs))
            st.metric("您的權限等級", LEVEL_MAP.get(user_lvl, 0))

    # -------------------------------------------
    # 頁面: 電力設施 (All)
    # -------------------------------------------
    elif selection == "⚡ 電力設施 (Logic)":
        st.header("⚡ 邏輯閘視覺化")
        col1, col2 = st.columns([1, 2])
        with col1:
            gate = st.selectbox("選擇邏輯閘", ["AND", "OR", "XOR", "MUX"])
        with col2:
            render_svg(SVG_ICONS.get(gate, SVG_ICONS["AND"]))

    # -------------------------------------------
    # 頁面: 布林轉換器 (Lv1+)
    # -------------------------------------------
    elif selection == "🧩 布林轉換器 (Lv1+)":
        if check_access(user_lvl, "初級管理員"):
            st.header("🧩 布林代數實驗室")
            st.caption("Boolean Algebra Converter")
            
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("真值表生成器")
                op = st.selectbox("運算邏輯", ["A AND B", "A OR B", "A XOR B", "NOT A", "NAND"])
            
            with c2:
                st.subheader("結果")
                res = []
                for a in [0, 1]:
                    for b in [0, 1]:
                        if op == "A AND B": val = a & b
                        elif op == "A OR B": val = a | b
                        elif op == "A XOR B": val = a ^ b
                        elif op == "NOT A": val = 1 - a
                        elif op == "NAND": val = 1 - (a & b)
                        res.append({"A": a, "B": b, "Out": val})
                st.dataframe(pd.DataFrame(res), use_container_width=True)
        else:
            st.error("🔒 權限不足：需要 [初級管理員] 權限。")

    # -------------------------------------------
    # 頁面: 格雷碼核心 (Lv2+)
    # -------------------------------------------
    elif selection == "🏦 格雷碼核心 (Lv2+)":
        if check_access(user_lvl, "中級管理員"):
            st.header("🏦 格雷碼運算單元")
            st.caption("Gray Code Processor")
            st.info("權限驗證通過：中級管理員存取權限")
            
            val_str = st.text_input("輸入十進位數值", "127")
            if val_str.isdigit():
                val = int(val_str)
                gray_val = val ^ (val >> 1)
                c1, c2 = st.columns(2)
                with c1: st.metric("Binary", bin(val)[2:])
                with c2: st.metric("Gray Code", bin(gray_val)[2:])
                st.success(f"轉換成功：{val} -> {bin(gray_val)[2:]}")
            else:
                st.error("請輸入整數")
        else:
            st.error("🔒 權限不足：需要 [中級管理員] 權限。")

    # -------------------------------------------
    # 頁面: 進制轉換 (Lv2+)
    # -------------------------------------------
    elif selection == "🔢 進制轉換 (Lv2+)":
        if check_access(user_lvl, "中級管理員"):
            st.header("🔢 多功能進制轉換器")
            st.caption("Advanced Base Converter (2/8/10/16)")
            
            c1, c2 = st.columns(2)
            with c1:
                base_from = st.selectbox("來源進制", [2, 8, 10, 16], index=2)
                num_input = st.text_input("輸入數值", "255")
            
            with c2:
                try:
                    dec_val = int(num_input, base_from)
                    st.write("---")
                    st.write(f"**BIN (2):** `{bin(dec_val)[2:]}`")
                    st.write(f"**OCT (8):** `{oct(dec_val)[2:]}`")
                    st.write(f"**DEC (10):** `{dec_val}`")
                    st.write(f"**HEX (16):** `{hex(dec_val)[2:].upper()}`")
                except ValueError:
                    st.error("輸入格式與選擇的進制不符")
        else:
            st.error("🔒 權限不足：需要 [中級管理員] 權限。")

    # -------------------------------------------
    # 頁面: 資訊安全局 (Lv2+) - NEW
    # -------------------------------------------
    elif selection == "🛡️ 資訊安全局 (Lv2+)":
        if check_access(user_lvl, "中級管理員"):
            st.header("🛡️ 資訊安全局 (InfoSec Bureau)")
            st.caption("Cryptography & Hashing Tools")
            
            tab_crypt, tab_hash = st.tabs(["🔐 凱薩加密 (Caesar)", "#️⃣ 數位雜湊 (Hashing)"])
            
            with tab_crypt:
                st.subheader("古典加密通訊")
                c1, c2 = st.columns([2, 1])
                with c1:
                    plain_text = st.text_input("輸入明文 (Plain Text)", "HELLO CITY")
                    shift = st.slider("偏移量 (Shift Key)", 1, 25, 3)
                with c2:
                    st.write("")
                    st.write("")
                    mode = st.radio("模式", ["加密", "解密"], horizontal=True)
                
                result_text = ""
                if plain_text:
                    for char in plain_text:
                        if char.isalpha():
                            start = 65 if char.isupper() else 97
                            offset = shift if mode == "加密" else -shift
                            result_text += chr((ord(char) - start + offset) % 26 + start)
                        else:
                            result_text += char
                
                st.success(f"運算結果: {result_text}")

            with tab_hash:
                st.subheader("單向雜湊驗證")
                st.info("雜湊函數是不可逆的，常用於密碼儲存與檔案驗證。")
                
                hash_input = st.text_input("輸入任意字串", "MyPassword123")
                if hash_input:
                    # MD5
                    md5_val = hashlib.md5(hash_input.encode()).hexdigest()
                    # SHA256
                    sha_val = hashlib.sha256(hash_input.encode()).hexdigest()
                    
                    st.code(f"MD5    : {md5_val}", language="text")
                    st.code(f"SHA-256: {sha_val}", language="text")

        else:
            st.error("🔒 權限不足：需要 [中級管理員] 權限。")

    # -------------------------------------------
    # 頁面: 卡諾圖 (Lv3+)
    # -------------------------------------------
    elif selection == "🗺️ 卡諾圖 (Lv3+)":
        if check_access(user_lvl, "高級管理員"):
            st.header("🗺️ 卡諾圖求簡 (3變數)")
            st.caption("Karnaugh Map Solver")
            
            c_label, c00, c01, c11, c10 = st.columns([1,1,1,1,1])
            with c_label: st.write("**BC:**")
            with c00: st.write("00")
            with c01: st.write("01")
            with c11: st.write("11")
            with c10: st.write("10")
            
            # Row A=0
            r0_label, r0_00, r0_01, r0_11, r0_10 = st.columns([1,1,1,1,1])
            with r0_label: st.write("**A=0**")
            m0 = r0_00.checkbox("m0", key="k0")
            m1 = r0_01.checkbox("m1", key="k1")
            m3 = r0_11.checkbox("m3", key="k3")
            m2 = r0_10.checkbox("m2", key="k2")
            
            # Row A=1
            r1_label, r1_00, r1_01, r1_11, r1_10 = st.columns([1,1,1,1,1])
            with r1_label: st.write("**A=1**")
            m4 = r1_00.checkbox("m4", key="k4")
            m5 = r1_01.checkbox("m5", key="k5")
            m7 = r1_11.checkbox("m7", key="k7")
            m6 = r1_10.checkbox("m6", key="k6")

            minterms = []
            if m0: minterms.append(0)
            if m1: minterms.append(1)
            if m2: minterms.append(2)
            if m3: minterms.append(3)
            if m4: minterms.append(4)
            if m5: minterms.append(5)
            if m6: minterms.append(6)
            if m7: minterms.append(7)
            
            st.divider()
            if minterms:
                st.info(f"Σm({', '.join(map(str, minterms))})")
                st.write("Sum of Minterms 計算完成。")
            else:
                st.write("輸出為 0")
        else:
            st.error("🔒 權限不足：需要 [高級管理員] 權限。")

    # -------------------------------------------
    # 頁面: 市政學院 (All)
    # -------------------------------------------
    elif selection == "🎓 市政學院":
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
    # 頁面: 更新日誌 (All)
    # -------------------------------------------
    elif selection == "📜 更新日誌":
        st.header("📜 CityOS 系統更新日誌")
        st.markdown("""
        ### Version 3.2 (Security Update)
        * **New Feature**: 新增 **[🛡️ 資訊安全局]**，包含凱薩加密 (Caesar Cipher) 與 雜湊計算 (SHA-256)。
        * **Permission**: 資訊安全局列為 **Level 2 (中級管理員)** 功能。
        
        ### Version 3.1
        * **Architecture**: 權限架構優化，格雷碼獨立為 Lv2 功能。
        * **UI**: 更新日誌移至側欄底部，新增儀表板簡介。

        ### Version 3.0
        * **Core**: 實裝五級權限系統 (Intern ~ Commander)。
        * **Modules**: 新增布林轉換、進制轉換、卡諾圖。
        """)

    # -------------------------------------------
    # 頁面: 人事檔案 (All)
    # -------------------------------------------
    elif selection == "📂 人事檔案":
        st.header("📂 檔案管理中心")
        st.text_input("當前用戶", user['name'], disabled=True)
        st.info(f"目前權限等級: {user_lvl}")
        st.selectbox("介面主題", list(THEMES.keys()), key="theme_name")
        
        st.subheader("📊 考核績效趨勢")
        if "history" in user and user["history"]:
            hist_df = pd.DataFrame(user["history"])
            try:
                hist_df["numeric_score"] = hist_df["score"].apply(lambda x: int(str(x).split('/')[0]))
                st.line_chart(hist_df[["date", "numeric_score"]].set_index("date"))
            except:
                st.dataframe(hist_df)
        else: st.info("尚無考核紀錄")
        
        if st.button("登出系統"):
            st.session_state.logged_in = False
            st.session_state.user_data = {}
            st.rerun()

    # -------------------------------------------
    # 頁面: 核心控制 (Commander Only)
    # -------------------------------------------
    elif selection == "☢️ 核心控制" and is_commander:
        st.title("☢️ 核心控制台")
        st.warning("Commander Access Granted")
        
        all_db = load_users()
        # 顯示並編輯用戶等級
        st.subheader("用戶權限管理")
        
        c_adm1, c_adm2, c_adm3 = st.columns(3)
        with c_adm1:
            target = st.selectbox("選擇目標用戶", list(all_db["users"].keys()))
        with c_adm2:
            new_lvl = st.selectbox("調整權限等級", ["實習生", "初級管理員", "中級管理員", "高級管理員", "最高指揮官"])
        with c_adm3:
            st.write("")
            st.write("")
            if st.button("更新權限"):
                if target == "frank" and new_lvl != "最高指揮官":
                    st.error("不能降級指揮官")
                else:
                    all_db["users"][target]["level"] = new_lvl
                    save_users(all_db)
                    st.success(f"{target} 已更新為 {new_lvl}")
                    time.sleep(1)
                    st.rerun()
                    
        st.divider()
        users_list = [{"ID":k, "Name":v["name"], "Level":v["level"]} for k,v in all_db["users"].items()]
        st.dataframe(pd.DataFrame(users_list), use_container_width=True)

# ==================================================
# 4. 登入頁面
# ==================================================
def login_page():
    apply_theme()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("CityOS V3.2")
        st.caption("Secure Information Systems")
        
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
