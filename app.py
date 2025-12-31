import streamlit as st
import pandas as pd
import random

# =========================================
# 1. 視覺引擎：CSS 深度修正 (解決偏移問題)
# =========================================
def apply_theme(p):
    # 根據背景深淺自動決定文字顏色 (黑/白)
    txt_color = "#000000" if (int(p['bg'].lstrip('#'), 16) > 0x888888) else "#FFFFFF"
    
    st.markdown(f"""
    <style>
    /* 全域背景設定 */
    .stApp {{ background-color: {p['bg']} !important; }}
    
    /* 強制所有標準文字與標題顏色，確保可見 */
    h1, h2, h3, h4, p, span, label, li {{ color: {txt_color} !important; }}
    
    /* 【V46 核心修正】圖片容器完美置中 */
    /* 直接針對 Streamlit 的圖片區塊進行樣式設定，不再需要外包 div */
    div[data-testid="stImage"] {{
        background-color: #FFFFFF !important; /* 強制白底 */
        padding: 25px !important;             /* 增加內部留白 */
        border-radius: 16px !important;       /* 圓角 */
        box-shadow: 0 6px 12px rgba(0,0,0,0.15); /* 精緻陰影 */
        /* 關鍵：使用 Flex 強制內容水平與垂直置中 */
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        margin-bottom: 20px;
    }}
    /* 確保圖片本身沒有額外的邊距干擾對齊 */
    div[data-testid="stImage"] img {{
        margin: 0 !important;
        display: block !important;
    }}
    
    /* 強制下拉選單與輸入框為白底黑字，防止隱形 */
    div[data-baseweb="select"] > div, input {{
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #ccc !important;
    }}
    div[data-baseweb="select"] span {{ color: #000000 !important; }}

    /* 按鈕樣式優化 */
    .stButton>button {{
        background-color: {p['btn']} !important;
        color: white !important;
        border-radius: 50px;
        font-weight: bold;
        border: 2px solid {txt_color};
        padding: 10px 24px;
        transition: all 0.3s ease;
    }}
    .stButton>button:hover {{ transform: scale(1.02); }}
    </style>
    """, unsafe_allow_html=True)

# =========================================
# 2. 智慧分級題庫 (完整 21 題)
# =========================================
QUESTION_BANK = {
    "初級 (Easy)": [
        {"q": "AND 閘輸入為 (1, 0) 時，輸出為何？", "o": ["0", "1"], "a": "0"},
        {"q": "哪種邏輯閘在輸入為 0 時輸出為 1？", "o": ["AND", "OR", "NOT"], "a": "NOT"},
        {"q": "OR 閘任一輸入為 1，輸出即為？", "o": ["0", "1"], "a": "1"},
        {"q": "數位電路中最基礎的單位 0 代表？", "o": ["高電壓", "低電壓"], "a": "低電壓"},
        {"q": "NAND 閘是哪兩種閘的組合？", "o": ["AND+NOT", "OR+NOT"], "a": "AND+NOT"},
        {"q": "二進制 1 + 0 的結果是？", "o": ["0", "1"], "a": "1"},
        {"q": "邏輯閘符號中，前端的小圓圈代表？", "o": ["加強", "反相 (Invert)"], "a": "反相 (Invert)"}
    ],
    "中級 (Medium)": [
        {"q": "半加器無法處理下列哪一項？", "o": ["輸入加法", "低位進位 (Cin)", "輸出進位"], "a": "低位進位 (Cin)"},
        {"q": "2對4解碼器當輸入為 (1, 0) 時，哪條線輸出為 1？", "o": ["Y0", "Y2", "Y3"], "a": "Y2"},
        {"q": "格雷碼的優點是相鄰兩數僅有幾個位元變動？", "o": ["1個", "2個", "全部"], "a": "1個"},
        {"q": "XOR 閘在兩輸入相同時輸出為何？", "o": ["0", "1"], "a": "0"},
        {"q": "多工器 (MUX) 的主要功能是？", "o": ["數據分發", "數據選擇", "運算"], "a": "數據選擇"},
        {"q": "二進制 1010 轉為格雷碼是？", "o": ["1111", "15", "1101"], "a": "1111"},
        {"q": "全加器的 Sum 公式由幾個 XOR 組成？", "o": ["1個", "2個", "3個"], "a": "2個"}
    ],
    "大師 (Hard)": [
        {"q": "D正反器在時鐘觸發前會保持原值，這稱為？", "o": ["運算", "記憶/鎖存", "清除"], "a": "記憶/鎖存"},
        {"q": "布林代數簡化：A + AB 等於？", "o": ["A", "B", "AB"], "a": "A"},
        {"q": "JK正反器當 J=1, K=1 時，輸出 Q 會如何？", "o": ["不變", "歸零", "反轉 (Toggle)"], "a": "反轉 (Toggle)"},
        {"q": "1-Bit 比較器，若 A=0, B=1，則 A<B 的輸出是？", "o": ["0", "1"], "a": "1"},
        {"q": "時序電路與組合電路最大的差別在於具備？", "o": ["邏輯閘", "回授/記憶", "開關"], "a": "回授/記憶"},
        {"q": "格雷碼 1010 轉為二進制是？", "o": ["1100", "1010", "1111"], "a": "1100"},
        {"q": "傳播延遲主要由什麼引起的？", "o": ["電壓不足", "電子元件切換時間", "導線長度"], "a": "電子元件切換時間"}
    ]
}

# =========================================
# 3. 主程式架構
# =========================================
# 初始化 session state
if "last_score" not in st.session_state: st.session_state.last_score = 0
if "prefs" not in st.session_state: st.session_state.prefs = {"bg":"#0E1117","btn":"#00FFCC"}

def main():
    p = st.session_state.prefs
    apply_theme(p)
    
    with st.sidebar:
        st.title(f"🏙️ {st.session_state.name}")
        st.write(f"上次檢定分數：**{st.session_state.last_score}**")
        # 智慧判定難度
        if st.session_state.last_score >= 85: level = "大師 (Hard)"
        elif st.session_state.last_score >= 60: level = "中級 (Medium)"
        else: level = "初級 (Easy)"
        st.info(f"當前建議難度：{level}")
        st.divider()
        st.write("🌐 **核心連線狀態**")
        # 模擬網路數據跳動
        latency = random.randint(15, 35)
        st.caption(f"Latency: {latency}ms | Secure Port: 443 | Status: Stable")
        st.progress(100)
        page = st.radio("導航中心", ["🏠 願景大廳", "🔬 基礎邏輯館", "🏗️ 進階電路區", "🔄 數據轉換站", "🎓 智慧考評中心", "🎨 城市規劃室"])
        if st.button("🚪 安全登出"): 
            st.session_state.clear()
            st.rerun()

    # --- 1. 首頁 ---
    if page == "🏠 願景大廳":
        st.header("歡迎回到 LogiMind V46")
        st.write(f"管理員 **{st.session_state.name}**，視覺系統已升級至完美對齊版本。")
        st.write("這是一座適應性智慧城市，系統會根據您的考評表現自動調整學習難度。")
        # 這張圖片會自動套用完美的白底置中樣式
        st.image("https://img.icons8.com/clouds/200/smart-city.png", width=150)

    # --- 2. 基礎邏輯閘 ---
    elif page == "🔬 基礎邏輯館":
        st.header("🔬 基礎邏輯視覺符號")
        g = st.selectbox("選擇組件", ["AND", "OR", "NOT", "XOR", "NAND", "NOR"])
        urls = {
            "AND": "https://upload.wikimedia.org/wikipedia/commons/6/64/AND_ANSI.svg",
            "OR": "https://upload.wikimedia.org/wikipedia/commons/b/b5/OR_ANSI.svg",
            "NOT": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Not_gate_ansi.svg",
            "XOR": "https://upload.wikimedia.org/wikipedia/commons/0/01/XOR_ANSI.svg",
            "NAND": "https://upload.wikimedia.org/wikipedia/commons/f/f2/NAND_ANSI.svg",
            "NOR": "https://upload.wikimedia.org/wikipedia/commons/6/6c/NOR_ANSI.svg"
        }
        # 注意：這裡不再需要手動加 div wrapper 了
        st.image(urls[g], width=300, caption=f"{g} Gate 標準符號")
        
        st.write("---")
        st.subheader(f"{g} 真值表示例")
        # 簡單的真值表邏輯範例
        if g == "NOT":
             df = pd.DataFrame({"Input":[0,1], "Output":[1,0]})
        else:
             df = pd.DataFrame({"A":[0,0,1,1],"B":[0,1,0,1],"Y":["?","?","?","?"]})
             st.caption("請參考教科書填寫正確輸出結果。")
        st.table(df)

    # --- 3. 進階電路 ---
    elif page == "🏗️ 進階電路區":
        st.header("🏗️ 進階組合與時序邏輯")
        adv = st.selectbox("查看結構", ["半加器", "全加器", "解碼器", "D正反器"])
        
        # 這些圖片也都會自動完美置中
        if adv == "全加器":
            st.image("https://upload.wikimedia.org/wikipedia/commons/a/a9/Full-adder.svg", width=400)
            st.latex(r"Sum = A \oplus B \oplus C_{in}")
        elif adv == "D正反器":
            st.image("https://upload.wikimedia.org/wikipedia/commons/2/2f/D-Type_Flip-flop_Symbol.svg", width=300)
            st.write("時序邏輯基礎：在時鐘訊號(CLK)上升緣時，將輸入(D)的值存入(Q)。")
        elif adv == "半加器":
            st.image("https://upload.wikimedia.org/wikipedia/commons/d/d9/Half_Adder.svg", width=300)
            st.latex(r"Sum = A \oplus B, \quad Carry = A \cdot B")
        else:
            st.image("https://upload.wikimedia.org/wikipedia/commons/d/d0/2-to-4_Decoder.svg", width=350)
            st.write("將 2 個輸入位元解碼為 4 條獨熱(One-hot)輸出線。")

    # --- 4. 智慧考評中心 (21題智慧分級) ---
    elif page == "🎓 智慧考評中心":
        st.header(f"🎓 數位邏輯檢定 - {level}")
        st.write(f"系統已根據您的程度挑選了 7 題 **{level}** 試題。請謹慎作答。")
        
        current_qs = QUESTION_BANK[level]
        score = 0
        # 使用 form 避免每次點擊選項就刷新
        with st.form("exam_form"):
            user_ans = []
            for i, q in enumerate(current_qs):
                st.write(f"**Q{i+1}. {q['q']}**")
                user_ans.append(st.radio(f"選擇答案 (Q{i+1})", q['o'], key=f"exam_{level}_{i}", label_visibility="collapsed"))
                st.divider()
            
            submitted = st.form_submit_button("提交檢定報告", type="primary")
            if submitted:
                for i, q in enumerate(current_qs):
                    if user_ans[i] == q['a']: score += (100 // len(current_qs))
                # 將分數存入 session state 以便下次判定難度
                st.session_state.last_score = score
                st.write(f"### 本次檢定得分：{score} / 100")
                if score >= 90: 
                    st.balloons()
                    st.success("表現卓越！系統難度將提升至下一等級。")
                elif score >= 60:
                    st.info("通過檢定。繼續保持！")
                else:
                    st.error("未通過。建議回到基礎館複習。")
                # 稍微延遲後刷新頁面以更新側邊欄狀態
                # st.rerun() 

    # --- 其他功能 ---
    elif page == "🔄 數據轉換站":
        st.header("🔄 數制互補轉換 (Binary ↔ Gray)")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Binary to Gray")
            b_in = st.text_input("輸入二進制", "1010")
            try:
                g_out = bin(int(b_in, 2) ^ (int(b_in, 2) >> 1))[2:].zfill(len(b_in))
                st.success(f"格雷碼: {g_out}")
            except: st.error("格式錯誤")
        with col2:
            st.subheader("Gray to Binary")
            g_in = st.text_input("輸入格雷碼", "1111")
            try:
                b = g_in[0]
                for i in range(1, len(g_in)): b += str(int(b[-1]) ^ int(g_in[i]))
                st.info(f"二進制: {b}")
            except: st.error("格式錯誤")

    elif page == "🎨 城市規劃室":
        st.header("🎨 風格個性化設定")
        st.write("調整您的專屬控制台風格。")
        col1, col2 = st.columns(2)
        with col1:
            new_bg = st.color_picker("城市底色 (背景)", p['bg'])
            if new_bg != p['bg']:
                st.session_state.prefs['bg'] = new_bg
                st.rerun()
        with col2:
            new_btn = st.color_picker("強調色 (按鈕/邊框)", p['btn'])
            if new_btn != p['btn']:
                st.session_state.prefs['btn'] = new_btn
                st.rerun()

# --- 登入介面 ---
if "name" not in st.session_state:
    st.title("🛡️ LogiMind 啟動入口")
    st.write("請輸入您的管理員身份以連接至核心系統。")
    n = st.text_input("管理員代號")
    if st.button("啟動系統", type="primary"): 
        if n.strip():
            st.session_state.name = n
            st.rerun()
        else:
            st.warning("請輸入有效的代號。")
else:
    main()
