import streamlit as st
import pandas as pd
import json
import os
import re
from datetime import datetime

# =========================================
# 1. 究極樣式引擎 (修復文字隱形問題)
# =========================================
def apply_theme(p):
    hide_style = f"""
    <style>
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    .stApp {{
        background-color: {p.get('bg', '#121212')}; 
        color: {p.get('txt_color', '#FFFFFF')};
        font-size: {p.get('font_size', 16)}px;
    }}
    /* 強制設定所有標籤文字顏色，避免白底白字 */
    label, p, span, .stMarkdown {{
        color: {p.get('txt_color', '#FFFFFF')} !important;
    }}
    .stButton>button {{
        background-color: {p.get('btn', '#00D1B2')}; 
        color: white; 
        border-radius: {p.get('radius', 10)}px;
        border: {p.get('border_w', 2)}px solid white;
        font-weight: {'bold' if p.get('bold_txt', True) else 'normal'};
    }}
    /* 卡片與表格保護色 */
    div[data-testid="stTable"], .stAlert {{
        background-color: white !important; 
        color: black !important; 
        border-radius: 10px;
        padding: 10px;
    }}
    div[data-testid="stTable"] * {{ color: black !important; }}
    </style>
    """
    st.markdown(hide_style, unsafe_allow_html=True)

# =========================================
# 2. 完整邏輯閘與圖形引擎
# =========================================
SVG_LIB = {
    "AND": '''<svg viewBox="0 0 120 70" width="180"><path d="M40,10 H50 A25,25 0 0,1 50,60 H40 Z" fill="none" stroke="black" stroke-width="3"/><line x1="10" y1="25" x2="40" y2="25" stroke="black" stroke-width="3"/><line x1="10" y1="45" x2="40" y2="45" stroke="black" stroke-width="3"/><line x1="75" y1="35" x2="110" y2="35" stroke="black" stroke-width="3"/></svg>''',
    "OR": '''<svg viewBox="0 0 120 70" width="180"><path d="M35,10 Q50,35 35,60 Q70,60 95,35 Q70,10 35,10 Z" fill="none" stroke="black" stroke-width="3"/><line x1="10" y1="25" x2="38" y2="25" stroke="black" stroke-width="3"/><line x1="10" y1="45" x2="38" y2="45" stroke="black" stroke-width="3"/><line x1="95" y1="35" x2="115" y2="35" stroke="black" stroke-width="3"/></svg>''',
    "NOT": '''<svg viewBox="0 0 120 70" width="180"><path d="M40,15 L80,35 L40,55 Z" fill="none" stroke="black" stroke-width="3"/><circle cx="85" cy="35" r="5" fill="none" stroke="black" stroke-width="2"/><line x1="10" y1="35" x2="40" y2="35" stroke="black" stroke-width="3"/><line x1="90" y1="35" x2="115" y2="35" stroke="black" stroke-width="3"/></svg>''',
    "NAND": '''<svg viewBox="0 0 120 70" width="180"><path d="M40,10 H50 A25,25 0 0,1 50,60 H40 Z" fill="none" stroke="black" stroke-width="3"/><circle cx="80" cy="35" r="5" fill="none" stroke="black" stroke-width="2"/><line x1="10" y1="25" x2="40" y2="25" stroke="black" stroke-width="3"/><line x1="10" y1="45" x2="40" y2="45" stroke="black" stroke-width="3"/><line x1="85" y1="35" x2="110" y2="35" stroke="black" stroke-width="3"/></svg>''',
    "XOR": '''<svg viewBox="0 0 120 70" width="180"><path d="M35,10 Q50,35 35,60" fill="none" stroke="black" stroke-width="3"/><path d="M42,10 Q57,35 42,60 Q77,60 102,35 Q77,10 42,10 Z" fill="none" stroke="black" stroke-width="3"/><line x1="10" y1="25" x2="35" y2="25" stroke="black" stroke-width="3"/><line x1="10" y1="45" x2="35" y2="45" stroke="black" stroke-width="3"/><line x1="102" y1="35" x2="115" y2="35" stroke="black" stroke-width="3"/></svg>''',
    "FA": '''<svg viewBox="0 0 260 130" width="300"><rect x="80" y="15" width="100" height="100" fill="white" stroke="black" stroke-width="3"/><text x="130" y="70" text-anchor="middle" font-weight="bold">Full Adder</text><text x="30" y="40">A</text><text x="30" y="70">B</text><text x="230" y="45">Sum</text><text x="230" y="95">Cout</text></svg>'''
}

def render_svg(key, p):
    st.markdown(f'''<div style="display: table; margin: 15px auto; padding: 25px; background: white; border-radius: {p['radius']}px; border: {p['border_w']}px solid {p['btn']}; box-shadow: 0 8px 16px rgba(0,0,0,0.3);">{SVG_LIB[key]}</div>''', unsafe_allow_html=True)

# =========================================
# 3. 系統認證與註冊
# =========================================
DB_FILE = "logimind_v26_master.json"
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return {}
def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(db, f, indent=4, ensure_ascii=False)

def auth_gate():
    apply_theme({"bg":"#121212","txt_color":"#FFFFFF","btn":"#00D1B2","radius":10})
    st.title("🧪 LogiMind V26 究極個人化版")
    tab1, tab2 = st.tabs(["🔑 登入", "📝 嚴格註冊"])
    with tab2:
        n = st.text_input("真實姓名 (必填)", key="reg_n")
        u = st.text_input("使用者帳號 (英數)", key="reg_u")
        p = st.text_input("登入密碼 (需大於 8 碼)", type="password", key="reg_p")
        if st.button("確認註冊並建立環境"):
            db = load_db()
            if not n: st.error("姓名為必填項目")
            elif u in db: st.error("帳號已存在，請選擇其他名稱")
            elif len(p) <= 8: st.error("密碼長度不足，請設定 9 位以上")
            else:
                db[u] = {"pw":p, "name":n, "scores":[], "prefs":{"bg":"#0E1117","btn":"#00FFCC","txt_color":"#FFFFFF","font_size":16,"radius":12,"border_w":3,"bold_txt":True}}
                save_db(db); st.success("註冊成功！請切換至登入頁面")
    with tab1:
        ul, pl = st.text_input("帳號", key="lu"), st.text_input("密碼", type="password", key="lp")
        if st.button("進入實驗室"):
            db = load_db()
            if ul in db and db[ul]["pw"] == pl:
                st.session_state.user, st.session_state.name = ul, db[ul]["name"]
                st.session_state.prefs = db[ul]["prefs"]
                st.session_state.scores = db[ul].get("scores", [])
                st.rerun()

# =========================================
# 4. 主系統介面
# =========================================
def main():
    p = st.session_state.prefs
    apply_theme(p)
    db = load_db()

    with st.sidebar:
        st.title(f"🚀 {st.session_state.name}")
        page = st.radio("導覽選單", ["🏠 歡迎首頁", "🔬 完整邏輯閘", "🔢 格雷碼模組", "📝 20題挑戰賽", "🎨 個人化工作室", "📜 更新日誌", "🚪 登出"])

    if page == "🏠 歡迎首頁":
        st.header(f"🌟 實驗室已就緒，{st.session_state.name}！")
        st.write("這是您的全能邏輯控制台。所有的視覺顏色現在都能在「個人化工作室」自訂。")
        render_svg("FA", p)

    elif page == "🔬 完整邏輯閘":
        st.header("對稱視覺組件庫")
        g = st.selectbox("切換邏輯閘", ["AND", "OR", "NOT", "NAND", "XOR"])
        render_svg(g, p)

    elif page == "🔢 格雷碼模組":
        st.header("🔢 格雷碼轉換器")
        b_in = st.text_input("輸入二進制 (如 1101)", "1101")
        try:
            val = int(b_in, 2)
            gray = bin(val ^ (val >> 1))[2:].zfill(len(b_in))
            st.success(f"格雷碼結果: {gray}")
        except: st.error("請輸入正確的二進制格式")

    elif page == "🎨 個人化工作室":
        st.header("🎨 「億」點點風格自定義")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.prefs['bg'] = st.color_picker("背景顏色", p['bg'])
            st.session_state.prefs['txt_color'] = st.color_picker("文字顏色 (若配白底請選深色)", p['txt_color'])
            st.session_state.prefs['btn'] = st.color_picker("強調顏色 (按鈕與邊框)", p['btn'])
        with col2:
            st.session_state.prefs['font_size'] = st.slider("全域字體大小", 12, 32, p['font_size'])
            st.session_state.prefs['radius'] = st.slider("元件圓角", 0, 50, p['radius'])
            st.session_state.prefs['border_w'] = st.slider("邊框粗細", 1, 10, p['border_w'])
            st.session_state.prefs['bold_txt'] = st.checkbox("標題文字加粗", p['bold_txt'])
        
        if st.button("💾 儲存並套用新風格"):
            db[st.session_state.user]["prefs"] = st.session_state.prefs
            save_db(db); st.rerun()

    elif page == "📜 更新日誌":
        st.header("📜 版本傳奇 V26")
        st.table(pd.DataFrame([{"版本": "V25", "內容": "補齊邏輯閘、格雷碼回歸"}, {"版本": "V26", "內容": "修復文字隱形、增加字體大小與邊框個人化"}]))

    elif page == "🚪 登出":
        del st.session_state.user; st.rerun()

if "user" not in st.session_state: auth_gate()
else: main()
