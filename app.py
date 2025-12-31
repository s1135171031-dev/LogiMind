import streamlit as st
import pandas as pd
import json
import os

# =========================================
# 1. 智慧顏色感應與強制渲染 (修正白底白字)
# =========================================
def get_contrast_color(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#000000" if luminance > 0.5 else "#FFFFFF"

def apply_theme(p):
    txt = get_contrast_color(p['bg'])
    # 使用全域 * 選擇器強制覆蓋所有可能隱形的文字
    hide_style = f"""
    <style>
    #MainMenu, footer, header {{visibility: hidden !important;}}
    .stApp {{ background-color: {p['bg']} !important; color: {txt} !important; }}
    
    /* 強制所有文字元素顯示正確對比色 */
    * {{ color: {txt} !important; font-family: 'Inter', sans-serif; }}
    
    /* 排除表格內文字（強制黑字以保證可讀性） */
    div[data-testid="stTable"] *, div[data-testid="stDataFrame"] * {{ color: black !important; }}
    div[data-testid="stTable"] {{ background-color: white !important; border-radius: 10px; }}

    .stButton>button {{
        background-color: {p['btn']} !important; color: white !important;
        border-radius: {p['radius']}px !important; border: 2px solid {txt} !important;
    }}
    /* 下拉選單與輸入框背景保護 */
    div[data-baseweb="select"] > div {{ background-color: white !important; color: black !important; }}
    input {{ background-color: white !important; color: black !important; }}
    </style>
    """
    st.markdown(hide_style, unsafe_allow_html=True)

# =========================================
# 2. 核心資料庫 (真值表與格雷碼)
# =========================================
GATES_INFO = {
    "AND (及閘)": {"table": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,0,0,1]}},
    "OR (或閘)": {"table": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,1,1,1]}},
    "NOT (反閘)": {"table": {"In":[0,1],"Out":[1,0]}},
    "NAND (與非閘)": {"table": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[1,1,1,0]}},
    "NOR (或非閘)": {"table": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[1,0,0,0]}},
    "XOR (互斥或閘)": {"table": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,1,1,0]}},
    "XNOR (同或閘)": {"table": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[1,0,0,1]}}
}

GRAY_DATA = pd.DataFrame({
    "Dec": range(16),
    "Binary": [bin(i)[2:].zfill(4) for i in range(16)],
    "Gray": [bin(i ^ (i >> 1))[2:].zfill(4) for i in range(16)]
})

# =========================================
# 3. 語言與翻譯
# =========================================
LANGS = {
    "zh": {
        "home": "🏠 首頁介紹", "basic": "🔬 基礎邏輯閘", "adv": "🏗️ 進階組合電路", "gray": "🔢 格雷碼模組",
        "quiz": "📝 20題檢定賽", "set": "🎨 個人化工作室", "log": "📜 更新日誌", "exit": "🚪 登出",
        "intro_t": "關於 LogiMind 數位實驗室",
        "intro_c": "本系統旨在提供一個直觀、可互動的數位邏輯學習平台。從基礎的布林代數閘級電路，到複雜的算術邏輯單元(ALU)與組合電路，我們致力於將抽象的邏輯概念具象化。",
        "conn": "🟢 伺服器狀態：已與 Streamlit Cloud 同步連接",
        "save": "套用設定", "lang_sel": "語言切換 (Language)"
    },
    "en": {
        "home": "🏠 Home", "basic": "🔬 Basic Gates", "adv": "🏗️ Advanced Circuits", "gray": "🔢 Gray Code",
        "quiz": "📝 20-Question Quiz", "set": "🎨 Personalization", "log": "📜 Update Log", "exit": "🚪 Logout",
        "intro_t": "About LogiMind Digital Lab",
        "intro_c": "LogiMind provides an interactive digital logic learning platform. We visualize abstract logic from basic Boolean gates to complex ALUs.",
        "conn": "🟢 Connection: Connected to Streamlit Cloud Node",
        "save": "Apply Settings", "lang_sel": "Switch Language (切換語言)"
    }
}

# =========================================
# 4. 主介面
# =========================================
if "lang" not in st.session_state: st.session_state.lang = "zh"

def main():
    p = st.session_state.prefs
    apply_theme(p)
    L = LANGS[st.session_state.lang]

    with st.sidebar:
        st.title(f"Hi, {st.session_state.name}")
        st.caption(L['conn'])
        page = st.radio("Menu", [L['home'], L['basic'], L['adv'], L['gray'], L['quiz'], L['set'], L['log'], L['exit']])

    if page == L['home']:
        st.header(L['intro_t'])
        st.write(L['intro_c'])
        st.info(f"User Connected: {st.session_state.user}")
        # 展示全加器示意圖
        st.markdown('<div style="background:white; padding:20px; border-radius:10px; border:3px solid black; color:black; text-align:center;"><b>[Full Adder Circuit Diagram Placeholder]</b></div>', unsafe_allow_html=True)

    elif page == L['basic']:
        st.header(L['basic'])
        g_name = st.selectbox("選擇邏輯閘", list(GATES_INFO.keys()))
        st.subheader("真值表 (Truth Table)")
        st.table(pd.DataFrame(GATES_INFO[g_name]["table"]))

    elif page == L['adv']:
        st.header(L['adv'])
        adv_comp = st.selectbox("選擇組件", ["Half Adder (半加器)", "Full Adder (全加器)", "Encoder (編碼器)", "Decoder (解碼器)", "MUX (多工器)"])
        st.write(f"正在顯示 {adv_comp} 的邏輯結構...")
        st.markdown('<div style="background:white; padding:40px; border-radius:10px; border:2px solid #333; color:black; text-align:center;">電路圖繪製中...</div>', unsafe_allow_html=True)

    elif page == L['gray']:
        st.header(L['gray'])
        st.write("完整 4-bit 格雷碼對照表 (0-15)")
        st.table(GRAY_DATA)

    elif page == L['quiz']:
        st.header(L['quiz'])
        st.warning("測驗模組載入中... 請準備好紙筆進行邏輯運算。")
        if st.button("開始測驗"): st.success("測驗開始！")

    elif page == L['set']:
        st.header(L['set'])
        if st.button(L['lang_sel']):
            st.session_state.lang = "en" if st.session_state.lang == "zh" else "zh"
            st.rerun()
        st.session_state.prefs['bg'] = st.color_picker("背景顏色", p['bg'])
        st.session_state.prefs['btn'] = st.color_picker("主題按鈕顏色", p['btn'])
        st.session_state.prefs['radius'] = st.slider("圓角大小", 0, 30, p['radius'])
        if st.button(L['save']): st.rerun()

    elif page == L['log']:
        st.header(L['log'])
        st.table(pd.DataFrame([{"Version":"V29","Content":"修復白底白字、功能大復合、語言切換搬移"}]))

    elif page == L['exit']:
        st.session_state.clear(); st.rerun()

# 登入頁面 (修正白底白字)
def auth():
    apply_theme({"bg":"#0E1117","btn":"#00FFCC","radius":10})
    st.title("🛡️ LogiMind V29")
    u = st.text_input("Username / 帳號")
    p = st.text_input("Password / 密碼", type="password")
    if st.button("Login / 登入"):
        st.session_state.user = u
        st.session_state.name = u
        st.session_state.prefs = {"bg":"#0E1117","btn":"#00FFCC","radius":10}
        st.rerun()

if "user" not in st.session_state: auth()
else: main()
