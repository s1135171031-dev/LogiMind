import streamlit as st
import pandas as pd
import random
import time

# =========================================
# 1. 專業題庫定義 (您可以隨時增加題目)
# =========================================
QUESTION_BANK = [
    {"q": "AND 閘的輸入為 1 和 0 時，輸出為何？", "o": ["0", "1"], "a": "0"},
    {"q": "OR 閘的輸入為 1 和 0 時，輸出為何？", "o": ["0", "1"], "a": "1"},
    {"q": "NOT 閘輸入為 1 時，輸出為何？", "o": ["0", "1"], "a": "0"},
    {"q": "XOR 閘輸入相同時（如 1,1），輸出為何？", "o": ["0", "1"], "a": "0"},
    {"q": "哪種邏輯閘又被稱為『互斥或閘』？", "o": ["AND", "XOR"], "a": "XOR"},
    {"q": "二進位 10 (Dec:2) 轉換為格雷碼為何？", "o": ["11", "01"], "a": "11"},
    {"q": "格雷碼 11 轉換為二進位為何？", "o": ["10", "11"], "a": "10"},
    {"q": "全加器比半加器多了哪一個輸入？", "o": ["進位輸入 Ci", "時脈 Clk"], "a": "進位輸入 Ci"},
    {"q": "2對4解碼器有幾個輸出端？", "o": ["2", "4"], "a": "4"},
    {"q": "布林代數中 A + 0 等於？", "o": ["A", "0"], "a": "A"},
    # ... (您可以依照此格式補足到 20 題或更多)
]

# =========================================
# 2. 語系與視覺 (加入強制白底圖片修正)
# =========================================
LANG_PACK = {
    "繁體中文": {
        "title": "🏙️ LogiMind 數位邏輯城",
        "menu": ["🏠 願景大廳", "🔬 基礎邏輯館", "🏗️ 進階電路區", "🔄 格雷碼轉換大樓", "📡 網路更新中心", "🎓 智慧考評中心", "🎨 個人化設定"],
    },
    "English": {
        "title": "🏙️ LogiMind Digital City",
        "menu": ["🏠 Hall of Vision", "🔬 Logic Gate Lab", "🏗️ Advanced Circuit", "🔄 Gray Code Tower", "📡 Network Update", "🎓 Smart Exam", "🎨 Personalization"],
    }
}

def apply_style(p):
    txt_color = "#000000" if (int(p['bg'].lstrip('#'), 16) > 0x888888) else "#FFFFFF"
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {p['bg']} !important; }}
    h1, h2, h3, p, span, label, li {{ color: {txt_color} !important; font-size: {p['fs']}px !important; }}
    
    /* 圖片背景修正：強制所有圖片放在白底卡片中，並加上邊距 */
    div[data-testid="stImage"] {{
        background-color: #FFFFFF !important;
        padding: 20px !important;
        border-radius: 15px !important;
        display: flex;
        justify-content: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }}
    .table-container {{ background-color: #FFFFFF !important; padding: 15px; border-radius: 10px; margin: 10px 0; }}
    .logic-table td, .logic-table th {{ color: #000!important; border: 1px solid #ddd; padding: 8px; }}
    </style>
    """, unsafe_allow_html=True)

# =========================================
# 3. 功能邏輯 (格雷碼雙向轉換)
# =========================================
def bin_to_gray(b_str):
    try:
        n = int(b_str, 2)
        return bin(n ^ (n >> 1))[2:].zfill(len(b_str))
    except: return "N/A"

def gray_to_bin(g_str):
    try:
        b = g_str[0]
        for i in range(1, len(g_str)):
            b += str(int(b[-1]) ^ int(g_str[i]))
        return b
    except: return "N/A"

# =========================================
# 4. 初始化與主程式
# =========================================
for key, val in {"score": 0, "level": "初級管理員", "exam_active": False, "net_data": "系統已連線", 
                 "prefs": {"bg":"#0E1117", "btn":"#00D4FF", "fs": 18, "lang": "繁體中文"}}.items():
    if key not in st.session_state: st.session_state[key] = val

def main():
    p = st.session_state.prefs
    L = LANG_PACK[p['lang']]
    apply_style(p)
    
    with st.sidebar:
        st.title(L["title"])
        st.write(f"管理員: **{st.session_state.name}**")
        st.write(f"等級: **{st.session_state.level}**")
        st.divider()
        page = st.radio("選單", L["menu"], label_visibility="collapsed")
        if st.button("登出"): st.session_state.clear(); st.rerun()

    # --- 願景大廳 ---
    if page in ["🏠 願景大廳", "🏠 Hall of Vision"]:
        st.title("🏙️ 數位邏輯指揮中心")
        c1, c2, c3 = st.columns(3)
        c1.metric("管理等級", st.session_state.level)
        c2.metric("最高考評分數", f"{st.session_state.score}/100")
        c3.metric("安全同步", "已加密")
        
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.1); padding:20px; border-radius:15px; border-left: 5px solid {p['btn']};">
        <h3>📢 歡迎回來，{st.session_state.name}</h3>
        這座城市建立在 0 與 1 的基礎之上。身為管理員，您的任務是掌握信號的流向，並通過考評來升級您的權限。
        </div>
        """, unsafe_allow_html=True)
        st.image("https://upload.wikimedia.org/wikipedia/commons/6/64/AND_ANSI.svg", width=300)

    # --- 基礎邏輯館 ---
    elif page in ["🔬 基礎邏輯館", "🔬 Logic Gate Lab"]:
        st.header(page)
        gate = st.selectbox("選擇閘極", ["AND", "OR", "XOR", "NOT"])
        img_urls = {
            "AND": "https://upload.wikimedia.org/wikipedia/commons/6/64/AND_ANSI.svg",
            "OR": "https://upload.wikimedia.org/wikipedia/commons/b/b5/OR_ANSI.svg",
            "XOR": "https://upload.wikimedia.org/wikipedia/commons/0/01/XOR_ANSI.svg",
            "NOT": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/NOT_ANSI.svg/250px-NOT_ANSI.svg.png"
        }
        st.image(img_urls[gate], width=250)
        st.write(f"💡 目前雲端資料：{st.session_state.net_data}")

    # --- 進階電路區 ---
    elif page in ["🏗️ 進階電路區", "🏗️ Advanced Circuit"]:
        st.header("🏗️ 進階模組研究")
        tab1, tab2 = st.tabs(["全加器", "解碼器"])
        with tab1:
            st.write("全加器（Full Adder）是運算核心。")
            st.image("https://upload.wikimedia.org/wikipedia/commons/a/a9/Full-adder.svg", width=400)
        with tab2:
            st.write("2對4解碼器。")
            st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/1_bit_Decoder_2-to-4_line_zh_hant.svg/960px-1_bit_Decoder_2-to-4_line_zh_hant.svg.png", width=400)

    # --- 格雷碼大樓 ---
    elif page in ["🔄 格雷碼轉換大樓", "🔄 Gray Code Tower"]:
        st.header("🔄 格雷碼雙向中心")
        c1, c2 = st.columns(2)
        with c1:
            b_in = st.text_input("Binary -> Gray", "1011")
            st.success(f"結果: {bin_to_gray(b_in)}")
        with c2:
            g_in = st.text_input("Gray -> Binary", "1110")
            st.info(f"結果: {gray_to_bin(g_in)}")
        
        # 4-bit Table
        st.subheader("📋 4-Bit 對照表")
        df = pd.DataFrame([{"Dec": i, "Bin": bin(i)[2:].zfill(4), "Gray": bin_to_gray(bin(i)[2:].zfill(4))} for i in range(16)])
        st.table(df)

    # --- 智慧考評中心 (完善題庫系統) ---
    elif page in ["🎓 智慧考評中心", "🎓 Smart Exam"]:
        st.header("🎓 管理員晉升檢定")
        if not st.session_state.exam_active:
            st.write("準備好進行 10 題核心邏輯檢定嗎？（目前題庫提供 10 題精華）")
            if st.button("開始測驗"):
                st.session_state.exam_active = True
                st.rerun()
        else:
            with st.form("exam"):
                user_answers = []
                for i, item in enumerate(QUESTION_BANK):
                    st.write(f"**Q{i+1}: {item['q']}**")
                    user_answers.append(st.radio("選擇答案", item['o'], key=f"q_{i}", horizontal=True))
                
                if st.form_submit_button("提交測驗"):
                    correct_count = sum(1 for ua, item in zip(user_answers, QUESTION_BANK) if ua == item['a'])
                    final_score = int((correct_count / len(QUESTION_BANK)) * 100)
                    st.session_state.score = final_score
                    st.session_state.level = "高級工程師" if final_score >= 80 else "中級管理員" if final_score >= 60 else "初級管理員"
                    st.session_state.exam_active = False
                    st.success(f"測驗完成！得分：{final_score}。您的等級已更新為：{st.session_state.level}")
                    st.rerun()

    # --- 網路更新中心 ---
    elif page in ["📡 網路更新中心", "📡 Network Update"]:
        st.header("📡 全球網路同步")
        if st.button("執行同步掃描"):
            with st.spinner("正在爬取 IEEE 規格..."):
                time.sleep(1.5)
                st.session_state.net_data = f"同步成功！最後更新：{time.strftime('%H:%M:%S')}"
                st.success(st.session_state.net_data)

    # --- 個人化設定 ---
    elif page in ["🎨 個人化設定", "🎨 Personalization"]:
        st.header("🎨 介面自定義")
        new_fs = st.slider("字體大小", 14, 30, p['fs'])
        new_bg = st.color_picker("系統背景", p['bg'])
        if st.button("儲存並套用"):
            st.session_state.prefs.update({"bg": new_bg, "fs": new_fs})
            st.rerun()

# --- 登入流程 ---
if "name" not in st.session_state:
    st.title("🛡️ LogiMind 行政特區登入")
    name = st.text_input("管理員授權代號")
    if st.button("進入城市"):
        if name: st.session_state.name = name; st.rerun()
else:
    st.set_page_config(page_title="LogiMind V55", layout="wide")
    main()
