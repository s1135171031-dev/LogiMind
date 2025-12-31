import streamlit as st
import pandas as pd
import json
import os
import re
from datetime import datetime

# =========================================
# 1. 視覺純淨化與樣式引擎 (徹底隱藏灰色文字)
# =========================================
def apply_theme(p):
    # 注入 CSS 隱藏所有 Streamlit 標記 (footer, header, burger menu)
    hide_style = f"""
    <style>
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    .stApp {{
        background-color: {p['bg']}; 
        color: {p['txt_color']};
        font-size: {p['font_size']}px;
    }}
    .stButton>button {{
        background-color: {p['btn']}; 
        color: white; 
        border-radius: {p['radius']}px;
        border: none;
        transition: 0.3s;
    }}
    .stButton>button:hover {{ border: 2px solid white; }}
    div[data-testid="stTable"] {{ background-color: white; color: black; border-radius: 10px; }}
    </style>
    """
    st.markdown(hide_style, unsafe_allow_html=True)

# =========================================
# 2. 專業對稱繪圖引擎 (V20 核心)
# =========================================
SVG_LIB = {
    "AND": '''<svg viewBox="0 0 120 70" width="180"><path d="M40,10 H50 A25,25 0 0,1 50,60 H40 Z" fill="none" stroke="black" stroke-width="3"/><line x1="10" y1="25" x2="40" y2="25" stroke="black" stroke-width="3"/><line x1="10" y1="45" x2="40" y2="45" stroke="black" stroke-width="3"/><line x1="75" y1="35" x2="110" y2="35" stroke="black" stroke-width="3"/></svg>''',
    "OR": '''<svg viewBox="0 0 120 70" width="180"><path d="M35,10 Q50,35 35,60 Q70,60 95,35 Q70,10 35,10 Z" fill="none" stroke="black" stroke-width="3"/><line x1="10" y1="25" x2="38" y2="25" stroke="black" stroke-width="3"/><line x1="10" y1="45" x2="38" y2="45" stroke="black" stroke-width="3"/><line x1="95" y1="35" x2="115" y2="35" stroke="black" stroke-width="3"/></svg>''',
    "FA": '''<svg viewBox="0 0 260 130" width="300"><rect x="80" y="15" width="100" height="100" fill="white" stroke="black" stroke-width="3"/><text x="130" y="70" text-anchor="middle" font-family="Arial" font-weight="bold" font-size="14">Full Adder</text><text x="35" y="40" font-size="14">A</text><line x1="50" y1="35" x2="80" y2="35" stroke="black" stroke-width="2.5"/><text x="35" y="65" font-size="14">B</text><line x1="50" y1="60" x2="80" y2="60" stroke="black" stroke-width="2.5"/><text x="25" y="95" font-size="14">Cin</text><line x1="55" y1="90" x2="80" y2="90" stroke="black" stroke-width="2.5"/><line x1="180" y1="40" x2="210" y2="40" stroke="black" stroke-width="2.5"/><text x="220" y="45" font-size="14" text-anchor="start">Sum</text><line x1="180" y1="80" x2="210" y2="80" stroke="black" stroke-width="2.5"/><text x="220" y="85" font-size="14" text-anchor="start">Cout</text></svg>''',
    "ENCODER": '''<svg viewBox="0 0 260 160" width="300"><rect x="80" y="15" width="100" height="120" fill="white" stroke="black" stroke-width="3"/><text x="130" y="80" text-anchor="middle" font-weight="bold" font-size="14">Encoder</text><text x="40" y="40" font-size="14">D3</text><line x1="65" y1="35" x2="80" y2="35" stroke="black" stroke-width="2"/><text x="40" y="65" font-size="14">D2</text><line x1="65" y1="60" x2="80" y2="60" stroke="black" stroke-width="2"/><text x="40" y="90" font-size="14">D1</text><line x1="65" y1="85" x2="80" y2="85" stroke="black" stroke-width="2"/><text x="40" y="115" font-size="14">D0</text><line x1="65" y1="110" x2="80" y2="110" stroke="black" stroke-width="2"/><line x1="180" y1="50" x2="210" y2="50" stroke="black" stroke-width="2"/><text x="220" y="55" font-size="14" text-anchor="start">Y1</text><line x1="180" y1="90" x2="210" y2="90" stroke="black" stroke-width="2"/><text x="220" y="95" font-size="14" text-anchor="start">Y0</text></svg>'''
}

def render_svg(key, p):
    st.markdown(f'''<div style="display: table; margin: 15px auto; padding: 25px; background: white; border-radius: {p['radius']}px; border: 4px solid {p['btn']}; box-shadow: 0 8px 16px rgba(0,0,0,0.2);">{SVG_LIB[key]}</div>''', unsafe_allow_html=True)

# =========================================
# 3. 資料庫與爬蟲統整資料
# =========================================
DB_FILE = "logimind_v21_master.json"
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return {}
def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(db, f, indent=4)

WEB_KNOWLEDGE = [
    {"site": "All About Circuits", "url": "https://www.allaboutcircuits.com", "topic": "Digital Logic Fundamentals"},
    {"site": "Electronics Tutorials", "url": "https://www.electronics-tutorials.ws", "topic": "Combinational Logic Gates"},
    {"site": "GeeksforGeeks", "url": "https://www.geeksforgeeks.org/digital-electronics-logic-design-tutorials", "topic": "CS Perspective Logic Design"},
    {"site": "CircuitVerse", "url": "https://circuitverse.org", "topic": "Online Simulator & Interactive Learning"},
    {"site": "Electrical4U", "url": "https://www.electrical4u.com", "topic": "Digital Electronics Encyclopedia"},
    {"site": "DigiKey TechForum", "url": "https://forum.digikey.com", "topic": "Practical Logic IC Implementation"},
    {"site": "NPTEL", "url": "https://nptel.ac.in", "topic": "Advanced Digital Circuits Video Lectures"},
    {"site": "FPGA4Fun", "url": "https://www.fpga4fun.com", "topic": "Logic Design into Hardware (FPGA)"},
    {"site": "Learn About Electronics", "url": "http://www.learnabout-electronics.org", "topic": "Binary Arithmetic & Counters"},
    {"site": "TutorialsPoint", "url": "https://www.tutorialspoint.com", "topic": "Digital Circuits Quick Guide"}
]

# =========================================
# 4. 考試 20 題庫
# =========================================
QUIZ_DATA = [
    ("AND 閘輸入為 (1, 0) 時輸出為何？", ["0", "1"], "0"),
    ("OR 閘輸入為 (1, 0) 時輸出為何？", ["0", "1"], "1"),
    ("NOT 閘輸入為 0 時輸出為何？", ["0", "1"], "1"),
    ("XOR 閘輸入相同時輸出為何？", ["0", "1"], "0"),
    ("全加器比半加器多了哪一個輸入？", ["B", "Cin", "S"], "Cin"),
    ("2對4解碼器有幾個輸出端？", ["2", "4", "8"], "4"),
    ("8進制數字 7 的二進制是？", ["111", "110", "101"], "111"),
    ("卡諾圖 (K-map) 主要用於？", ["電路模擬", "化簡布林函數", "測量電壓"], "化簡布林函數"),
    ("D型正反器在時鐘觸發時會？", ["保持原值", "跟隨輸入D", "反轉輸出"], "跟隨輸入D"),
    ("JK正反器當 J=1, K=1 時會？", ["保持", "歸零", "反轉(Toggle)"], "反轉(Toggle)"),
    ("十六進制 F 的十進制值是？", ["14", "15", "16"], "15"),
    ("一個 4 位元二進制數最大值是？", ["7", "15", "31"], "15"),
    ("下列何者是萬用閘 (Universal Gate)？", ["AND", "NAND", "OR"], "NAND"),
    ("De Morgan 定律中，!(A & B) 等於？", ["!A & !B", "!A | !B", "A | B"], "!A | !B"),
    ("多工器 (MUX) 1011 選擇線有兩條，輸出端有幾個？", ["1", "2", "4"], "1"),
    ("4對2編碼器 (Encoder) 當 D2=1 時，Y1Y0輸出為？", ["00", "10", "11"], "10"),
    ("正反器 (Flip-Flop) 是屬於哪種電路？", ["組合電路", "時序電路", "類比電路"], "時序電路"),
    ("摩爾定律與下列何者最相關？", ["電晶體數量", "電池容量", "螢幕解析度"], "電晶體數量"),
    ("二進制 1010 + 0001 = ？", ["1011", "1111", "1000"], "1011"),
    ("布林運算 A + 1 等於？", ["0", "A", "1"], "1")
]

# =========================================
# 5. 主系統流程
# =========================================
def auth_gate():
    apply_theme({"bg":"#0E1117","txt_color":"white","btn":"#3B82F6","font_size":16,"radius":8})
    st.title("🛡️ LogiMind V21 終極旗艦版")
    tab1, tab2 = st.tabs(["🔑 登入", "📝 快速註冊"])
    with tab2:
        u = st.text_input("新帳號 (限英數)", key="ru")
        p = st.text_input("密碼", type="password", key="rp")
        if st.button("確認註冊"):
            if re.match("^[a-zA-Z0-9]+$", u):
                db = load_db()
                db[u] = {"pw":p, "favs":[], "scores":[], "prefs":{"bg":"#0E1117","btn":"#00FFCC","txt_color":"#FFFFFF","font_size":16,"radius":12}}
                save_db(db); st.success("註冊成功！")
            else: st.error("請勿使用中文")
    with tab1:
        ul, pl = st.text_input("帳號", key="lu"), st.text_input("密碼", type="password", key="lp")
        if st.button("進入系統"):
            db = load_db()
            if ul in db and db[ul]["pw"] == pl:
                st.session_state.user, st.session_state.prefs = ul, db[ul]["prefs"]
                st.session_state.favs = db[ul].get("favs", [])
                st.session_state.scores = db[ul].get("scores", [])
                st.rerun()

def main():
    p = st.session_state.prefs
    apply_theme(p)
    db = load_db()

    with st.sidebar:
        st.title(f"👤 {st.session_state.user}")
        page = st.radio("選單", ["🏠 首頁", "🔬 實驗室", "📝 20題挑戰賽", "📊 分數查詢", "🌐 網路修復與統整", "⚙️ 個人化與數據管理", "🆙 更新傳奇", "🚪 登出"])

    if page == "🏠 首頁":
        st.header(f"歡迎來到 LogiMind 旗艦版")
        st.success("視覺純淨化已啟動：灰色字體已全數移除。")
        render_svg("FA", p)

    elif page == "🔬 實驗室":
        st.header("邏輯組件庫")
        g = st.selectbox("選擇組件", ["AND", "OR", "ENCODER", "FA"])
        render_svg(g, p)

    elif page == "📝 20題挑戰賽":
        st.header("🧠 邏輯設計 20 題檢定")
        if "quiz_start" not in st.session_state:
            st.warning("您準備好開始 20 題考試了嗎？這將會列入歷史分數紀錄。")
            if st.button("🔥 我準備好了，開始考試！"):
                st.session_state.quiz_start = True
                st.rerun()
        else:
            score = 0
            with st.form("quiz_form"):
                ans_list = []
                for i, (q, opts, a) in enumerate(QUIZ_DATA):
                    ans_list.append(st.radio(f"{i+1}. {q}", opts, key=f"q{i}"))
                if st.form_submit_button("送出試卷"):
                    for i in range(20):
                        if ans_list[i] == QUIZ_DATA[i][2]: score += 5
                    new_score = {"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "score": score}
                    st.session_state.scores.append(new_score)
                    db[st.session_state.user]["scores"] = st.session_state.scores
                    save_db(db)
                    st.balloons()
                    st.success(f"考試結束！您的分數是：{score} 分")
                    del st.session_state.quiz_start

    elif page == "📊 分數查詢":
        st.header("📈 歷史分數紀錄")
        if not st.session_state.scores: st.info("尚無考試紀錄")
        else: st.table(pd.DataFrame(st.session_state.scores))

    elif page == "🌐 網路修復與統整":
        st.header("🌐 邏輯設計網頁大數據")
        if st.button("🚀 執行爬蟲同步更新 (模擬)"):
            with st.spinner("正在抓取最新網頁資料..."):
                st.table(pd.DataFrame(WEB_KNOWLEDGE))
                st.success("已從 10 個核心網站完成數據更新！")

    elif page == "⚙️ 個人化與數據管理":
        t1, t2 = st.tabs(["🎨 億點個人化", "🛠️ 手動數據實驗室"])
        with t1:
            st.session_state.prefs['bg'] = st.color_picker("背景顏色", p['bg'])
            st.session_state.prefs['btn'] = st.color_picker("主題按鈕顏色", p['btn'])
            st.session_state.prefs['font_size'] = st.slider("全域字體大小", 12, 30, p['font_size'])
            st.session_state.prefs['radius'] = st.slider("元件圓角程度", 0, 30, p['radius'])
            if st.button("💾 儲存所有個人化設定"):
                db[st.session_state.user]["prefs"] = st.session_state.prefs
                save_db(db); st.rerun()
        with t2:
            st.warning("⚠️ 此處可手動修改 JSON 資料庫 (慎用)")
            raw_data = st.text_area("JSON 原始數據", json.dumps(db[st.session_state.user], indent=4, ensure_ascii=False))
            if st.button("📝 覆蓋手動更改"):
                db[st.session_state.user] = json.loads(raw_data)
                save_db(db); st.rerun()

    elif page == "🆙 更新傳奇":
        st.header("📜 LogiMind 演進史")
        logs = {
            "版本": ["V0-V5", "V6-V10", "V11-V15", "V16-V20", "V21 (Final)"],
            "重大更新內容": [
                "核心邏輯運算建立，文字模式介面。",
                "導入 SVG 繪圖，解決邏輯閘視覺化問題。",
                "帳號系統與 JSON 資料庫持久化開發。",
                "視覺大修正：解決文字縫合、白條與破圖。",
                "旗艦整合：20題考試、爬蟲統整、個人化、視覺純淨化。"
            ]
        }
        st.table(pd.DataFrame(logs))

    elif page == "🚪 登出":
        del st.session_state.user; st.rerun()

if "user" not in st.session_state: auth_gate()
else: main()