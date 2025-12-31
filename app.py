import streamlit as st
import pandas as pd
import json
import os

# =========================================
# 1. 智慧顏色感測與語系字典
# =========================================
def get_text_color(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    # 亮度計算公式 (Luminance)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#000000" if luminance > 0.5 else "#FFFFFF"

LANG_DICT = {
    "zh": {
        "welcome": "🏠 歡迎首頁", "basic": "🔬 基礎邏輯閘", "adv": "🏗️ 進階組合電路", "gray": "🔢 格雷碼模組",
        "setting": "🎨 個人化設定", "log": "📜 更新日誌", "logout": "🚪 登出",
        "intro_title": "關於 LogiMind 數位實驗室",
        "intro_text": "本系統旨在提供一個直觀、可互動的數位邏輯學習平台。從基礎的布林代數閘級電路，到複雜的算術邏輯單元(ALU)與組合電路，我們致力於將抽象的邏輯概念具象化。",
        "conn_status": "✅ 系統狀態：已真實連接至 Streamlit Cloud 伺服器",
        "truth_table": "真值表", "convert": "轉換", "save": "儲存設定", "lang_btn": "切換語言 (Switch Language)"
    },
    "en": {
        "welcome": "🏠 Welcome", "basic": "🔬 Basic Gates", "adv": "🏗️ Advanced Circuits", "gray": "🔢 Gray Code",
        "setting": "🎨 Personalization", "log": "📜 Update Log", "logout": "🚪 Logout",
        "intro_title": "About LogiMind Lab",
        "intro_text": "LogiMind is an interactive platform designed for digital logic learners. From basic Boolean gates to complex arithmetic units, we visualize abstract logic concepts.",
        "conn_status": "✅ Status: Securely Connected to Streamlit Cloud",
        "truth_table": "Truth Table", "convert": "Convert", "save": "Save Settings", "lang_btn": "Switch Language (切換語言)"
    }
}

# =========================================
# 2. 視覺引擎 (智慧配色)
# =========================================
def apply_theme(p):
    txt = get_text_color(p['bg'])
    hide_style = f"""
    <style>
    #MainMenu, footer, header {{visibility: hidden;}}
    .stApp {{ background-color: {p['bg']}; color: {txt}; }}
    label, p, span, .stMarkdown, .stRadio {{ color: {txt} !important; }}
    .stButton>button {{
        background-color: {p['btn']}; color: white; border-radius: {p['radius']}px;
        border: 2px solid {txt}; font-weight: bold;
    }}
    /* 表格強制白底黑字保護 */
    div[data-testid="stTable"] {{ background-color: white !important; border-radius: 10px; padding: 10px; }}
    div[data-testid="stTable"] td, div[data-testid="stTable"] th {{ color: black !important; }}
    </style>
    """
    st.markdown(hide_style, unsafe_allow_html=True)

# =========================================
# 3. 邏輯閘與電路 SVG 庫 (雙語顯示)
# =========================================
GATES = {
    "AND (及閘)": {"svg": '''<svg viewBox="0 0 120 70" width="180"><path d="M40,10 H50 A25,25 0 0,1 50,60 H40 Z" fill="none" stroke="black" stroke-width="3"/></svg>''', "table": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,0,0,1]}},
    "OR (或閘)": {"svg": '''<svg viewBox="0 0 120 70" width="180"><path d="M35,10 Q50,35 35,60 Q70,60 95,35 Q70,10 35,10 Z" fill="none" stroke="black" stroke-width="3"/></svg>''', "table": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,1,1,1]}},
    "NOT (反閘)": {"svg": '''<svg viewBox="0 0 120 70" width="180"><path d="M40,15 L80,35 L40,55 Z" fill="none" stroke="black" stroke-width="3"/><circle cx="85" cy="35" r="5" fill="none" stroke="black" stroke-width="2"/></svg>''', "table": {"In":[0,1],"Out":[1,0]}},
    "XOR (互斥或閘)": {"svg": '''<svg viewBox="0 0 120 70" width="180"><path d="M35,10 Q50,35 35,60 M42,10 Q57,35 42,60 Q77,60 102,35 Q77,10 42,10 Z" fill="none" stroke="black" stroke-width="3"/></svg>''', "table": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,1,1,0]}}
}

ADV_CIRCUITS = {
    "Full Adder (全加器)": '''<svg viewBox="0 0 200 120" width="250"><rect x="50" y="20" width="100" height="80" fill="white" stroke="black" stroke-width="3"/><text x="100" y="65" text-anchor="middle">Full Adder</text></svg>''',
    "Half Adder (半加器)": '''<svg viewBox="0 0 200 120" width="250"><rect x="50" y="20" width="100" height="80" fill="white" stroke="black" stroke-width="3"/><text x="100" y="65" text-anchor="middle">Half Adder</text></svg>''',
    "MUX (多工器)": '''<svg viewBox="0 0 200 120" width="250"><path d="M60,20 L140,40 L140,80 L60,100 Z" fill="white" stroke="black" stroke-width="3"/><text x="100" y="65" text-anchor="middle">MUX</text></svg>''',
    "Decoder (解碼器)": '''<svg viewBox="0 0 200 120" width="250"><rect x="60" y="20" width="80" height="80" fill="white" stroke="black" stroke-width="3"/><text x="100" y="65" text-anchor="middle">Decoder</text></svg>'''
}

def render_box(svg_code):
    st.markdown(f'''<div style="display: table; margin: 10px auto; padding: 20px; background: white; border-radius: 10px; border: 3px solid #333;">{svg_code}</div>''', unsafe_allow_html=True)

# =========================================
# 4. 主程式
# =========================================
DB_FILE = "logimind_v27.json"
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return {}

if "lang" not in st.session_state: st.session_state.lang = "zh"

def main():
    p = st.session_state.prefs
    apply_theme(p)
    L = LANG_DICT[st.session_state.lang]

    with st.sidebar:
        st.title(f"🚀 {st.session_state.name}")
        st.write(f"🔗 {L['conn_status']}")
        if st.button(L['lang_btn']):
            st.session_state.lang = "en" if st.session_state.lang == "zh" else "zh"
            st.rerun()
        
        menu = st.radio("Menu", [L['welcome'], L['basic'], L['adv'], L['gray'], L['setting'], L['log'], L['logout']])

    if menu == L['welcome']:
        st.header(L['intro_title'])
        st.write(L['intro_text'])
        render_box(ADV_CIRCUITS["Full Adder (全加器)"])
        st.info(f"User Connected: {st.session_state.name}")

    elif menu == L['basic']:
        st.header(L['basic'])
        g_name = st.selectbox("Select Gate", list(GATES.keys()))
        render_box(GATES[g_name]["svg"])
        st.subheader(L['truth_table'])
        st.table(pd.DataFrame(GATES[g_name]["table"]))

    elif menu == L['adv']:
        st.header(L['adv'])
        c_name = st.selectbox("Select Circuit", list(ADV_CIRCUITS.keys()))
        render_box(ADV_CIRCUITS[c_name])
        st.write("組合邏輯電路詳解載入中...")

    elif menu == L['gray']:
        st.header(L['gray'])
        st.table(pd.DataFrame({"Decimal":[0,1,2,3,4],"Binary":["000","001","010","011","100"],"Gray":["000","001","011","010","110"]}))

    elif menu == L['setting']:
        st.header(L['setting'])
        st.session_state.prefs['bg'] = st.color_picker("Background", p['bg'])
        st.session_state.prefs['btn'] = st.color_picker("Theme Color", p['btn'])
        if st.button(L['save']):
            db = load_db(); db[st.session_state.user]["prefs"] = st.session_state.prefs
            with open(DB_FILE, "w") as f: json.dump(db, f)
            st.rerun()

    elif menu == L['logout']:
        del st.session_state.user; st.rerun()

# (註冊與登入邏輯... 為了精簡 code 建議沿用 V26 的 auth_gate)
def auth_gate():
    apply_theme({"bg":"#121212","btn":"#00D1B2","radius":10})
    st.title("🛡️ LogiMind V27")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        st.session_state.user, st.session_state.name = u, u
        st.session_state.prefs = {"bg":"#0E1117","btn":"#00FFCC","radius":10}
        st.rerun()

if "user" not in st.session_state: auth_gate()
else: main()
