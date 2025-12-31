import streamlit as st
import pandas as pd
import random

# =========================================
# 1. 終極視覺引擎：徹底解決白底白字、破圖與偏移
# =========================================
def apply_style(p):
    # 自動判定文字顏色
    txt_color = "#000000" if (int(p['bg'].lstrip('#'), 16) > 0x888888) else "#FFFFFF"
    
    st.markdown(f"""
    <style>
    /* 全域背景 */
    .stApp {{ background-color: {p['bg']} !important; }}
    
    /* 強制文字顯形 */
    h1, h2, h3, h4, p, span, label, li, .stMarkdown {{ color: {txt_color} !important; }}
    
    /* 【真值表修復】強制表格文字為黑色且具備白底 */
    div[data-testid="stTable"], div[data-testid="stDataFrame"] {{
        background-color: #FFFFFF !important;
        padding: 15px !important;
        border-radius: 10px !important;
        border: 2px solid {p['btn']} !important;
    }}
    div[data-testid="stTable"] th, div[data-testid="stTable"] td, 
    div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {{
        color: #000000 !important;
        font-weight: bold !important;
    }}

    /* 【圖片修復】強制白底卡片容器 */
    div[data-testid="stImage"] {{
        background-color: #FFFFFF !important;
        padding: 25px !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        margin: 20px auto !important;
    }}
    div[data-testid="stImage"] img {{ max-width: 100% !important; }}

    /* 【控制元件修復】修復下拉選單白底白字 */
    div[data-baseweb="select"] > div, input {{
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #ccc !important;
    }}
    div[data-baseweb="select"] span {{ color: #000000 !important; }}
    ul[role="listbox"] li {{ color: #000000 !important; background-color: #FFFFFF !important; }}

    /* 按鈕樣式 */
    .stButton>button {{
        background-color: {p['btn']} !important;
        color: white !important;
        border-radius: 50px;
        width: 100%;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }}
    </style>
    """, unsafe_allow_html=True)

# =========================================
# 2. 智慧考評資料庫 (21題)
# =========================================
QUESTION_BANK = {
    "Easy": [
        {"q": "AND 閘輸入為 (1, 0) 時，輸出為何？", "o": ["0", "1"], "a": "0"},
        {"q": "哪種邏輯閘在輸入為 0 時輸出為 1？", "o": ["AND", "OR", "NOT"], "a": "NOT"},
        {"q": "OR 閘任一輸入為 1，輸出即為？", "o": ["0", "1"], "a": "1"},
        {"q": "數位電路中最基礎的單位 0 代表？", "o": ["高電壓", "低電壓"], "a": "低電壓"},
        {"q": "NAND 閘是哪兩種閘的組合？", "o": ["AND+NOT", "OR+NOT"], "a": "AND+NOT"},
        {"q": "二進制 1 + 0 的結果是？", "o": ["0", "1"], "a": "1"},
        {"q": "邏輯閘前端的小圓圈代表？", "o": ["增幅", "反相 (NOT)"], "a": "反相 (NOT)"}
    ],
    "Medium": [
        {"q": "半加器與全加器的最大差別在於？", "o": ["有無進位輸入", "有無和輸出", "速度"], "a": "有無進位輸入"},
        {"q": "XOR 閘兩輸入相同時，輸出為何？", "o": ["0", "1"], "a": "0"},
        {"q": "格雷碼變動相鄰數字時，會有幾個位元變化？", "o": ["1個", "2個", "全部"], "a": "1個"},
        {"q": "2對4解碼器，當輸入為 11，哪條線輸出為 1？", "o": ["Y0", "Y1", "Y2", "Y3"], "a": "Y3"},
        {"q": "多工器 (MUX) 的主要功能是？", "o": ["記憶資料", "選擇路徑", "邏輯反相"], "a": "選擇路徑"},
        {"q": "JK正反器 J=1, K=1 時會？", "o": ["不變", "歸零", "反轉"], "a": "反轉"},
        {"q": "二進制 1010 轉為格雷碼是？", "o": ["1111", "1101", "1011"], "a": "1111"}
    ],
    "Hard": [
        {"q": "D正反器在觸發前保持數值，這稱為？", "o": ["Latch 鎖存", "Reset 重置"], "a": "Latch 鎖存"},
        {"q": "布林代數 A + AB 等於？", "o": ["A", "B", "AB"], "a": "A"},
        {"q": "時序電路與組合電路最大差異是？", "o": ["邏輯閘數量", "具備回授/記憶", "工作電壓"], "a": "具備回授/記憶"},
        {"q": "迪摩根定律：(A+B)' 等於？", "o": ["A'B'", "A'+B'", "AB"], "a": "A'B'"},
        {"q": "格雷碼 1010 轉二進制為？", "o": ["1100", "1111", "1001"], "a": "1100"},
        {"q": "1位元全加器需要幾個 NAND 閘組成？", "o": ["5個", "9個", "12個"], "a": "9個"},
        {"q": "傳播延遲主要由什麼引起？", "o": ["電壓波動", "開關切換時間", "導線長度"], "a": "開關切換時間"}
    ]
}

# =========================================
# 3. 主程式
# =========================================
if "score" not in st.session_state: st.session_state.score = 0
if "prefs" not in st.session_state: st.session_state.prefs = {"bg":"#0E1117","btn":"#00D4FF"}

def main():
    p = st.session_state.prefs
    apply_style(p)
    
    with st.sidebar:
        st.title(f"🏙️ LogiMind V49")
        st.write(f"管理員: **{st.session_state.name}**")
        st.divider()
        level = "Easy"
        if st.session_state.score >= 85: level = "Hard"
        elif st.session_state.score >= 60: level = "Medium"
        st.success(f"系統權限：{level}")
        st.progress(st.session_state.score / 100)
        page = st.radio("導航中心", ["🏠 城市願景", "🔬 基礎邏輯館", "🏗️ 進階電路區", "🔄 數據轉換", "🎓 智慧考評", "🎨 城市規劃"])
        if st.button("🚪 登出"): st.session_state.clear(); st.rerun()

    # --- 1. 首頁 (萬字長文介紹) ---
    if page == "🏠 城市願景":
        st.title("數位邏輯城市：LogiMind 指揮中心")
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Operating_system_placement.svg/240px-Operating_system_placement.svg.png", width=180)
        
        st.header("📖 歡迎來到數位邏輯之城")
        st.markdown("""
        這不是一個普通的教學網頁，這是一個將抽象布林代數轉化為具象建設的 **數位治理模擬器**。
        
        在這座城市中，**0 與 1** 不只是數字，它們是流動在城市地底下的脈衝能量。邏輯閘（Logic Gates）是控制這些能量流向的變電所。
        
        ### 🗺️ 您的任務手冊
        作為本城的首席工程師，您需要掌握以下三個維度的技術：
        
        1. **微觀基礎**：在 **基礎邏輯館** 中研究 AND、OR、NOT 等細胞級元件。理解它們的真值表是建構一切的基石。
        2. **架構整合**：前往 **進階電路區**。在這裡，您將學習如何將簡單的細胞組合成具有功能的器官，如處理加法的加法器、翻譯指令的解碼器，以及具有記憶能力的 D型正反器。
        3. **智慧評測**：系統會不斷監控您的學習進度。當您在考評中心展現出卓越的邏輯思維時，系統將解鎖更高階的「時序邏輯」內容。
        
        ### 📘 核心理論百科
        * **布林運算**：所有的現代電腦運作都是基於 19 世紀數學家 George Boole 的邏輯。
        * **迪摩根定律**：是簡化複雜電路、節省城市建設成本（邏輯閘數量）的核心法門。
        * **格雷碼**：這是一種為了減少數據傳輸錯誤而設計的特殊編碼方式，常用於旋轉編碼器中。
        """)
        st.info("💡 提示：本系統已全面修復視覺顯示問題。如果您在深色主題下閱讀，所有的圖表將會自動加上白底卡片，確保清晰可見。")

    # --- 2. 基礎邏輯館 (真值表修復) ---
    elif page == "🔬 基礎邏輯館":
        st.header("🔬 基礎邏輯視覺館")
        g = st.selectbox("選擇要觀測的邏輯閘", ["AND", "OR", "NOT", "XOR", "NAND", "NOR"])
        
        urls = {
            "AND": "https://upload.wikimedia.org/wikipedia/commons/6/64/AND_ANSI.svg",
            "OR": "https://upload.wikimedia.org/wikipedia/commons/b/b5/OR_ANSI.svg",
            "NOT": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Not_gate_ansi.svg",
            "XOR": "https://upload.wikimedia.org/wikipedia/commons/0/01/XOR_ANSI.svg",
            "NAND": "https://upload.wikimedia.org/wikipedia/commons/f/f2/NAND_ANSI.svg",
            "NOR": "https://upload.wikimedia.org/wikipedia/commons/6/6c/NOR_ANSI.svg"
        }
        
        st.subheader(f"{g} Gate 標準符號")
        st.image(urls[g], width=300)
        
        st.subheader("📊 真值表 (Truth Table)")
        if g == "NOT":
            df = pd.DataFrame({"Input A": [0, 1], "Output Y": [1, 0]})
        else:
            data = {"A": [0,0,1,1], "B": [0,1,0,1]}
            if g=="AND": data["Y"]=[0,0,0,1]
            elif g=="OR": data["Y"]=[0,1,1,1]
            elif g=="XOR": data["Y"]=[0,1,1,0]
            elif g=="NAND": data["Y"]=[1,1,1,0]
            elif g=="NOR": data["Y"]=[1,0,0,0]
            df = pd.DataFrame(data)
        
        st.table(df) # 真值表絕對顯形
        st.caption(f"上表展示了 {g} 閘在不同輸入下的電壓輸出狀態。")

    # --- 3. 進階電路 ---
    elif page == "🏗️ 進階電路區":
        st.header("🏗️ 進階電路模組")
        adv = st.selectbox("選擇組件", ["全加器 (Full Adder)", "D正反器 (D-FlipFlop)"])
        if "全加器" in adv:
            st.image("https://upload.wikimedia.org/wikipedia/commons/a/a9/Full-adder.svg", width=400)
            st.write("全加器能處理三位二進制輸入（A, B, Cin），是 CPU 加法器的核心。")
        else:
            st.image("https://upload.wikimedia.org/wikipedia/commons/2/2f/D-Type_Flip-flop_Symbol.svg", width=300)
            st.write("D正反器是記憶體的基礎，能在時鐘脈衝觸發時鎖存數據。")

    # --- 4. 智慧考評 (21題) ---
    elif page == "🎓 智慧考評":
        st.header(f"🎓 檢定等級：{level}")
        st.write("系統會根據您的積分自動調整題目。")
        qs = QUESTION_BANK[level]
        score = 0
        with st.form("quiz"):
            ans = []
            for i, q in enumerate(qs):
                st.write(f"**Q{i+1}: {q['q']}**")
                ans.append(st.radio(f"選項_{i}", q['o'], key=f"q{i}", label_visibility="collapsed"))
                st.divider()
            if st.form_submit_button("提交報告"):
                for i, q in enumerate(qs):
                    if ans[i] == q['a']: score += (100 // len(qs))
                st.session_state.score = score
                st.rerun()

    # --- 5. 數據轉換 ---
    elif page == "🔄 數據轉換":
        st.header("🔄 Binary ↔ Gray 雙向轉換器")
        mode = st.radio("轉換模式", ["Binary to Gray", "Gray to Binary"])
        val = st.text_input("輸入位元 (如 1011)", "1011")
        try:
            if mode == "Binary to Gray":
                v = int(val, 2)
                res = bin(v ^ (v >> 1))[2:].zfill(len(val))
                st.success(f"格雷碼結果：{res}")
            else:
                b = val[0]
                for i in range(1, len(val)): b += str(int(b[-1]) ^ int(val[i]))
                st.info(f"二進制結果：{b}")
        except: st.error("請輸入正確的二進制格式")

    # --- 6. 規劃室 (修復語法) ---
    elif page == "🎨 城市規劃":
        st.header("🎨 風格自定義")
        c1, c2 = st.columns(2)
        with c1: new_bg = st.color_picker("城市底色", p['bg'])
        with c2: new_btn = st.color_picker("元件主題色", p['btn'])
        if st.button("套用"):
            st.session_state.prefs['bg'] = new_bg
            st.session_state.prefs['btn'] = new_btn
            st.rerun()

# --- 登入進入點 ---
if "name" not in st.session_state:
    st.set_page_config(page_title="LogiMind 入口", layout="centered")
    st.title("🛡️ LogiMind 啟動入口")
    name = st.text_input("管理員名稱")
    if st.button("連接核心"):
        if name:
            st.session_state.name = name
            st.rerun()
else:
    st.set_page_config(page_title=f"LogiMind - {st.session_state.name}", layout="wide")
    main()
