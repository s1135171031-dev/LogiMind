import streamlit as st
import pandas as pd
import random
import time

# =========================================
# 1. 語系包與核心定義
# =========================================
LANG_PACK = {
    "繁體中文": {
        "title": "🏙️ LogiMind 數位邏輯城",
        "menu": ["🏠 願景大廳", "🔬 基礎邏輯館", "🏗️ 進階電路區", "🔄 格雷碼轉換大樓", "📡 網路更新中心", "🎓 智慧考評中心", "🎨 個人化設定"],
        "welcome": "歡迎回來，管理員",
        "sys_status": "系統運行狀態",
        "convert_btn": "立即轉換",
        "save_btn": "儲存設定"
    },
    "English": {
        "title": "🏙️ LogiMind Digital City",
        "menu": ["🏠 Hall of Vision", "🔬 Logic Gate Lab", "🏗️ Advanced Circuit", "🔄 Gray Code Tower", "📡 Network Update", "🎓 Smart Exam", "🎨 Personalization"],
        "welcome": "Welcome Back, Admin",
        "sys_status": "System Status",
        "convert_btn": "Convert Now",
        "save_btn": "Save Settings"
    }
}

# =========================================
# 2. 視覺引擎 (CSS 強化)
# =========================================
def apply_style(p):
    txt_color = "#000000" if (int(p['bg'].lstrip('#'), 16) > 0x888888) else "#FFFFFF"
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {p['bg']} !important; }}
    h1, h2, h3, p, span, label, li {{ 
        color: {txt_color} !important; 
        font-size: {p['fs']}px !important; 
    }}
    .metric-card {{
        background: rgba(255,255,255,0.1);
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid {p['btn']};
        margin-bottom: 20px;
    }}
    .table-container {{ background-color: #FFFFFF !important; padding: 10px; border-radius: 8px; }}
    .logic-table td, .logic-table th {{ color: #000!important; font-size: 14px!important; border: 1px solid #eee; }}
    </style>
    """, unsafe_allow_html=True)

def render_table(df):
    html = '<div class="table-container"><table class="logic-table" style="width:100%; border-collapse:collapse;"><thead><tr>'
    html += ''.join(f'<th>{col}</th>' for col in df.columns) + '</tr></thead><tbody>'
    for _, row in df.iterrows():
        html += '<tr>' + ''.join(f'<td>{val}</td>' for val in row) + '</tr>'
    html += '</tbody></table></div>'
    st.markdown(html, unsafe_allow_html=True)

# =========================================
# 3. 邏輯運算工具
# =========================================
def bin_to_gray(b_str):
    try:
        n = int(b_str, 2)
        return bin(n ^ (n >> 1))[2:].zfill(len(b_str))
    except: return "Error"

def gray_to_bin(g_str):
    try:
        b = g_str[0]
        for i in range(1, len(g_str)):
            b += str(int(b[-1]) ^ int(g_str[i]))
        return b
    except: return "Error"

# =========================================
# 4. 初始化
# =========================================
if "score" not in st.session_state: st.session_state.score = 0
if "level" not in st.session_state: st.session_state.level = "Junior Admin"
if "exam_active" not in st.session_state: st.session_state.exam_active = False
if "prefs" not in st.session_state: st.session_state.prefs = {"bg":"#0E1117", "btn":"#00D4FF", "fs": 18, "lang": "繁體中文"}
if "net_data" not in st.session_state: st.session_state.net_data = "系統已就緒。"

# =========================================
# 5. 主程式頁面
# =========================================
def main():
    p = st.session_state.prefs
    L = LANG_PACK[p['lang']]
    apply_style(p)
    
    with st.sidebar:
        st.title(L["title"])
        st.markdown(f"👤 **{st.session_state.name}**")
        st.divider()
        page = st.radio("導航", L["menu"], label_visibility="collapsed")
        if st.button("Logout"): st.session_state.clear(); st.rerun()

    # --- 頁面 1: 願景大廳 (華麗版) ---
    if page in ["🏠 願景大廳", "🏠 Hall of Vision"]:
        st.title(f"🚀 {L['welcome']}")
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("當前權限", st.session_state.level)
        with col2: st.metric("考評積分", f"{st.session_state.score} pts")
        with col3: st.metric("網路狀態", "穩定", delta="OK")

        st.markdown(f"""<div class="metric-card"><h3>🏢 指揮部簡報</h3>
        <p>歡迎來到數位之城。這裡不僅是學習場所，更是您掌控邏輯流向的基地。</p>
        <p><b>最新指令：</b> 請先確保同步全球數據庫，以獲取最新的邏輯描述資訊。</p></div>""", unsafe_allow_html=True)
        
        st.header("🏗️ 城市藍圖")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📍 核心區")
            st.write("• **基礎邏輯館**: 學習 0 與 1 的基本原子。")
            st.write("• **進階電路區**: 構建運算器的核心零件。")
        with c2:
            st.subheader("📍 數據區")
            st.write("• **格雷碼大樓**: 處理精密機械通訊的轉換。")
            st.write("• **智慧考評中心**: AI 輔助的升階之路。")

    # --- 頁面 2: 基礎邏輯館 ---
    elif page in ["🔬 基礎邏輯館", "🔬 Logic Gate Lab"]:
        st.header(page)
        g = st.selectbox("選擇邏輯閘", ["AND", "OR", "NOT", "XOR"])
        urls = {"AND": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/AND_ANSI.svg/330px-AND_ANSI.svg.png",
                "OR": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/OR_ANSI.svg/330px-OR_ANSI.svg.png",
                "NOT": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/NOT_ANSI.svg/330px-NOT_ANSI.svg.png",
                "XOR": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/XOR_ANSI.svg/330px-XOR_ANSI.svg.png"}
        st.image(urls[g], width=250)
        st.info(f"📡 雲端數據：{st.session_state.net_data}")
        
        df = pd.DataFrame({"A":[0,0,1,1],"B":[0,1,0,1],"Y":[0,0,0,1] if g=="AND" else [0,1,1,1]})
        render_table(df)

    # --- 頁面 3: 進階電路區 (修復圖片網址) ---
    elif page in ["🏗️ 進階電路區", "🏗️ Advanced Circuit"]:
        st.header("🏗️ 進階數位電路模組")
        mode = st.tabs(["全加器 (Full Adder)", "解碼器 (Decoder)"])
        
        with mode[0]:
            st.subheader("全加器 (Full Adder)")
            st.write("全加器考慮了進位 (Carry-in)，是數位加法的核心。")
            st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Full-adder_logic_diagram.svg/500px-Full-adder_logic_diagram.svg.png", width=400)
            st.markdown("- **S (Sum)** = $A \oplus B \oplus C_{in}$ \n- **C_out** = $AB + C_{in}(A \oplus B)$")
            
        with mode[1]:
            st.subheader("2對4解碼器 (2-to-4 Decoder)")
            st.write("將 2 位元編碼輸入轉換為 4 個獨立輸出訊號。")
            st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/1_bit_Decoder_2-to-4_line_zh_hant.svg/960px-1_bit_Decoder_2-to-4_line_zh_hant.svg.png", width=400)

    # --- 頁面 4: 格雷碼大樓 (雙向轉換) ---
    elif page in ["🔄 格雷碼轉換大樓", "🔄 Gray Code Tower"]:
        st.header("🔄 格雷碼雙向通訊中心")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("二進制 ➔ 格雷碼")
            b_in = st.text_input("輸入 Binary", "1010", key="b2g")
            st.code(f"Gray Output: {bin_to_gray(b_in)}")
        with c2:
            st.subheader("格雷碼 ➔ 二進制")
            g_in = st.text_input("輸入 Gray", "1111", key="g2b")
            st.code(f"Binary Output: {gray_to_bin(g_in)}")

    # --- 頁面 5: 智慧考評中心 (20題) ---
    elif page in ["🎓 智慧考評中心", "🎓 Smart Exam"]:
        st.header(page)
        if not st.session_state.exam_active:
            if st.button("開始 20 題能力檢定"): 
                st.session_state.exam_active = True
                st.rerun()
        else:
            with st.form("exam_form"):
                st.write("### 檢定測驗中...")
                ans = [st.radio(f"Q{i+1}: 模擬邏輯問題 {i+1}", ["0", "1"], horizontal=True) for i in range(20)]
                if st.form_submit_button("提交檢定報告"):
                    st.session_state.score = random.randint(70, 100)
                    st.session_state.exam_active = False
                    st.rerun()

    # --- 頁面 6: 網路更新與設定 ---
    elif page in ["📡 網路更新中心", "📡 Network Update"]:
        st.header(page)
        if st.button("同步雲端資料庫"):
            st.session_state.net_data = f"更新完成於 {time.strftime('%H:%M:%S')}"
            st.success("同步成功！")

    elif page in ["🎨 個人化設定", "🎨 Personalization"]:
        st.header("🎨 系統環境設定")
        new_fs = st.slider("字體大小", 14, 30, p['fs'])
        new_bg = st.color_picker("背景顏色", p['bg'])
        if st.button("套用設定"):
            st.session_state.prefs.update({"bg": new_bg, "fs": new_fs})
            st.rerun()

# --- 入口 ---
if "name" not in st.session_state:
    st.set_page_config(page_title="LogiMind Login")
    st.title("🛡️ 管理員登入")
    name = st.text_input("代號")
    if st.button("進入城市"):
        if name: st.session_state.name = name; st.rerun()
else:
    st.set_page_config(page_title="LogiMind V54.1", layout="wide")
    main()

