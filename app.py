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
# 0. 系統核心設定 (System Core)
# ==============================================================================
st.set_page_config(
    page_title="CityOS V7.3 Final Fixed",
    layout="wide",
    page_icon="🏙️",
    initial_sidebar_state="expanded"
)

# 檔案路徑
USER_DB_FILE = "users.json"
QS_FILE = "questions.txt"

# 職業系統 (定義特權與描述)
CLASSES = {
    "None": {
        "name": "一般市民 (Citizen)", 
        "desc": "無特殊能力，可自由瀏覽基礎設施。", 
        "icon": "👤", "color": "#888888",
        "perks": ["基礎儀表板"]
    },
    "Guardian": {
        "name": "守護者 (Guardian)", 
        "desc": "擁有資安監控權限，可看到系統攻擊日誌。", 
        "icon": "🛡️", "color": "#00FF99",
        "perks": ["儀表板: 資安威脅地圖", "工具箱: 高階雜湊"]
    },
    "Architect": {
        "name": "架構師 (Architect)", 
        "desc": "系統核心設計者，唯一能操作卡諾圖 (K-Map) 的職業。", 
        "icon": "⚡", "color": "#00CCFF",
        "perks": ["解鎖: 卡諾圖化簡器", "儀表板: CPU 核心深層分析"]
    },
    "Oracle": {
        "name": "預言家 (Oracle)", 
        "desc": "數據分析專家，能在儀表板看到未來趨勢預測。", 
        "icon": "🔮", "color": "#D500F9",
        "perks": ["儀表板: 趨勢預測模型", "商店: 預知折扣"]
    },
    "Engineer": {
        "name": "工程師 (Engineer)", 
        "desc": "硬體維修專家，唯一能進入電路實驗室的人。", 
        "icon": "🔧", "color": "#FF9900",
        "perks": ["解鎖: 電路實驗室", "儀表板: 電壓監控"]
    }
}

# 介面主題 (修復顏色數量不足的問題)
THEMES = {
    "Night City": {"bg": "#212529", "txt": "#E9ECEF", "btn": "#495057", "card": "#343A40", "chart": ["#00ADB5", "#FF2E63", "#FFFFFF"]},
    "Day City": {"bg": "#F8F9FA", "txt": "#212529", "btn": "#ADB5BD", "card": "#FFFFFF", "chart": ["#343A40", "#6C757D", "#ADB5BD"]},
    "Cyber Punk": {"bg": "#0B0C10", "txt": "#C5C6C7", "btn": "#FCA311", "card": "#1F2833", "chart": ["#FCA311", "#66FCF1", "#45A29E"]},
    "Matrix": {"bg": "#000000", "txt": "#00FF41", "btn": "#003B00", "card": "#001A00", "chart": ["#008F11", "#003B00", "#00FF41"]},
    "Royal": {"bg": "#2C001E", "txt": "#FFD700", "btn": "#590035", "card": "#420025", "chart": ["#FFD700", "#FF007F", "#9D00FF"]},
}

# SVG 圖示庫 (修復破圖問題)
SVG_LIB = {
    "AND": '''<svg width="200" height="120" xmlns="http://www.w3.org/2000/svg"><path d="M20,20 L80,20 C110,20 130,40 130,60 C130,80 110,100 80,100 L20,100 Z" fill="none" stroke="#888" stroke-width="5"/><path d="M0,40 L20,40 M0,80 L20,80 M130,60 L160,60" stroke="#888" stroke-width="5"/></svg>''',
    "OR": '''<svg width="200" height="120" xmlns="http://www.w3.org/2000/svg"><path d="M20,20 L70,20 Q100,60 70,100 L20,100 Q50,60 20,20 Z" fill="none" stroke="#888" stroke-width="5"/><path d="M0,40 L30,40 M0,80 L30,80 M90,60 L120,60" stroke="#888" stroke-width="5"/></svg>''',
    "NOT": '''<svg width="200" height="120" xmlns="http://www.w3.org/2000/svg"><path d="M40,20 L40,100 L120,60 Z" fill="none" stroke="#888" stroke-width="5"/><circle cx="130" cy="60" r="8" fill="none" stroke="#888" stroke-width="4"/><path d="M0,60 L40,60 M138,60 L160,60" stroke="#888" stroke-width="5"/></svg>''',
    "XOR": '''<svg width="200" height="120" xmlns="http://www.w3.org/2000/svg"><path d="M40,20 L90,20 Q120,60 90,100 L40,100 Q70,60 40,20 Z" fill="none" stroke="#888" stroke-width="5"/><path d="M20,20 Q50,60 20,100" fill="none" stroke="#888" stroke-width="5"/><path d="M0,40 L30,40 M0,80 L30,80 M110,60 L140,60" stroke="#888" stroke-width="5"/></svg>'''
}

# ==============================================================================
# 1. 工具函式
# ==============================================================================
def init_files():
    """強制修復 frank 並初始化檔案"""
    frank_data = {
        "password": "x12345678x", 
        "name": "Frank (Commander)", 
        "level": "最高指揮官", 
        "exp": 99999, "rpg_level": 99, "coins": 999999, 
        "class_type": "Architect", 
        "inventory": list(THEMES.keys()), 
        "last_login": ""
    }

    # 讀取或創建 DB
    if os.path.exists(USER_DB_FILE):
        try:
            with open(USER_DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            data = {"users": {}}
    else:
        data = {"users": {}}

    # 強制覆蓋 frank (確保能登入)
    data["users"]["frank"] = frank_data
    
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
            
    # 題庫
    if not os.path.exists(QS_FILE):
        with open(QS_FILE, "w", encoding="utf-8") as f:
            f.write("1|Easy|1+1 in Binary?|10,11,100|10")

def load_db():
    init_files()
    with open(USER_DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(data):
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def apply_theme():
    theme_key = st.session_state.get("theme_name", "Night City")
    t = THEMES.get(theme_key, THEMES["Night City"])
    st.markdown(f"""
    <style>
        .stApp {{ background-color: {t['bg']}; color: {t['txt']}; }}
        h1, h2, h3, h4, h5, p, li, label, .stMarkdown {{ color: {t['txt']} !important; }}
        .stButton>button {{ background-color: {t['btn']} !important; color: white; border-radius: 5px; }}
        .stat-card {{ background: {t['card']}; padding: 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); }}
    </style>
    """, unsafe_allow_html=True)

def render_svg(svg_string):
    """修復版的 SVG 渲染"""
    theme_key = st.session_state.get("theme_name", "Night City")
    color = "#333" if "Day" in theme_key else "#EEE"
    # 替換顏色
    svg_colored = svg_string.replace("#888", color)
    # 轉 base64
    b64 = base64.b64encode(svg_colored.encode('utf-8')).decode("utf-8")
    # 使用 img 標籤渲染，這是最穩定的方法
    st.markdown(
        f'<div style="display:flex; justify-content:center;"><img src="data:image/svg+xml;base64,{b64}" width="300"></div>',
        unsafe_allow_html=True
    )

# ==============================================================================
# 2. 主要功能頁面
# ==============================================================================

def main_app():
    user = st.session_state.user_data
    u_class = user.get("class_type", "None")
    apply_theme()
    
    # --- Sidebar ---
    with st.sidebar:
        st.title("🏙️ CityOS V7.3")
        
        # 顯示職業卡片
        cls_info = CLASSES[u_class]
        st.markdown(f"""
        <div style="background-color:{cls_info['color']}; padding:5px; border-radius:5px 5px 0 0;"></div>
        <div class="stat-card" style="border-top:0; border-radius:0 0 5px 5px;">
            <h3>{cls_info['icon']} {user['name']}</h3>
            <p><b>職業:</b> {cls_info['name']}</p>
            <p><b>等級:</b> Lv.{user.get('rpg_level', 99)}</p>
            <p><b>金幣:</b> 💰 {user.get('coins', 0)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        menu = {
            "Dash": "📊 城市儀表板",
            "Career": "🏹 轉職者中心 (New)",
            "Logic": "⚡ 邏輯閘",
            "Circuit": "🔌 電路實驗室",
            "KMap": "🗺️ 卡諾圖",
            "Shop": "🛒 補給站"
        }
        
        page = st.radio("導航", list(menu.values()), label_visibility="collapsed")
        
        if st.button("🚪 登出 (Logout)"):
            st.session_state.logged_in = False
            st.rerun()

    # --- Content ---
    
    # 1. Dashboard (根據職業顯示不同內容)
    if page == "📊 城市儀表板":
        st.header(f"監控中心 - {user['name']}")
        
        # 通用圖表 (CPU)
        st.subheader("核心負載 (通用)")
        # 修正: 確保顏色數量足夠
        chart_color = THEMES[st.session_state.get("theme_name", "Night City")]["chart"]
        df = pd.DataFrame(np.random.randn(20, 3), columns=['Core A', 'Core B', 'Core C'])
        st.area_chart(df, color=chart_color)
        
        # 職業專屬區塊
        st.divider()
        if u_class == "Guardian":
            st.success("🛡️ [守護者權限] 資安威脅雷達已啟動")
            st.metric("入侵攔截", "1,240 次", "+5%")
        elif u_class == "Oracle":
            st.info("🔮 [預言家權限] 下一小時流量預測")
            st.line_chart(np.random.randn(10, 1) + 50)
        elif u_class == "Engineer":
            st.warning("🔧 [工程師權限] 硬體電壓監控")
            st.bar_chart({"V1": 5.0, "V2": 3.3, "V3": 12.0})
        elif u_class == "Architect":
            st.info("⚡ [架構師權限] 系統邏輯拓樸圖")
            st.caption("System Logic Map: Optimized")
        else:
            st.caption("市民權限僅能查看基礎負載。轉職以解鎖更多資訊。")

    # 2. Career Center (轉職中心)
    elif page == "🏹 轉職者中心 (New)":
        st.header("🏹 職業公會")
        st.write("選擇你的專精領域，解鎖系統特殊功能。")
        
        cols = st.columns(2)
        for idx, (key, info) in enumerate(CLASSES.items()):
            if key == "None": continue
            with cols[idx % 2]:
                with st.container(border=True):
                    st.subheader(f"{info['icon']} {info['name']}")
                    st.write(info['desc'])
                    st.markdown("**特權功能:**")
                    for p in info['perks']:
                        st.code(p)
                    
                    if u_class == key:
                        st.button("✅ 當前職業", key=f"btn_{key}", disabled=True)
                    else:
                        if st.button(f"轉職為 {key}", key=f"btn_{key}"):
                            user["class_type"] = key
                            # 存檔
                            db = load_db()
                            db["users"][st.session_state.user_key] = user
                            save_db(db)
                            st.session_state.user_data = user
                            st.toast(f"轉職成功！歡迎成為 {info['name']}", icon="🎉")
                            time.sleep(1)
                            st.rerun()

    # 3. Logic Gates
    elif page == "⚡ 邏輯閘":
        st.header("⚡ 邏輯閘視覺化")
        gate = st.selectbox("選擇元件", list(SVG_LIB.keys()))
        render_svg(SVG_LIB[gate]) # 呼叫修復後的渲染函式
        
        # 簡單互動
        st.subheader("真值表模擬")
        c1, c2 = st.columns(2)
        a = c1.toggle("Input A")
        b = c2.toggle("Input B")
        res = False
        if gate == "AND": res = a and b
        elif gate == "OR": res = a or b
        elif gate == "XOR": res = a != b
        elif gate == "NOT": res = not a
        
        st.metric("Output", "1 (High)" if res else "0 (Low)")

    # 4. Circuit Lab (工程師限定)
    elif page == "🔌 電路實驗室":
        if u_class not in ["Engineer", "Architect"] and user['level'] != "最高指揮官":
            st.error("⛔ 存取被拒：此區域僅限「工程師」或「架構師」進入。")
            st.info("請前往「轉職者中心」進行轉職。")
        else:
            st.header("🔌 歐姆定律實驗室")
            v = st.slider("電壓 (V)", 0, 24, 5)
            r = st.slider("電阻 (Ω)", 1, 1000, 220)
            i = v / r * 1000
            st.success(f"電流 I = {i:.2f} mA")

    # 5. K-Map (架構師限定)
    elif page == "🗺️ 卡諾圖":
        if u_class not in ["Architect"] and user['level'] != "最高指揮官":
            st.error("⛔ 存取被拒：此高階邏輯工具僅限「架構師」使用。")
            st.info("請前往「轉職者中心」進行轉職。")
        else:
            st.header("🗺️ 4-Variable K-Map")
            st.write("這是架構師專用的邏輯化簡介面。")
            # 簡單示意圖
            st.dataframe(pd.DataFrame(np.random.randint(0,2,size=(4,4)), 
                         columns=["00","01","11","10"], 
                         index=["00","01","11","10"]))

    # 6. Shop
    elif page == "🛒 補給站":
        st.header("主題商店")
        current = st.session_state.get("theme_name", "Night City")
        for t_name in THEMES.keys():
            if st.button(f"套用 {t_name}", disabled=(t_name == current)):
                st.session_state.theme_name = t_name
                st.rerun()

# ==============================================================================
# 3. 登入頁面
# ==============================================================================
def login_page():
    st.markdown("<h1 style='text-align: center;'>🏙️ CityOS V7.3 Fixed</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        with st.form("login"):
            u = st.text_input("帳號 (預設: frank)")
            p = st.text_input("密碼 (預設: x12345678x)", type="password")
            if st.form_submit_button("🚀 登入"):
                db = load_db() # 這裡會自動修復 frank
                if u in db["users"] and db["users"][u]["password"] == p:
                    st.session_state.logged_in = True
                    st.session_state.user_key = u
                    st.session_state.user_data = db["users"][u]
                    st.rerun()
                else:
                    st.error("帳號或密碼錯誤 (Frank 已被自動修復，請重試)")

# ==============================================================================
# Main
# ==============================================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    main_app()
else:
    login_page()
