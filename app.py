import streamlit as st
import pandas as pd

# =========================================
# 1. 視覺核心：強制對比色引擎
# =========================================
def get_contrast_color(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    # 亮度 (Luminance) 計算
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#000000" if lum > 0.5 else "#FFFFFF"

def apply_theme(p):
    txt = get_contrast_color(p['bg'])
    # 極度強制的 CSS 覆蓋
    st.markdown(f"""
    <style>
    /* 全域背景 */
    .stApp {{ background-color: {p['bg']} !important; }}
    
    /* 強制文字顏色：針對所有標籤、段落、Span 與標題 */
    * {{ color: {txt} !important; }}
    
    /* 側邊欄文字保護 */
    [data-testid="stSidebar"] *, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {{ 
        color: {txt} !important; 
    }}
    
    /* 表格專區：強制白底黑字，確保看得到數據 */
    div[data-testid="stDataFrame"] *, div[data-testid="stTable"] * {{ 
        color: black !important; 
    }}
    div[data-testid="stTable"], div[data-testid="stDataFrame"] {{ 
        background-color: white !important; 
        border-radius: 10px; 
        padding: 10px;
    }}
    
    /* 輸入框與下拉選單：維持清晰外觀 */
    div[data-baseweb="select"] > div, input {{ 
        background-color: white !important; 
        color: black !important; 
    }}
    
    /* 按鈕樣式 */
    .stButton>button {{
        background-color: {p['btn']} !important; 
        color: white !important;
        border: 2px solid {txt} !important;
        border-radius: 8px;
    }}
    </style>
    """, unsafe_allow_html=True)

# =========================================
# 2. 數據與模擬器邏輯
# =========================================
# 邏輯閘名稱：永遠維持雙語格式
GATES_DB = {
    "AND (及閘)": {"logic": lambda a, b: a & b, "table": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,0,0,1]}},
    "OR (或閘)": {"logic": lambda a, b: a | b, "table": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,1,1,1]}},
    "XOR (互斥或閘)": {"logic": lambda a, b: a ^ b, "table": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,1,1,0]}},
    "NAND (與非閘)": {"logic": lambda a, b: 1 if not (a & b) else 0, "table": {"A":[0,0,1,1],"B":[0,1,0,1],"Out":[1,1,1,0]}},
    "NOT (反閘)": {"logic": lambda a: 1 - a, "table": {"In":[0,1],"Out":[1,0]}}
}

# =========================================
# 3. 語言與翻譯字典
# =========================================
LANGS = {
    "zh": {
        "h": "🏠 首頁介紹", "b": "🔬 基礎邏輯模擬", "a": "🏗️ 進階電路計算", "g": "🔢 格雷碼模組", "s": "🎨 個人化設定",
        "intro_t": "關於 LogiMind 數位實驗室",
        "intro_c": """
        本系統致力於簡化數位邏輯的學習門檻：
        - **基礎模擬**：提供及、或、互斥等七大閘級實驗。
        - **進階電路**：包含加法器、編碼器、多工器等組合邏輯。
        - **轉換工具**：內建 Binary 與 Gray Code 雙向對照與計算。
        - **動態 UI**：支援亮度感應配色與多國語系。
        """,
        "conn": "🟢 連接狀態：已連線至 frank's 實驗中心",
        "update_log": "V34 更新：修復白底白字、新增邏輯模擬器、移除表格索引"
    },
    "en": {
        "h": "🏠 Home", "b": "🔬 Basic Gates", "a": "🏗️ Advanced Circuits", "g": "🔢 Gray Code", "s": "🎨 Personalization",
        "intro_t": "About LogiMind Lab",
        "intro_c": """
        Simplifying digital logic learning:
        - **Basic Gates**: Simulators for AND, OR, XOR, etc.
        - **Advanced Circuits**: Adders, Encoders, and Mux analysis.
        - **Tools**: Binary and Gray code conversion.
        - **Dynamic UI**: Contrast-aware themes and dual languages.
        """,
        "conn": "🟢 Status: Connected to frank's Core",
        "update_log": "V34: Fixed contrast issues, added Simulators, hidden table index"
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
        st.title("LogiMind V34")
        st.write(L['conn'])
        page = st.radio("導航選單", [L['h'], L['b'], L['a'], L['g'], L['s'], "🚪 Logout"])
        st.markdown("---")
        st.write(f"Connected as: **{st.session_state.name}**")

    if page == L['h']:
        st.header(L['intro_t'])
        st.write(L['intro_c'])
        st.info(L['update_log'])
        st.markdown(f'<div style="background:{p["btn"]}; padding:10px; border-radius:5px; color:white !important;">User: {st.session_state.name} 連線成功</div>', unsafe_allow_html=True)

    elif page == L['b']:
        st.header(L['b'])
        g_name = st.selectbox("選擇要模擬的邏輯閘", list(GATES_DB.keys()))
        
        # 互動模擬器功能
        st.subheader("💡 即時模擬測試")
        col1, col2 = st.columns(2)
        if "NOT" in g_name:
            in_a = col1.radio("Input", [0, 1])
            res = GATES_DB[g_name]["logic"](in_a)
            st.success(f"Output: {res}")
        else:
            in_a = col1.radio("Input A", [0, 1])
            in_b = col2.radio("Input B", [0, 1])
            res = GATES_DB[g_name]["logic"](in_a, in_b)
            st.success(f"Output: {res}")
            
        st.subheader("📊 真值表 (已隱除索引)")
        st.dataframe(pd.DataFrame(GATES_DB[g_name]["table"]), hide_index=True)

    elif page == L['a']:
        st.header(L['a'])
        mode = st.selectbox("選擇進階電路", ["半加器 (Half Adder)", "全加器 (Full Adder)", "編碼器 (Encoder)", "解碼器 (Decoder)", "多工器 (MUX)"])
        
        # 加法器模擬功能
        if "Adder" in mode:
            st.subheader(f"{mode} 即時運算")
            a = st.slider("Input A", 0, 1)
            b = st.slider("Input B", 0, 1)
            if "Full" in mode:
                cin = st.slider("Carry In (Cin)", 0, 1)
                sum_res = a ^ b ^ cin
                cout = (a & b) | (cin & (a ^ b))
                st.code(f"Sum = {sum_res}, Carry Out = {cout}")
            else:
                st.code(f"Sum = {a ^ b}, Carry = {a & b}")

    elif page == L['g']:
        st.header(L['g'])
        st.write("4-bit 完整格雷碼對照表 (0-15):")
        gray_data = pd.DataFrame({
            "Decimal": range(16),
            "Binary": [bin(i)[2:].zfill(4) for i in range(16)],
            "Gray": [bin(i ^ (i >> 1))[2:].zfill(4) for i in range(16)]
        })
        st.dataframe(gray_data, hide_index=True)

    elif page == L['s']:
        st.header(L['s'])
        if st.button("切換語言 (Switch Language)"):
            st.session_state.lang = "en" if st.session_state.lang == "zh" else "zh"
            st.rerun()
        st.session_state.prefs['bg'] = st.color_picker("實驗室背景顏色", p['bg'])
        st.session_state.prefs['btn'] = st.color_picker("按鈕強調色", p['btn'])
        if st.button("套用設定"): st.rerun()

    elif page == "🚪 Logout":
        st.session_state.clear(); st.rerun()

def auth():
    apply_theme({"bg":"#0E1117","btn":"#00FFCC"})
    st.title("🧪 LogiMind 數位邏輯中心")
    name = st.text_input("輸入實驗員姓名")
    if st.button("啟動系統"):
        st.session_state.user = name; st.session_state.name = name
        st.session_state.prefs = {"bg":"#0E1117","btn":"#00FFCC"}
        st.rerun()

if "user" not in st.session_state: auth()
else: main()
