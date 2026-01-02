import streamlit as st
import pandas as pd
import random
import os

# =========================================
# 1. 核心設定與 Frank 權限系統
# =========================================
if "name" not in st.session_state:
    st.session_state.update({
        "name": "", "level": "初級管理員", "score": 0, "used_ids": [],
        "prefs": {"bg": "#0E1117", "btn": "#FF4B4B", "fs": 18}
    })

def has_access(rank):
    # 終端管理員 Frank 擁有最高權限且不顯示鎖定字樣
    if st.session_state.name.lower() == "frank": return True
    order = ["初級管理員", "中級管理員", "高級工程師", "終端管理員"]
    try:
        return order.index(st.session_state.level) >= order.index(rank)
    except:
        return False

# =========================================
# 2. 視覺防護引擎 (強制修復白底白字)
# =========================================
def apply_advanced_theme():
    p = st.session_state.prefs
    # 計算背景亮度
    bg_hex = p['bg'].lstrip('#')
    r, g, b = tuple(int(bg_hex[i:i+2], 16) for i in (0, 2, 4))
    brightness = (r * 0.299 + g * 0.587 + b * 0.114)
    # 主文字顏色
    txt_color = "#000000" if brightness > 128 else "#FFFFFF"
    
    st.markdown(f"""
    <style>
    /* 全域文字與背景 */
    .stApp {{ background-color: {p['bg']} !important; color: {txt_color}; }}
    h1, h2, h3, p, span, label, li {{ color: {txt_color} !important; font-size: {p['fs']}px !important; }}
    
    /* 強制圖片白底容器 (要求 2) */
    div[data-testid="stImage"] {{
        background-color: #FFFFFF !important;
        padding: 20px !important;
        border-radius: 12px !important;
        border: 2px solid #EEE;
    }}

    /* 強制修復表格內文字 (解決字不見問題) */
    .stTable, [data-testid="stTable"], .stDataFrame {{
        background-color: #FFFFFF !important;
        border-radius: 10px;
    }}
    .stTable td, .stTable th, [data-testid="stTable"] p, .stDataFrame td {{
        color: #000000 !important; /* 強制表格字體為黑色 */
    }}

    /* 按鈕樣式與手機優化 (要求 6) */
    .stButton>button {{
        background-color: {p['btn']} !important;
        color: white !important;
        width: 100%;
        border-radius: 8px;
        padding: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

# =========================================
# 3. 題庫讀取 (要求 3, 4)
# =========================================
def load_q():
    q_list = []
    if os.path.exists("questions.txt"):
        with open("questions.txt", "r", encoding="utf-8") as f:
            for line in f:
                p = line.strip().split("|")
                if len(p) == 5: q_list.append({"id": p[0], "diff": p[1], "q": p[2], "o": p[3].split(","), "a": p[4]})
    return q_list

# =========================================
# 4. 主程式結構 (修正縮排錯誤)
# =========================================
def main():
    apply_advanced_theme()
    is_frank = st.session_state.name.lower() == "frank"
    
    with st.sidebar:
        st.title("🏙️ LogiMind V90")
        if not is_frank:
            st.info(f"當前等級：{st.session_state.level}")
        
        st.divider()
        # 選單邏輯 (要求 5: Frank 不顯示鎖定字樣)
        m1 = "🔬 基礎邏輯視覺符號"
        m2 = "🎓 智慧考評中心"
        m3 = "🧮 布林代數轉換" if is_frank or has_access("中級管理員") else "🔒 功能鎖定"
        m4 = "🗺️ 卡諾圖實驗室" if is_frank or has_access("高級工程師") else "🔒 功能鎖定"
        m5 = "➕ 數學運算中心" if is_frank or has_access("終端管理員") else "🔒 功能鎖定"
        m6 = "🎨 個人化中心"
        
        page = st.radio("功能選單", [m1, m2, m3, m4, m5, m6])

    # --- 1. 基礎邏輯館 (要求 3: 真值表) ---
    if page == m1:
        st.header("🔬 基礎邏輯館")
        gate = st.selectbox("選擇組件", ["AND", "OR", "XOR", "NOT"])
        
        st.subheader("真值表參考")
        df_data = {
            "AND": {"A": [0,0,1,1], "B": [0,1,0,1], "Y": [0,0,0,1]},
            "OR":  {"A": [0,0,1,1], "B": [0,1,0,1], "Y": [0,1,1,1]},
            "XOR": {"A": [0,0,1,1], "B": [0,1,0,1], "Y": [0,1,1,0]},
            "NOT": {"Input": [0,1], "Output": [1,0]}
        }
        st.table(pd.DataFrame(df_data[gate]))

        urls = {
            "AND": "https://upload.wikimedia.org/wikipedia/commons/6/64/AND_ANSI.svg",
            "OR": "https://upload.wikimedia.org/wikipedia/commons/b/b5/OR_ANSI.svg",
            "XOR": "https://upload.wikimedia.org/wikipedia/commons/0/01/XOR_ANSI.svg",
            "NOT": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/NOT_ANSI.svg/250px-NOT_ANSI.svg.png"
        }
        st.image(urls[gate], caption=f"{gate} Gate Symbol", width=300)

    # --- 2. 智慧考評中心 (要求 4: 不重複題庫) ---
    elif page == m2:
        st.header("🎓 考評中心")
        qs = load_q()
        if not qs:
            st.error("請檢查 questions.txt 檔案是否存在。")
        else:
            pool = [q for q in qs if q['id'] not in st.session_state.used_ids]
            if not pool:
                st.success("所有題目已答完，為您重新刷新題庫！")
                st.session_state.used_ids = []
                pool = qs
            
            with st.form("exam_form"):
                batch = random.sample(pool, min(len(pool), 3))
                answers = []
                for q in batch:
                    st.write(f"**{q['q']}**")
                    answers.append(st.radio(f"選項 ({q['id']})", q['o'], key=f"q_{q['id']}"))
                
                if st.form_submit_button("提交回答"):
                    correct = sum(1 for a, q in zip(answers, batch) if a == q['a'])
                    st.session_state.used_ids.extend([q['id'] for q in batch])
                    st.success(f"完成！正確：{correct}/{len(batch)}")
                    st.rerun()

    # --- 3. 布林代數 (要求 5) ---
    elif "布林" in page:
        st.header("🧮 布林代數轉換")
        st.code("F = A'B + AB = B(A' + A) = B")
        st.write("布林自動化簡引擎已啟動。")

    # --- 4. 卡諾圖 (要求 5) ---
    elif "卡諾圖" in page:
        st.header("🗺️ 卡諾圖實驗室")
        st.image("https://upload.wikimedia.org/wikipedia/commons/0/03/K-map_minterms_4x4.png", width=400)
        st.write("這是一個 4 變數卡諾圖，請根據邏輯值進行圈選。")

    # --- 5. 數學運算 (要求 5) ---
    elif "數學運算" in page:
        st.header("➕ 數位數學中心")
        st.subheader("二進位加法模擬")
        n1 = st.text_input("Binary A", "1101")
        n2 = st.text_input("Binary B", "1011")
        if st.button("計算"):
            res = bin(int(n1, 2) + int(n2, 2))[2:]
            st.success(f"結果為：{res}")

    # --- 6. 個人化中心 (要求 7) ---
    elif page == m6:
        st.header("🎨 個人化設定")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.prefs['bg'] = st.color_picker("系統背景顏色", st.session_state.prefs['bg'])
            st.session_state.prefs['btn'] = st.color_picker("按鈕強調色", st.session_state.prefs['btn'])
        with col2:
            st.session_state.prefs['fs'] = st.slider("系統字體大小", 14, 32, st.session_state.prefs['fs'])
        if st.button("儲存並刷新"): st.rerun()

# --- 登入介面 ---
if not st.session_state.name:
    apply_advanced_theme()
    st.title("🛡️ LogiMind 授權入口")
    user_input = st.text_input("輸入代碼", placeholder="frank")
    if st.button("解鎖"):
        if user_input:
            st.session_state.name = user_input
            st.rerun()
else:
    st.set_page_config(page_title="LogiMind V90", layout="wide")
    main()
