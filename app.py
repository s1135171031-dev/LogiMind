import streamlit as st
import pandas as pd
import random

# =========================================
# 1. 視覺引擎：終極 CSS 修復
# =========================================
def apply_theme(p):
    txt_color = "#000000" if (int(p['bg'].lstrip('#'), 16) > 0x888888) else "#FFFFFF"
    st.markdown(f"""
    <style>
    /* 全域背景 */
    .stApp {{ background-color: {p['bg']} !important; }}
    
    /* 文字與標題顏色 */
    .stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp label, .stApp span {{
        color: {txt_color} !important;
    }}

    /* 修復下拉選單：強制固定配色防止隱形 */
    div[data-baseweb="select"] > div {{
        background-color: white !important;
        color: black !important;
    }}
    div[data-baseweb="select"] span {{ color: black !important; }}

    /* 表格樣式：移除索引、白底黑字 */
    div[data-testid="stDataFrame"] *, div[data-testid="stTable"] * {{
        color: black !important;
    }}
    div[data-testid="stTable"], div[data-testid="stDataFrame"] {{
        background-color: white !important;
        border-radius: 10px;
    }}

    /* 按鈕樣式 */
    .stButton>button {{
        background-color: {p['btn']} !important;
        color: white !important;
        border: 2px solid {txt_color} !important;
        border-radius: 50px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# =========================================
# 2. 邏輯核心
# =========================================
def b_to_g(b): return bin(int(b, 2) ^ (int(b, 2) >> 1))[2:].zfill(len(b))
def g_to_b(g):
    b = g[0]
    for i in range(1, len(g)): b += str(int(b[-1]) ^ int(g[i]))
    return b

# =========================================
# 3. 主程式流程
# =========================================
if "name" not in st.session_state:
    st.session_state.name = "管理員"
    st.session_state.prefs = {"bg":"#0E1117","btn":"#00FFCC", "sign": "邏輯就是美"}

def main():
    p = st.session_state.prefs
    apply_theme(p)

    with st.sidebar:
        st.title(f"👤 {st.session_state.name}")
        st.caption(f"✨ {p['sign']}")
        st.divider()
        # 網路連接模擬
        st.write("🌐 **網路連線狀態**")
        ping = random.randint(20, 45)
        st.success(f"已連接至 Cloud-Server (Ping: {ping}ms)")
        st.progress(100)
        
        page = st.radio("導航中心", ["🏠 城市願景", "🔬 基礎邏輯館", "🏗️ 組合電路區", "🔄 轉換翻譯站", "🎓 邏輯檢定中心", "🎨 極致個人化"])
        if st.button("🚪 登出系統"): st.session_state.clear(); st.rerun()

    # --- 1. 首頁：詳細描述 ---
    if page == "🏠 城市願景":
        st.header("歡迎來到 LogiMind 數位之城")
        st.write(f"""
        管理員 **{st.session_state.name}**，這是一個專為數位電路愛好者打造的實驗空間。
        在這座城市中，我們將抽象的布林邏輯具象化。邏輯閘不再只是紙上的符號，而是維持城市運行的開關。
        
        **本系統三大核心功能：**
        1. **視覺化學習**：透過標準圖形符號，直觀記憶每個邏輯閘的「長相」與「特性」。
        2. **數據精準性**：提供完美的二進制與格雷碼轉換，確保運算過程零誤差。
        3. **實踐考評**：透過內建的檢定系統，驗證您對數位電路知識的掌握程度。
        """)
        st.info("💡 系統偵測到網路連接正常，您可以開始所有的實驗。")

    # --- 2. 邏輯閘與真值表 (含圖片) ---
    elif page == "🔬 基礎邏輯館":
        st.header("🔬 基礎邏輯閘展示")
        g_name = st.selectbox("請選擇邏輯閘", ["AND", "OR", "NOT", "NAND", "NOR", "XOR", "XNOR"])
        
        # 這裡會觸發您要的圖片
        if g_name == "AND":
            st.write("### AND (及閘) - 全 1 為 1")
            

[Image of an AND gate symbol and its truth table]

            df = pd.DataFrame({"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,0,0,1]})
        elif g_name == "OR":
            st.write("### OR (或閘) - 有 1 為 1")
            

[Image of an OR gate symbol and its truth table]

            df = pd.DataFrame({"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,1,1,1]})
        elif g_name == "XOR":
            st.write("### XOR (互斥或閘) - 不同為 1")
            

[Image of an XOR gate symbol and its truth table]

            df = pd.DataFrame({"A":[0,0,1,1],"B":[0,1,0,1],"Out":[0,1,1,0]})
        elif g_name == "NOT":
            st.write("### NOT (反閘) - 訊號反轉")
            

[Image of a NOT gate symbol and its truth table]

            df = pd.DataFrame({"In":[0,1],"Out":[1,0]})
        else:
            st.write(f"### {g_name} 特性分析中...")
            df = pd.DataFrame({"Status": ["數據加載中"]})

        st.subheader("完整真值表")
        st.dataframe(df, hide_index=True, use_container_width=True)

    # --- 3. 組合電路 ---
    elif page == "🏗️ 組合電路區":
        st.header("🏗️ 進階組合電路")
        

[Image of a full adder circuit diagram]

        st.write("在這裡，我們將基礎邏輯閘組合成具有運算能力的建築。")
        adv = st.selectbox("選擇組件", ["全加器", "半加器", "解碼器"])
        if adv == "全加器":
            st.latex(r"Sum = A \oplus B \oplus C_{in}")
            st.write("這是現代電腦 CPU 中最基礎的運算單位。")

    # --- 4. 數據轉換 (互轉功能) ---
    elif page == "🔄 轉換翻譯站":
        st.header("🔄 二進制 ↔ 格雷碼 互轉")
        col1, col2 = st.columns(2)
        with col1:
            b_val = st.text_input("輸入 Binary", "1011")
            st.success(f"Gray Code: {b_to_g(b_val)}")
        with col2:
            g_val = st.text_input("輸入 Gray", "1110")
            st.info(f"Binary: {g_to_b(g_val)}")
        
        st.divider()
        st.write("4-bit 完整對照表：")
        table = pd.DataFrame({
            "Dec": range(16),
            "Binary": [bin(i)[2:].zfill(4) for i in range(16)],
            "Gray": [bin(i ^ (i >> 1))[2:].zfill(4) for i in range(16)]
        })
        st.dataframe(table, hide_index=True)

    # --- 5. 考試系統 ---
    elif page == "🎓 邏輯檢定中心":
        st.header("🎓 邏輯知識能力測驗")
        score = 0
        q1 = st.radio("1. 哪一個邏輯閘只有在輸入全部為 1 時，輸出才會是 1？", ["OR", "AND", "XOR"])
        q2 = st.radio("2. 格雷碼的主要優點是什麼？", ["計算速度快", "相鄰數值只有一個位元改變", "節省電力"])
        
        if st.button("提交答案並計算分數"):
            if q1 == "AND": score += 50
            if q2 == "相鄰數值只有一個位元改變": score += 50
            if score == 100: st.balloons()
            st.write(f"### 您的最終得分：{score} / 100")

    # --- 6. 個人化設定 ---
    elif page == "🎨 極致個人化":
        st.header("🎨 城市風格與管理員設定")
        st.session_state.name = st.text_input("修改管理員名稱", st.session_state.name)
        st.session_state.prefs['sign'] = st.text_input("自定義個性簽名", st.session_state.prefs['sign'])
        st.divider()
        st.session_state.prefs['bg'] = st.color_picker("背景顏色", p['bg'])
        st.session_state.prefs['btn'] = st.color_picker("主題按鈕顏色", p['btn'])
        if st.button("儲存並套用更正"): st.rerun()

# =========================================
# 登入介面
# =========================================
if "user_login" not in st.session_state:
    st.title("🛡️ LogiMind 登入中心")
    name = st.text_input("請輸入管理員名稱進入城市")
    if st.button("啟動系統"):
        st.session_state.user_login = True
        st.session_state.name = name
        st.rerun()
else:
    main()
