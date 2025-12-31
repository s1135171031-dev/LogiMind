import streamlit as st
import pandas as pd

# =========================================
# 1. 終極 CSS 注入 (專治下拉選單白底白字)
# =========================================
def get_contrast_color(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#000000" if lum > 0.5 else "#FFFFFF"

def apply_theme(p):
    txt = get_contrast_color(p['bg'])
    st.markdown(f"""
    <style>
    /* 全域背景 */
    .stApp {{ background-color: {p['bg']} !important; }}
    
    /* 強制所有文字顏色 (包含標籤與段落) */
    .stApp, .stApp p, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3 {{
        color: {txt} !important;
    }}

    /* 終極修復：下拉選單 (Selectbox) 內部文字 */
    div[data-baseweb="select"] > div {{
        background-color: white !important;
        color: black !important;
    }}
    div[data-baseweb="select"] span {{
        color: black !important;
    }}
    /* 下拉選單展開後的選項顏色 */
    ul[role="listbox"] li {{
        color: black !important;
        background-color: white !important;
    }}

    /* 表格樣式：移除索引並強制黑字 */
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
        border: 2px solid {txt} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# =========================================
# 2. 完整邏輯數據 (7大閘 + 16位格雷碼)
# =========================================
GATES_DATA = {
    "AND (及閘)": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,0,0,1]},
    "OR (或閘)": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,1,1,1]},
    "NOT (反閘)": {"In":[0,1],"Out":[1,0]},
    "NAND (與非閘)": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[1,1,1,0]},
    "NOR (或非閘)": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[1,0,0,0]},
    "XOR (互斥或閘)": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,1,1,0]},
    "XNOR (同或閘)": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[1,0,0,1]}
}

GRAY_FULL = pd.DataFrame({
    "十進制": range(16),
    "二進制": [bin(i)[2:].zfill(4) for i in range(16)],
    "格雷碼": [bin(i ^ (i >> 1))[2:].zfill(4) for i in range(16)]
})

# =========================================
# 3. 語言字典
# =========================================
LANGS = {
    "zh": {
        "h": "🏠 城市介紹", "b": "🔬 邏輯閘大會堂", "a": "🏗️ 組合電路城區", "g": "🔢 格雷碼廣場", "s": "🎨 個人化工作室",
        "intro_t": "歡迎來到 LogiMind 數位城市",
        "intro_c": "我們的城市致力於將數位邏輯實體化。在這裡，每一道電路都是城市的街道，每一個邏輯閘都是運作的基石。我們正在建立一個自動化、透明且可互動的邏輯教學體系。",
        "lang_btn": "切換為 English"
    },
    "en": {
        "h": "🏠 City Intro", "b": "🔬 Logic Hall", "a": "🏗️ Circuit District", "g": "🔢 Gray Square", "s": "🎨 Studio",
        "intro_t": "Welcome to LogiMind Digital City",
        "intro_c": "Our city is dedicated to embodying digital logic. Here, every circuit is a street and every gate is a foundation. We are building an automated and interactive logic ecosystem.",
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
        st.title("LogiMind V35")
        page = st.radio("導航", [L['h'], L['b'], L['a'], L['g'], L['s'], "🚪 Logout"])
        st.write("---")
        st.caption(f"Connected User: {st.session_state.name}")

    if page == L['h']:
        st.header(L['intro_t'])
        st.write(L['intro_c'])
        # 增加一些「城市進度」的感覺
        st.success("🏗️ 當前建設進度：基礎邏輯閘區 (100%) | 進階組合區 (85%)")

    elif page == L['b']:
        st.header("🔬 邏輯閘大會堂")
        g_name = st.selectbox("請選擇邏輯閘 (這應該是黑色的字！)", list(GATES_DATA.keys()))
        st.subheader(f"{g_name} 真值表")
        # 隱藏索引
        st.table(pd.DataFrame(GATES_DATA[g_name]))

    elif page == L['a']:
        st.header("🏗️ 組合電路城區")
        adv = st.selectbox("選擇建築結構", ["全加器", "半加器", "編碼器", "解碼器", "多工器"])
        st.write(f"正在分析 {adv} 的邏輯流向...")

    elif page == L['g']:
        st.header("🔢 格雷碼廣場")
        st.write("完整 4-bit 對照表 (0-15)：")
        st.dataframe(GRAY_FULL, hide_index=True)

    elif page == L['s']:
        st.header(L['s'])
        # 語言切換按鈕放在這裡
        if st.button(L['lang_btn']):
            st.session_state.lang = "en" if st.session_state.lang == "zh" else "zh"
            st.rerun()
        st.divider()
        st.session_state.prefs['bg'] = st.color_picker("背景色", p['bg'])
        st.session_state.prefs['btn'] = st.color_picker("按鈕色", p['btn'])
        if st.button("確認修改"): st.rerun()

    elif page == "🚪 Logout":
        st.session_state.clear(); st.rerun()

def auth():
    apply_theme({"bg":"#0E1117","btn":"#00FFCC"})
    st.title("🧪 進入 LogiMind 城市")
    u = st.text_input("實驗員姓名")
    if st.button("登入"):
        st.session_state.user = u; st.session_state.name = u
        st.session_state.prefs = {"bg":"#0E1117","btn":"#00FFCC"}
        st.rerun()

if "user" not in st.session_state: auth()
else: main()
