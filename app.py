import streamlit as st
import pandas as pd
import random
import time

# =========================================
# 1. 強力視覺引擎：封殺白底白字 & 深度自定義
# =========================================
def apply_theme(p):
    txt = "#000000" if (int(p['bg'].lstrip('#'), 16) > 0xFFFFFF // 2) else "#FFFFFF"
    st.markdown(f"""
    <style>
    /* 全域背景 */
    .stApp {{ background-color: {p['bg']} !important; }}
    
    /* 文字與標題顏色鎖定 */
    .stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp label, .stApp span {{
        color: {txt} !important;
    }}

    /* 修復下拉選單 (Selectbox) 白底白字問題 */
    div[data-baseweb="select"] > div {{
        background-color: #f0f2f6 !important;
        color: #000000 !important;
    }}
    div[data-baseweb="select"] span {{ color: #000000 !important; }}

    /* 表格樣式：移除索引、強制白底黑字 */
    div[data-testid="stDataFrame"] *, div[data-testid="stTable"] * {{
        color: black !important;
    }}
    div[data-testid="stTable"], div[data-testid="stDataFrame"] {{
        background-color: white !important;
        border-radius: 10px;
        padding: 8px;
    }}

    /* 按鈕樣式 */
    .stButton>button {{
        background-color: {p['btn']} !important;
        color: white !important;
        border-radius: 20px !important;
        border: 2px solid {txt} !important;
        width: 100%;
    }}

    /* 邏輯閘圖形模擬器樣式 */
    .gate-container {{
        border: 3px solid {p['btn']};
        padding: 20px;
        border-radius: 15px;
        background: rgba(255,255,255,0.1);
        text-align: center;
    }}
    </style>
    """, unsafe_allow_html=True)

# =========================================
# 2. 邏輯運算與轉換函數
# =========================================
def b_to_g(b): return bin(int(b, 2) ^ (int(b, 2) >> 1))[2:].zfill(len(b))
def g_to_b(g):
    b = g[0]
    for i in range(1, len(g)): b += str(int(b[-1]) ^ int(g[i]))
    return b

# =========================================
# 3. 主程式架構
# =========================================
if "name" not in st.session_state: 
    st.session_state.name = "Guest"
    st.session_state.prefs = {"bg":"#0E1117","btn":"#00FFCC", "avatar": "👤", "msg": "歡迎進入邏輯領域"}

def main():
    p = st.session_state.prefs
    apply_theme(p)

    # --- 側邊欄：網路連接狀態 & 個人化頭像 ---
    with st.sidebar:
        st.markdown(f"### {p['avatar']} {st.session_state.name}")
        st.caption(f"💬 {p['msg']}")
        st.divider()
        st.write("🌐 **網路核心狀態**")
        st.progress(100)
        st.caption(f"Lat: {random.randint(15, 35)}ms | Link: Secure 🔒")
        
        page = st.radio("城市導覽", ["🏙️ 願景大廳", "🔬 視覺化實驗室", "🏗️ 組合建築區", "🔄 數據轉換站", "🎓 邏輯檢定中心", "🎨 個人化規劃"])
        if st.button("🚪 安全登出"): st.session_state.clear(); st.rerun()

    # --- 1. 首頁：多益點的深度描述 ---
    if page == "🏙️ 願景大廳":
        st.header("LogiMind：數位邏輯城市願景")
        st.write(f"""
        管理員 **{st.session_state.name}** 您好，歡迎來到這座由 0 與 1 構築的巔峰之城。
        
        數位邏輯不只是工程學，它是處理資訊的哲學。本系統旨在提供以下專業價值：
        - **結構化學習**：從單一的 **與、或、非** 邏輯閘開始，建立穩固的底層邏輯知識。
        - **運算具象化**：透過組合電路特區，您可以理解計算機是如何透過電子訊號完成加法運算。
        - **數據完整性**：在轉換站中，我們處理格雷碼與二進制的對應，這是通訊系統中防止錯誤的關鍵技術。
        - **實戰考評**：透過檢定中心，將理論轉化為實際的判斷力。
        """)
        st.image("https://img.icons8.com/clouds/200/city.png", width=150)

    # --- 2. 邏輯閘視覺化 (長相描述) ---
    elif page == "🔬 視覺化實驗室":
        st.header("🔬 邏輯閘外觀視覺化")
        g = st.selectbox("挑選邏輯閘組件", ["AND (及閘)", "OR (或閘)", "NOT (反閘)", "XOR (互斥或閘)"])
        
        st.markdown('<div class="gate-container">', unsafe_allow_html=True)
        if "AND" in g:
            st.write("### [= D >-]")
            st.write("**視覺外觀**：像一個橫放的字母 **D**。輸入端在左側平面，輸出端在右側圓弧。")
        elif "OR" in g:
            st.write("### [= )) >-]")
            st.write("**視覺外觀**：像一個**火箭頭**或帶有弧形的月牙。具有流線型的外觀，代表訊號的匯集。")
        elif "NOT" in g:
            st.write("### [|>o -]")
            st.write("**視覺外觀**：一個**三角形**，右尖端有一個**小圓圈 (Bubble)**，代表訊號的徹底反轉。")
        elif "XOR" in g:
            st.write("### [)) ) >-]")
            st.write("**視覺外觀**：像 OR 閘，但在輸入端多了一條**雙重弧線**，代表「互斥」的排他性。")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- 3. 組合電路特區 ---
    elif page == "🏗️ 組合建築區":
        st.header("🏗️ 組合電路特區")
        mode = st.selectbox("選擇建築", ["半加器 (Half Adder)", "2對4解碼器", "多工器"])
        if "半加器" in mode:
            st.subheader("半加器：運算的起點")
            st.write("由一個 XOR (處理 Sum) 與 一個 AND (處理 Carry) 組成。")
            st.table(pd.DataFrame({"A":[0,0,1,1],"B":[0,1,0,1],"Sum":[0,1,1,0],"Carry":[0,0,0,1]}))

    # --- 4. 數據轉換站 (雙向互轉) ---
    elif page == "🔄 數據轉換站":
        st.header("🔄 二進制 ↔ 格雷碼 互轉")
        col1, col2 = st.columns(2)
        with col1:
            b_in = st.text_input("輸入二進制 (Binary)", "1010")
            st.success(f"結果 (Gray): {b_to_g(b_in)}")
        with col2:
            g_in = st.text_input("輸入格雷碼 (Gray)", "1111")
            st.info(f"結果 (Binary): {g_to_b(g_in)}")

    # --- 5. 考試系統 (新增功能) ---
    elif page == "🎓 邏輯檢定中心":
        st.header("🎓 數位邏輯能力檢定")
        q1 = st.radio("1. 當 AND 閘輸入為 (1, 0) 時，輸出為何？", ["0", "1"])
        q2 = st.radio("2. 哪個邏輯閘的外觀帶有一個代表反向的小圓圈？", ["AND", "OR", "NOT"])
        if st.button("提交檢定"):
            score = 0
            if q1 == "0": score += 50
            if q2 == "NOT": score += 50
            st.balloons()
            st.write(f"### 您的得分：{score} / 100")

    # --- 6. 極致個人化規劃 ---
    elif page == "🎨 個人化規劃":
        st.header("🎨 城市風格管理")
        st.session_state.name = st.text_input("管理員名稱", st.session_state.name)
        st.session_state.prefs['avatar'] = st.selectbox("選擇頭像", ["👤", "👨‍💻", "👩‍🔬", "🤖", "🌟"])
        st.session_state.prefs['msg'] = st.text_input("城市歡迎語", st.session_state.prefs['msg'])
        st.divider()
        st.session_state.prefs['bg'] = st.color_picker("城市背景顏色", p['bg'])
        st.session_state.prefs['btn'] = st.color_picker("主題按鈕顏色", p['btn'])
        if st.button("套用所有更正"): st.rerun()

# =========================================
# 4. 登入系統
# =========================================
def auth():
    apply_theme({"bg":"#0E1117","btn":"#00FFCC"})
    st.title("🛡️ LogiMind 登入中心")
    n = st.text_input("請輸入您的管理員代號")
    if st.button("啟動系統"):
        st.session_state.name = n
        st.rerun()

if "name" not in st.session_state or st.session_state.name == "Guest": auth()
else: main()
