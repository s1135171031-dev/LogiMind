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
# 1. 系統核心設定 & 常數定義
# ==============================================================================
st.set_page_config(
    page_title="CityOS V7.4 Final",
    layout="wide",
    page_icon="🏙️",
    initial_sidebar_state="expanded"
)

# 檔案路徑
USER_DB_FILE = "users.json"
QS_FILE = "questions.txt"

# 職業系統定義 (含圖示、顏色、特權描述)
CLASSES = {
    "None": {
        "name": "一般市民 (Citizen)", 
        "desc": "無特殊能力，僅能瀏覽基礎設施。", 
        "icon": "👤", "color": "#888888",
        "perks": ["基礎儀表板"]
    },
    "Guardian": {
        "name": "守護者 (Guardian)", 
        "desc": "資安專精，可監控系統威脅與加密雜湊。", 
        "icon": "🛡️", "color": "#00FF99",
        "perks": ["儀表板: 資安威脅地圖", "工具箱: 進階雜湊工具"]
    },
    "Architect": {
        "name": "架構師 (Architect)", 
        "desc": "邏輯運算核心，唯一能操作 K-Map 的職業。", 
        "icon": "⚡", "color": "#00CCFF",
        "perks": ["解鎖: 卡諾圖 (K-Map)", "儀表板: CPU 深度分析"]
    },
    "Oracle": {
        "name": "預言家 (Oracle)", 
        "desc": "數據預測專家，能看到未來的數據走向。", 
        "icon": "🔮", "color": "#D500F9",
        "perks": ["儀表板: 股市/流量預測", "商店: 預知折扣"]
    },
    "Engineer": {
        "name": "工程師 (Engineer)", 
        "desc": "硬體維護專家，擁有進入電路實驗室的權限。", 
        "icon": "🔧", "color": "#FF9900",
        "perks": ["解鎖: 電路實驗室", "儀表板: 電壓監控"]
    }
}

# 介面主題 (修復: 確保 chart 陣列至少有 3 個顏色，避免崩潰)
THEMES = {
    "Night City": {"bg": "#212529", "txt": "#E9ECEF", "btn": "#495057", "card": "#343A40", "chart": ["#00ADB5", "#FF2E63", "#F8F9FA"]},
    "Day City": {"bg": "#F8F9FA", "txt": "#212529", "btn": "#ADB5BD", "card": "#FFFFFF", "chart": ["#343A40", "#6C757D", "#212529"]},
    "Cyber Punk": {"bg": "#0B0C10", "txt": "#C5C6C7", "btn": "#FCA311", "card": "#1F2833", "chart": ["#FCA311", "#66FCF1", "#45A29E"]},
    "Matrix": {"bg": "#000000", "txt": "#00FF41", "btn": "#003B00", "card": "#001A00", "chart": ["#008F11", "#003B00", "#00FF41"]},
    "Royal": {"bg": "#2C001E", "txt": "#FFD700", "btn": "#590035", "card": "#420025", "chart": ["#FFD700", "#FF007F", "#9D00FF"]},
}

# SVG 圖示庫 (標準化尺寸與 stroke，確保不破圖)
SVG_LIB = {
    "AND": '''<svg width="200" height="100" xmlns="http://www.w3.org/2000/svg"><path d="M20,10 L80,10 C110,10 130,30 130,50 C130,70 110,90 80,90 L20,90 Z" fill="none" stroke="#888" stroke-width="4"/><path d="M0,30 L20,30 M0,70 L20,70 M130,50 L160,50" stroke="#888" stroke-width="4"/></svg>''',
    "OR": '''<svg width="200" height="100" xmlns="http://www.w3.org/2000/svg"><path d="M20,10 L70,10 Q100,50 70,90 L20,90 Q50,50 20,10 Z" fill="none" stroke="#888" stroke-width="4"/><path d="M0,30 L30,30 M0,70 L30,70 M90,50 L120,50" stroke="#888" stroke-width="4"/></svg>''',
    "NOT": '''<svg width="200" height="100" xmlns="http://www.w3.org/2000/svg"><path d="M40,10 L40,90 L110,50 Z" fill="none" stroke="#888" stroke-width="4"/><circle cx="118" cy="50" r="6" fill="none" stroke="#888" stroke-width="3"/><path d="M0,50 L40,50 M126,50 L160,50" stroke="#888" stroke-width="4"/></svg>''',
    "XOR": '''<svg width="200" height="100" xmlns="http://www.w3.org/2000/svg"><path d="M40,10 L90,10 Q120,50 90,90 L40,90 Q70,50 40,10 Z" fill="none" stroke="#888" stroke-width="4"/><path d="M20,10 Q50,50 20,90" fill="none" stroke="#888" stroke-width="4"/><path d="M0,30 L30,30 M0,70 L30,70 M110,50 L140,50" stroke="#888" stroke-width="4"/></svg>'''
}

# ==============================================================================
# 2. 輔助函式 (Backend Utils)
# ==============================================================================
def init_files():
    """初始化系統檔案，並確保 frank 存在且資料正確"""
    frank_data = {
        "password": "x12345678x", 
        "name": "Frank (Supreme)", 
        "level": "最高指揮官", 
        "exp": 999999, "rpg_level": 100, "coins": 999999, 
        "class_type": "Architect", 
        "inventory": list(THEMES.keys()), 
        "last_login": ""
    }

    # 讀取現有資料
    if os.path.exists(USER_DB_FILE):
        try:
            with open(USER_DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            data = {"users": {}}
    else:
        data = {"users": {}}

    # 強制修復 Frank
    data["users"]["frank"] = frank_data
    
    # 寫入檔案
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
            
    # 確保題庫存在
    if not os.path.exists(QS_FILE):
        with open(QS_FILE, "w", encoding="utf-8") as f:
            f.write("1|Easy|Binary 1+1?|10,11,100|10")

def load_db():
    init_files() # 每次讀取前都確保檔案結構正確
    with open(USER_DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(data):
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def apply_theme():
    """注入 CSS 樣式"""
    theme_key = st.session_state.get("theme_name", "Night City")
    t = THEMES.get(theme_key, THEMES["Night City"])
    st.markdown(f"""
    <style>
        .stApp {{ background-color: {t['bg']}; color: {t['txt']}; }}
        h1, h2, h3, h4, h5, p, li, label, .stMarkdown, .stText {{ color: {t['txt']} !important; }}
        .stButton>button {{ background-color: {t['btn']}; color: white; border-radius: 8px; border: none; transition: 0.2s; }}
        .stButton>button:hover {{ filter: brightness(1.2); }}
        .stat-card {{ background: {t['card']}; padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 15px; }}
        div[data-testid="stExpander"] {{ background-color: {t['card']}; border: 1px solid rgba(255,255,255,0.1); }}
    </style>
    """, unsafe_allow_html=True)

def render_svg(svg_string):
    """將 SVG 轉為 Base64 圖片，徹底解決破圖問題"""
    theme_key = st.session_state.get("theme_name", "Night City")
    # 根據主題調整線條顏色
    stroke_color = "#333" if "Day" in theme_key else "#EEE"
    svg_colored = svg_string.replace("#888", stroke_color)
    
    b64 = base64.b64encode(svg_colored.encode('utf-8')).decode("utf-8")
    html = f'<div style="display:flex; justify-content:center; margin: 20px;"><img src="data:image/svg+xml;base64,{b64}" width="250"></div>'
    st.markdown(html, unsafe_allow_html=True)

# ==============================================================================
# 3. 核心功能頁面 (App Logic)
# ==============================================================================

def main_app():
    user = st.session_state.user_data
    u_class = user.get("class_type", "None")
    apply_theme()
    
    # --- Sidebar (側邊欄) ---
    with st.sidebar:
        st.title("🏙️ CityOS V7.4")
        st.caption("Ultimate Fixed Edition")
        
        # 使用者資訊卡
        cls_info = CLASSES.get(u_class, CLASSES["None"])
        st.markdown(f"""
        <div class="stat-card" style="border-left: 5px solid {cls_info['color']};">
            <h3>{cls_info['icon']} {user['name']}</h3>
            <p style="margin:0;"><b>職業:</b> {cls_info['name']}</p>
            <p style="margin:0;"><b>等級:</b> Lv.{user.get('rpg_level', 1)}</p>
            <hr style="opacity:0.2; margin:10px 0;">
            <div style="display:flex; justify-content:space-between;">
                <span>💰 {user.get('coins', 0):,}</span>
                <span>⭐ {user.get('level', '市民')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 選單
        menu_options = {
            "Dash": "📊 城市儀表板",
            "Career": "🏹 轉職者中心",
            "Logic": "⚡ 邏輯閘",
            "Circuit": "🔌 電路實驗室", 
            "KMap": "🗺️ 卡諾圖",
            "Shop": "🛒 補給站"
        }
        if user['level'] == "最高指揮官":
            menu_options["Admin"] = "☢️ 核心控制台"
            
        page = st.radio("導航", list(menu_options.values()), label_visibility="collapsed")
        
        st.divider()
        if st.button("🚪 登出系統"):
            st.session_state.logged_in = False
            st.rerun()

    # --- Main Content (主畫面) ---
    
    # 1. Dashboard (儀表板 - 依職業變化)
    if page == "📊 城市儀表板":
        st.header(f"監控中心 - {user['name']}")
        
        # 顯示歡迎與簽到
        today = str(date.today())
        if user.get("last_login") != today:
            if st.button("🎁 每日簽到 (+100 Coins)"):
                user["last_login"] = today
                user["coins"] += 100
                # Update DB
                db = load_db()
                db["users"][st.session_state.user_key] = user
                save_db(db)
                st.balloons()
                st.rerun()

        # 通用數據
        c1, c2, c3 = st.columns(3)
        c1.metric("CPU 負載", f"{random.randint(20,60)}%", "-2%")
        c2.metric("記憶體", f"{random.randint(4,12)} GB", "正常")
        c3.metric("網路延遲", f"{random.randint(10,50)} ms", "優良")
        
        st.divider()
        
        # 職業專屬區塊
        if u_class == "Guardian":
            st.subheader("🛡️ 資安監控 (守護者限定)")
            st.error("偵測到外部掃描嘗試: 12 次 (已攔截)")
            map_data = pd.DataFrame(np.random.randn(100, 2) / [50, 50] + [25.03, 121.56], columns=['lat', 'lon'])
            st.map(map_data)
            
        elif u_class == "Oracle":
            st.subheader("🔮 趨勢預測 (預言家限定)")
            chart_data = pd.DataFrame({
                "歷史數據": np.random.randn(20).cumsum(),
                "AI 預測": np.random.randn(20).cumsum() + 5
            })
            st.line_chart(chart_data, color=["#FF0000", "#00FF00"])
            
        elif u_class == "Engineer":
            st.subheader("🔧 硬體電壓監控 (工程師限定)")
            st.bar_chart({"Core V": 1.2, "DRAM V": 1.35, "IO V": 3.3})
            
        elif u_class == "Architect":
            st.subheader("⚡ 核心邏輯拓樸 (架構師限定)")
            st.info("系統核心架構完整，邏輯閘延遲 < 1ns")
            
        else: # None
            st.subheader("📊 基礎流量")
            # 這裡使用 3 色陣列，防止 StreamlitColorLengthError
            chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["A區", "B區", "C區"])
            colors = THEMES[st.session_state.get("theme_name", "Night City")]["chart"]
            st.area_chart(chart_data, color=colors)
            st.caption("💡 提示：前往「轉職者中心」轉職，可解鎖更多專業數據。")

    # 2. Career Center (轉職中心)
    elif page == "🏹 轉職者中心":
        st.header("🏹 職業公會")
        st.write("選擇您的專精領域。每次轉職需消耗 0 金幣 (開發者模式)。")
        
        cols = st.columns(2)
        idx = 0
        for key, info in CLASSES.items():
            if key == "None": continue
            with cols[idx % 2]:
                with st.container(border=True):
                    st.markdown(f"### {info['icon']} {info['name']}")
                    st.write(info['desc'])
                    st.markdown("**特權功能:**")
                    for perk in info['perks']:
                        st.code(perk)
                    
                    if u_class == key:
                        st.button("✅ 當前職業", key=f"btn_{key}", disabled=True, use_container_width=True)
                    else:
                        if st.button(f"轉職為 {key}", key=f"btn_{key}", use_container_width=True):
                            user["class_type"] = key
                            # Save
                            db = load_db()
                            db["users"][st.session_state.user_key] = user
                            save_db(db)
                            st.session_state.user_data = user
                            st.toast(f"恭喜轉職為 {info['name']}！", icon="🎉")
                            time.sleep(0.5)
                            st.rerun()
            idx += 1

    # 3. Logic Gates
    elif page == "⚡ 邏輯閘":
        st.header("⚡ 邏輯閘實驗")
        c1, c2 = st.columns([1, 2])
        with c1:
            gate = st.selectbox("選擇元件", list(SVG_LIB.keys()))
            st.write("真值表模擬:")
            in_a = st.toggle("Input A (0/1)")
            in_b = st.toggle("Input B (0/1)")
            
            res = False
            if gate == "AND": res = in_a and in_b
            elif gate == "OR": res = in_a or in_b
            elif gate == "XOR": res = in_a != in_b
            elif gate == "NOT": res = not in_a
            
            st.metric("Output", "1 (High)" if res else "0 (Low)")
            
        with c2:
            st.markdown("##### 電路符號")
            render_svg(SVG_LIB[gate]) # 使用修復後的渲染

    # 4. Circuit (Role Locked)
    elif page == "🔌 電路實驗室":
        # 權限檢查
        if u_class not in ["Engineer", "Architect"] and user['level'] != "最高指揮官":
            st.warning("⛔ 權限不足：此區域僅限「工程師」進入。")
            st.info("請前往「轉職者中心」進行轉職。")
        else:
            st.header("🔌 歐姆定律計算器")
            c1, c2 = st.columns(2)
            with c1:
                v = st.number_input("電壓 (V)", 1.0, 100.0, 5.0)
                r = st.number_input("電阻 (Ω)", 1.0, 10000.0, 220.0)
            with c2:
                i = (v / r) * 1000
                p = (v ** 2) / r
                st.metric("電流 (Current)", f"{i:.2f} mA")
                st.metric("功率 (Power)", f"{p:.2f} W")

    # 5. K-Map (Role Locked)
    elif page == "🗺️ 卡諾圖":
        # 權限檢查
        if u_class not in ["Architect"] and user['level'] != "最高指揮官":
            st.warning("⛔ 權限不足：此區域僅限「架構師」進入。")
            st.info("請前往「轉職者中心」進行轉職。")
        else:
            st.header("🗺️ 卡諾圖化簡器 (4-Var)")
            st.caption("點擊按鈕切換 0/1")
            
            if "kmap" not in st.session_state:
                st.session_state.kmap = [0]*16
            
            # 格雷碼排列
            gray_indices = [
                [0, 1, 3, 2],
                [4, 5, 7, 6],
                [12, 13, 15, 14],
                [8, 9, 11, 10]
            ]
            
            cols = st.columns(5)
            cols[0].write("**AB \ CD**")
            cols[1].write("00"); cols[2].write("01"); cols[3].write("11"); cols[4].write("10")
            
            row_lbl = ["00", "01", "11", "10"]
            for r in range(4):
                cols = st.columns(5)
                cols[0].write(f"**{row_lbl[r]}**")
                for c in range(4):
                    idx = gray_indices[r][c]
                    val = st.session_state.kmap[idx]
                    if cols[c+1].button(f"{val}", key=f"k_{idx}", type="primary" if val else "secondary"):
                        st.session_state.kmap[idx] = 1 - val
                        st.rerun()
            
            st.markdown("---")
            minterms = [i for i, v in enumerate(st.session_state.kmap) if v == 1]
            st.write(f"Minterms: {minterms}")
            if len(minterms) == 0: st.code("F = 0")
            elif len(minterms) == 16: st.code("F = 1")
            else: st.code("F = (化簡邏輯已啟動...)")

    # 6. Shop
    elif page == "🛒 補給站":
        st.header("🛒 介面風格商店")
        current_theme = st.session_state.get("theme_name", "Night City")
        
        cols = st.columns(3)
        for idx, t_name in enumerate(THEMES.keys()):
            with cols[idx % 3]:
                st.markdown(f"**{t_name}**")
                if t_name == current_theme:
                    st.button("使用中", key=t_name, disabled=True)
                else:
                    if st.button(f"套用", key=t_name):
                        st.session_state.theme_name = t_name
                        st.rerun()

    # 7. Admin
    elif page == "☢️ 核心控制台":
        st.title("Admin Console")
        db = load_db()
        st.json(db)

# ==============================================================================
# 4. 登入入口 (Entry Point)
# ==============================================================================
def login_page():
    st.markdown("<h1 style='text-align: center;'>🏙️ CityOS V7.4</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>修復版：Frank 帳號已自動鎖定，請直接登入。</p>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        with st.form("login_form"):
            user_input = st.text_input("帳號", value="frank")
            pass_input = st.text_input("密碼", value="x12345678x", type="password")
            
            submitted = st.form_submit_button("🚀 進入系統", use_container_width=True)
            
            if submitted:
                db = load_db()
                if user_input in db["users"] and db["users"][user_input]["password"] == pass_input:
                    st.session_state.logged_in = True
                    st.session_state.user_key = user_input
                    st.session_state.user_data = db["users"][user_input]
                    st.toast("登入成功！", icon="✅")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("帳號或密碼錯誤 (請確認 users.json 是否被外部程式鎖定)")

# ==============================================================================
# Main Execution
# ==============================================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 每次執行都初始化，確保 Frank 活著
init_files()

if st.session_state.logged_in:
    main_app()
else:
    login_page()
