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
# 0. 系統核心配置
# ==============================================================================
st.set_page_config(
    page_title="CityOS V7.5 Ultimate",
    layout="wide",
    page_icon="🏙️",
    initial_sidebar_state="expanded"
)

# 檔案設定
USER_DB_FILE = "users.json"

# 職業設定 (保留 RPG 元素)
CLASSES = {
    "None": {"name": "市民", "icon": "👤", "color": "#888888", "desc": "基礎權限"},
    "Guardian": {"name": "守護者", "icon": "🛡️", "color": "#00FF99", "desc": "資安與加密專精"},
    "Architect": {"name": "架構師", "icon": "⚡", "color": "#00CCFF", "desc": "邏輯與核心運算"},
    "Oracle": {"name": "預言家", "icon": "🔮", "color": "#D500F9", "desc": "大數據與預測"},
    "Engineer": {"name": "工程師", "icon": "🔧", "color": "#FF9900", "desc": "硬體與電路修復"}
}

# 主題配色 (確保 chart 至少有 3 色以免報錯)
THEMES = {
    "Night City": {"bg": "#212529", "txt": "#E9ECEF", "btn": "#495057", "card": "#343A40", "chart": ["#00ADB5", "#FF2E63", "#F8F9FA"]},
    "Day City": {"bg": "#F8F9FA", "txt": "#212529", "btn": "#ADB5BD", "card": "#FFFFFF", "chart": ["#343A40", "#6C757D", "#212529"]},
    "Cyber Punk": {"bg": "#0B0C10", "txt": "#C5C6C7", "btn": "#FCA311", "card": "#1F2833", "chart": ["#FCA311", "#66FCF1", "#45A29E"]},
    "Matrix": {"bg": "#000000", "txt": "#00FF41", "btn": "#003B00", "card": "#001A00", "chart": ["#008F11", "#003B00", "#00FF41"]},
}

# 邏輯閘 SVG (Base64 用)
SVG_LIB = {
    "AND": '''<svg width="200" height="100" xmlns="http://www.w3.org/2000/svg"><path d="M20,10 L80,10 C110,10 130,30 130,50 C130,70 110,90 80,90 L20,90 Z" fill="none" stroke="#888" stroke-width="4"/><path d="M0,30 L20,30 M0,70 L20,70 M130,50 L160,50" stroke="#888" stroke-width="4"/></svg>''',
    "OR": '''<svg width="200" height="100" xmlns="http://www.w3.org/2000/svg"><path d="M20,10 L70,10 Q100,50 70,90 L20,90 Q50,50 20,10 Z" fill="none" stroke="#888" stroke-width="4"/><path d="M0,30 L30,30 M0,70 L30,70 M90,50 L120,50" stroke="#888" stroke-width="4"/></svg>''',
    "NOT": '''<svg width="200" height="100" xmlns="http://www.w3.org/2000/svg"><path d="M40,10 L40,90 L110,50 Z" fill="none" stroke="#888" stroke-width="4"/><circle cx="118" cy="50" r="6" fill="none" stroke="#888" stroke-width="3"/><path d="M0,50 L40,50 M126,50 L160,50" stroke="#888" stroke-width="4"/></svg>''',
    "XOR": '''<svg width="200" height="100" xmlns="http://www.w3.org/2000/svg"><path d="M40,10 L90,10 Q120,50 90,90 L40,90 Q70,50 40,10 Z" fill="none" stroke="#888" stroke-width="4"/><path d="M20,10 Q50,50 20,90" fill="none" stroke="#888" stroke-width="4"/><path d="M0,30 L30,30 M0,70 L30,70 M110,50 L140,50" stroke="#888" stroke-width="4"/></svg>''',
    "NAND": '''<svg width="200" height="100" xmlns="http://www.w3.org/2000/svg"><path d="M20,10 L80,10 C110,10 130,30 130,50 C130,70 110,90 80,90 L20,90 Z" fill="none" stroke="#888" stroke-width="4"/><circle cx="138" cy="50" r="6" fill="none" stroke="#888" stroke-width="3"/><path d="M0,30 L20,30 M0,70 L20,70 M146,50 L160,50" stroke="#888" stroke-width="4"/></svg>'''
}

# ==============================================================================
# 1. 工具與初始化
# ==============================================================================
def init_files():
    """強制 Frank 存活"""
    frank_data = {
        "password": "x12345678x", "name": "Frank (Supreme)", 
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
        .stButton>button {{ background-color: {t['btn']}; color: #FFF; border-radius: 6px; border:none; }}
        .stat-card {{ background: {t['card']}; padding: 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 10px; }}
    </style>
    """, unsafe_allow_html=True)

def render_svg(svg_str):
    """渲染 SVG 圖示"""
    t_name = st.session_state.get("theme_name", "Night City")
    color = "#333" if "Day" in t_name else "#EEE"
    svg = svg_str.replace("#888", color)
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    st.markdown(f'<div style="text-align:center; margin:10px;"><img src="data:image/svg+xml;base64,{b64}" width="250"></div>', unsafe_allow_html=True)

# ==============================================================================
# 2. 功能頁面模組
# ==============================================================================

# --- 邏輯閘頁面 ---
def page_logic_gates():
    st.header("⚡ 邏輯閘視覺化 (Logic Visualizer)")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        gate_type = st.selectbox("選擇邏輯閘", list(SVG_LIB.keys()))
        st.caption("調整輸入訊號以觀察輸出")
        
        # 輸入控制
        in_a = st.toggle("Input A", value=False)
        in_b = False
        if gate_type != "NOT":
            in_b = st.toggle("Input B", value=False)
            
        # 計算結果
        out = False
        if gate_type == "AND": out = in_a and in_b
        elif gate_type == "OR": out = in_a or in_b
        elif gate_type == "NOT": out = not in_a
        elif gate_type == "XOR": out = in_a != in_b
        elif gate_type == "NAND": out = not (in_a and in_b)
        
        # 顯示狀態
        st.divider()
        st.metric("Output (Y)", "1 (High)" if out else "0 (Low)")
        
    with col2:
        st.subheader("電路符號 & 真值表")
        render_svg(SVG_LIB[gate_type])
        
        # 動態生成真值表顯示
        if gate_type == "NOT":
            df = pd.DataFrame({"A": [0, 1], "Y": [1, 0]})
        else:
            data = []
            for a in [0, 1]:
                for b in [0, 1]:
                    res = 0
                    if gate_type=="AND": res=a&b
                    elif gate_type=="OR": res=a|b
                    elif gate_type=="XOR": res=a^b
                    elif gate_type=="NAND": res=1-(a&b)
                    data.append({"A": a, "B": b, "Y": res})
            df = pd.DataFrame(data)
            
        # Highlighting current state
        st.dataframe(df.style.apply(lambda x: ['background: #00ADB5' if (gate_type=="NOT" and x['A']==int(in_a)) or (gate_type!="NOT" and x['A']==int(in_a) and x['B']==int(in_b)) else '' for i in x], axis=1), use_container_width=True)

# --- 卡諾圖頁面 ---
def page_kmap():
    st.header("🗺️ 卡諾圖 (K-Map Solver)")
    st.write("點擊網格切換 0/1，系統將自動計算 Minterms。")
    
    if "kmap_grid" not in st.session_state:
        st.session_state.kmap_grid = [0] * 16

    # 格雷碼索引對應 (4x4)
    # AB \ CD | 00 | 01 | 11 | 10
    # ---------------------------
    # 00      |  0 |  1 |  3 |  2
    # 01      |  4 |  5 |  7 |  6
    # 11      | 12 | 13 | 15 | 14
    # 10      |  8 |  9 | 11 | 10
    
    indices = [
        [0, 1, 3, 2],
        [4, 5, 7, 6],
        [12, 13, 15, 14],
        [8, 9, 11, 10]
    ]
    
    col_labels = ["00", "01", "11", "10"]
    row_labels = ["00", "01", "11", "10"]
    
    # Header Row
    cols = st.columns(5)
    cols[0].markdown("**AB \\ CD**")
    for i in range(4): cols[i+1].markdown(f"**{col_labels[i]}**")
    
    # Grid Rows
    for r in range(4):
        cols = st.columns(5)
        cols[0].markdown(f"**{row_labels[r]}**")
        for c in range(4):
            idx = indices[r][c]
            val = st.session_state.kmap_grid[idx]
            # Button Logic
            btn_lbl = "1" if val else "0"
            if cols[c+1].button(btn_lbl, key=f"km_{idx}", type="primary" if val else "secondary"):
                st.session_state.kmap_grid[idx] = 1 - val
                st.rerun()

    # Result Analysis
    st.divider()
    minterms = [i for i, v in enumerate(st.session_state.kmap_grid) if v == 1]
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Minterms (Σm)")
        if not minterms: st.info("無 (Output = 0)")
        else: st.code(f"Σm({', '.join(map(str, minterms))})")
    
    with c2:
        st.markdown("#### 邏輯表達式 (簡易)")
        if len(minterms) == 16: st.success("F = 1 (Always High)")
        elif len(minterms) == 0: st.warning("F = 0 (Always Low)")
        else: st.caption("完整布林代數化簡需升級至 V8.0 核心。")

# --- 數位工具箱 (進制/資安) ---
def page_tools():
    st.header("🧰 數位工具箱 (Digital Toolkit)")
    
    tab1, tab2 = st.tabs(["🔢 進制轉換", "🔐 資安雜湊"])
    
    with tab1:
        st.subheader("數值系統轉換器")
        col1, col2 = st.columns(2)
        with col1:
            dec_input = st.number_input("輸入十進位整數 (Decimal)", value=255, min_value=0)
            st.caption("支援 Dec -> Bin/Oct/Hex/Gray")
        with col2:
            b_val = bin(dec_input)[2:]
            o_val = oct(dec_input)[2:]
            h_val = hex(dec_input)[2:].upper()
            g_val = dec_input ^ (dec_input >> 1) # Gray Code Formula
            
            st.text_input("二進位 (Binary)", value=b_val, disabled=True)
            st.text_input("八進位 (Octal)", value=o_val, disabled=True)
            st.text_input("十六進位 (Hex)", value=h_val, disabled=True)
            st.text_input("格雷碼 (Gray Code)", value=bin(g_val)[2:], disabled=True)
            
    with tab2:
        st.subheader("密碼學雜湊計算 (Hash Gen)")
        txt = st.text_input("輸入字串", "CityOS_Admin")
        if txt:
            md5 = hashlib.md5(txt.encode()).hexdigest()
            sha256 = hashlib.sha256(txt.encode()).hexdigest()
            
            st.markdown("**MD5:**")
            st.code(md5)
            st.markdown("**SHA-256:**")
            st.code(sha256)
            
            st.info("此雜湊值不可逆，僅用於驗證一致性。")

# --- 電路實驗室 ---
def page_circuit():
    st.header("🔌 電路實驗室 (Ohm's Law)")
    c1, c2 = st.columns(2)
    with c1:
        v = st.slider("電壓 Voltage (V)", 0.1, 24.0, 5.0)
        r = st.slider("電阻 Resistance (Ω)", 1, 1000, 220)
    with c2:
        i = v / r
        p = v * i
        st.metric("電流 (Current)", f"{i*1000:.2f} mA")
        st.metric("功率 (Power)", f"{p:.3f} W")
        st.latex(r"I = \frac{V}{R}, \quad P = V \cdot I")

# ==============================================================================
# 3. 主程式邏輯
# ==============================================================================
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # 登入畫面
    if not st.session_state.logged_in:
        st.markdown("<h1 style='text-align:center'>🏙️ CityOS V7.5</h1>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            with st.form("login"):
                u = st.text_input("User", "frank")
                p = st.text_input("Pass", "x12345678x", type="password")
                if st.form_submit_button("Login"):
                    db = load_db()
                    if u in db["users"] and db["users"][u]["password"] == p:
                        st.session_state.logged_in = True
                        st.session_state.user_key = u
                        st.session_state.user_data = db["users"][u]
                        st.rerun()
                    else:
                        st.error("Access Denied")
        return

    # 主畫面
    user = st.session_state.user_data
    u_class = user.get("class_type", "None")
    apply_theme()
    
    # 側邊欄
    with st.sidebar:
        st.title("CityOS Ultimate")
        st.caption("All Features Restored")
        
        # 顯示卡片
        info = CLASSES.get(u_class, CLASSES["None"])
        st.markdown(f"""
        <div class="stat-card" style="border-left: 5px solid {info['color']};">
            <h3>{info['icon']} {user['name']}</h3>
            <p>{info['name']} (Lv.{user.get('rpg_level', 99)})</p>
            <p>💰 {user.get('coins', 0):,}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 選單
        pages = {
            "Dash": "📊 城市儀表板",
            "Logic": "⚡ 邏輯閘視覺化",
            "KMap": "🗺️ 卡諾圖 Solver",
            "Tools": "🧰 數位工具箱",
            "Circuit": "🔌 電路實驗室",
            "Career": "🏹 轉職中心",
            "Shop": "🛒 主題商店"
        }
        selection = st.radio("Nav", list(pages.values()), label_visibility="collapsed")
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    # 頁面路由
    if selection == "📊 城市儀表板":
        st.header("系統監控")
        # 修正圖表顏色問題
        chart_colors = THEMES[st.session_state.get("theme_name", "Night City")]["chart"]
        st.line_chart(pd.DataFrame(np.random.randn(20, 3), columns=["A","B","C"]), color=chart_colors)
        
        # 職業特效
        if u_class == "Guardian": st.error("🛡️ 資安日誌: 0 威脅")
        elif u_class == "Oracle": st.success("🔮 預測明日流量: +15%")

    elif selection == "⚡ 邏輯閘視覺化":
        page_logic_gates()
        
    elif selection == "🗺️ 卡諾圖 Solver":
        # 權限控制示例 (最高指揮官 Frank 無視限制)
        if u_class == "Architect" or user["level"] == "最高指揮官":
            page_kmap()
        else:
            st.warning("🔒 需轉職為 [架構師] 解鎖此功能")

    elif selection == "🧰 數位工具箱":
        # 包含進制轉換與密碼學
        page_tools()

    elif selection == "🔌 電路實驗室":
        if u_class == "Engineer" or user["level"] == "最高指揮官":
            page_circuit()
        else:
            st.warning("🔒 需轉職為 [工程師] 解鎖此功能")
            
    elif selection == "🏹 轉職中心":
        st.header("職業公會")
        cols = st.columns(2)
        i = 0
        for k, v in CLASSES.items():
            if k == "None": continue
            with cols[i%2]:
                with st.container(border=True):
                    st.subheader(f"{v['icon']} {v['name']}")
                    st.write(v['desc'])
                    if st.button(f"轉職 {k}", key=f"job_{k}"):
                        user["class_type"] = k
                        db = load_db()
                        db["users"][st.session_state.user_key] = user
                        save_db(db)
                        st.session_state.user_data = user
                        st.rerun()
            i+=1

    elif selection == "🛒 主題商店":
        st.header("介面風格")
        for t in THEMES.keys():
            if st.button(f"套用 {t}"):
                st.session_state.theme_name = t
                st.rerun()

if __name__ == "__main__":
    main()
