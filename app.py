import streamlit as st
import pandas as pd
import random

# =========================================
# 1. 視覺引擎：全域樣式與圖片卡片化重塑
# =========================================
def apply_theme(p):
    # 自動判定文字顏色
    txt_color = "#000000" if (int(p['bg'].lstrip('#'), 16) > 0x888888) else "#FFFFFF"
    
    st.markdown(f"""
    <style>
    /* 全域背景設定 */
    .stApp {{ background-color: {p['bg']} !important; }}
    
    /* 強制所有標準文字顏色，確保對比度 */
    h1, h2, h3, h4, p, span, label, li, .stMarkdown {{ color: {txt_color} !important; }}
    
    /* 【核心修正】圖片容器完美白底卡片化 */
    /* 直接鎖定 Streamlit 的圖片區塊 */
    div[data-testid="stImage"] {{
        background-color: #FFFFFF !important; /* 強制純白背景 */
        padding: 30px !important;             /* 增加內部留白，讓圖片呼吸 */
        border-radius: 20px !important;       /* 大圓角，更現代 */
        box-shadow: 0 8px 16px rgba(0,0,0,0.2) !important; /* 強烈的立體陰影 */
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        margin: 20px auto !important;         /* 上下留白並水平置中 */
        max-width: 80%;                       /* 限制最大寬度，防止過大 */
    }}
    
    /* 確保圖片本身不受其他樣式干擾 */
    div[data-testid="stImage"] img {{
        margin: 0 !important;
        display: block !important;
        max-width: 100% !important;
        height: auto !important;
    }}
    
    /* 【核心修正】強制修復表單元件的白底白字問題 */
    /* 針對下拉選單選擇後的值和輸入框 */
    div[data-baseweb="select"] > div, input[type="text"] {{
        background-color: #FFFFFF !important; /* 強制白底 */
        color: #000000 !important;            /* 強制黑字 */
        border: 2px solid #e0e0e0 !important; /* 增加邊框提升識別度 */
        border-radius: 8px !important;
    }}
    /* 針對下拉選單的 placeholder 和圖標 */
    div[data-baseweb="select"] span, div[data-baseweb="select"] svg {{
        color: #000000 !important;
    }}
    /* 針對下拉選單展開後的選項列表 */
    ul[role="listbox"] li {{
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }}

    /* 表格樣式優化 */
    div[data-testid="stDataFrame"] *, div[data-testid="stTable"] * {{
        color: black !important;
    }}
    div[data-testid="stTable"], div[data-testid="stDataFrame"] {{
        background-color: #ffffff !important;
        border-radius: 12px;
        padding: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }}

    /* 按鈕樣式 */
    .stButton>button {{
        background-color: {p['btn']} !important;
        color: white !important;
        border-radius: 30px;
        font-weight: bold;
        border: none;
        padding: 12px 24px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }}
    .stButton>button:hover {{ transform: translateY(-2px); box-shadow: 0 6px 8px rgba(0,0,0,0.3); }}
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

# 圖片連結字典 (使用穩定圖源)
GATE_URLS = {
    "AND": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/AND_ANSI.svg/200px-AND_ANSI.svg.png",
    "OR": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/OR_ANSI.svg/200px-OR_ANSI.svg.png",
    "NOT": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Not_gate_ansi.svg/200px-Not_gate_ansi.svg.png",
    "XOR": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/XOR_ANSI.svg/200px-XOR_ANSI.svg.png",
    "NAND": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/NAND_ANSI.svg/200px-NAND_ANSI.svg.png",
    "NOR": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/NOR_ANSI.svg/200px-NOR_ANSI.svg.png",
    "Full Adder": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Full-adder.svg/300px-Full-adder.svg.png",
    "Half Adder": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Half_Adder.svg/300px-Half_Adder.svg.png",
    "Decoder": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/2-to-4_Decoder.svg/300px-2-to-4_Decoder.svg.png",
    "D-FF": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/D-Type_Flip-flop_Symbol.svg/300px-D-Type_Flip-flop_Symbol.svg.png"
}

# =========================================
# 3. 主程式架構
# =========================================
# 初始化 session state
if "last_score" not in st.session_state: st.session_state.last_score = 0
if "prefs" not in st.session_state: st.session_state.prefs = {"bg":"#0E1117","btn":"#00D4FF"}

def main():
    p = st.session_state.prefs
    apply_theme(p)
    
    # 側邊欄設計
    with st.sidebar:
        st.title(f"🏙️ LogiMind 控制台")
        st.write(f"管理員：**{st.session_state.name}**")
        
        # 智慧難度顯示
        score = st.session_state.last_score
        if score >= 85: level, color = "大師 (Hard)", "red"
        elif score >= 60: level, color = "中級 (Medium)", "orange"
        else: level, color = "初級 (Easy)", "green"
        st.markdown(f"當前權限等級：<span style='color:{color};font-weight:bold;'>{level}</span> (上次得分: {score})", unsafe_allow_html=True)
        
        st.divider()
        st.write("🌐 **核心連線狀態**")
        latency = random.randint(15, 45)
        st.caption(f"Server: AWS-Quantum | Latency: {latency}ms | Status: Stable")
        st.progress(100)
        
        st.divider()
        page = st.radio("導航中心", ["🏠 城市願景大廳", "🔬 基礎邏輯館", "🏗️ 進階電路區", "🔄 數據轉換站", "🎓 智慧考評中心", "🎨 城市規劃室"])
        st.divider()
        if st.button("🚪 安全登出系統"): 
            st.session_state.clear()
            st.rerun()

    # --- 1. 首頁：願景大廳 (大量文字介紹 + 修復破圖) ---
    if page == "🏠 城市願景大廳":
        st.title("歡迎來到 LogiMind：數位邏輯之城")
        st.markdown(f"尊敬的 **{st.session_state.name}** 管理員，歡迎回到您的指揮中心。")
        
        # 修復破圖，使用穩定的圖源，並會自動套用白底卡片樣式
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Operating_system_placement.svg/240px-Operating_system_placement.svg.png", caption="LogiMind 核心架構圖")

        st.header("關於這座城市 (About Our City)")
        st.markdown("""
        LogiMind 不僅僅是一個模擬器，它是一座將抽象的布林代數理論具象化的數位城市。在這裡，0 和 1 是流動的能量，邏輯閘是控制能量流向的樞紐，而複雜的電路則是構成城市運作的宏偉建築。我們的目標是提供一個直觀、互動且深度的學習環境，讓每一位「管理員」都能掌握數位世界的基石。
        """)
        
        st.subheader("🗺️ 您的學習路徑規劃")
        st.markdown("""
        為了協助您系統性地掌握數位邏輯，我們規劃了以下三階段的學習路徑：

        1.  **基礎奠基階段 (Foundation)**：前往 **🔬 基礎邏輯館**。在這裡，您將認識 AND, OR, NOT 等七大基礎邏輯閘。透過觀察它們的標準符號並對照真值表，建立對基本邏輯運算的直觀理解。這是城市建設的基石。
        2.  **進階架構階段 (Architecture)**：進入 **🏗️ 進階電路區**。了解如何將基礎邏輯閘組合起來，創造出具有特定功能的模組。您將學習到半加器如何進行簡單加法，全加器如何處理進位，以及解碼器如何將編碼訊號翻譯成獨立的輸出指令。
        3.  **時序與系統階段 (System & Timing)**：在 **🏗️ 進階電路區** 中接觸 D型正反器，理解電路如何擁有「記憶」功能，這是邁向時序邏輯和計算機記憶體原理的關鍵一步。同時，在 **🔄 數據轉換站** 掌握不同數制系統間的轉換技巧。
        """)
        
        st.subheader("✨ 核心功能亮點")
        st.markdown("""
        * **智慧適應性考評**：我們的 **🎓 智慧考評中心** 採用動態難度調整演算法。系統會根據您的歷史測驗成績，自動為您分派「初級」、「中級」或「大師」難度的試題，確保您始終在最適合的挑戰區間學習。
        * **極致視覺體驗**：全站採用現代化的 **🎨 深色/淺色主題切換**，並針對所有邏輯符號圖片導入了**白底卡片式設計**。無論您選擇何種背景，電路圖都能清晰、美觀地呈現，提供教科書級別的閱讀體驗。
        * **互動式模擬**：告別枯燥的理論背誦。在 LogiMind，您可以親自操作數據輸入，觀察二進制與格雷碼的即時轉換結果，從實踐中深化理解。
        """)
        st.info("💡 提示：您的每一次互動和考評成績都會被系統記錄，作為解鎖更高階內容的依據。現在，請從側邊欄選擇您的目的地，開始今天的探索之旅！")

    # --- 2. 基礎邏輯館 (重新排版：左右分欄 + 白底圖卡) ---
    elif page == "🔬 基礎邏輯館":
        st.title("🔬 基礎邏輯視覺符號館")
        st.write("這裡展示了構成數位世界的最基本元素。請選擇一個邏輯閘進行研究。")
        
        g = st.selectbox("請選擇邏輯閘組件", list(GATE_URLS.keys())[:6])
        
        st.divider()
        
        # 使用 columns 進行左右排版
        col1, col2 = st.columns([1, 1.5], gap="large")
        
        with col1:
            st.subheader("視覺符號 (Symbol)")
            # 圖片會自動套用完美的白底卡片樣式
            st.image(GATE_URLS[g], use_column_width=True, caption=f"{g} Gate ANSI 標準符號")
            st.info(f"上圖為 {g} 閘在電路圖中的標準表示方式。")
            
        with col2:
            st.subheader("真值表 (Truth Table)")
            # 根據選擇動態生成真值表
            if g == "NOT":
                 df = pd.DataFrame({"Input A":[0,1], "Output Y":[1,0]})
            elif g in ["AND", "OR", "NAND", "NOR", "XOR"]:
                 data = {"Input A":[0,0,1,1], "Input B":[0,1,0,1]}
                 if g == "AND": data["Output Y"] = [0,0,0,1]
                 elif g == "OR": data["Output Y"] = [0,1,1,1]
                 elif g == "NAND": data["Output Y"] = [1,1,1,0]
                 elif g == "NOR": data["Output Y"] = [1,0,0,0]
                 elif g == "XOR": data["Output Y"] = [0,1,1,0]
                 df = pd.DataFrame(data)
            
            # 顯示表格，隱藏索引，並設定寬度
            st.dataframe(df, hide_index=True, use_container_width=True)
            st.caption("真值表列出了該邏輯閘在所有可能輸入組合下的輸出結果。")

    # --- 3. 進階電路區 (白底圖卡 + 詳細說明) ---
    elif page == "🏗️ 進階電路區":
        st.title("🏗️ 進階組合與時序邏輯區")
        st.write("在此區域，我們將基礎邏輯閘組合起來，構建具有更複雜功能的電路模組。")
        
        adv = st.selectbox("請選擇要分析的電路結構", ["半加器 (Half Adder)", "全加器 (Full Adder)", "2-to-4 解碼器 (Decoder)", "D型正反器 (D-FF)"])
        st.divider()
        
        if "半加器" in adv:
            st.subheader("半加器 (Half Adder)")
            st.image(GATE_URLS["Half Adder"], width=350, caption="半加器邏輯電路圖")
            st.markdown("""
            **功能描述**：
            半加器是最簡單的加法電路，用於對兩個單一位元的二進制數進行相加。
            
            **邏輯公式**：
            - **和 (Sum, S)**：$S = A \oplus B$ (由 XOR 閘產生)
            - **進位 (Carry, C)**：$C = A \cdot B$ (由 AND 閘產生)
            
            *注意：半加器不考慮來自低位的進位輸入。*
            """)
        elif "全加器" in adv:
            st.subheader("全加器 (Full Adder)")
            st.image(GATE_URLS["Full Adder"], width=400, caption="全加器邏輯電路圖")
            st.markdown("""
            **功能描述**：
            全加器是執行多位元二進制加法的核心元件。與半加器不同，它考慮了三個輸入：兩個加數位元 (A, B) 和一個來自低位的進位輸入 (Cin)。
            
            **邏輯公式**：
            - **和 (Sum, S)**：$S = A \oplus B \oplus C_{in}$
            - **進位輸出 (Cout)**：$C_{out} = (A \cdot B) + (C_{in} \cdot (A \oplus B))$
            """)
        elif "解碼器" in adv:
            st.subheader("2-to-4 解碼器 (Decoder)")
            st.image(GATE_URLS["Decoder"], width=400, caption="2-to-4 線解碼器")
            st.markdown("""
            **功能描述**：
            解碼器是一種組合電路，它將 $n$ 個輸入線的二進制編碼信息轉換為 $2^n$ 個獨特的輸出線。對於 2-to-4 解碼器，兩個輸入 (A1, A0) 的四種組合 (00, 01, 10, 11) 會分別啟動四個輸出 (Y0, Y1, Y2, Y3) 中的一個。
            
            **應用**：常另外於記憶體位址解碼或數據路由。
            """)
        elif "D-FF" in adv:
            st.subheader("D型正反器 (D Flip-Flop)")
            st.image(GATE_URLS["D-FF"], width=300, caption="D型正反器符號")
            st.markdown("""
            **功能描述**：
            D型正反器是最基本的時序邏輯元件，具有「記憶」功能。它可以在時鐘訊號 (CLK) 的特定邊緣（如上升緣）觸發時，捕捉輸入端 (D) 的數據狀態，並將其鎖存到輸出端 (Q)，直到下一次時鐘觸發。
            
            **特點**：它是構建暫存器 (Register) 和計算機記憶體的基礎單元。
            """)

    # --- 4. 智慧考評中心 (21題智慧分級 + 完美表單體驗) ---
    elif page == "🎓 智慧考評中心":
        st.title(f"🎓 數位邏輯智慧檢定 - {level}")
        st.write(f"系統已根據您的權限等級，為您準備了 7 道 **{level}** 難度的試題。請專注作答。")
        st.progress(st.session_state.last_score / 100)
        
        current_qs = QUESTION_BANK[level]
        score = 0
        
        with st.form("exam_form"):
            user_ans = []
            for i, q in enumerate(current_qs):
                st.subheader(f"問題 {i+1}")
                # 使用 radio 並隱藏 label，讓排版更整潔
                user_ans.append(st.radio(q['q'], q['o'], key=f"exam_{level}_{i}"))
                st.divider()
            
            submitted = st.form_submit_button("提交檢定試卷", type="primary")
            
            if submitted:
                st.balloons()
                for i, q in enumerate(current_qs):
                    if user_ans[i] == q['a']: score += (100 // len(current_qs))
                
                st.session_state.last_score = score
                
                st.title(f"📝 檢定結果報告")
                st.metric(label="本次得分", value=f"{score} / 100", delta=f"{score - 60} (及格基準)")
                
                if score >= 90: 
                    st.success("🎉 表現卓越！您的邏輯思維非常清晰，系統權限已提升。")
                elif score >= 60:
                    st.info("✅ 通過檢定。您已掌握了本階層的核心知識，請繼續努力。")
                else:
                    st.error("⚠️ 未通過檢定。建議您回到基礎館和進階區重新複習相關概念。")

    # --- 5. 數據轉換站 (左右分欄 + 錯誤處理) ---
    elif page == "🔄 數據轉換站":
        st.title("🔄 數制互補轉換工具")
        st.write("此工具提供二進制 (Binary) 與格雷碼 (Gray Code) 之間的即時雙向轉換。請在下方輸入數值。")
        
        st.divider()
        
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            st.subheader("Binary ➔ Gray")
            b_in = st.text_input("輸入二進制字串 (例如: 1010)", value="", placeholder="在此輸入 0/1 組合...")
            if b_in:
                try:
                    # 驗證輸入是否只包含 0 和 1
                    if not all(c in '01' for c in b_in): raise ValueError
                    g_out = bin(int(b_in, 2) ^ (int(b_in, 2) >> 1))[2:].zfill(len(b_in))
                    st.success(f"轉換結果 (Gray): **{g_out}**")
                except:
                    st.error("輸入格式錯誤！請僅輸入 0 和 1 的組合。")
            
        with col2:
            st.subheader("Gray ➔ Binary")
            g_in = st.text_input("輸入格雷碼字串 (例如: 1111)", value="", placeholder="在此輸入 0/1 組合...")
            if g_in:
                try:
                    if not all(c in '01' for c in g_in): raise ValueError
                    b = g_in[0]
                    for i in range(1, len(g_in)): b += str(int(b[-1]) ^ int(g_in[i]))
                    st.info(f"轉換結果 (Binary): **{b}**")
                except:
                    st.error("輸入格式錯誤！請僅輸入 0 和 1 的組合。")

    # --- 6. 城市規劃室 (個人化設定) ---
    elif page == "🎨 城市規劃室":
        st.title("🎨 城市風格個性化設定")
        st.write("在這裡，您可以自定義 LogiMind 控制台的視覺風格。設定將即時套用。")
        
        st.divider()
        
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.subheader("城市基調 (背景色)")
            new_bg = st.color_picker("選擇背景顏色", p['bg'])
            if new_bg != p['bg']:
                st.session_state.prefs['bg'] = new_bg
                st.rerun()
                
        with col2:
            st.subheader("控制元件 (強調色)")
            new_btn = st.color_picker("選擇按鈕與邊框顏色", p['btn'])
            if new
