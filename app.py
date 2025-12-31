import streamlit as st
import pandas as pd

# =========================================
# 1. 視覺引擎：強制黑字 HTML 表格與樣式
# =========================================
def apply_style(p):
    # 根據背景亮度決定主文字顏色
    txt_color = "#000000" if (int(p['bg'].lstrip('#'), 16) > 0x888888) else "#FFFFFF"
    
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {p['bg']} !important; }}
    h1, h2, h3, h4, p, span, label, li {{ color: {txt_color} !important; }}
    
    /* 圖片卡片化 */
    div[data-testid="stImage"] {{
        background-color: #FFFFFF !important;
        padding: 20px !important;
        border-radius: 15px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
        margin-bottom: 20px !important;
    }}

    /* 強制下拉選單與輸入框為白底黑字 */
    div[data-baseweb="select"] > div, input {{
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }}
    div[data-baseweb="select"] span {{ color: #000000 !important; }}

    /* 自定義 HTML 表格樣式：解決白底白字 */
    .table-container {{
        background-color: #FFFFFF !important;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }}
    .logic-table {{
        width: 100%;
        border-collapse: collapse;
        color: #000000 !important;
    }}
    .logic-table th, .logic-table td {{
        border: 1px solid #DDDDDD;
        padding: 10px;
        text-align: center;
        color: #000000 !important; /* 強制每一格都是黑字 */
    }}
    .logic-table th {{ background-color: #F2F2F2; }}
    </style>
    """, unsafe_allow_html=True)

# 渲染真值表的函數
def render_logic_table(df):
    html = '<div class="table-container"><table class="logic-table"><thead><tr>'
    html += ''.join(f'<th>{col}</th>' for col in df.columns) + '</tr></thead><tbody>'
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
        {"q": "哪種邏輯閘在輸入為 0 時輸出為 1？", "o": ["AND", "OR", "NOT"], "a": "NOT"}
    ],
    "Medium": [
        {"q": "XOR 閘在兩輸入相同時，輸出為何？", "o": ["0", "1"], "a": "0"},
        {"q": "2對4解碼器輸入為 10 (2)，哪條輸出線為 1？", "o": ["Y0", "Y2"], "a": "Y2"}
    ],
    "Hard": [
        {"q": "D正反器在觸發前保持數值，這稱為？", "o": ["鎖存 (Latch)", "重置 (Reset)"], "a": "鎖存 (Latch)"},
        {"q": "布林代數 A + AB 等於？", "o": ["A", "B"], "a": "A"}
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
        st.title("🏙️ LogiMind V51")
        st.write(f"管理員: **{st.session_state.name}**")
        st.divider()
        page = st.radio("導航中心", ["🏠 願景大廳", "🔬 基礎邏輯館", "🏗️ 進階電路區", "🎓 智慧考評中心", "🎨 城市規劃室"])
        if st.button("安全登出"):
            st.session_state.clear()
            st.rerun()

    # --- 1. 願景大廳：超長文字介紹 ---
    if page == "🏠 願景大廳":
        st.title("歡迎來到 LogiMind：數位邏輯之城指揮部 ")
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Operating_system_placement.svg/240px-Operating_system_placement.svg.png", width=120)
        
        st.header("📜 第一章：數位邏輯的演進與城市的誕生")
        st.write("""
        在二十世紀中葉，當人類第一次嘗試將數學運算自動化時，Claude Shannon 發現了布林代數與電子開關之間的驚人連結。
        這一發現奠定了我們今天所在這座「LogiMind 數位之城」的所有基石。在這裡，複雜的邏輯不再是紙上的公式，而是流動的電子脈衝。
        
        作為這座城市的管理員，您正在操控著人類文明最偉大的發明——數位邏輯。從最簡單的燈泡開關到現代的超級電腦，
        其核心邏輯依然遵循著您將在基礎邏輯館中學到的那七大閘極。當你覺得熟練了，辦去了解進階電路區在做什麼吧!!!
        """)
        
        st.header("🏗️ 第二章：系統架構與學習路徑")
        st.markdown("""
        為了讓管理員能有系統地掌握知識，LogiMind 規劃了以下學習路徑，請務必詳細閱讀：
        
        1. **初探原子結構 (基礎邏輯館)**：
           在這裡，您將學習數位電路的「原子」——邏輯閘。我們會展示 ANSI 標準符號以及絕對正確的真值表。
           請注意，真值表是工程師的聖經，它定義了每一個元件在面對 0 與 1 組合時的法律行為。
           
        2. **構建功能模組 (進階電路區)**：
           當您掌握了原子，就可以開始建造「分子」。例如，兩個邏輯閘可以組成一個半加器，
           而多個半加器可以組成執行人類算術運算的中央處理器 (CPU)。我們也會在這裡介紹『正反器』，
           這讓電路擁有了記憶，是電腦存儲數據的根本。
           
        3. **智慧檢定與晉升 (智慧考評中心)**：
           系統內建了 AI 評核機制。您的每一場測驗都會被記錄，當您的積分累積到一定程度，
           系統會自動將難度從初級調整為大師級。這不僅是測試，更是您對這座城市掌控權的證明。

        4. **進階表格與編碼 (格雷碼轉換大樓)**：
            當你了解了邏輯閘與進階電路後，這裡能幫助你將格雷碼與二進制互相轉換，在邏輯設計中
            是一個很重要的角色，讓你在操控機械時可以更準確，不會產生誤差。
        """)
        
        st.header("🛠️ 第三章：管理員操作手冊")
        st.info("""
        * **主題自定義**：在城市規劃室中，您可以自由調整背景色與按鈕顏色。
        * **動態數據觀察**：本系統備有網路連接功能，若您感覺邏輯閘顯示詭異，請立即與網路連接。
        * **實時模擬**：請多利用格雷碼轉換大樓來練習二進制與格雷碼的切換，這在工業自動化中極其重要。
        """)
        st.write("---")
        st.caption("LogiMind V51 - 致力於提供最精準的數位邏輯教育體驗。")

    # --- 2. 基礎邏輯館：修復真值表 ---
    elif page == "🔬 基礎邏輯館":
        st.header("🔬 基礎邏輯視覺符號")
        g = st.selectbox("選擇組件", ["AND", "OR", "NOT", "XOR"])
        urls = {
            "AND": "https://upload.wikimedia.org/wikipedia/commons/6/64/AND_ANSI.svg",
            "OR": "https://upload.wikimedia.org/wikipedia/commons/b/b5/OR_ANSI.svg",
            "NOT": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Not_gate_ansi.svg",
            "XOR": "https://upload.wikimedia.org/wikipedia/commons/0/01/XOR_ANSI.svg"
        }
        st.image(urls[g], width=250)
        
        st.subheader("📊 靜態真值表")
        if g == "NOT":
            df = pd.DataFrame({"A": [0, 1], "Y": [1, 0]})
        else:
            data = {"A": [0,0,1,1], "B": [0,1,0,1]}
            if g=="AND": data["Y"]=[0,0,0,1]
            elif g=="OR": data["Y"]=[0,1,1,1]
            elif g=="XOR": data["Y"]=[0,1,1,0]
            df = pd.DataFrame(data)
        
        render_logic_table(df)

    # --- 3. 進階電路區 ---
    elif page == "🏗️ 進階電路區":
        st.header("🏗️ 進階電路模組")
        adv = st.radio("選擇電路", ["全加器", "半加器"])
        if adv == "全加器":
            st.image("https://upload.wikimedia.org/wikipedia/commons/a/a9/Full-adder.svg", width=350)
            st.write("全加器考慮了低位的進位，是執行多位元加法的基礎。")
        else:
            st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Half_Adder.svg/500px-Half_Adder.svg.png", width=250)
            st.write("半加器不考慮低位的進位，是執行最基礎單位元加法以及構成全加器的基礎。")

    # --- 4. 智慧考評 ---
    elif page == "🎓 智慧考評中心":
        st.header("🎓 智慧檢定系統")
        # 簡單示例
        q = QUESTION_BANK["Easy"][0]
        st.write(f"**題目: {q['q']}**")
        ans = st.radio("選擇答案", q['o'])
        if st.button("提交"):
            if ans == q['a']: st.success("正確！")
            else: st.error("錯誤，再試一次。")

    # --- 5. 城市規劃室：修復語法錯誤 ---
    elif page == "🎨 城市規劃室":
        st.header("🎨 風格自定義面板")
        new_bg = st.color_picker("城市背景色", p['bg'])
        new_btn = st.color_picker("按鈕強調色", p['btn'])
        
        # 這裡完整修復了語法錯誤
        if st.button("儲存並套用設定"):
            st.session_state.prefs['bg'] = new_bg
            st.session_state.prefs['btn'] = new_btn
            st.success("設定已更新，正在重新載入城市...")
            st.rerun()

# --- 啟動入口 ---
if "name" not in st.session_state:
    st.set_page_config(page_title="LogiMind 入口", layout="centered")
    st.title("🛡️ LogiMind 管理員登入")
    name = st.text_input("輸入代號")
    if st.button("啟動系統"):
        if name:
            st.session_state.name = name
            st.rerun()
else:
    st.set_page_config(page_title=f"LogiMind - {st.session_state.name}", layout="wide")
    main()



