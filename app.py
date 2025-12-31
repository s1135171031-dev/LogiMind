import streamlit as st
import pandas as pd

# =========================================
# 1. 智慧顏色與 CSS 注入 (解決白底白字)
# =========================================
def get_contrast_color(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    # 亮度計算
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#000000" if luminance > 0.5 else "#FFFFFF"

def apply_theme(p):
    txt = get_contrast_color(p['bg'])
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {p['bg']} !important; }}
    /* 全域文字與標籤顏色鎖定 */
    .stApp, .stApp p, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3 {{
        color: {txt} !important;
    }}
    /* 下拉選單與輸入框強制白底黑字 */
    div[data-baseweb="select"] > div, input {{
        background-color: white !important;
        color: black !important;
    }}
    /* 表格強制保護色：白底黑字，並移除索引欄 */
    div[data-testid="stDataFrame"] *, div[data-testid="stTable"] * {{
        color: black !important;
    }}
    div[data-testid="stTable"], div[data-testid="stDataFrame"] {{
        background-color: white !important;
        border-radius: 8px;
    }}
    /* 按鈕樣式 */
    .stButton>button {{
        background-color: {p['btn']} !important;
        color: white !important;
        border-radius: 10px;
        border: 2px solid {txt};
    }}
    </style>
    """, unsafe_allow_html=True)

# =========================================
# 2. 數據庫定義 (基礎與進階分離)
# =========================================
GATES_BASIC = {
    "AND (及閘)": {"A": [0,0,1,1], "B": [0,1,0,1], "Out": [0,0,0,1]},
    "OR (或閘)": {"A": [0,0,1,1], "B": [0,1,0,1], "Out": [0,1,1,1]},
    "NOT (反閘)": {"Input": [0,1], "Output": [1,0]},
    "NAND (與非閘)": {"A": [0,0,1,1], "B": [0,1,0,1], "Out": [1,1,1,0]},
    "NOR (或非閘)": {"A": [0,0,1,1], "B": [0,1,0,1], "Out": [1,0,0,0]},
    "XOR (互斥或閘)": {"A": [0,0,1,1], "B": [0,1,0,1], "Out": [0,1,1,0]},
    "XNOR (同或閘)": {"A": [0,0,1,1], "B": [0,1,0,1], "Out": [1,0,0,1]}
}

ADV_CIRCUITS = ["Half Adder (半加器)", "Full Adder (全加器)", "Encoder (編碼器)", "Decoder (解碼器)", "MUX (多工器)"]

# =========================================
# 3. 多國語言字典
# =========================================
LANGS = {
    "zh": {
        "menu_h": "🏠 首頁介紹", "menu_b": "🔬 基礎邏輯閘", "menu_a": "🏗️ 進階組合電路", "menu_g": "🔢 格雷碼模組", "menu_s": "🎨 個人化設定",
        "intro_t": "歡迎來到 LogiMind 數位邏輯實驗室",
        "intro_body": """
        本網站是一個專為數位電路學習者設計的互動式平台。我們提供以下核心功能：
        1. **視覺化邏輯閘**：收錄從最基礎的 AND、OR 到 XOR 等七大邏輯閘的詳盡介紹與真值表。
        2. **組合電路分析**：深入探討半加器、全加器、編碼器與解碼器等複雜電路結構。
        3. **格雷碼轉換系統**：提供精確的二進制與格雷碼對照表，並內建即時轉換工具。
        4. **個人化實驗環境**：使用者可以自由調整實驗室的背景顏色、按鈕風格，並支持中英文切換。
        
        無論您是數位電路的新手還是進階開發者，LogiMind 都能協助您將抽象的邏輯概念具象化。
        """,
        "conn_status": "🟢 系統狀態：已成功與伺服器連接",
        "gray_label": "請輸入 4 位二進制 (如 1101)"
    },
    "en": {
        "menu_h": "🏠 Home", "menu_b": "🔬 Basic Gates", "menu_a": "🏗️ Advanced Circuits", "menu_g": "🔢 Gray Code", "menu_s": "🎨 Personalization",
        "intro_t": "Welcome to LogiMind Digital Lab",
        "intro_body": """
        LogiMind is an interactive platform designed for digital logic learners. Key features include:
        1. **Visualized Logic Gates**: Detailed guides and truth tables for AND, OR, XOR, and more.
        2. **Circuit Analysis**: Explore Half Adders, Full Adders, Encoders, and Decoders.
        3. **Gray Code System**: Precise Binary-to-Gray mapping with real-time conversion tools.
        4. **Personalized UI**: Customize your lab background, button themes, and switch between languages.
        
        LogiMind helps bridge the gap between abstract logic and practical application.
        """,
        "conn_status": "🟢 Status: Securely Connected to Server",
        "gray_label": "Input 4-bit Binary (e.g., 1101)"
    }
}

# =========================================
# 4. 主程式架構
# =========================================
if "lang" not in st.session_state: st.session_state.lang = "zh"

def main():
    p = st.session_state.prefs
    apply_theme(p)
    L = LANGS[st.session_state.lang]

    with st.sidebar:
        st.title(f"Hello, {st.session_state.name}")
        st.caption(L["conn_status"])
        page = st.radio("選單 / Menu", [L["menu_h"], L["menu_b"], L["menu_a"], L["menu_g"], L["menu_s"], "🚪 Logout"])

    if page == L["menu_h"]:
        st.header(L["intro_t"])
        st.write(L["intro_body"])
        st.markdown(f"""
        <div style="background:#262730; padding:15px; border-radius:10px; border-left: 5px solid {p['btn']};">
            <b>User Connected:</b> {st.session_state.name}
        </div>
        """, unsafe_allow_html=True)

    elif page == L["menu_b"]:
        st.header(L["menu_b"])
        g_name = st.selectbox("選擇邏輯閘", list(GATES_BASIC.keys()))
        st.subheader("真值表 (Truth Table)")
        # 移除索引
        st.dataframe(pd.DataFrame(GATES_BASIC[g_name]), hide_index=True, use_container_width=True)

    elif page == L["menu_a"]:
        st.header(L["menu_a"])
        comp = st.selectbox("選擇組件", ADV_CIRCUITS)
        st.info(f"正在展示 {comp} 的邏輯結構...")
        st.markdown('<div style="background:white; height:150px; border-radius:10px; display:flex; align-items:center; justify-content:center; color:black;">[電路圖視覺化區域]</div>', unsafe_allow_html=True)

    elif page == L["menu_g"]:
        st.header(L["menu_g"])
        b_in = st.text_input(L["gray_label"], "1010")
        try:
            val = int(b_in, 2)
            gray = bin(val ^ (val >> 1))[2:].zfill(len(b_in))
            st.success(f"轉換結果: {gray}")
        except: pass
        
        st.write("完整對照表 (0-15):")
        gray_data = pd.DataFrame({
            "Dec": range(16),
            "Binary": [bin(i)[2:].zfill(4) for i in range(16)],
            "Gray": [bin(i ^ (i >> 1))[2:].zfill(4) for i in range(16)]
        })
        st.dataframe(gray_data, hide_index=True)

    elif page == L["menu_s"]:
        st.header(L["menu_s"])
        if st.button("切換語言 / Switch Language"):
            st.session_state.lang = "en" if st.session_state.lang == "zh" else "zh"
            st.rerun()
        st.session_state.prefs['bg'] = st.color_picker("背景顏色", p['bg'])
        st.session_state.prefs['btn'] = st.color_picker("主題按鈕顏色", p['btn'])
        if st.button("儲存套用"): st.rerun()

    elif page == "🚪 Logout":
        st.session_state.clear(); st.rerun()

def auth():
    apply_theme({"bg":"#0E1117","btn":"#00FFCC"})
    st.title("🧪 LogiMind 實驗室登入")
    name = st.text_input("請輸入姓名")
    if st.button("進入網站"):
        st.session_state.user = name; st.session_state.name = name
        st.session_state.prefs = {"bg":"#0E1117","btn":"#00FFCC"}
        st.rerun()

if "user" not in st.session_state: auth()
else: main()
