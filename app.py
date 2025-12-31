import streamlit as st
import pandas as pd
import random

# =========================================
# 1. 視覺引擎：深度鎖定配色 (解決白底白字)
# =========================================
def apply_theme(p):
    # 自動判定背景深淺，切換主文字顏色
    txt_color = "#000000" if (int(p['bg'].lstrip('#'), 16) > 0x888888) else "#FFFFFF"
    
    st.markdown(f"""
    <style>
    /* 全域背景 */
    .stApp {{ background-color: {p['bg']} !important; }}
    
    /* 強制所有標準文字與標題顯形 */
    h1, h2, h3, h4, p, span, label {{ color: {txt_color} !important; }}

    /* 終極修復選單與輸入框：固定為淺色背景+黑色字，確保一定看得到 */
    div[data-baseweb="select"] > div, input {{
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid {p['btn']} !important;
    }}
    div[data-baseweb="select"] span, div[role="listbox"] div {{
        color: #000000 !important;
    }}

    /* 表格樣式：移除索引、強制白底黑字 */
    div[data-testid="stDataFrame"] *, div[data-testid="stTable"] * {{
        color: black !important;
    }}
    div[data-testid="stTable"], div[data-testid="stDataFrame"] {{
        background-color: white !important;
        border-radius: 12px;
    }}

    /* 按鈕樣式：極致個人化圓角 */
    .stButton>button {{
        background-color: {p['btn']} !important;
        color: white !important;
        border-radius: 30px !important;
        border: 2px solid {txt_color} !important;
        transition: 0.3s;
    }}
    .stButton>button:hover {{ transform: scale(1.05); }}
    </style>
    """, unsafe_allow_html=True)

# =========================================
# 2. 邏輯核心與數據
# =========================================
GATE_IMGS = {
    "AND": "https://upload.wikimedia.org/wikipedia/commons/6/64/AND_ANSI.svg",
    "OR": "https://upload.wikimedia.org/wikipedia/commons/b/b5/OR_ANSI.svg",
    "NOT": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Not_gate_ansi.svg",
    "XOR": "https://upload.wikimedia.org/wikipedia/commons/0/01/XOR_ANSI.svg",
    "NAND": "https://upload.wikimedia.org/wikipedia/commons/f/f2/NAND_ANSI.svg",
    "Full Adder": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Full-adder.svg"
}

def b_to_g(b): 
    try: return bin(int(b, 2) ^ (int(b, 2) >> 1))[2:].zfill(len(b))
    except: return "Error"

def g_to_b(g):
    try:
        b = g[0]
        for i in range(1, len(g)): b += str(int(b[-1]) ^ int(g[i]))
        return b
    except: return "Error"

# =========================================
# 3. 主介面流程
# =========================================
if "prefs" not in st.session_state:
    st.session_state.prefs = {"bg":"#0E1117","btn":"#FF4B4B", "avatar": "🤖", "status": "Online"}

def main():
    p = st.session_state.prefs
    apply_theme(p)

    with st.sidebar:
        st.title(f"{p['avatar']} {st.session_state.name}")
        st.write(f"狀態: **{p['status']}**")
        st.divider()
        # 網路連接模擬
        st.write("🌐 **核心網路連接**")
        ping = random.randint(10, 40)
        st.caption(f"Server: AWS-Tokyo | Ping: {ping}ms")
        st.progress(100)
        
        page = st.radio("導航中心", ["🏠 城市願景", "🔬 基礎邏輯館", "🏗️ 組合建築區", "🔄 數據轉換站", "🎓 考評中心", "🎨 個人化設定"])
        if st.button("🚪 安全登出"): 
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()

    # --- 1. 首頁：城市願景 ---
    if page == "🏠 城市願景":
        st.header("歡迎來到 LogiMind 數位邏輯之城")
        st.write(f"""
        管理員 **{st.session_state.name}**，這座城市由布林代數驅動。
        
        這是一個極致互動的學習環境。從單個電晶體的開關邏輯，到複雜的算術邏輯單元 (ALU)，
        我們將抽象的電學原理轉化為視覺化的城市建築。
        
        **城市指南：**
        - **基礎邏輯館**：觀察邏輯閘的標準符號與真值對照。
        - **考評中心**：透過實戰測驗檢驗您的邏輯掌握程度。
        - **數據轉換站**：實現二進制與格雷碼的無損溝通。
        """)
        st.image("https://img.icons8.com/clouds/200/smart-city.png", width=150)

    # --- 2. 基礎邏輯閘 (含圖片與真值表) ---
    elif page == "🔬 基礎邏輯館":
        st.header("🔬 基礎邏輯閘與視覺符號")
        g_name = st.selectbox("選擇要研究的邏輯閘", ["AND", "OR", "NOT", "XOR", "NAND"])
        
        col1, col2 = st.columns([1, 1.2])
        with col1:
            st.write(f"### {g_name} Gate 符號")
            st.image(GATE_IMGS[g_name], width=200)
        
        with col2:
            st.write("### 真值表")
            if g_name == "AND": df = pd.DataFrame({"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,0,0,1]})
            elif g_name == "OR": df = pd.DataFrame({"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,1,1,1]})
            elif g_name == "NOT": df = pd.DataFrame({"In":[0,1],"Out":[1,0]})
            else: df = pd.DataFrame({"A":[0,0,1,1],"B":[0,1,0,1],"Out":[1,1,1,0]})
            st.dataframe(df, hide_index=True)

    # --- 3. 組合電路 ---
    elif page == "🏗️ 組合建築區":
        st.header("🏗️ 進階組合電路")
        st.image(GATE_IMGS["Full Adder"], caption="全加器 (Full Adder) 電路圖")
        st.write("全加器能夠處理來自低位的進位，是構成 CPU 運算核心的基石。")

    # --- 4. 數據轉換站 ---
    elif page == "🔄 數據轉換站":
        st.header("🔄 數據雙向轉換器")
        mode = st.radio("轉換類型", ["Binary ➔ Gray", "Gray ➔ Binary"])
        val = st.text_input("輸入 0/1 字串", "1011")
        if mode == "Binary ➔ Gray":
            st.success(f"結果: {b_to_g(val)}")
        else:
            st.info(f"結果: {g_to_b(val)}")

    # --- 5. 考試系統 ---
    elif page == "🎓 考評中心":
        st.header("🎓 數位邏輯檢定測驗")
        q1 = st.radio("1. 哪種邏輯閘在輸入為 (1, 0) 時輸出 1？", ["AND", "OR", "XOR (兩者皆可)"])
        q2 = st.selectbox("2. 格雷碼與二進制的主要差別為何？", ["計算較快", "相鄰數值僅變動一個位元", "沒有差別"])
        
        if st.button("提交考卷"):
            score = 0
            if "兩者皆可" in q1: score += 50
            if "一個位元" in q2: score += 50
            st.write(f"### 測驗得分：{score} / 100")
            if score == 100: st.balloons()

    # --- 6. 個人化設定 ---
    elif page == "🎨 個人化設定":
        st.header("🎨 極致個人化空間")
        st.session_state.name = st.text_input("管理員名稱", st.session_state.name)
        st.session_state.prefs['avatar'] = st.selectbox("更換頭像", ["🤖", "👤", "🌟", "👨‍🔬"])
        st.divider()
        st.session_state.prefs['bg'] = st.color_picker("背景顏色", p['bg'])
        st.session_state.prefs['btn'] = st.color_picker("主題色", p['btn'])
        if st.button("更新設定"): st.rerun()

# --- 登入頁面 ---
if "name" not in st.session_state:
    st.title("🛡️ LogiMind 啟動中心")
    name = st.text_input("請輸入管理員代號")
    if st.button("進入城市"):
        st.session_state.name = name
        st.rerun()
else:
    main()
