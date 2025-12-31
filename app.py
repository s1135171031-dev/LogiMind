import streamlit as st
import pandas as pd
import json
import os

# =========================================
# 1. 強力視覺引擎 (封殺白底白字 & 隱形文字)
# =========================================
def get_contrast_color(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return "#000000" if (0.299 * r + 0.587 * g + 0.114 * b) / 255 > 0.5 else "#FFFFFF"

def apply_theme(p):
    txt = get_contrast_color(p['bg'])
    st.markdown(f"""
    <style>
    /* 全域文字顏色強制設定 */
    .stApp, .stApp * {{ color: {txt} !important; }}
    
    /* 側邊欄專屬保護 */
    [data-testid="stSidebar"] * {{ color: {txt} !important; }}
    
    /* 修正下拉選單與輸入框：強制白底黑字，確保看得到輸入內容 */
    div[data-baseweb="select"] > div, input {{ 
        background-color: white !important; 
        color: black !important; 
    }}
    div[data-baseweb="popover"] * {{ color: black !important; }}
    
    /* 移除表格索引 & 強制表格黑字 (解決真值表看不見問題) */
    div[data-testid="stDataFrame"] *, div[data-testid="stTable"] * {{ 
        color: black !important; 
    }}
    div[data-testid="stTable"] {{ 
        background-color: white !important; 
        border-radius: 10px; 
        overflow: hidden;
    }}

    /* 按鈕樣式 */
    .stButton>button {{
        background-color: {p['btn']} !important; color: white !important;
        border-radius: {p['radius']}px !important; border: 2px solid {txt} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# =========================================
# 2. 數據定義 (移除 Index)
# =========================================
GATES = {
    "AND (及閘)": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,0,0,1]},
    "OR (或閘)": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,1,1,1]},
    "NOT (反閘)": {"In":[0,1],"Out":[1,0]},
    "NAND (與非閘)": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[1,1,1,0]},
    "NOR (或非閘)": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[1,0,0,0]},
    "XOR (互斥或閘)": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,1,1,0]},
    "XNOR (同或閘)": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[1,0,0,1]}
}

GRAY_16 = pd.DataFrame({
    "十進制": range(16),
    "二進制 (Binary)": [bin(i)[2:].zfill(4) for i in range(16)],
    "格雷碼 (Gray Code)": [bin(i ^ (i >> 1))[2:].zfill(4) for i in range(16)]
})

# =========================================
# 3. 多國語言
# =========================================
LANGS = {
    "zh": {
        "h": "🏠 系統首頁", "b": "🔬 基礎邏輯閘", "a": "🏗️ 進階組合電路", "g": "🔢 格雷碼模組", "s": "🎨 個人化設定", "out": "🚪 登出",
        "intro_t": "關於 LogiMind 數位實驗室",
        "intro_c": "本系統旨在提供一個直觀、可互動的數位邏輯學習平台。從基礎的布林代數閘級電路，到複雜的算術邏輯單元(ALU)與組合電路，我們致力於將抽象的邏輯概念具象化。",
        "gray_in": "請輸入二進制 (如 1011)", "lang_btn": "切換語言 (English)"
    },
    "en": {
        "h": "🏠 Home", "b": "🔬 Basic Gates", "a": "🏗️ Advanced Circuits", "g": "🔢 Gray Code", "s": "🎨 Personalization", "out": "🚪 Logout",
        "intro_t": "About LogiMind Digital Lab",
        "intro_c": "LogiMind provides an interactive platform for digital logic learning. We visualize abstract logic from basic Boolean gates to complex ALUs.",
        "gray_in": "Input Binary (e.g., 1011)", "lang_btn": "Switch Language (中文)"
    }
}

# =========================================
# 4. 主程式頁面
# =========================================
if "lang" not in st.session_state: st.session_state.lang = "zh"

def main():
    p = st.session_state.prefs
    apply_theme(p)
    L = LANGS[st.session_state.lang]

    with st.sidebar:
        st.title("LogiMind V31")
        page = st.radio("導覽 / Nav", [L['h'], L['b'], L['a'], L['g'], L['s'], L['out']])
        st.markdown("---")
        st.caption("🟢 Connected to Cloud-Server")

    if page == L['h']:
        st.header(L['intro_t'])
        st.write(L['intro_c'])
        # 截圖中的 Full Adder 方框
        st.markdown(f'''
            <div style="background:white; border:3px solid #000; border-radius:15px; padding:60px; text-align:center; margin:30px 0;">
                <h1 style="color:black !important; margin:0; font-size:40px;">Full Adder</h1>
            </div>
            <div style="background:#1E2633; padding:15px; border-radius:8px; border-left: 5px solid {p['btn']};">
                <span style="color:white !important; font-weight:bold;">User Connected: {st.session_state.name}</span>
            </div>
        ''', unsafe_allow_html=True)

    elif page == L['b']:
        st.header("🔬 基礎邏輯閘全系列")
        g_sel = st.selectbox("選擇邏輯閘", list(GATES.keys()))
        st.subheader("真值表 (Truth Table)")
        # 使用 hide_index=True 移除 0,1,2,3
        st.dataframe(pd.DataFrame(GATES[g_sel]), hide_index=True, use_container_width=True)

    elif page == L['a']:
        st.header("🏗️ 進階組合電路")
        comp = st.selectbox("選擇組件", ["Half Adder (半加器)", "Full Adder (全加器)", "Encoder (編碼器)", "Decoder (解碼器)", "MUX (多工器)"])
        st.markdown(f'''<div style="background:white; padding:50px; border-radius:10px; border:4px solid {p['btn']}; text-align:center;">
            <h2 style="color:black !important;">{comp}</h2>
            <p style="color:#666 !important;">電路結構分析圖載入中...</p>
        </div>''', unsafe_allow_html=True)

    elif page == L['g']:
        st.header("🔢 格雷碼與二進制對照表")
        b_in = st.text_input(L['gray_in'], "1010")
        try:
            val = int(b_in, 2)
            gray_res = bin(val ^ (val >> 1))[2:].zfill(len(b_in))
            st.success(f"轉換輸出: {gray_res}")
        except: pass
        
        st.write("完整 4-bit 對照表 (0-15):")
        st.dataframe(GRAY_16, hide_index=True, use_container_width=True)

    elif page == L['s']:
        st.header(L['s'])
        if st.button(L['lang_btn']):
            st.session_state.lang = "en" if st.session_state.lang == "zh" else "zh"
            st.rerun()
        st.session_state.prefs['bg'] = st.color_picker("背景色", p['bg'])
        st.session_state.prefs['btn'] = st.color_picker("主題色", p['btn'])
        if st.button("確認套用"): st.rerun()

    elif page == L['out']:
        st.session_state.clear(); st.rerun()

def auth():
    apply_theme({"bg":"#0E1117","btn":"#00FFCC","radius":10})
    st.title("🛡️ LogiMind 入口")
    n = st.text_input("輸入姓名登入")
    if st.button("開始實驗"):
        st.session_state.user = n; st.session_state.name = n
        st.session_state.prefs = {"bg":"#0E1117","btn":"#00FFCC","radius":10}
        st.rerun()

if "user" not in st.session_state: auth()
else: main()
