import streamlit as st
import pandas as pd

# =========================================
# 1. 核心視覺引擎 (確保亮/暗色文字絕對對比)
# =========================================
def get_contrast_color(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    # 根據亮度公式判斷背景是亮色還是暗色
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#000000" if luminance > 0.5 else "#FFFFFF"

def apply_theme(p):
    txt = get_contrast_color(p['bg'])
    st.markdown(f"""
    <style>
    /* 全域背景與文字強制染色 */
    .stApp {{ background-color: {p['bg']} !important; }}
    * {{ color: {txt} !important; }}
    
    /* 側邊欄特殊處理 */
    [data-testid="stSidebar"] {{ background-color: rgba(255,255,255,0.05) !important; }}
    [data-testid="stSidebar"] * {{ color: {txt} !important; }}

    /* 下拉選單與輸入框：維持白底黑字以保證輸入可見度 */
    div[data-baseweb="select"] > div, input {{
        background-color: white !important;
        color: black !important;
    }}
    div[data-baseweb="popover"] * {{ color: black !important; }}
    
    /* 表格專屬樣式：強制黑字並移除索引外觀 */
    div[data-testid="stDataFrame"] *, div[data-testid="stTable"] * {{
        color: black !important;
        font-family: 'Courier New', monospace;
    }}
    div[data-testid="stTable"], div[data-testid="stDataFrame"] {{
        background-color: white !important;
        border-radius: 12px;
        padding: 5px;
    }}

    /* 按鈕樣式優化 */
    .stButton>button {{
        background-color: {p['btn']} !important;
        color: white !important;
        border-radius: 8px !important;
        border: 2px solid {txt} !important;
        font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

# =========================================
# 2. 邏輯數據定義
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

# =========================================
# 3. 語系與更新資訊
# =========================================
LANGS = {
    "zh": {
        "menu_h": "🏠 首頁與更新", "menu_b": "🔬 基礎邏輯閘", "menu_a": "🏗️ 進階組合電路", "menu_g": "🔢 格雷碼模組", "menu_s": "🎨 個人化設定",
        "intro_t": "歡迎來到 LogiMind 數位邏輯實驗室",
        "intro_body": "本平台旨在將抽象的數位電路理論轉化為具體的互動體驗，協助學習者掌握布林代數與組合邏輯的核心。",
        "update_t": "🚀 最新功能與更新 (V33)",
        "updates": [
            "新增：基礎與進階電路分類選單",
            "新增：4位元格雷碼完整對照表 (0-15)",
            "優化：表格索引自動隱藏，介面更乾淨",
            "修正：亮色背景下的文字對比度問題",
            "新增：即時二進制轉格雷碼計算器"
        ],
        "conn": "✅ 伺服器狀態：真實連接至 Cloud Node",
        "lang_btn": "切換為 English"
    },
    "en": {
        "menu_h": "🏠 Home & Updates", "menu_b": "🔬 Basic Gates", "menu_a": "🏗️ Advanced Circuits", "menu_g": "🔢 Gray Code", "menu_s": "🎨 Personalization",
        "intro_t": "Welcome to LogiMind Lab",
        "intro_body": "Interactive platform designed to visualize Boolean logic and circuit theory.",
        "update_t": "🚀 New Features & Logs (V33)",
        "updates": [
            "Added: Separated Basic and Advanced circuit modules",
            "Added: Full 4-bit Gray code table (0-15)",
            "Opt: Auto-hide table index for cleaner UI",
            "Fix: Improved text contrast on light themes",
            "Added: Real-time Binary-to-Gray converter"
        ],
        "conn": "✅ Status: Connected to Cloud Node",
        "lang_btn": "Switch to 中文"
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
        st.title("LogiMind V33")
        st.caption(L["conn"])
        page = st.radio("導覽", [L["menu_h"], L["menu_b"], L["menu_a"], L["menu_g"], L["menu_s"], "🚪 Logout"])
        st.markdown("---")
        st.write(f"Logged as: **{st.session_state.name}**")

    if page == L["menu_h"]:
        st.header(L["intro_t"])
        st.write(L["intro_body"])
        
        # 更新日誌區塊
        st.subheader(L["update_t"])
        for update in L["updates"]:
            st.write(f"• {update}")
            
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.1); padding:20px; border-radius:15px; border: 2px solid {p['btn']}; margin-top:20px;">
            <h4 style="margin:0;">User Connected: {st.session_state.name}</h4>
            <p style="margin:0; opacity:0.8;">Session Active: Real-time Tracking Enabled</p>
        </div>
        """, unsafe_allow_html=True)

    elif page == L["menu_b"]:
        st.header(L["menu_b"])
        g_name = st.selectbox("選擇邏輯閘", list(GATES_BASIC.keys()))
        st.subheader("真值表 (Truth Table)")
        st.dataframe(pd.DataFrame(GATES_BASIC[g_name]), hide_index=True, use_container_width=True)

    elif page == L["menu_a"]:
        st.header(L["menu_a"])
        comp = st.selectbox("選擇組合電路", ["半加器 (Half Adder)", "全加器 (Full Adder)", "編碼器 (Encoder)", "解碼器 (Decoder)", "多工器 (MUX)"])
        st.markdown(f'''<div style="background:white; padding:40px; border-radius:12px; border:4px solid {p['btn']}; text-align:center;">
            <h2 style="color:black !important;">{comp}</h2>
            <p style="color:gray !important;">Logic Circuit Analysis Module</p>
        </div>''', unsafe_allow_html=True)

    elif page == L["menu_g"]:
        st.header(L["menu_g"])
        b_in = st.text_input("輸入二進制 (Input Binary)", "1100")
        try:
            val = int(b_in, 2)
            res = bin(val ^ (val >> 1))[2:].zfill(len(b_in))
            st.success(f"格雷碼輸出 (Gray Code): {res}")
        except: pass
        
        st.write("4-bit 完整對照表 (0-15):")
        gray_df = pd.DataFrame({
            "Dec": range(16),
            "Binary": [bin(i)[2:].zfill(4) for i in range(16)],
            "Gray": [bin(i ^ (i >> 1))[2:].zfill(4) for i in range(16)]
        })
        st.dataframe(gray_df, hide_index=True)

    elif page == L["menu_s"]:
        st.header(L["menu_s"])
        if st.button(L["lang_btn"]):
            st.session_state.lang = "en" if st.session_state.lang == "zh" else "zh"
            st.rerun()
        col1, col2 = st.columns(2)
        with col1: st.session_state.prefs['bg'] = st.color_picker("背景顏色", p['bg'])
        with col2: st.session_state.prefs['btn'] = st.color_picker("按鈕主題色", p['btn'])
        if st.button("套用並存檔"): st.rerun()

    elif page == "🚪 Logout":
        st.session_state.clear(); st.rerun()

def auth():
    apply_theme({"bg":"#0E1117","btn":"#00FFCC"})
    st.title("🛡️ LogiMind 登入")
    name = st.text_input("實驗員姓名")
    if st.button("進入實驗室"):
        st.session_state.user = name; st.session_state.name = name
        st.session_state.prefs = {"bg":"#0E1117","btn":"#00FFCC"}
        st.rerun()

if "user" not in st.session_state: auth()
else: main()
