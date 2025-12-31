import streamlit as st
import pandas as pd

# =========================================
# 1. 視覺引擎：深度文字對比與表格優化
# =========================================
def apply_theme(p):
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {p['bg']} !important; }}
    /* 強制文字顯形：解決白底白字 */
    h1, h2, h3, h4, p, span, label {{ color: white !important; }}
    
    /* 下拉選單與輸入框鎖定：淺灰底黑字 */
    div[data-baseweb="select"] > div, input {{
        background-color: #F0F2F6 !important;
        color: #000000 !important;
    }}
    div[data-baseweb="select"] * {{ color: #000000 !important; }}

    /* 表格樣式：移除索引、強制白底黑字 */
    div[data-testid="stDataFrame"] *, div[data-testid="stTable"] * {{
        color: black !important;
    }}
    div[data-testid="stTable"], div[data-testid="stDataFrame"] {{
        background-color: white !important;
        border-radius: 12px;
        padding: 10px;
    }}
    
    .stButton>button {{
        background-color: {p['btn']} !important;
        color: white !important;
        border-radius: 8px;
    }}
    </style>
    """, unsafe_allow_html=True)

# =========================================
# 2. 轉換邏輯：二進制 ↔ 格雷碼
# =========================================
def b_to_g(b_str):
    try:
        n = int(b_str, 2)
        return bin(n ^ (n >> 1))[2:].zfill(len(b_str))
    except: return "格式錯誤"

def g_to_b(g_str):
    try:
        res = g_str[0]
        for i in range(1, len(g_str)):
            res += str(int(res[-1]) ^ int(g_str[i]))
        return res
    except: return "格式錯誤"

# =========================================
# 3. 主頁面內容
# =========================================
if "lang" not in st.session_state: st.session_state.lang = "zh"

def main():
    p = st.session_state.prefs
    apply_theme(p)
    
    with st.sidebar:
        st.title("LogiMind V37")
        st.write(f"📡 伺服器：frank's Lab Core")
        page = st.radio("城市導航", ["🏠 城市願景 (Home)", "🔬 邏輯視覺館", "🏗️ 組合建築區", "🔄 數據翻譯站", "🎨 規劃室"])
        st.divider()
        st.caption(f"當前登入者：{st.session_state.name}")

    # --- 1. 首頁：豐富描述 ---
    if page == "🏠 城市願景 (Home)":
        st.header("歡迎來到 LogiMind：數位邏輯之城")
        st.write("""
        這是一座建立在 **0 與 1** 基石上的數位都市。在這裡，邏輯不只是數學公式，而是維持城市運作的電力與血管。
        
        **🏛️ 我們的城市結構：**
        1. **邏輯視覺館**：展示城市最基礎的單元——邏輯閘。在這裡你可以看到 AND, OR 等組件的符號與真值運算。
        2. **組合建築區**：展示如何將簡單的邏輯閘搭建成複雜的「建築」。包含能夠處理加法的『加法器』與分配訊號的『解碼器』。
        3. **數據翻譯站**：負責處理二進制與格雷碼（Gray Code）的雙向互補轉換，確保數據在流動時不會產生錯誤。
        4. **城市規劃室**：你可以自由更改這座城市的視覺風格與語言，打造專屬於你的實驗環境。
        
        這座城市旨在讓每一位管理員（使用者）都能透過互動，直觀地感受數位邏輯的嚴謹與美感。
        """)
        st.success(f"管理員 {st.session_state.name}，系統已就緒。")

    # --- 2. 邏輯閘視覺化 ---
    elif page == "🔬 邏輯視覺館":
        st.header("🔬 基礎邏輯閘外觀與特性")
        gate = st.selectbox("選擇要查看的組件", ["AND (及閘)", "OR (或閘)", "NOT (反閘)", "XOR (互斥或閘)", "NAND (與非閘)"])
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("視覺符號描述")
            if "AND" in gate:
                st.info("外觀：像一個橫放的 D 字型。兩個輸入 A, B，一個輸出 Out。")
            elif "OR" in gate:
                st.info("外觀：像一個尖銳的火箭前端或月牙形。")
            elif "NOT" in gate:
                st.info("外觀：一個三角形右尖端帶有一個小圓圈（代表反相）。")
                
        with col2:
            st.subheader("真值表")
            data = {"AND": {"A":[0,0,1,1],"B":[0,1,0,1],"Y":[0,0,0,1]}, "OR": {"A":[0,0,1,1],"B":[0,1,0,1],"Y":[0,1,1,1]}}
            key = gate.split(" ")[0]
            if key in data: st.table(pd.DataFrame(data[key]))
            else: st.write("數據加載中...")

    # --- 3. 組合電路 (修復並增加內容) ---
    elif page == "🏗️ 組合建築區":
        st.header("🏗️ 組合邏輯建築")
        adv = st.selectbox("選擇進階結構", ["全加器 (Full Adder)", "2-to-4 解碼器", "多工器 (MUX)"])
        
        if "全加器" in adv:
            st.subheader("全加器 (Full Adder) 結構")
            st.write("這是計算機算術單元的核心。它由兩個 XOR、兩個 AND 與一個 OR 閘組成。")
            st.latex(r"Sum = A \oplus B \oplus C_{in}")
            st.latex(r"C_{out} = (A \cdot B) + (C_{in} \cdot (A \oplus B))")
        elif "解碼器" in adv:
            st.subheader("解碼器 (Decoder) 邏輯")
            st.write("用於將編碼後的訊號解開為多個獨立路徑。")
            st.table(pd.DataFrame({"A":[0,0,1,1],"B":[0,1,0,1],"Y0":[1,0,0,0],"Y1":[0,1,0,0],"Y2":[0,0,1,0],"Y3":[0,0,0,1]}))

    # --- 4. 數據雙向轉換 ---
    elif page == "🔄 數據翻譯站":
        st.header("🔢 二進制 ↔ 格雷碼 互補轉換")
        mode = st.radio("轉換方向", ["Binary → Gray", "Gray → Binary"])
        val = st.text_input("輸入 0/1 字串 (如 1011)", "1011")
        
        if mode == "Binary → Gray":
            st.success(f"轉換後的格雷碼為：{b_to_g(val)}")
        else:
            st.success(f"轉換後的二進制為：{g_to_b(val)}")
            
        st.divider()
        st.write("4-bit 完整對照表：")
        df_all = pd.DataFrame({
            "Bin": [bin(i)[2:].zfill(4) for i in range(16)],
            "Gray": [bin(i ^ (i >> 1))[2:].zfill(4) for i in range(16)]
        })
        st.dataframe(df_all, hide_index=True)

    # --- 5. 規劃室 ---
    elif page == "🎨 規劃室":
        st.header("🎨 城市規劃設定")
        if st.button("切換語言 (English / 中文)"):
            st.session_state.lang = "en" if st.session_state.lang == "zh" else "zh"
            st.rerun()
        st.session_state.prefs['bg'] = st.color_picker("城市背景色", p['bg'])
        st.session_state.prefs['btn'] = st.color_picker("按鈕主題色", p['btn'])
        if st.button("儲存規劃"): st.rerun()

def auth():
    apply_theme({"bg":"#0E1117","btn":"#00FFCC"})
    st.title("🛡️ LogiMind 登入中心")
    n = st.text_input("請輸入實驗管理員姓名")
    if st.button("啟動城市系統"):
        st.session_state.name = n; st.session_state.prefs = {"bg":"#0E1117","btn":"#00FFCC"}
        st.rerun()

if "name" not in st.session_state: auth()
else: main()
