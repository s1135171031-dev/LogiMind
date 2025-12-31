import streamlit as st
import pandas as pd

# =========================================
# 1. 視覺引擎：深度鎖定文字顏色
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
    
    /* 強制所有標準文字、標籤與標題顏色 */
    .stApp, .stApp p, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4 {{
        color: {txt} !important;
    }}

    /* 修復下拉選單 (Selectbox) 與輸入框的白底白字 */
    div[data-baseweb="select"] > div {{
        background-color: #F0F2F6 !important; /* 固定淺灰底 */
        color: #000000 !important; /* 固定黑字 */
    }}
    div[data-baseweb="select"] * {{
        color: #000000 !important;
    }}
    input {{
        background-color: #F0F2F6 !important;
        color: #000000 !important;
    }}

    /* 表格：強制白底黑字以確保數據可讀性 */
    div[data-testid="stDataFrame"] *, div[data-testid="stTable"] * {{
        color: #000000 !important;
    }}
    div[data-testid="stTable"], div[data-testid="stDataFrame"] {{
        background-color: #FFFFFF !important;
        border-radius: 10px;
        padding: 5px;
    }}

    /* 按鈕樣式 */
    .stButton>button {{
        background-color: {p['btn']} !important;
        color: white !important;
        border: 2px solid {txt} !important;
        font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

# =========================================
# 2. 邏輯運算核心
# =========================================
def bin_to_gray(n_str):
    n = int(n_str, 2)
    return bin(n ^ (n >> 1))[2:].zfill(len(n_str))

def gray_to_bin(g_str):
    res = g_str[0]
    for i in range(1, len(g_str)):
        res += str(int(res[-1]) ^ int(g_str[i]))
    return res

# =========================================
# 3. 頁面內容：首頁、組合電路、格雷碼
# =========================================
LANGS = {
    "zh": {
        "h": "🏠 城市願景中心", "b": "🔬 基礎邏輯門戶", "a": "🏗️ 組合電路特區", "g": "🔢 數據轉換中心", "s": "🎨 城市規劃室",
        "intro_t": "歡迎來到 LogiMind：數位邏輯之城",
        "intro_c": """
        這是一座由布林代數支撐的現代化都市。在這裡，每一道邏輯閘（Logic Gate）都是城市的十字路口，引導著訊號的流向；
        每一條二進制電路都是城市的地下動脈，輸送著運算的生命力。
        
        **城市分區說明：**
        - **基礎邏輯門戶**：探訪 0 與 1 的起源，掌握七大基礎邏輯閘的真理。
        - **組合電路特區**：由數個邏輯閘搭建而成的宏偉建築，如加法器與編碼器，體現了複雜運算的結構美。
        - **數據轉換中心**：這裡是城市與外界溝通的翻譯館，處理格雷碼與二進制的精密轉換。
        
        我們邀請您一同參與這座邏輯城市的建設，將抽象的邏輯化為具體的實踐。
        """,
        "lang_btn": "Switch to English"
    },
    "en": {
        "h": "🏠 City Vision", "b": "🔬 Gate Portal", "a": "🏗️ Circuit District", "g": "🔢 Conversion Center", "s": "🎨 Studio",
        "intro_t": "Welcome to LogiMind: The City of Logic",
        "intro_c": "A city powered by Boolean logic. Every gate is a crossroad, every circuit is a pulse...",
        "lang_btn": "切換為 中文"
    }
}

# =========================================
# 4. 主程式流程
# =========================================
if "lang" not in st.session_state: st.session_state.lang = "zh"

def main():
    p = st.session_state.prefs
    apply_theme(p)
    L = LANGS[st.session_state.lang]

    with st.sidebar:
        st.title("LogiMind V36")
        page = st.radio("導航導覽", [L['h'], L['b'], L['a'], L['g'], L['s'], "🚪 Logout"])
        st.write("---")
        st.caption(f"實驗員: {st.session_state.name}")

    # --- 首頁 ---
    if page == L['h']:
        st.header(L['intro_t'])
        st.write(L['intro_c'])
        st.divider()
        st.info("💡 提示：您可以前往『城市規劃室』自定義城市色調。")

    # --- 基礎邏輯閘 ---
    elif page == L['b']:
        st.header("🔬 基礎邏輯門戶")
        gates = {
            "AND": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,0,0,1]},
            "OR": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,1,1,1]},
            "NOT": {"Input":[0,1],"Output":[1,0]},
            "XOR": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,1,1,0]}
        }
        choice = st.selectbox("選擇要查看的邏輯閘", list(gates.keys()))
        st.subheader(f"{choice} 真值表")
        st.table(pd.DataFrame(gates[choice]))

    # --- 組合電路 (修復顯示問題) ---
    elif page == L['a']:
        st.header("🏗️ 組合電路特區")
        adv_choice = st.selectbox("選擇進階組合建築", ["半加器 (Half Adder)", "全加器 (Full Adder)", "2對4解碼器 (Decoder)"])
        
        if "半加器" in adv_choice:
            st.subheader("半加器邏輯分析")
            st.code("Sum = A ⊕ B\nCarry = A ⋅ B", language='python')
            df = pd.DataFrame({"A":[0,0,1,1],"B":[0,1,0,1],"Sum":[0,1,1,0],"Carry":[0,0,0,1]})
            st.table(df)
        elif "全加器" in adv_choice:
            st.subheader("全加器邏輯分析")
            st.code("Sum = A ⊕ B ⊕ Cin\nCout = (A⋅B) + (Cin⋅(A⊕B))", language='python')
            st.write("全加器包含三個輸入，是構成電腦加法運算的基礎單元。")
        elif "解碼器" in adv_choice:
            st.subheader("2-to-4 Decoder 真值表")
            df = pd.DataFrame({
                "A":[0,0,1,1], "B":[0,1,0,1],
                "Y0":[1,0,0,0], "Y1":[0,1,0,0], "Y2":[0,0,1,0], "Y3":[0,0,0,1]
            })
            st.table(df)

    # --- 格雷碼雙向轉換 (新增功能) ---
    elif page == L['g']:
        st.header("🔢 數據轉換中心")
        tab1, tab2 = st.tabs(["⚡ 雙向轉換器", "📊 4-bit 對照表"])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                bin_input = st.text_input("二進制轉格雷碼 (輸入 0/1)", "1010")
                if bin_input:
                    st.success(f"格雷碼輸出: {bin_to_gray(bin_input)}")
            with col2:
                gray_input = st.text_input("格雷碼轉二進制 (輸入 0/1)", "1111")
                if gray_input:
                    st.success(f"二進制輸出: {gray_to_bin(gray_input)}")
        
        with tab2:
            df_g = pd.DataFrame({
                "Dec": range(16),
                "Binary": [bin(i)[2:].zfill(4) for i in range(16)],
                "Gray": [bin(i ^ (i >> 1))[2:].zfill(4) for i in range(16)]
            })
            st.dataframe(df_g, hide_index=True)

    # --- 個人化設定 ---
    elif page == L['s']:
        st.header("🎨 城市規劃室")
        if st.button(L['lang_btn']):
            st.session_state.lang = "en" if st.session_state.lang == "zh" else "zh"
            st.rerun()
        st.divider()
        st.session_state.prefs['bg'] = st.color_picker("更改城市背景色", p['bg'])
        st.session_state.prefs['btn'] = st.color_picker("設定按鈕主題色", p['btn'])
        if st.button("套用城市規劃"): st.rerun()

    elif page == "🚪 Logout":
        st.session_state.clear(); st.rerun()

def auth():
    apply_theme({"bg":"#0E1117","btn":"#00FFCC"})
    st.title("🛡️ 進入 LogiMind 邏輯之城")
    u = st.text_input("您的管理員姓名")
    if st.button("啟動城市系統"):
        st.session_state.user = u; st.session_state.name = u
        st.session_state.prefs = {"bg":"#0E1117","btn":"#00FFCC"}
        st.rerun()

if "user" not in st.session_state: auth()
else: main()
