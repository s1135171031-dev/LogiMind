import streamlit as st
import pandas as pd
import json
import os

# =========================================
# 1. 智慧對比偵測引擎
# =========================================
def get_contrast_color(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#000000" if luminance > 0.5 else "#FFFFFF"

# =========================================
# 2. 多國語言字典 (含介紹內容)
# =========================================
LANG_DICT = {
    "zh": {
        "welcome": "🏠 系統首頁", "basic": "🔬 基礎邏輯閘", "adv": "🏗️ 進階組合電路", "gray": "🔢 格雷碼模組",
        "setting": "🎨 個人化工作室", "log": "📜 更新日誌", "logout": "🚪 登出",
        "intro_title": "關於 LogiMind 數位實驗室",
        "intro_content": "本系統旨在提供一個直觀、可互動的數位邏輯學習平台。從基礎的布林代數閘級電路，到複雜的算術邏輯單元 (ALU) 與組合電路，我們致力於將抽象的邏輯概念具象化。",
        "conn_node": "實時連線節點：Streamlit Cloud - Taiwan North",
        "truth_table": "真值表內容", "lang_btn": "切換為 English", "save": "儲存並套用"
    },
    "en": {
        "welcome": "🏠 Home", "basic": "🔬 Basic Gates", "adv": "🏗️ Advanced Circuits", "gray": "🔢 Gray Code",
        "setting": "🎨 Studio", "log": "📜 History", "logout": "🚪 Logout",
        "intro_title": "About LogiMind Digital Lab",
        "intro_content": "LogiMind is an interactive platform for digital logic learning. From gate-level circuits to complex ALUs, we visualize abstract logic concepts for better understanding.",
        "conn_node": "Node: Streamlit Cloud - Global Entry",
        "truth_table": "Full Truth Table", "lang_btn": "Switch to 中文", "save": "Save & Apply"
    }
}

# =========================================
# 3. 強制視覺注入 (解決字體隱形問題)
# =========================================
def apply_theme(p):
    txt = get_contrast_color(p['bg'])
    st.markdown(f"""
    <style>
    #MainMenu, footer, header {{visibility: hidden;}}
    .stApp {{ background-color: {p['bg']}; color: {txt}; }}
    h1, h2, h3, p, span, label, .stMarkdown, .stRadio label {{ color: {txt} !important; }}
    .stButton>button {{
        background-color: {p['btn']}; color: white; border-radius: {p['radius']}px;
        border: 2px solid {txt}; transition: 0.3s;
    }}
    div[data-testid="stTable"] {{ background-color: white !important; border-radius: 10px; overflow: hidden; }}
    div[data-testid="stTable"] td, div[data-testid="stTable"] th {{ color: black !important; }}
    </style>
    """, unsafe_allow_html=True)

# =========================================
# 4. 完整資料庫 (邏輯閘 + 格雷碼)
# =========================================
GATES_DATA = {
    "AND (及閘)": {"table": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,0,0,1]}},
    "OR (或閘)": {"table": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,1,1,1]}},
    "NOT (反閘)": {"table": {"In":[0,1],"Out":[1,0]}},
    "NAND (與非閘)": {"table": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[1,1,1,0]}},
    "NOR (或非閘)": {"table": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[1,0,0,0]}},
    "XOR (互斥或閘)": {"table": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,1,1,0]}},
    "XNOR (同或閘)": {"table": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[1,0,0,1]}}
}

GRAY_TABLE_FULL = pd.DataFrame({
    "Dec": range(16),
    "Binary": [bin(i)[2:].zfill(4) for i in range(16)],
    "Gray": [(bin(i ^ (i >> 1))[2:].zfill(4)) for i in range(16)]
})

# =========================================
# 5. 主系統邏輯
# =========================================
if "lang" not in st.session_state: st.session_state.lang = "zh"

def main():
    p = st.session_state.prefs
    apply_theme(p)
    L = LANG_DICT[st.session_state.lang]

    with st.sidebar:
        st.title(f"Logged in: {st.session_state.name}")
        menu = st.radio("Navigation", [L['welcome'], L['basic'], L['adv'], L['gray'], L['setting'], L['logout']])
        st.markdown("---")
        st.caption(f"🟢 {L['conn_node']}")

    if menu == L['welcome']:
        st.header(L['intro_title'])
        st.write(L['intro_content'])
        # 顯示歡迎卡片
        st.markdown(f"""
        <div style="padding: 20px; border: 2px solid {p['btn']}; border-radius: 15px; background: rgba(255,255,255,0.1);">
            <h4 style="margin:0;">User Connected: {st.session_state.name}</h4>
            <p>Role: System Architect</p>
        </div>
        """, unsafe_allow_html=True)

    elif menu == L['basic']:
        st.header(L['basic'])
        g = st.selectbox("Select Gate Type", list(GATES_DATA.keys()))
        st.subheader(f"{g} - {L['truth_table']}")
        st.table(pd.DataFrame(GATES_DATA[g]["table"]))

    elif menu == L['adv']:
        st.header(L['adv'])
        adv_type = st.selectbox("Circuit Type", ["Half Adder (半加器)", "Full Adder (全加器)", "Encoder (編碼器)", "Decoder (解碼器)", "MUX (多工器)"])
        st.info(f"正在顯示 {adv_type} 的結構圖與運算邏輯...")
        st.write("這是一個將多個基礎邏輯閘組合而成的複雜電路系統。")

    elif menu == L['gray']:
        st.header(L['gray'])
        st.write("完整的 4 位元格雷碼對照表 (0-15)：")
        st.table(GRAY_TABLE_FULL)

    elif menu == L['setting']:
        st.header(L['setting'])
        # 語言切換按鈕放在這裡
        if st.button(L['lang_btn']):
            st.session_state.lang = "en" if st.session_state.lang == "zh" else "zh"
            st.rerun()
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.prefs['bg'] = st.color_picker("Background", p['bg'])
        with col2:
            st.session_state.prefs['btn'] = st.color_picker("Theme Color", p['btn'])
        
        if st.button(L['save']):
            st.success("Settings Saved!")
            st.rerun()

    elif menu == L['logout']:
        del st.session_state.user; st.rerun()

# 登入閘門 (Auth Gate)
def auth_gate():
    apply_theme({"bg":"#0E1117","btn":"#00FFCC","radius":10})
    st.title("🛡️ LogiMind V28 Entrance")
    user = st.text_input("Username")
    if st.button("Enter Lab"):
        st.session_state.user = user
        st.session_state.name = user
        st.session_state.prefs = {"bg":"#0E1117","btn":"#00FFCC","radius":10}
        st.rerun()

if "user" not in st.session_state: auth_gate()
else: main()
