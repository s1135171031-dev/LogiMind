import streamlit as st
import pandas as pd
import random

# =========================================
# 1. 視覺引擎：最強制級 CSS (解決白底白字)
# =========================================
def apply_style(p):
    txt_color = "#000000" if (int(p['bg'].lstrip('#'), 16) > 0x888888) else "#FFFFFF"
    
    st.markdown(f"""
    <style>
    /* 基礎背景與文字 */
    .stApp {{ background-color: {p['bg']} !important; }}
    h1, h2, h3, h4, p, span, label, li, .stMarkdown {{ color: {txt_color} !important; }}
    
    /* 【關鍵修復】自定義 HTML 表格樣式 - 徹底解決白底白字 */
    .truth-table-container {{
        background-color: #FFFFFF !important;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        margin: 10px 0;
    }}
    .custom-table {{
        width: 100%;
        border-collapse: collapse;
        background-color: #FFFFFF !important;
        color: #000000 !important; /* 強制黑字 */
    }}
    .custom-table th, .custom-table td {{
        border: 2px solid #EEEEEE;
        padding: 12px;
        text-align: center;
        color: #000000 !important; /* 二重強制 */
        font-family: sans-serif;
    }}
    .custom-table th {{
        background-color: #F8F9FA !important;
        font-weight: bold;
    }}

    /* 圖片卡片樣式 */
    div[data-testid="stImage"] {{
        background-color: #FFFFFF !important;
        padding: 25px !important;
        border-radius: 20px !important;
        box-shadow: 0 8px 30px rgba(0,0,0,0.4) !important;
        display: flex !important;
        justify-content: center !important;
        margin: 15px 0 !important;
    }}
    
    /* 下拉選單黑字修正 */
    div[data-baseweb="select"] > div {{ background-color: #FFFFFF !important; }}
    div[data-baseweb="select"] span {{ color: #000000 !important; }}
    
    /* 按鈕樣式 */
    .stButton>button {{
        background-color: {p['btn']} !important;
        color: white !important;
        border-radius: 8px;
        width: 100%;
        font-weight: bold;
        border: none;
    }}
    </style>
    """, unsafe_allow_html=True)

# 輔助函數：將 DataFrame 轉為強制黑字的 HTML 表格
def render_truth_table(df):
    html = f'<div class="truth-table-container"><table class="custom-table">'
    # Header
    html += '<thead><tr>' + ''.join(f'<th>{col}</th>' for col in df.columns) + '</tr></thead>'
    # Body
    html += '<tbody>'
    for _, row in df.iterrows():
        html += '<tr>' + ''.join(f'<td>{val}</td>' for val in row) + '</tr>'
    html += '</tbody></table></div>'
    st.markdown(html, unsafe_allow_html=True)

# =========================================
# 2. 智慧分級資料庫
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
        {"q": "半加器無法處理下列哪一項？", "o": ["輸入加法", "低位進位 (Cin)", "輸出進位"], "a": "低位進位 (Cin)"},
        {"q": "XOR 閘兩輸入相同時，輸出為何？", "o": ["0", "1"], "a": "0"},
        {"q": "格雷碼變動相鄰數字時，會有幾個位元變化？", "o": ["1個", "2個", "全部"], "a": "1個"},
        {"q": "2對4解碼器當輸入為 (1, 0) 時，哪條線輸出為 1？", "o": ["Y0", "Y2", "Y3"], "a": "Y2"},
        {"q": "多工器 (MUX) 的主要功能是？", "o": ["數據分發", "數據選擇", "運算"], "a": "數據選擇"},
        {"q": "二進制 1010 轉為格雷碼是？", "o": ["1111", "1101", "1011"], "a": "1111"},
        {"q": "全加器的 Sum 公式由幾個 XOR 組成？", "o": ["1個", "2個", "3個"], "a": "2個"}
    ],
    "Hard": [
        {"q": "D正反器在時鐘觸發前會保持原值，這稱為？", "o": ["運算", "鎖存 (Latch)", "清除"], "a": "鎖存 (Latch)"},
        {"q": "布林代數簡化：A + AB 等於？", "o": ["A", "B", "AB"], "a": "A"},
        {"q": "JK正反器當 J=1, K=1 時會如何？", "o": ["不變", "歸零", "反轉 (Toggle)"], "a": "反轉 (Toggle)"},
        {"q": "1-Bit 比較器，若 A=0, B=1，則 A<B 的輸出是？", "o": ["0", "1"], "a": "1"},
        {"q": "時序電路與組合電路最大的差別在於？", "o": ["邏輯閘", "具備記憶性", "電壓"], "a": "具備記憶性"},
        {"q": "格雷碼 1010 轉為二進制是？", "o": ["1100", "1010", "1111"], "a": "1100"},
        {"q": "傳播延遲主要由什麼引起？", "o": ["電壓", "電子元件切換時間", "線長"], "a": "電子元件切換時間"}
    ]
}

# =========================================
# 3. 主程式流程
# =========================================
if "score" not in st.session_state: st.session_state.score = 0
if "prefs" not in st.session_state: st.session_state.prefs = {"bg":"#0E1117","btn":"#00D4FF"}

def main():
    p = st.session_state.prefs
    apply_style(p)
    
    with st.sidebar:
        st.title(f"🏙️ LogiMind V50")
        st.write(f"管理員: **{st.session_state.name}**")
        st.divider()
        level = "Easy"
        if st.session_state.score >= 85: level = "Hard"
        elif st.session_state.score >= 60: level = "Medium"
        st.info(f"建議挑戰等級：{level}")
        st.progress(st.session_state.score / 100)
        page = st.radio("導航中心", ["🏠 願景大廳", "🔬 基礎邏輯館", "🏗️ 進階電路區", "🔄 數據轉換站", "🎓 智慧考評中心", "🎨 城市規劃室"])
        if st.button("🚪 安全登出"): st.session_state.clear(); st.rerun()

    if page == "🏠 願景大廳":
        st.title("歡迎回到 LogiMind 控制中心")
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Operating_system_placement.svg/240px-Operating_system_placement.svg.png", width=150)
        st.header("📖 城市治理與邏輯百科")
        st.markdown("""
        作為 LogiMind 的管理員，您的責任是確保整座城市的邏輯能量穩定流動。
        
        ### 🗺️ 指南文字介紹
        * **🔬 基礎邏輯館**：研究數位世界的最基本單元。這裡的每個邏輯閘都有其獨特的真值表，定義了電壓如何轉換。
        * **🏗️ 進階電路區**：組合基礎單元以實現複雜功能。您將學習到全加器、D正反器等核心架構。
        * **🎓 智慧考評中心**：系統會根據您的答題表現，動態解鎖更難的題目。
        
        ### 📘 核心理論提示
        在數位邏輯中，**真值表**是唯一的真理。它列出了所有輸入與對應輸出的組合。請確保您在挑戰大師難度前，已經熟記了 XOR 與 NAND 的特性。
        """)

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
        st.image(urls[g], width=300)
        
        st.subheader("📊 關鍵：真值表 (現在絕對可見)")
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
        
        # 使用修復後的 HTML 渲染函數
        render_truth_table(df)

    elif page == "🏗️ 進階電路區":
        st.header("🏗️ 進階電路架構")
        adv = st.selectbox("選擇組件", ["全加器", "D正反器"])
        if adv == "全加器":
            st.image("https://upload.wikimedia.org/wikipedia/commons/a/a9/Full-adder.svg", width=400)
        else:
            st.image("https://upload.wikimedia.org/wikipedia/commons/2/2f/D-Type_Flip-flop_Symbol.svg", width=300)

    elif page == "🎓 智慧考評中心":
        st.header(f"🎓 檢定等級: {level}")
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

    elif page == "🔄 數據轉換站":
        st.header("🔄 數據編碼轉換器")
        val = st.text_input("輸入二進制 (如 1011)", "1011")
        if val:
            try:
                v = int(val, 2)
                gray = bin(v ^ (v >> 1))[2:].zfill(len(val))
                st.success(f"格雷碼轉換結果: {gray}")
            except: st.error("格式錯誤")

    elif page == "🎨 城市規劃室":
        st.header("🎨 風格個性化")
        c1, c2 = st.columns(2)
        with c1: new_bg = st.color_picker("背景顏色", p['bg'])
        with c2: new_btn = st.color_picker("按鈕顏色", p['btn'])
        if st.button("套用修改"):
            st.session_state.prefs['bg'] = new_bg
            st.session_state.prefs['btn'] = new_btn
            st.rerun()

# --- 登入頁 ---
if "name" not in st.session_state:
    st.set_page_config(page_title="LogiMind 入口", layout="centered")
    st.title("🛡️ LogiMind 系統啟動")
    name = st.text_input("管理員代號")
    if st.button("建立連接"):
        if name: st.session_state.name = name; st.rerun()
else:
    st.set_page_config(page_title=f"LogiMind - {st.session_state.name}", layout="wide")
    main()
