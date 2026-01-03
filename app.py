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
    page_title="CityOS V7.1 Fixed",
    layout="wide",
    page_icon="🏙️",
    initial_sidebar_state="expanded"
)

# 檔案路徑
USER_DB_FILE = "users.json"
QS_FILE = "questions.txt"
EXP_PER_LEVEL = 100

# 職業系統 (RPG Classes)
CLASSES = {
    "None": {"name": "市民 (Citizen)", "desc": "一般市民，尚無專精", "icon": "👤", "color": "#888888"},
    "Guardian": {"name": "守護者 (Guardian)", "desc": "資訊安全與加密專精", "icon": "🛡️", "color": "#00FF99"},
    "Architect": {"name": "架構師 (Architect)", "desc": "邏輯運算與核心架構", "icon": "⚡", "color": "#00CCFF"},
    "Oracle": {"name": "預言家 (Oracle)", "desc": "大數據分析與預測", "icon": "🔮", "color": "#D500F9"},
    "Engineer": {"name": "工程師 (Engineer)", "desc": "硬體電路與歐姆定律", "icon": "🔧", "color": "#FF9900"}
}

# 商店物品
SHOP_ITEMS = {
    "theme_cyber": {"name": "主題: 賽博龐克 (Cyber)", "cost": 100, "type": "theme", "key": "Cyber Punk"},
    "theme_matrix": {"name": "主題: 駭客任務 (Matrix)", "cost": 150, "type": "theme", "key": "Matrix"},
    "theme_royal": {"name": "主題: 皇家特務 (Royal)", "cost": 300, "type": "theme", "key": "Royal"},
    "theme_amber": {"name": "主題: 復古終端 (Amber)", "cost": 200, "type": "theme", "key": "Retro Amber"},
    "theme_ocean": {"name": "主題: 深海潛航 (Ocean)", "cost": 250, "type": "theme", "key": "Deep Ocean"}
}

# 介面主題配色 (CSS Variables)
THEMES = {
    "Night City": {"bg": "#212529", "txt": "#E9ECEF", "btn": "#495057", "card": "#343A40", "chart": ["#00ADB5", "#FF2E63"]},
    "Day City": {"bg": "#F8F9FA", "txt": "#212529", "btn": "#ADB5BD", "card": "#FFFFFF", "chart": ["#343A40", "#6C757D"]},
    "Cyber Punk": {"bg": "#0B0C10", "txt": "#C5C6C7", "btn": "#FCA311", "card": "#1F2833", "chart": ["#FCA311", "#66FCF1"]},
    "Matrix": {"bg": "#000000", "txt": "#00FF41", "btn": "#003B00", "card": "#001A00", "chart": ["#008F11", "#003B00"]},
    "Royal": {"bg": "#2C001E", "txt": "#FFD700", "btn": "#590035", "card": "#420025", "chart": ["#FFD700", "#FF007F"]},
    "Retro Amber": {"bg": "#1A1A1A", "txt": "#FFB000", "btn": "#332200", "card": "#261C00", "chart": ["#FFB000", "#885500"]},
    "Deep Ocean": {"bg": "#001F3F", "txt": "#7FDBFF", "btn": "#0074D9", "card": "#003366", "chart": ["#7FDBFF", "#39CCCC"]}
}

# 權限表
LEVEL_MAP = {"實習生": 0, "初級管理員": 1, "中級管理員": 2, "高級管理員": 3, "最高指揮官": 99}

# 內嵌 SVG 圖示 (確保不破圖)
SVG_LIB = {
    "AND": '''<svg viewBox="0 0 100 60"><path d="M10,10 L40,10 C55,10 65,20 65,30 C65,40 55,50 40,50 L10,50 Z" fill="none" stroke="#888" stroke-width="3"/><path d="M0,20 L10,20 M0,40 L10,40 M65,30 L80,30" stroke="#888" stroke-width="3"/></svg>''',
    "OR": '''<svg viewBox="0 0 100 60"><path d="M10,10 L35,10 Q50,30 35,50 L10,50 Q25,30 10,10 Z" fill="none" stroke="#888" stroke-width="3"/><path d="M0,20 L15,20 M0,40 L15,40 M45,30 L60,30" stroke="#888" stroke-width="3"/></svg>''',
    "NOT": '''<svg viewBox="0 0 100 60"><path d="M20,10 L20,50 L60,30 Z" fill="none" stroke="#888" stroke-width="3"/><circle cx="65" cy="30" r="4" fill="none" stroke="#888" stroke-width="2"/><path d="M0,30 L20,30 M69,30 L80,30" stroke="#888" stroke-width="3"/></svg>''',
    "NAND": '''<svg viewBox="0 0 100 60"><path d="M10,10 L40,10 C55,10 65,20 65,30 C65,40 55,50 40,50 L10,50 Z" fill="none" stroke="#888" stroke-width="3"/><circle cx="70" cy="30" r="4" fill="none" stroke="#888" stroke-width="2"/><path d="M0,20 L10,20 M0,40 L10,40 M74,30 L85,30" stroke="#888" stroke-width="3"/></svg>''',
    "NOR": '''<svg viewBox="0 0 100 60"><path d="M10,10 L35,10 Q50,30 35,50 L10,50 Q25,30 10,10 Z" fill="none" stroke="#888" stroke-width="3"/><circle cx="50" cy="30" r="4" fill="none" stroke="#888" stroke-width="2"/><path d="M0,20 L15,20 M0,40 L15,40 M54,30 L70,30" stroke="#888" stroke-width="3"/></svg>''',
    "XOR": '''<svg viewBox="0 0 100 60"><path d="M20,10 L45,10 Q60,30 45,50 L20,50 Q35,30 20,10 Z" fill="none" stroke="#888" stroke-width="3"/><path d="M10,10 Q25,30 10,50" fill="none" stroke="#888" stroke-width="3"/><path d="M0,20 L15,20 M0,40 L15,40 M55,30 L70,30" stroke="#888" stroke-width="3"/></svg>''',
    "XNOR": '''<svg viewBox="0 0 100 60"><path d="M20,10 L45,10 Q60,30 45,50 L20,50 Q35,30 20,10 Z" fill="none" stroke="#888" stroke-width="3"/><path d="M10,10 Q25,30 10,50" fill="none" stroke="#888" stroke-width="3"/><circle cx="50" cy="30" r="4" fill="none" stroke="#888" stroke-width="2"/><path d="M0,20 L15,20 M0,40 L15,40 M54,30 L70,30" stroke="#888" stroke-width="3"/></svg>''',
    "MUX": '''<svg viewBox="0 0 120 100"><path d="M30,10 L90,25 L90,75 L30,90 Z" fill="none" stroke="#888" stroke-width="3"/><text x="45" y="55" fill="#888" font-size="14" font-family="sans-serif">MUX</text><path d="M10,25 L30,25 M10,40 L30,40 M10,55 L30,55 M10,70 L30,70 M90,50 L110,50 M60,85 L60,95" stroke="#888" stroke-width="2"/></svg>'''
}

# ==============================================================================
# 1. 工具函式 (Utilities) - 修復 frank 帳號
# ==============================================================================
def init_files():
    """初始化系統檔案，並強制修復 frank 帳號"""
    
    # 定義最高指揮官資料 (Supreme Commander Data)
    frank_data = {
        "password": "x12345678x", 
        "name": "Frank (Supreme Commander)", 
        "email": "frank@cityos.gov",
        "level": "最高指揮官", 
        "history": [], 
        "exp": 99999, 
        "rpg_level": 99, 
        "coins": 999999, 
        "class_type": "Architect", 
        "inventory": list(THEMES.keys()), 
        "last_login": ""
    }

    # 1. 處理使用者資料庫
    if not os.path.exists(USER_DB_FILE):
        # 檔案不存在，建立預設
        default_db = {"users": {"frank": frank_data}}
        with open(USER_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(default_db, f, indent=4, ensure_ascii=False)
    else:
        # 檔案存在，檢查 frank 是否被遺失
        try:
            with open(USER_DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 強制補回 frank
            if "frank" not in data["users"]:
                data["users"]["frank"] = frank_data
                with open(USER_DB_FILE, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                    
        except Exception:
            # 如果檔案損壞，重建
            default_db = {"users": {"frank": frank_data}}
            with open(USER_DB_FILE, "w", encoding="utf-8") as f:
                json.dump(default_db, f, indent=4, ensure_ascii=False)
            
    # 2. 處理題庫
    if not os.path.exists(QS_FILE):
        default_qs = "1|Easy|1 + 1 = ? in Binary|10,11,01,100|10\n" + \
                     "2|Medium|XOR(1, 1) = ?|0,1,10,11|0\n" + \
                     "3|Hard|Gate used for arithmetic sum?|AND,OR,XOR,NAND|XOR\n" + \
                     "4|Easy|Is NAND universal?|Yes,No,Maybe,Only on Sunday|Yes\n" + \
                     "5|Medium|Gray code for 3 (Dec)?|010,011,001,110|010"
        with open(QS_FILE, "w", encoding="utf-8") as f:
            f.write(default_qs)

def load_db():
    init_files()
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
        h1, h2, h3, h4, h5, h6, p, li, label, .stMarkdown, .stText {{ color: {t['txt']} !important; }}
        .stButton>button {{ background-color: {t['btn']} !important; color: white !important; border: none; font-weight: bold; transition: 0.3s; }}
        .stButton>button:hover {{ filter: brightness(1.2); }}
        div[data-testid="stExpander"], div[data-testid="stDataFrame"] {{ background-color: {t['card']}; border: 1px solid rgba(255,255,255,0.1); }}
        [data-testid="stSidebar"] {{ background-color: {t['card']}; border-right: 1px solid rgba(255,255,255,0.1); }}
        
        /* Custom Cards */
        .stat-card {{ background: {t['card']}; padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.2); margin-bottom: 10px; }}
        .commander-badge {{ background: linear-gradient(45deg, #FFD700, #FFA500); color: black; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 0.8em; }}
        
        /* K-Map Grid Buttons */
        div[data-testid="stHorizontalBlock"] button {{ height: 50px; }}
    </style>
    """, unsafe_allow_html=True)

def render_svg(svg_string):
    """渲染 SVG 字串，自動調整顏色以適應主題"""
    theme_key = st.session_state.get("theme_name", "Night City")
    stroke_color = "#333" if "Day" in theme_key else "#DDD"
    
    clean_svg = svg_string.replace("#888", stroke_color)
    b64 = base64.b64encode(clean_svg.encode('utf-8')).decode("utf-8")
    st.markdown(f'<div style="text-align:center; padding:20px;"><img src="data:image/svg+xml;base64,{b64}" width="220"></div>', unsafe_allow_html=True)

# ==============================================================================
# 2. 邏輯運算核心 (Logic Engines)
# ==============================================================================

# K-Map Solver (Quine-McCluskey Simplified)
def diff_by_one(s1, s2):
    diff = 0
    res = list(s1)
    for i in range(len(s1)):
        if s1[i] != s2[i]:
            diff += 1
            res[i] = '-'
    return diff == 1, "".join(res)

def solve_kmap_engine(minterms_indices):
    if not minterms_indices: return "0"
    if len(minterms_indices) == 16: return "1"
    
    # 1. 轉 Binary String (4 bits)
    terms = [format(m, '04b') for m in minterms_indices]
    
    # 2. Iterative Grouping
    prime_implicants = set(terms)
    
    while True:
        new_implicants = set()
        checked = set()
        sorted_terms = sorted(list(prime_implicants))
        merged_flag = False
        
        for i in range(len(sorted_terms)):
            for j in range(i + 1, len(sorted_terms)):
                t1, t2 = sorted_terms[i], sorted_terms[j]
                is_diff_one, merged_term = diff_by_one(t1, t2)
                if is_diff_one:
                    new_implicants.add(merged_term)
                    checked.add(t1)
                    checked.add(t2)
                    merged_flag = True
        
        # Add unmerged terms
        for t in prime_implicants:
            if t not in checked:
                new_implicants.add(t)
                
        if not merged_flag:
            break
        prime_implicants = new_implicants
        
    # 3. Format Output to LaTeX
    vars = ['A', 'B', 'C', 'D']
    latex_parts = []
    
    for term in prime_implicants:
        term_str = ""
        for i, bit in enumerate(term):
            if bit == '0': term_str += f"{vars[i]}'"
            elif bit == '1': term_str += f"{vars[i]}"
        if term_str == "": latex_parts.append("1")
        else: latex_parts.append(term_str)
        
    return " + ".join(latex_parts)

# ==============================================================================
# 3. 應用程式頁面 (Pages)
# ==============================================================================

def main_app():
    user = st.session_state.user_data
    apply_theme()
    
    # --- Sidebar ---
    with st.sidebar:
        st.title("🏙️ CityOS V7.1")
        st.caption("Ultimate Fixed Edition")
        
        # User Card
        u_cls = CLASSES[user.get("class_type", "None")]
        st.markdown(f"""
        <div class="stat-card" style="border-left: 5px solid {u_cls['color']};">
            <h4>{u_cls['icon']} {user['name']}</h4>
            <div style="font-size:0.9em; opacity:0.8;">{user['level']}</div>
            <hr style="margin:8px 0; opacity:0.2;">
            <div style="display:flex; justify-content:space-between;">
                <span>⚡ Lv.{user.get('rpg_level', 1)}</span>
                <span>💰 {user.get('coins', 0)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Menu
        pages = {
            "Dash": "📊 城市儀表板",
            "Logic": "⚡ 邏輯閘視覺化",
            "Circuit": "🔌 基礎電路實驗",
            "Tools": "🧰 數位工具箱", 
            "KMap": "🗺️ 卡諾圖 (K-Map)",
            "Academy": "🎓 市政學院",
            "Shop": "🛒 補給站",
            "Profile": "📂 市民檔案"
        }
        if user['level'] == "最高指揮官":
            pages["Admin"] = "☢️ 核心控制台"
            
        selection = st.radio("導航", list(pages.values()), label_visibility="collapsed")
        
        if st.button("🚪 登出系統"):
            st.session_state.logged_in = False
            st.rerun()

    # --- Page Content ---
    
    # 1. Dashboard
    if selection == "📊 城市儀表板":
        st.header(f"歡迎回來，{user['name']}")
        
        # Daily Login
        today_str = str(date.today())
        if user.get("last_login") != today_str:
            if st.button("🎁 簽到領取獎勵"):
                user["last_login"] = today_str
                user["coins"] += 100
                user["exp"] += 50
                st.session_state.user_data = user 
                db = load_db()
                db["users"][st.session_state.user_key] = user
                save_db(db)
                st.balloons()
                st.toast("獲得 100 Coins, 50 EXP", icon="🎉")
                time.sleep(1)
                st.rerun()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("CPU 負載", f"{random.randint(20, 80)}%", "穩定")
        col2.metric("網路流量", f"{random.randint(100, 900)} MB/s", "+12%")
        col3.metric("安全等級", "Level 5", "正常")
        
        st.subheader("系統監控")
        chart_data = pd.DataFrame(
            np.random.randn(20, 3),
            columns=['Core A', 'Core B', 'Core C']
        )
        st.area_chart(chart_data, color=THEMES[st.session_state.get("theme_name", "Night City")]["chart"])

    # 2. Logic Gates
    elif selection == "⚡ 邏輯閘視覺化":
        st.header("⚡ 數位邏輯閘")
        c1, c2 = st.columns([1, 2])
        with c1:
            gate_type = st.selectbox("選擇元件", list(SVG_LIB.keys()))
            st.info("原理說明會顯示於下方")
            data = []
            if gate_type == "NOT":
                data = [{"In":0, "Out":1}, {"In":1, "Out":0}]
            elif gate_type == "MUX":
                data = [{"Sel":0, "A":0, "B":"X", "Out":0}, {"Sel":0, "A":1, "B":"X", "Out":1}, {"Sel":1, "A":"X", "B":0, "Out":0}, {"Sel":1, "A":"X", "B":1, "Out":1}]
            else:
                for a in [0,1]:
                    for b in [0,1]:
                        res = 0
                        if gate_type=="AND": res=a&b
                        elif gate_type=="OR": res=a|b
                        elif gate_type=="XOR": res=a^b
                        elif gate_type=="NAND": res=1-(a&b)
                        elif gate_type=="NOR": res=1-(a|b)
                        elif gate_type=="XNOR": res=1-(a^b)
                        data.append({"A":a, "B":b, "Out":res})
            st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

        with c2:
            st.subheader("電路符號")
            render_svg(SVG_LIB[gate_type])
            if st.button("✨ 執行模擬運算"):
                st.toast("模擬成功！訊號傳遞正常。", icon="✅")

    # 3. Circuit
    elif selection == "🔌 基礎電路實驗":
        st.header("🔌 歐姆定律實驗室")
        tab1, tab2 = st.tabs(["基礎計算", "串並聯分析"])
        with tab1:
            c1, c2 = st.columns(2)
            with c1:
                v = st.number_input("電壓 (V)", 0.0, 100.0, 5.0)
                r = st.number_input("電阻 (Ω)", 1.0, 1000.0, 100.0)
            with c2:
                i = v / r
                st.latex(f"I = \\frac{{V}}{{R}} = \\frac{{{v}}}{{{r}}} = {i:.4f} A")
                st.metric("電流 (Current)", f"{i*1000:.2f} mA")
        with tab2:
            mode = st.radio("連接模式", ["串聯 (Series)", "並聯 (Parallel)"])
            r1 = st.slider("R1 (Ω)", 10, 500, 100)
            r2 = st.slider("R2 (Ω)", 10, 500, 100)
            if "串聯" in mode:
                rt = r1 + r2
                st.latex(f"R_T = R_1 + R_2 = {r1} + {r2} = {rt} \\Omega")
            else:
                rt = (r1 * r2) / (r1 + r2)
                st.latex(f"R_T = \\frac{{R_1 \\cdot R_2}}{{R_1 + R_2}} = {rt:.2f} \\Omega")

    # 4. Tools
    elif selection == "🧰 數位工具箱":
        st.header("🧰 工程師工具箱")
        tool_type = st.selectbox("選擇工具", ["進制轉換", "格雷碼計算", "資安雜湊"])
        if tool_type == "進制轉換":
            val = st.text_input("輸入十進位數值", "255")
            if val.isdigit():
                d = int(val)
                c1, c2, c3 = st.columns(3)
                c1.code(f"BIN: {bin(d)[2:]}")
                c2.code(f"OCT: {oct(d)[2:]}")
                c3.code(f"HEX: {hex(d)[2:].upper()}")
        elif tool_type == "格雷碼計算":
            val = st.number_input("輸入整數", 0, 255, 12)
            gray = val ^ (val >> 1)
            st.latex(f"Binary: {bin(val)[2:]} \\rightarrow Gray: {bin(gray)[2:]}")
        elif tool_type == "資安雜湊":
            txt = st.text_input("輸入文字", "CityOS")
            h = hashlib.sha256(txt.encode()).hexdigest()
            st.code(f"SHA-256: {h}")

    # 5. K-Map
    elif selection == "🗺️ 卡諾圖 (K-Map)":
        st.header("🗺️ 4變數卡諾圖化簡器")
        st.caption("Advanced Quine-McCluskey Engine Included")
        
        if "kmap_grid" not in st.session_state:
            st.session_state.kmap_grid = [0] * 16

        # Gray Code Order
        map_idx = [
            [0, 1, 3, 2],    # Row 00
            [4, 5, 7, 6],    # Row 01
            [12, 13, 15, 14],# Row 11
            [8, 9, 11, 10]   # Row 10
        ]
        
        col_ui, col_res = st.columns([1.5, 1])
        with col_ui:
            st.markdown("##### 設定真值表")
            cols = st.columns([0.5, 1, 1, 1, 1])
            cols[0].markdown("**AB\\CD**")
            cols[1].markdown("**00**"); cols[2].markdown("**01**"); cols[3].markdown("**11**"); cols[4].markdown("**10**")
            row_labels = ["00", "01", "11", "10"]
            
            for r in range(4):
                cols = st.columns([0.5, 1, 1, 1, 1])
                cols[0].markdown(f"**{row_labels[r]}**")
                for c in range(4):
                    idx = map_idx[r][c]
                    current_val = st.session_state.kmap_grid[idx]
                    btn_label = "1" if current_val else "0"
                    btn_type = "primary" if current_val else "secondary"
                    if cols[c+1].button(btn_label, key=f"kbtn_{idx}", type=btn_type, use_container_width=True):
                        st.session_state.kmap_grid[idx] = 1 - current_val
                        st.rerun()

            if st.button("🔄 清除全部"):
                st.session_state.kmap_grid = [0] * 16
                st.rerun()

        with col_res:
            st.markdown("##### 化簡結果")
            minterms = [i for i, v in enumerate(st.session_state.kmap_grid) if v == 1]
            expr = solve_kmap_engine(minterms)
            st.info(f"Minterms: $\\Sigma m({', '.join(map(str, minterms))})$")
            st.markdown("### 最簡布林代數式:")
            st.latex(f"F = {expr}")
            if st.button("💾 記錄到剪貼簿"):
                st.toast("已複製結果！", icon="📋")

    # 6. Academy
    elif selection == "🎓 市政學院":
        st.header("🎓 技能檢定")
        if "quiz_active" not in st.session_state: st.session_state.quiz_active = False
            
        if not st.session_state.quiz_active:
            if st.button("🚀 開始測驗"):
                with open(QS_FILE, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                valid_q = []
                for l in lines:
                    parts = l.strip().split("|")
                    if len(parts) == 5: valid_q.append(parts)
                if len(valid_q) > 0:
                    st.session_state.current_quiz = random.sample(valid_q, min(3, len(valid_q)))
                    st.session_state.quiz_active = True
                    st.rerun()
        else:
            with st.form("quiz_form"):
                score = 0
                for i, q_data in enumerate(st.session_state.current_quiz):
                    st.markdown(f"**Q{i+1}: {q_data[2]}**")
                    st.radio(f"選項 {i}", q_data[3].split(","), key=f"q_{i}", label_visibility="collapsed")
                    st.divider()
                if st.form_submit_button("📝 提交答案"):
                    for i, q_data in enumerate(st.session_state.current_quiz):
                        if st.session_state.get(f"q_{i}") == q_data[4]: score += 1
                    user["coins"] += score * 20
                    user["exp"] += score * 15
                    db = load_db()
                    db["users"][st.session_state.user_key] = user
                    save_db(db)
                    st.toast(f"+{score * 20} Coins", icon="💰")
                    st.session_state.quiz_active = False
                    time.sleep(1)
                    st.rerun()

    # 7. Shop
    elif selection == "🛒 補給站":
        st.header("🛒 風格補給站")
        cols = st.columns(3)
        for idx, (item_id, item) in enumerate(SHOP_ITEMS.items()):
            with cols[idx % 3]:
                st.markdown(f"**{item['name']}**")
                st.caption(f"價格: {item['cost']} Coins")
                if item["key"] in user.get("inventory", []):
                    st.button("已擁有", key=item_id, disabled=True)
                else:
                    if st.button("購買", key=item_id):
                        if user["coins"] >= item["cost"]:
                            user["coins"] -= item["cost"]
                            user["inventory"].append(item["key"])
                            db = load_db()
                            db["users"][st.session_state.user_key] = user
                            save_db(db)
                            st.toast("購買成功！", icon="🛍️")
                            st.rerun()

    # 8. Profile
    elif selection == "📂 市民檔案":
        st.header("📂 設定與轉職")
        inv = user.get("inventory", ["Night City"])
        current = st.session_state.get("theme_name", "Night City")
        new_theme = st.selectbox("選擇主題", inv, index=inv.index(current) if current in inv else 0)
        if new_theme != current:
            st.session_state.theme_name = new_theme
            st.rerun()
            
        st.divider()
        st.subheader("⚔️ 職業轉職")
        if user["class_type"] == "None":
            c1, c2, c3, c4 = st.columns(4)
            if c1.button("轉職 守護者"): user["class_type"] = "Guardian"; st.rerun()
            if c2.button("轉職 架構師"): user["class_type"] = "Architect"; st.rerun()
            if c3.button("轉職 預言家"): user["class_type"] = "Oracle"; st.rerun()
            if c4.button("轉職 工程師"): user["class_type"] = "Engineer"; st.rerun()
        else:
            st.info(f"你目前的職業是: {CLASSES[user['class_type']]['name']}")
            if st.button("重置職業 (500$)"):
                if user["coins"] >= 500:
                    user["coins"] -= 500
                    user["class_type"] = "None"
                    st.rerun()

    # 9. Admin
    elif selection == "☢️ 核心控制台":
        st.title("Admin Console")
        db = load_db()
        st.dataframe(pd.DataFrame(db["users"]).T)

# ==============================================================================
# 4. 登入入口 (Login Entry)
# ==============================================================================

def login_page():
    st.markdown("<h1 style='text-align: center;'>🏙️ CityOS V7.1</h1>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        tab1, tab2 = st.tabs(["登入", "註冊"])
        with tab1:
            u = st.text_input("帳號", key="l_user")
            p = st.text_input("密碼", type="password", key="l_pass")
            if st.button("🚀 進入系統", use_container_width=True):
                db = load_db()
                if u in db["users"] and db["users"][u]["password"] == p:
                    st.session_state.logged_in = True
                    st.session_state.user_key = u
                    st.session_state.user_data = db["users"][u]
                    st.session_state.theme_name = "Night City" 
                    st.rerun()
                else:
                    st.error("帳號或密碼錯誤")
        with tab2:
            nu = st.text_input("設定帳號", key="r_user")
            np_ = st.text_input("設定密碼", type="password", key="r_pass")
            if st.button("📝 建立市民檔案", use_container_width=True):
                db = load_db()
                if nu in db["users"]:
                    st.error("帳號已存在")
                elif nu and np_:
                    db["users"][nu] = {
                        "password": np_, "name": nu, "email": "", 
                        "level": "實習生", "exp": 0, "coins": 100, 
                        "class_type": "None", "inventory": ["Night City", "Day City"], 
                        "last_login": ""
                    }
                    save_db(db)
                    st.success("註冊成功！請切換至登入頁面。")

# ==============================================================================
# Main Execution
# ==============================================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

init_files() # This will FIX the frank account

if st.session_state.logged_in:
    main_app()
else:
    login_page()
