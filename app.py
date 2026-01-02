import streamlit as st
import pandas as pd
import random
import time

# =========================================
# 1. 語系與字典包 (繁中/EN)
# =========================================
TEXTS = {
    "繁體中文": {
        "title": "🏙️ LogiMind 數位城",
        "vision": "🏠 願景大廳",
        "logic_lab": "🔬 基礎邏輯館",
        "circuit": "🏗️ 進階電路區",
        "gray": "🔄 格雷碼大樓",
        "exam": "🎓 智慧考評中心",
        "boolean": "🧮 布林代數室 (中級解鎖)",
        "kmap": "🗺️ 卡諾圖實驗室 (高級解鎖)",
        "math": "➕ 數位運算中心 (專家解鎖)",
        "config": "🎨 個人化中心",
        "locked": "🔒 權限不足，請提升等級",
        "welcome": "歡迎，管理員",
        "rank": "權限等級",
        "score_last": "上次得分",
        "sync": "同步雲端",
        "logout": "登出",
        "start_exam": "開始動態測驗",
        "submit": "提交報告",
        "save": "儲存並套用"
    },
    "English": {
        "title": "🏙️ LogiMind City",
        "vision": "🏠 Vision Hall",
        "logic_lab": "🔬 Logic Lab",
        "circuit": "🏗️ Circuit Area",
        "gray": "🔄 Gray Tower",
        "exam": "🎓 Exam Center",
        "boolean": "🧮 Boolean Room (Med)",
        "kmap": "🗺️ K-Map Lab (High)",
        "math": "➕ Math Center (Expert)",
        "config": "🎨 Personalization",
        "locked": "🔒 Insufficient Rank",
        "welcome": "Welcome, Admin",
        "rank": "Current Rank",
        "score_last": "Last Score",
        "sync": "Sync Cloud",
        "logout": "Logout",
        "start_exam": "Start Exam",
        "submit": "Submit Exam",
        "save": "Save & Apply"
    }
}

# =========================================
# 2. 隨機動態題庫 (按難度分類)
# =========================================
BANK = {
    "Junior": [
        {"q": "AND 閘輸入 (1,0) 為何？", "o": ["0", "1"], "a": "0"},
        {"q": "OR 閘輸入 (1,0) 為何？", "o": ["0", "1"], "a": "1"},
        {"q": "NOT 閘輸入 0 為何？", "o": ["0", "1"], "a": "1"},
        {"q": "XOR 閘輸入 (1,1) 為何？", "o": ["0", "1"], "a": "0"},
        {"q": "NAND 閘輸入 (1,1) 為何？", "o": ["0", "1"], "a": "0"}
    ],
    "Medium": [
        {"q": "2進位 1011 轉格雷碼？", "o": ["1110", "1101"], "a": "1110"},
        {"q": "布林代數 A + A' = ?", "o": ["1", "0"], "a": "1"},
        {"q": "半加器有幾個輸出？", "o": ["2", "1"], "a": "2"},
        {"q": "全加器 Ci 的功能是？", "o": ["進位輸入", "時脈"], "a": "進位輸入"},
        {"q": "狄摩根定律 (A+B)' = ?", "o": ["A'·B'", "A'+B'"], "a": "A'·B'"}
    ],
    "High": [
        {"q": "4對1 MUX 需要幾條選擇線？", "o": ["2", "4"], "a": "2"},
        {"q": "JK 觸發器 J=1, K=1 時狀態？", "o": ["Toggle", "Reset"], "a": "Toggle"},
        {"q": "格雷碼 1000 轉二進位？", "o": ["1111", "1000"], "a": "1111"},
        {"q": "卡諾圖中相鄰項合併可消去？", "o": ["變數", "雜訊"], "a": "變數"},
        {"q": "3位元同步計數器最大模數？", "o": ["8", "7"], "a": "8"}
    ]
}

# =========================================
# 3. 核心視覺引擎 (Mobile Ready & Anti-Contrast)
# =========================================
def apply_custom_style():
    p = st.session_state.prefs
    # 計算亮度來決定文字顏色 (黑或白)
    bg = p['bg'].lstrip('#')
    r, g, b = tuple(int(bg[i:i+2], 16) for i in (0, 2, 4))
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    txt_color = "#000000" if brightness > 128 else "#FFFFFF"
    
    st.markdown(f"""
    <style>
    /* 全域設定 */
    .stApp {{ background-color: {p['bg']} !important; color: {txt_color}; }}
    h1, h2, h3, p, span, label, li, .stMarkdown {{ color: {txt_color} !important; font-size: {p['fs']}px !important; }}
    
    /* 按鈕個性化 */
    button[kind="primary"], .stButton>button {{
        background-color: {p['btn']} !important;
        color: white !important;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
        width: 100%; /* 手機版按鈕全寬化 */
    }}

    /* 強制白底圖片卡片 */
    [data-testid="stImage"] {{
        background-color: #FFFFFF !important;
        padding: 15px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        margin: 10px auto;
    }}

    /* 手機頁面間距優化 */
    @media (max-width: 640px) {{
        .main .block-container {{ padding: 1rem !important; }}
        h1 {{ font-size: 1.5rem !important; }}
    }}
    
    /* 表格自動白底防止文字衝突 */
    .stTable, .table-container {{ 
        background-color: #FFFFFF !important; 
        color: #000000 !important; 
        border-radius: 10px; 
        padding: 10px; 
    }}
    </style>
    """, unsafe_allow_html=True)

# =========================================
# 4. 權限檢查邏輯
# =========================================
def check_permission(required_rank):
    if st.session_state.name.lower() == "frank":
        return True
    ranks = ["初級管理員", "中級管理員", "高級工程師", "終端管理員"]
    try:
        user_idx = ranks.index(st.session_state.level)
        req_idx = ranks.index(required_rank)
        return user_idx >= req_idx
    except:
        return False

# =========================================
# 5. 初始化 Session
# =========================================
if "score" not in st.session_state:
    st.session_state.update({
        "score": 0, "level": "初級管理員", "exam_active": False,
        "name": "", "prefs": {
            "bg": "#0E1117", "btn": "#FF4B4B", "fs": 18, "lang": "繁體中文"
        }
    })

# =========================================
# 6. 主程式
# =========================================
def main():
    p = st.session_state.prefs
    L = TEXTS[p['lang']]
    apply_custom_style()
    
    # 側邊導航
    with st.sidebar:
        st.title(L['title'])
        st.subheader(f"👤 {st.session_state.name}")
        st.caption(f"🛡️ {L['rank']}: {st.session_state.level}")
        st.divider()
        
        pages = [L['vision'], L['logic_lab'], L['circuit'], L['gray'], L['exam'], L['boolean'], L['kmap'], L['math'], L['config']]
        page = st.radio("MENU", pages, label_visibility="collapsed")
        
        if st.button(L['logout']): 
            st.session_state.clear()
            st.rerun()

    # --- 願景大廳 ---
    if page == L['vision']:
        st.title(f"🏙️ {L['welcome']}")
        c1, c2 = st.columns(2)
        c1.metric(L['rank'], st.session_state.level)
        c2.metric(L['score_last'], f"{st.session_state.score} pts")
        
        st.info("系統狀態：手機/桌機響應式模組已啟動。文字對比度保護已開啟。")
        

    # --- 基礎邏輯館 ---
    elif page == L['logic_lab']:
        st.header(L['logic_lab'])
        gate = st.selectbox("選取組件", ["AND", "OR", "NOT", "XOR"])
        urls = {
            "AND": "https://upload.wikimedia.org/wikipedia/commons/6/64/AND_ANSI.svg",
            "OR": "https://upload.wikimedia.org/wikipedia/commons/b/b5/OR_ANSI.svg",
            "NOT": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/NOT_ANSI.svg/250px-NOT_ANSI.svg.png",
            "XOR": "https://upload.wikimedia.org/wikipedia/commons/0/01/XOR_ANSI.svg"
        }
        st.image(urls[gate], width=300)

    # --- 智慧考評中心 (難度動態抽題) ---
    elif page == L['exam']:
        st.header(L['exam'])
        if not st.session_state.exam_active:
            st.write(f"目前等級：{st.session_state.level}。系統將根據等級出題。")
            if st.button(L['start_exam']):
                st.session_state.exam_active = True
                # 根據等級決定題庫
                diff = "Junior" if st.session_state.level == "初級管理員" else "Medium" if st.session_state.level == "中級管理員" else "High"
                st.session_state.current_quiz = random.sample(BANK[diff], 5)
                st.rerun()
        else:
            with st.form("quiz"):
                score = 0
                for i, q in enumerate(st.session_state.current_quiz):
                    st.write(f"**Q{i+1}: {q['q']}**")
                    ans = st.radio("Ans", q['o'], key=f"q_{i}", horizontal=True)
                    if ans == q['a']: score += 20
                if st.form_submit_button(L['submit']):
                    st.session_state.score = score
                    if score >= 80:
                        ranks = ["初級管理員", "中級管理員", "高級工程師", "終端管理員"]
                        cur_idx = ranks.index(st.session_state.level)
                        if cur_idx < 2: st.session_state.level = ranks[cur_idx+1]
                    st.session_state.exam_active = False
                    st.success(f"考試結束！得分：{score}")
                    st.rerun()

    # --- 權限鎖定區：布林代數 ---
    elif page == L['boolean']:
        if check_permission("中級管理員"):
            st.header("🧮 布林代數運算中心")
            st.code("A · (A + B) = A")
            st.write("布林化簡功能已解鎖。")
            
        else:
            st.warning(L['locked'])

    # --- 權限鎖定區：卡諾圖 ---
    elif page == L['kmap']:
        if check_permission("高級工程師"):
            st.header("🗺️ 卡諾圖化簡實驗室")
            st.write("2-4 變數卡諾圖矩陣已就緒。")
            
        else:
            st.warning(L['locked'])

    # --- 個人化中心 ---
    elif page == L['config']:
        st.header(L['config'])
        c1, c2 = st.columns(2)
        with c1:
            lang = st.selectbox("Language", ["繁體中文", "English"], index=0 if p['lang']=="繁體中文" else 1)
            fs = st.slider("Font Size", 12, 32, p['fs'])
        with c2:
            bg_c = st.color_picker("Background", p['bg'])
            btn_c = st.color_picker("Button", p['btn'])
            
        if st.button(L['save']):
            st.session_state.prefs.update({"lang": lang, "fs": fs, "bg": bg_c, "btn": btn_c})
            st.rerun()

# --- 登入頁面 ---
if not st.session_state.name:
    st.set_page_config(page_title="LogiMind Login", layout="centered")
    apply_custom_style()
    st.title("🏙️ LogiMind 授權入口")
    name = st.text_input("Admin Code", placeholder="Type 'frank' for full access")
    if st.button("Unlock System"):
        if name:
            st.session_state.name = name
            if name.lower() == "frank": 
                st.session_state.level = "終端管理員"
            st.rerun()
else:
    st.set_page_config(page_title="LogiMind City V60", layout="wide")
    main()
