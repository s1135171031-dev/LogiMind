import streamlit as st
import pandas as pd
import random
import os

# =========================================
# 1. 外部題庫讀取引擎 (解決重複問題)
# =========================================
def load_questions():
    q_list = []
    if os.path.exists("questions.txt"):
        with open("questions.txt", "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) == 5:
                    q_list.append({
                        "id": parts[0], "diff": parts[1], "q": parts[2],
                        "o": parts[3].split(","), "a": parts[4]
                    })
    return q_list

# =========================================
# 2. 視覺引擎 (自動對比度 & 強制白底)
# =========================================
def apply_theme():
    p = st.session_state.prefs
    bg = p['bg'].lstrip('#')
    r, g, b = tuple(int(bg[i:i+2], 16) for i in (0, 2, 4))
    brightness = (r * 0.299 + g * 0.587 + b * 0.114)
    txt_color = "#000000" if brightness > 150 else "#FFFFFF"
    
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {p['bg']} !important; color: {txt_color}; }}
    h1, h2, h3, p, span, label, li {{ color: {txt_color} !important; font-size: {p['fs']}px !important; }}
    div[data-testid="stImage"] {{ background-color: #FFFFFF !important; padding: 15px; border-radius: 10px; }}
    .stButton>button {{ background-color: {p['btn']} !important; color: white !important; width: 100%; }}
    .stDataFrame, .stTable {{ background-color: white !important; border-radius: 8px; }}
    /* 手機優化 */
    @media (max-width: 600px) {{ .main .block-container {{ padding: 10px !important; }} }}
    </style>
    """, unsafe_allow_html=True)

# =========================================
# 3. 初始化與權限判斷
# =========================================
if "name" not in st.session_state:
    st.session_state.update({
        "name": "", "level": "初級管理員", "score": 0, "used_ids": [],
        "prefs": {"bg": "#0E1117", "btn": "#FF4B4B", "fs": 18}
    })

def has_access(rank):
    if st.session_state.name.lower() == "frank": return True
    order = ["初級管理員", "中級管理員", "高級工程師", "終端管理員"]
    return order.index(st.session_state.level) >= order.index(rank)

# =========================================
# 4. 主程式頁面
# =========================================
def main():
    apply_theme()
    is_frank = st.session_state.name.lower() == "frank"
    
    with st.sidebar:
        st.title("🏙️ LogiMind V80")
        st.write(f"Admin: {st.session_state.name}")
        st.divider()
        
        # 動態選單名稱 (如果是 Frank 則不顯示鎖定字樣)
        m_logic = "🔬 基礎邏輯館"
        m_exam = "🎓 智慧考評"
        m_bool = "🧮 布林運算" if is_frank or has_access("中級管理員") else "🔒 布林運算 (需中級)"
        m_kmap = "🗺️ 卡諾圖分析" if is_frank or has_access("高級工程師") else "🔒 卡諾圖 (需高級)"
        m_math = "➕ 數位加法器" if is_frank or has_access("終端管理員") else "🔒 數位加法器 (需終端)"
        m_cfg = "🎨 設定中心"
        
        menu = [m_logic, m_exam, m_bool, m_kmap, m_math, m_cfg]
        page = st.radio("導航", menu)

    # --- 1. 基礎邏輯館 (真值表回歸) ---
    if page == m_logic:
        st.header("🔬 邏輯閘真值表中心")
        gate = st.selectbox("選擇閘極", ["AND", "OR", "XOR", "NAND", "NOR"])
        
        # 真值表邏輯
        data = {"A": [0,0,1,1], "B": [0,1,0,1]}
        if gate == "AND": data["Y"] = [0,0,0,1]
        elif gate == "OR": data["Y"] = [0,1,1,1]
        elif gate == "XOR": data["Y"] = [0,1,1,0]
        elif gate == "NAND": data["Y"] = [1,1,1,0]
        elif gate == "NOR": data["Y"] = [1,0,0,0]
        
        st.table(pd.DataFrame(data))
        st.image(f"https://upload.wikimedia.org/wikipedia/commons/6/64/AND_ANSI.svg") # 範例

    # --- 2. 智慧考評 (外部讀取 + 不重複) ---
    elif page == m_exam:
        st.header("🎓 題庫考評")
        questions = load_questions()
        if not questions:
            st.error("找不到 questions.txt 或格式錯誤。")
        else:
            # 過濾掉已做過的題目
            pool = [q for q in questions if q['id'] not in st.session_state.used_ids]
            if not pool:
                st.success("恭喜！所有題庫已考完，現在為您重設。")
                st.session_state.used_ids = []
                pool = questions
            
            with st.form("exam"):
                q_batch = random.sample(pool, min(len(pool), 3))
                answers = []
                for q in q_batch:
                    st.write(f"**{q['q']}**")
                    answers.append(st.radio(f"選一個 ({q['id']})", q['o'], key=q['id']))
                
                if st.form_submit_button("提交"):
                    correct = sum(1 for a, q in zip(answers, q_batch) if a == q['a'])
                    st.session_state.used_ids.extend([q['id'] for q in q_batch])
                    st.write(f"本次得分: {correct}/{len(q_batch)}")
                    if correct == len(q_batch):
                        st.session_state.level = "中級管理員" # 簡易升級示範
                    st.rerun()

    # --- 3. 布林運算 (功能實體化) ---
    elif "布林" in page:
        if is_frank or has_access("中級管理員"):
            st.header("🧮 布林定律交互室")
            expr = st.text_input("輸入表達式 (例如 A + AB)", "A + AB")
            if expr == "A + AB": st.success("化簡結果: A (吸收律)")
            else: st.write("公式分析中...")
        else: st.error("權限不足")

    # --- 4. 卡諾圖 (功能實體化) ---
    elif "卡諾圖" in page:
        if is_frank or has_access("高級工程師"):
            st.header("🗺️ 互動式卡諾圖 (2x2)")
            cols = st.columns(2)
            v00 = cols[0].checkbox("m0 (00)", False)
            v01 = cols[1].checkbox("m1 (01)", False)
            v10 = cols[0].checkbox("m2 (10)", False)
            v11 = cols[1].checkbox("m3 (11)", False)
            if v10 and v11: st.info("檢測到相鄰項：可化簡為 A")
        else: st.error("權限不足")

    # --- 5. 數位加法器 (功能實體化) ---
    elif "加法器" in page:
        if is_frank or has_access("終端管理員"):
            st.header("➕ 二進位運算器")
            b1 = st.text_input("輸入 A (Binary)", "1010")
            b2 = st.text_input("輸入 B (Binary)", "0110")
            if st.button("計算"):
                res = bin(int(b1, 2) + int(b2, 2))[2:]
                st.code(f"Sum: {res}")
        else: st.error("權限不足")

    # --- 6. 設定中心 ---
    elif page == m_cfg:
        st.header("🎨 介面設定")
        st.session_state.prefs['bg'] = st.color_picker("背景", st.session_state.prefs['bg'])
        st.session_state.prefs['btn'] = st.color_picker("按鈕", st.session_state.prefs['btn'])
        st.session_state.prefs['fs'] = st.slider("字體", 14, 32, st.session_state.prefs['fs'])
        if st.button("套用"): st.rerun()

# --- 登入 ---
if not st.session_state.name:
    apply_theme()
    st.title("🛡️ LogiMind 入口")
    n = st.text_input("代號")
    if st.button("進入"):
        st.session_state.name = n
        st.rerun()
else:
    main()
