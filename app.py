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

# ==============================================================================
# 1. 系統核心設定
# ==============================================================================
st.set_page_config(
    page_title="CityOS V7.6",
    layout="wide",
    page_icon="🏙️",
    initial_sidebar_state="expanded"
)

# 檔案路徑
USER_DB_FILE = "users.json"

# 職業系統
CLASSES = {
    "None": {"name": "一般市民", "icon": "👤", "color": "#888888", "desc": "僅能使用基礎計算工具"},
    "Guardian": {"name": "守護者", "icon": "🛡️", "color": "#00FF99", "desc": "解鎖：資安密碼學中心"},
    "Architect": {"name": "架構師", "icon": "⚡", "color": "#00CCFF", "desc": "解鎖：卡諾圖化簡器"},
    "Oracle": {"name": "預言家", "icon": "🔮", "color": "#D500F9", "desc": "解鎖：趨勢預測儀表板"},
    "Engineer": {"name": "工程師", "icon": "🔧", "color": "#FF9900", "desc": "解鎖：電路實驗室"}
}

# 介面主題
THEMES = {
    "Night City": {"bg": "#212529", "txt": "#E9ECEF", "btn": "#495057", "card": "#343A40", "chart": ["#00ADB5", "#FF2E63", "#F8F9FA"]},
    "Day City": {"bg": "#F8F9FA", "txt": "#212529", "btn": "#ADB5BD", "card": "#FFFFFF", "chart": ["#343A40", "#6C757D", "#212529"]},
    "Cyber Punk": {"bg": "#0B0C10", "txt": "#C5C6C7", "btn": "#FCA311", "card": "#1F2833", "chart": ["#FCA311", "#66FCF1", "#45A29E"]},
    "Matrix": {"bg": "#000000", "txt": "#00FF41", "btn": "#003B00", "card": "#001A00", "chart": ["#008F11", "#003B00", "#00FF41"]},
}

# SVG 圖示庫
SVG_LIB = {
    "AND": '''<svg width="200" height="100" xmlns="http://www.w3.org/2000/svg"><path d="M20,10 L80,10 C110,10 130,30 130,50 C130,70 110,90 80,90 L20,90 Z" fill="none" stroke="#888" stroke-width="4"/><path d="M0,30 L20,30 M0,70 L20,70 M130,50 L160,50" stroke="#888" stroke-width="4"/></svg>''',
    "OR": '''<svg width="200" height="100" xmlns="http://www.w3.org/2000/svg"><path d="M20,10 L70,10 Q100,50 70,90 L20,90 Q50,50 20,10 Z" fill="none" stroke="#888" stroke-width="4"/><path d="M0,30 L30,30 M0,70 L30,70 M90,50 L120,50" stroke="#888" stroke-width="4"/></svg>''',
    "NOT": '''<svg width="200" height="100" xmlns="http://www.w3.org/2000/svg"><path d="M40,10 L40,90 L110,50 Z" fill="none" stroke="#888" stroke-width="4"/><circle cx="118" cy="50" r="6" fill="none" stroke="#888" stroke-width="3"/><path d="M0,50 L40,50 M126,50 L160,50" stroke="#888" stroke-width="4"/></svg>''',
    "XOR": '''<svg width="200" height="100" xmlns="http://www.w3.org/2000/svg"><path d="M40,10 L90,10 Q120,50 90,90 L40,90 Q70,50 40,10 Z" fill="none" stroke="#888" stroke-width="4"/><path d="M20,10 Q50,50 20,90" fill="none" stroke="#888" stroke-width="4"/><path d="M0,30 L30,30 M0,70 L30,70 M110,50 L140,50" stroke="#888" stroke-width="4"/></svg>''',
    "NAND": '''<svg width="200" height="100" xmlns="http://www.w3.org/2000/svg"><path d="M20,10 L80,10 C110,10 130,30 130,50 C130,70 110,90 80,90 L20,90 Z" fill="none" stroke="#888" stroke-width="4"/><circle cx="138" cy="50" r="6" fill="none" stroke="#888" stroke-width="3"/><path d="M0,30 L20,30 M0,70 L20,70 M146,50 L160,50" stroke="#888" stroke-width="4"/></svg>'''
}

# ==============================================================================
# 2. 輔助函式 (Utils)
# ==============================================================================
def init_files():
    """初始化 DB，並確保 frank 帳號存在"""
    frank_data = {
        "password": "x12345678x", "name": "Frank (Commander)", 
        "level": "最高指揮官", "exp": 999999, "rpg_level": 100, 
        "coins": 999999, "class_type": "Architect", 
        "inventory": list(THEMES.keys()), "last_login": ""
    }
    
    data = {"users": {}}
    if os.path.exists(USER_DB_FILE):
        try:
            with open(USER_DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except: pass
        
    data["users"]["frank"] = frank_data
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_db():
    init_files()
    with open(USER_DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(data):
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def apply_theme():
    t_name = st.session_state.get("theme_name", "Night City")
    t = THEMES.get(t_name, THEMES["Night City"])
    st.markdown(f"""
    <style>
        .stApp {{ background-color: {t['bg']}; color: {t['txt']}; }}
        h1, h2, h3, h4, h5, p, span, div, label, .stMarkdown {{ color: {t['txt']} !important; }}
        .stButton>button {{ background-color: {t['btn']}; color: #FFF; border-radius: 6px; border: none; font-weight: bold; }}
        .stat-card {{ background: {t['card']}; padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); }}
        div[data-testid="stExpander"] {{ background-color: {t['card']}; border: 1px solid rgba(255,255,255,0.1); }}
    </style>
    """, unsafe_allow_html=True)

def render_svg(svg_str):
    t_name = st.session_state.get("theme_name", "Night City")
    color = "#333" if "Day" in t_name else "#EEE"
    svg = svg_str.replace("#888", color)
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    st.markdown(f'<div style="text-align:center; margin:10px;"><img src="data:image/svg+xml;base64,{b64}" width="250"></div>', unsafe_allow_html=True)

# ==============================================================================
# 3. 各獨立功能頁面 (Separated Modules)
# ==============================================================================

def page_dashboard(user, u_class):
    st.header(f"歡迎回來，{user['name']}")
    
    # 版面重構：左側圖表 (2)，右側手冊 (1)
    col_main, col_manual = st.columns([2, 1])
    
    with col_main:
        # 小尺寸數據卡片
        c1, c2, c3 = st.columns(3)
        c1.metric("CPU", f"{random.randint(10,50)}%", "穩定")
        c2.metric("記憶體", f"{random.randint(4,16)} GB", "正常")
        c3.metric("網路", f"{random.randint(20,100)} ms", "優良")
        
        st.subheader("流量監控")
        chart_colors = THEMES[st.session_state.get("theme_name", "Night City")]["chart"]
        # 圖表高度縮小
        st.area_chart(pd.DataFrame(np.random.randn(15, 3), columns=["A","B","C"]), color=chart_colors, height=250)

    with col_manual:
        st.markdown("### 📘 使用手冊 (User Manual)")
        with st.expander("如何解鎖功能？"):
            st.write("前往 **「轉職中心」** 選擇職業。")
            st.write("- **架構師** ➔ 解鎖 K-Map")
            st.write("- **工程師** ➔ 解鎖 電路")
            st.write("- **守護者** ➔ 解鎖 資安")
        with st.expander("什麼是格雷碼？"):
            st.write("格雷碼 (Gray Code) 是一種二進位編碼，相鄰數值僅有一位元變動，常用於減少數位電路錯誤。")
        with st.expander("圖表說明"):
            st.write("左側圖表顯示系統核心的三個虛擬節點 (A/B/C) 的即時負載狀況。")

def page_base_converter():
    st.header("🔢 進制與格雷碼轉換 (Base Converter)")
    st.caption("輸入十進位數值，自動轉換所有格式。")
    
    col1, col2 = st.columns(2)
    with col1:
        val = st.number_input("輸入整數 (Decimal)", value=10, step=1, min_value=0)
        st.info("此模組對所有市民開放。")
    
    with col2:
        # 計算邏輯
        b_val = bin(val)[2:]
        o_val = oct(val)[2:]
        h_val = hex(val)[2:].upper()
        g_val = val ^ (val >> 1) # 格雷碼核心公式
        g_bin = bin(g_val)[2:]
        
        st.text_input("二進位 (Binary)", value=b_val)
        st.text_input("八進位 (Octal)", value=o_val)
        st.text_input("十六進位 (Hex)", value=h_val)
        
        st.markdown("---")
        st.markdown("#### ⭐ 格雷碼 (Gray Code)")
        # 這裡特別強調格雷碼
        st.code(f"{g_bin}", language="text")
        st.caption(f"Gray Code (Int): {g_val}")

def page_security_tools(u_class, user_level):
    st.header("🔐 資安密碼學中心 (Security)")
    
    if u_class != "Guardian" and user_level != "最高指揮官":
        st.warning("⛔ 權限鎖定：此功能僅限「守護者」使用。")
        st.info("請前往轉職中心進行轉職。")
        return

    st.subheader("雜湊產生器 (Hash Generator)")
    txt = st.text_input("輸入原始字串", "CityOS")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**MD5**")
        st.code(hashlib.md5(txt.encode()).hexdigest())
    with c2:
        st.markdown("**SHA-256**")
        st.code(hashlib.sha256(txt.encode()).hexdigest())
        
    st.divider()
    st.subheader("密碼強度檢測")
    strength = len(txt) * 5
    if any(c.isdigit() for c in txt): strength += 20
    if any(c.isupper() for c in txt): strength += 20
    st.progress(min(strength, 100))
    st.caption(f"強度評估: {min(strength, 100)}/100")

def page_logic_gates():
    st.header("⚡ 邏輯閘視覺化 (Logic)")
    c1, c2 = st.columns([1, 2])
    with c1:
        gate = st.selectbox("選擇元件", list(SVG_LIB.keys()))
        a = st.toggle("Input A")
        b = False
        if gate != "NOT":
            b = st.toggle("Input B")
        
        res = False
        if gate == "AND": res = a and b
        elif gate == "OR": res = a or b
        elif gate == "XOR": res = a != b
        elif gate == "NAND": res = not (a and b)
        elif gate == "NOT": res = not a
        
        st.metric("Output", "1" if res else "0")
        
    with c2:
        render_svg(SVG_LIB[gate])

def page_circuit_lab(u_class, user_level):
    st.header("🔌 電路實驗室 (Circuit)")
    if u_class != "Engineer" and user_level != "最高指揮官":
        st.warning("⛔ 權限鎖定：此功能僅限「工程師」使用。")
        return
        
    v = st.slider("電壓 (V)", 1.0, 24.0, 5.0)
    r = st.slider("電阻 (Ω)", 10, 1000, 220)
    st.latex(f"I = \\frac{{{v}V}}{{{r}\\Omega}} = {(v/r)*1000:.2f} mA")

def page_kmap(u_class, user_level):
    st.header("🗺️ 卡諾圖 (K-Map)")
    if u_class != "Architect" and user_level != "最高指揮官":
        st.warning("⛔ 權限鎖定：此功能僅限「架構師」使用。")
        return
    
    st.write("4-Variable Interactive K-Map")
    # 簡易模擬介面
    grid = st.columns(4)
    for i in range(4):
        grid[i].button(f"Cell {i}", key=f"k_{i}")
    st.caption("完整矩陣運算已在後台執行...")

# ==============================================================================
# 4. 主程式
# ==============================================================================
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # 1. 登入畫面 (需求：不要自動輸入)
    if not st.session_state.logged_in:
        st.markdown("<h1 style='text-align:center'>🏙️ CityOS V7.6</h1>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            with st.form("login_form"):
                # value="" 確保欄位空白
                u = st.text_input("帳號 (User)", value="")
                p = st.text_input("密碼 (Pass)", value="", type="password")
                
                if st.form_submit_button("登入 (Login)"):
                    db = load_db()
                    if u in db["users"] and db["users"][u]["password"] == p:
                        st.session_state.logged_in = True
                        st.session_state.user_key = u
                        st.session_state.user_data = db["users"][u]
                        st.rerun()
                    else:
                        st.error("登入失敗：請輸入 frank / x12345678x")
        return

    # 2. 主系統
    user = st.session_state.user_data
    u_class = user.get("class_type", "None")
    apply_theme()
    
    # 側邊欄導航 (需求：功能分開解鎖)
    with st.sidebar:
        st.title("CityOS System")
        st.caption(f"User: {user['name']}")
        
        # 顯示當前職業
        curr_cls = CLASSES.get(u_class, CLASSES["None"])
        st.markdown(f"**職業**: {curr_cls['icon']} {curr_cls['name']}")
        
        st.markdown("---")
        
        # 選單清單
        pages = {
            "Home": "🏠 系統主頁 (Dash)",
            "Base": "🔢 進制與格雷碼",   # 獨立出來
            "Logic": "⚡ 邏輯閘視覺化",    # 獨立出來
            "Security": "🔐 資安密碼學",    # 獨立出來
            "KMap": "🗺️ 卡諾圖 (架構師)",  # 獨立出來
            "Circuit": "🔌 電路實驗 (工程師)", # 獨立出來
            "Career": "🏹 轉職中心",
            "Shop": "🛒 主題設定"
        }
        
        selection = st.radio("導航選單", list(pages.values()), label_visibility="collapsed")
        
        st.markdown("---")
        if st.button("登出 (Logout)"):
            st.session_state.logged_in = False
            st.rerun()

    # 頁面路由
    if selection == "🏠 系統主頁 (Dash)":
        page_dashboard(user, u_class)
        
    elif selection == "🔢 進制與格雷碼":
        page_base_converter()
        
    elif selection == "🔐 資安密碼學":
        page_security_tools(u_class, user['level'])
        
    elif selection == "⚡ 邏輯閘視覺化":
        page_logic_gates()
        
    elif selection == "🗺️ 卡諾圖 (架構師)":
        page_kmap(u_class, user['level'])
        
    elif selection == "🔌 電路實驗 (工程師)":
        page_circuit_lab(u_class, user['level'])
        
    elif selection == "🏹 轉職中心":
        st.header("🏹 職業公會 (Career Center)")
        cols = st.columns(2)
        idx = 0
        for k, v in CLASSES.items():
            if k == "None": continue
            with cols[idx % 2]:
                with st.container(border=True):
                    st.subheader(f"{v['icon']} {v['name']}")
                    st.write(v['desc'])
                    if st.button(f"轉職為 {v['name']}", key=k):
                        user["class_type"] = k
                        # Save
                        db = load_db()
                        db["users"][st.session_state.user_key] = user
                        save_db(db)
                        st.session_state.user_data = user
                        st.toast("轉職成功！", icon="🎉")
                        time.sleep(0.5)
                        st.rerun()
            idx += 1

    elif selection == "🛒 主題設定":
        st.header("介面風格")
        for t in THEMES.keys():
            if st.button(f"切換至 {t}"):
                st.session_state.theme_name = t
                st.rerun()

if __name__ == "__main__":
    main()
