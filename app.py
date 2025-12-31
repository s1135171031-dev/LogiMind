import streamlit as st
import pandas as pd
import random

# =========================================
# 1. 核心視覺引擎：解決破圖、偏移與白底白字
# =========================================
def apply_style(p):
    # 自動判定文字顏色 (黑/白)
    txt_color = "#000000" if (int(p['bg'].lstrip('#'), 16) > 0x888888) else "#FFFFFF"
    
    st.markdown(f"""
    <style>
    /* 全域背景 */
    .stApp {{ background-color: {p['bg']} !important; }}
    
    /* 文字顏色強制修正 */
    h1, h2, h3, h4, p, span, label, li, .stMarkdown {{ color: {txt_color} !important; }}
    
    /* 【核心修正】所有圖片強制容器化、白底、置中 */
    div[data-testid="stImage"] {{
        background-color: #FFFFFF !important;
        padding: 30px !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3) !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        margin: 20px auto !important;
        border: 2px solid {p['btn']} !important;
    }}
    div[data-testid="stImage"] img {{ max-width: 100% !important; height: auto !important; }}

    /* 【核心修正】修復下拉選單/輸入框「白底白字」問題 */
    div[data-baseweb="select"] > div, input {{
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #ccc !important;
    }}
    div[data-baseweb="select"] span {{ color: #000000 !important; }}
    
    /* 下拉選單展開後的選項列表文字顏色 */
    ul[role="listbox"] li {{ color: #000000 !important; background-color: #FFFFFF !important; }}

    /* 表格樣式優化 */
    div[data-testid="stTable"] {{ background-color: white !important; border-radius: 10px; }}
    div[data-testid="stTable"] th, div[data-testid="stTable"] td {{ color: black !important; }}

    /* 按鈕樣式 */
    .stButton>button {{
        background-color: {p['btn']} !important;
        color: white !important;
        border-radius: 12px;
        width: 100%;
        border: none;
        height: 3em;
        font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

# =========================================
# 2. 智慧分級題庫 (共 21 題)
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

# 穩定圖源
URLS = {
    "LOGO": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Operating_system_placement.svg/240px-Operating_system_placement.svg.png",
    "AND": "https://upload.wikimedia.org/wikipedia/commons/6/64/AND_ANSI.svg",
    "OR": "https://upload.wikimedia.org/wikipedia/commons/b/b5/OR_ANSI.svg",
    "NOT": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Not_gate_ansi.svg",
    "XOR": "https://upload.wikimedia.org/wikipedia/commons/0/01/XOR_ANSI.svg",
    "NAND": "https://upload.wikimedia.org/wikipedia/commons/f/f2/NAND_ANSI.svg",
    "NOR": "https://upload.wikimedia.org/wikipedia/commons/6/6c/NOR_ANSI.svg",
    "Full Adder": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Full-adder.svg",
    "D-FF": "https://upload.wikimedia.org/wikipedia/commons/2/2f/D-Type_Flip-flop_Symbol.svg"
}

# =========================================
# 3. 主程式流程
# =========================================
if "last_score" not in st.session_state: st.session_state.last_score = 0
if "prefs" not in st.session_state: st.session_state.prefs = {"bg":"#0E1117","btn":"#00D4FF"}

def main():
    p = st.session_state.prefs
    apply_style(p)
    
    with st.sidebar:
        st.title(f"🛡️ Admin: {st.session_state.name}")
        st.write(f"當前積分：**{st.session_state.last_score}**")
        level = "Easy"
        if st.session_state.last_score >= 85: level = "Hard"
        elif st.session_state.last_score >= 60: level = "Medium"
        st.info(f"建議挑戰等級：{level}")
        st.divider()
        page = st.radio("導航中心", ["🏠 願景大廳", "🔬 基礎邏輯館", "🏗️ 進階電路區", "🔄 數據轉換站", "🎓 智慧考評中心", "🎨 城市規劃室"])
        if st.button("登出系統"):
            st.session_state.clear()
            st.rerun()

    # --- 1. 首頁：願景大廳 (大量文字介紹) ---
    if page == "🏠 願景大廳":
        st.title("歡迎來到 LogiMind：數位邏輯之城 V48")
        st.image(URLS["LOGO"], width=150)
        
        st.markdown(f"### 管理員 {st.session_state.name}，系統已全量啟動。")
        st.write("---")
        
        st.header("📖 城市背景與核心願景")
        st.markdown("""
        在數位科技日新月異的今天，所有的電腦、智慧手機、甚至雲端伺服器，其核心運作邏輯都是由最基本的「0」與「1」構成的。**LogiMind** 是一座專門為數位邏輯學習者設計的智慧城市，將枯燥的布林代數理論轉化為視覺化的互動體驗。
        
        我們的使命是透過**視覺引導**與**智慧適應學習**，讓每一位管理員都能從基礎的「邏輯閘」開始，逐步構建出複雜的「時序邏輯」與「運算單元」。
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🛠️ 基礎建設：邏輯閘")
            st.write("這是數位世界的細胞。AND, OR, NOT 等基礎組件決定了資料流動的規則。在基礎邏輯館中，您可以觀察到每個閘的電子特性與真值表。")
        with col2:
            st.subheader("🏗️ 高階建築：組合電路")
            st.write("當數個細胞結合，就產生了加法器、解碼器與正反器。這些建築負責處理複雜的運算與數據存儲，是現代計算機架構的縮影。")
            
        st.header("📜 數位邏輯百科：布林運算定律")
        st.markdown("""
        為了協助您在考評中心取得高分，請務必複習以下核心定律：
        * **交換律 (Commutative Law)**：$A + B = B + A$ / $A \cdot B = B \cdot A$
        * **結合律 (Associative Law)**：$A + (B + C) = (A + B) + C$
        * **分配律 (Distributive Law)**：$A(B + C) = AB + AC$
        * **迪摩根定律 (De Morgan's Laws)**：$\overline{A+B} = \overline{A} \cdot \overline{B}$ / $\overline{A \cdot B} = \overline{A} + \overline{B}$
        * **吸收律 (Absorption Law)**：$A + AB = A$
        """)
        st.info("💡 提示：本系統會根據您的「智慧考評」成績自動調整導航難度。當您積分超過 85 分，系統將解鎖『大師級』時序邏輯題目。")

    # --- 2. 基礎邏輯館 (重新排版) ---
    elif page == "🔬 基礎邏輯館":
        st.header("🔬 基礎邏輯視覺館")
        g = st.selectbox("選擇要研究的邏輯閘", ["AND", "OR", "NOT", "XOR", "NAND", "NOR"])
        
        c1, c2 = st.columns([1, 1])
        with c1:
            st.subheader("ANSI 標準符號")
            st.image(URLS[g], width=250)
        with c2:
            st.subheader("真值表參考")
            if g == "AND":
                df = pd.DataFrame({"A":[0,0,1,1],"B":[0,1,0,1],"Y":[0,0,0,1]})
            elif g == "OR":
                df = pd.DataFrame({"A":[0,0,1,1],"B":[0,1,0,1],"Y":[0,1,1,1]})
            else:
                df = pd.DataFrame({"Input":[0,1],"Output":[1,0]})
            st.table(df)

    # --- 3. 進階電路區 ---
    elif page == "🏗️ 進階電路區":
        st.header("🏗️ 進階電路建築學")
        adv = st.selectbox("選擇組件", ["全加器", "D正反器"])
        if adv == "全加器":
            st.image(URLS["Full Adder"], width=400)
            st.latex(r"Sum = A \oplus B \oplus C_{in}")
        else:
            st.image(URLS["D-FF"], width=300)
            st.write("當時鐘脈衝 CLK 上升時，將 D 的值鎖存到輸出 Q。")

    # --- 4. 智慧考評中心 (21題) ---
    elif page == "🎓 智慧考評中心":
        st.header(f"🎓 數位邏輯檢定 - 等級: {level}")
        st.write("每組測驗包含 7 題，每題約 14 分，滿分 100 分。")
        
        qs = QUESTION_BANK[f"{'初級 (Easy)' if level=='Easy' else '中級 (Medium)' if level=='Medium' else '大師 (Hard)'}"]
        score = 0
        with st.form("quiz"):
            ans_list = []
            for i, q in enumerate(qs):
                st.write(f"**Q{i+1}: {q['q']}**")
                ans_list.append(st.radio(f"選項 {i}", q['o'], key=f"q{i}", label_visibility="collapsed"))
                st.divider()
            
            if st.form_submit_button("提交檢定報告"):
                for i, q in enumerate(qs):
                    if ans_list[i] == q['a']: score += 14.3
                st.session_state.last_score = int(score)
                st.rerun()

    # --- 5. 數據轉換 ---
    elif page == "🔄 數據轉換站":
        st.header("🔄 二進制 ↔ 格雷碼 轉換器")
        b_in = st.text_input("輸入二進制數值 (如: 1011)", "1011")
        try:
            val = int(b_in, 2)
            gray = bin(val ^ (val >> 1))[2:]
            st.success(f"對應格雷碼: {gray}")
        except: st.error("請輸入正確的二進制格式")

    # --- 6. 設定 (修復語法錯誤) ---
    elif page == "🎨 城市規劃室":
        st.header("🎨 個性化控制台")
        new_bg = st.color_picker("背景色", p['bg'])
        new_btn = st.color_picker("主題色", p['btn'])
        if st.button("套用設定"):
            st.session_state.prefs['bg'] = new_bg
            st.session_state.prefs['btn'] = new_btn
            st.rerun()

# --- 啟動入口 ---
if "name" not in st.session_state:
    st.set_page_config(page_title="LogiMind Login", layout="centered")
    st.title("🛡️ LogiMind 啟動")
    name = st.text_input("輸入管理員名稱")
    if st.button("啟動系統"):
        if name:
            st.session_state.name = name
            st.rerun()
else:
    st.set_page_config(page_title="LogiMind V48", layout="wide")
    main()
