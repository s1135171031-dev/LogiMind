import streamlit as st
import pandas as pd
import json
import os

# =========================================
# 1. 核心樣式引擎 (徹底解決隱形字)
# =========================================
def get_contrast_color(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#000000" if luminance > 0.5 else "#FFFFFF"

def apply_theme(p):
    txt = get_contrast_color(p['bg'])
    st.markdown(f"""
    <style>
    /* 全域強制染色 */
    .stApp {{ background-color: {p['bg']} !important; }}
    h1, h2, h3, h4, p, span, label {{ color: {txt} !important; }}
    
    /* 修正 Selectbox 與 Input 的文字看不到的問題 */
    div[data-baseweb="select"] > div {{ background-color: white !important; color: black !important; }}
    div[data-testid="stMarkdownContainer"] p {{ color: {txt} !important; }}
    input {{ color: black !important; }}
    
    /* 表格強制白底黑字保護，解決真值表看不見的問題 */
    div[data-testid="stTable"] {{ 
        background-color: white !important; 
        border-radius: 10px !important; 
        padding: 5px !important; 
    }}
    div[data-testid="stTable"] td, div[data-testid="stTable"] th {{ 
        color: black !important; 
        font-weight: bold !important; 
    }}
    
    .stButton>button {{
        background-color: {p['btn']} !important; color: white !important;
        border-radius: {p['radius']}px !important; border: 2px solid {txt} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# =========================================
# 2. 數據與語言字典
# =========================================
LANGS = {
    "zh": {
        "home": "🏠 系統首頁", "basic": "🔬 基礎邏輯閘", "adv": "🏗️ 進階組合電路", "gray": "🔢 格雷碼模組",
        "set": "🎨 個人化工作室", "exit": "🚪 登出",
        "intro_t": "關於 LogiMind 數位實驗室",
        "intro_c": "本系統旨在提供一個直觀、可互動的數位邏輯學習平台。從基礎的布林代數閘級電路，到複雜的算術邏輯單元(ALU)與組合電路，我們致力於將抽象的邏輯概念具象化。",
        "gray_in": "輸入二進制數 (例如 1010)", "gray_out": "轉換後的格雷碼為："
    },
    "en": {
        "home": "🏠 Home", "basic": "🔬 Basic Gates", "adv": "🏗️ Advanced Circuits", "gray": "🔢 Gray Code",
        "set": "🎨 Studio", "exit": "🚪 Logout",
        "intro_t": "About LogiMind Lab",
        "intro_c": "An interactive platform for learning digital logic. Visualizing concepts from Boolean gates to complex ALUs.",
        "gray_in": "Input Binary (e.g. 1010)", "gray_out": "Converted Gray Code:"
    }
}

GATES_DB = {
    "AND (及閘)": {"table": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,0,0,1]}},
    "OR (或閘)": {"table": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,1,1,1]}},
    "NOT (反閘)": {"table": {"In":[0,1],"Out":[1,0]}},
    "NAND (與非閘)": {"table": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[1,1,1,0]}},
    "XOR (互斥或閘)": {"table": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,1,1,0]}}
}

# =========================================
# 3. 主程式邏輯
# =========================================
if "lang" not in st.session_state: st.session_state.lang = "zh"

def main():
    p = st.session_state.prefs
    apply_theme(p)
    L = LANGS[st.session_state.lang]

    with st.sidebar:
        st.title("LogiMind V30")
        page = st.radio("選單 / Menu", [L['home'], L['basic'], L['adv'], L['gray'], L['set'], L['exit']])
        st.write("---")
        st.caption("🟢 已連線至：Streamlit Cloud Server")

    if page == L['home']:
        st.header(L['intro_t'])
        st.write(L['intro_c'])
        # 復刻圖片中的 Full Adder 方框與狀態列
        st.markdown(f'''
            <div style="background:white; border:2px solid {p['btn']}; border-radius:10px; padding:30px; text-align:center; margin:20px 0;">
                <h2 style="color:black !important;">Full Adder</h2>
            </div>
            <div style="background:#1E2633; padding:15px; border-radius:10px; color:white !important;">
                User Connected: {st.session_state.name}
            </div>
        ''', unsafe_allow_html=True)

    elif page == L['basic']:
        st.header(L['basic'])
        g = st.selectbox("選擇邏輯閘", list(GATES_DB.keys()))
        st.subheader("真值表 (Truth Table)")
        st.table(pd.DataFrame(GATES_DB[g]["table"]))

    elif page == L['adv']:
        st.header(L['adv'])
        comp = st.selectbox("組件選單", ["Full Adder (全加器)", "Half Adder (半加器)", "Encoder (編碼器)", "Decoder (解碼器)", "MUX (多工器)"])
        # 繪製圖形 (SVG)
        st.markdown(f'<div style="background:white; padding:30px; border-radius:10px; border:3px solid {p["btn"]}; text-align:center;"><h2 style="color:black !important;">{comp}</h2><p style="color:gray !important;">Logic Diagram Visualization</p></div>', unsafe_allow_html=True)

    elif page == L['gray']:
        st.header(L['gray'])
        b_in = st.text_input(L['gray_in'], "1010")
        try:
            val = int(b_in, 2)
            res = bin(val ^ (val >> 1))[2:].zfill(len(b_in))
            st.success(f"{L['gray_out']} {res}")
        except: st.error("請輸入二進制格式")
        st.write("對照表 (0-7)：")
        st.table(pd.DataFrame({"Dec":[0,1,2,3,4,5,6,7], "Bin":["000","001","010","011","100","101","110","111"], "Gray":["000","001","011","010","110","111","101","100"]}))

    elif page == L['set']:
        st.header(L['set'])
        if st.button("切換語言 / Switch Language"):
            st.session_state.lang = "en" if st.session_state.lang == "zh" else "zh"
            st.rerun()
        st.session_state.prefs['bg'] = st.color_picker("背景顏色", p['bg'])
        st.session_state.prefs['btn'] = st.color_picker("強調顏色", p['btn'])
        if st.button("儲存套用"): st.rerun()

    elif page == L['exit']:
        st.session_state.clear(); st.rerun()

def auth():
    apply_theme({"bg":"#0E1117","btn":"#00FFCC","radius":10})
    st.title("🛡️ LogiMind 登入")
    name = st.text_input("請輸入您的姓名")
    if st.button("進入系統"):
        st.session_state.user = name; st.session_state.name = name
        st.session_state.prefs = {"bg":"#0E1117","btn":"#00FFCC","radius":12}
        st.rerun()

if "user" not in st.session_state: auth()
else: main()
