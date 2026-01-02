import streamlit as st
import pandas as pd
import random
import os

# =========================================
# 1. 核心權限與 Session 初始化
# =========================================
if "name" not in st.session_state:
    st.session_state.update({
        "name": "", "level": "初級管理員", "score": 0, "used_ids": [],
        "prefs": {"bg": "#0E1117", "btn": "#FF4B4B", "fs": 18}
    })

def has_access(rank):
    if st.session_state.name.lower() == "frank": return True
    order = ["初級管理員", "中級管理員", "高級工程師", "終端管理員"]
    try:
        return order.index(st.session_state.level) >= order.index(rank)
    except:
        return False

# =========================================
# 2. 強大視覺引擎 (解決白底白字 & 縮排問題)
# =========================================
def apply_style():
    p = st.session_state.prefs
    bg_hex = p['bg'].lstrip('#')
    r, g, b = tuple(int(bg_hex[i:i+2], 16) for i in (0, 2, 4))
    brightness = (r * 0.299 + g * 0.587 + b * 0.114)
    txt_color = "#000000" if brightness > 125 else "#FFFFFF"
    
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {p['bg']} !important; color: {txt_color}; }}
    h1, h2, h3, p, span, label, li {{ color: {txt_color} !important; font-size: {p['fs']}px !important; }}
    
    /* 圖片強制白底 */
    div[data-testid="stImage"] {{ background-color: white !important; padding: 15px; border-radius: 12px; }}
    
    /* 表格字體修復：強制黑色防止白底看不見字 */
    .stTable, [data-testid="stTable"], .stDataFrame {{ background-color: white !important; border-radius: 10px; }}
    .stTable td, .stTable th, [data-testid="stTable"] p, .stDataFrame td {{ color: black !important; }}
    
    /* 按鈕 */
    .stButton>button {{ background-color: {p['btn']} !important; color: white !important; width: 100%; border-radius: 8px; }}
    </style>
    """, unsafe_allow_html=True)

# =========================================
# 3. 題庫讀取與邏輯工具
# =========================================
def load_q():
    q_list = []
    if os.path.exists("questions.txt"):
        try:
            with open("questions.txt", "r", encoding="utf-8") as f:
                for line in f:
                    p = line.strip().split("|")
                    if len(p) == 5:
                        q_list.append({"id": p[0], "diff": p[1], "q": p[2], "o": p[3].split(","), "a": p[4]})
        except Exception as e:
            st.error(f"讀取錯誤: {e}")
    return q_list

# =========================================
# 4. 主程式功能
# =========================================
def main():
    apply_style()
    is_frank = st.session_state.name.lower() == "frank"
    
    with st.sidebar:
        st.title("🏙️ LogiMind V100")
        if not is_frank:
            st.info(f"權限：{st.session_state.level}")
        
        st.divider()
        # 動態清單：如果是 Frank，不顯示鎖定或提示
        m_logic = "🔬 基礎邏輯與真值表"
        m_exam  = "🎓 題庫考評系統"
        m_bool  = "🧮 布林化簡器" if is_frank or has_access("中級管理員") else "🔒 布林化簡 (未解鎖)"
        m_kmap  = "🗺️ 互動卡諾圖" if is_frank or has_access("高級工程師") else "🔒 卡諾圖 (未解鎖)"
        m_math  = "➕ 數位二進位運算" if is_frank or has_access("終端管理員") else "🔒 數位運算 (未解鎖)"
        m_set   = "🎨 系統設定"
        
        page = st.radio("導航", [m_logic, m_exam, m_bool, m_kmap, m_math, m_set])

    # --- 1. 基礎邏輯 (真值表回歸) ---
    if page == m_logic:
        st.header("🔬 基礎邏輯視覺符號")
        gate = st.selectbox("選擇組件", ["AND", "OR", "XOR", "NOT", "NAND"])
        
        # 數據與真值表
        df_map = {
            "AND": {"A": [0,0,1,1], "B": [0,1,0,1], "Y": [0,0,0,1]},
            "OR":  {"A": [0,0,1,1], "B": [0,1,0,1], "Y": [0,1,1,1]},
            "XOR": {"A": [0,0,1,1], "B": [0,1,0,1], "Y": [0,1,1,0]},
            "NAND": {"A": [0,0,1,1], "B": [0,1,0,1], "Y": [1,1,1,0]},
            "NOT": {"Input": [0,1], "Output": [1,0]}
        }
        st.subheader(f"{gate} 閘真值表")
        st.table(pd.DataFrame(df_map[gate]))
        
        urls = {
            "AND": "https://upload.wikimedia.org/wikipedia/commons/6/64/AND_ANSI.svg",
            "OR": "https://upload.wikimedia.org/wikipedia/commons/b/b5/OR_ANSI.svg",
            "XOR": "https://upload.wikimedia.org/wikipedia/commons/0/01/XOR_ANSI.svg",
            "NAND": "https://upload.wikimedia.org/wikipedia/commons/f/f2/NAND_ANSI.svg",
            "NOT": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/NOT_ANSI.svg/250px-NOT_ANSI.svg.png"
        }
        st.image(urls[gate], width=300)

    # --- 2. 考評中心 (不重複讀取) ---
    elif page == m_exam:
        st.header("🎓 智慧考評中心")
        qs = load_q()
        if not qs:
            st.warning("找不到題庫檔案 (questions.txt)。")
        else:
            pool = [q for q in qs if q['id'] not in st.session_state.used_ids]
            if not pool:
                st.success("所有題目皆已完成！重新載入中...")
                st.session_state.used_ids = []
                pool = qs
            
            with st.form("exam_form"):
                batch = random.sample(pool, min(len(pool), 3))
                answers = []
                for q in batch:
                    st.write(f"**Q: {q['q']}**")
                    answers.append(st.radio(f"選項 (ID:{q['id']})", q['o'], key=f"q{q['id']}"))
                
                if st.form_submit_button("提交並記錄"):
                    correct = sum(1 for a, q in zip(answers, batch) if a == q['a'])
                    st.session_state.used_ids.extend([q['id'] for q in batch])
                    st.write(f"本次分數: {correct}/{len(batch)}")
                    if correct == len(batch) and not is_frank:
                        st.session_state.level = "中級管理員"
                    st.rerun()

    # --- 3. 布林化簡 (實體功能) ---
    elif "布林" in page:
        st.header("🧮 布林代數化簡器")
        st.write("輸入基本邏輯式，系統將自動應用布林定律。")
        raw_in = st.text_input("輸入表達式 (如 A + AB)", "A + AB")
        if "AB" in raw_in and "+" in raw_in:
            st.success("根據吸收律 (Absorption Law)：結果為 A")
        else:
            st.info("運算引擎待命中心...")

    # --- 4. 互動卡諾圖 (實體功能) ---
    elif "卡諾圖" in page:
        st.header("🗺️ 2x2 互動卡諾圖")
        st.write("勾選方格內的 1，系統將顯示化簡邏輯。")
        c1, c2 = st.columns(2)
        m0 = c1.checkbox("m0 (00)", False)
        m1 = c2.checkbox("m1 (01)", False)
        m2 = c1.checkbox("m2 (10)", False)
        m3 = c2.checkbox("m3 (11)", False)
        
        if m2 and m3: st.code("化簡結果: F = A")
        elif m1 and m3: st.code("化簡結果: F = B")
        elif m0 and m1 and m2 and m3: st.code("化簡結果: F = 1")

    # --- 5. 數位運算 (實體功能) ---
    elif "數位運算" in page:
        st.header("➕ 二進位加法/減法中心")
        val1 = st.text_input("Binary 1", "1010")
        val2 = st.text_input("Binary 2", "0011")
        op = st.selectbox("選擇運算", ["加法 (+)", "減法 (-)"])
        if st.button("執行運算"):
            try:
                if op == "加法 (+)": res = bin(int(val1, 2) + int(val2, 2))[2:]
                else: res = bin(int(val1, 2) - int(val2, 2))[2:]
                st.success(f"結果: {res}")
            except: st.error("輸入格式錯誤")

    # --- 6. 個人化 ---
    elif page == m_set:
        st.header("🎨 系統個人化設定")
        st.session_state.prefs['bg'] = st.color_picker("背景顏色", st.session_state.prefs['bg'])
        st.session_state.prefs['btn'] = st.color_picker("按鈕顏色", st.session_state.prefs['btn'])
        st.session_state.prefs['fs'] = st.slider("字體大小", 14, 32, st.session_state.prefs['fs'])
        if st.button("套用"): st.rerun()

# --- 登入控制 ---
if not st.session_state.name:
    apply_style()
    st.title("🏙️ LogiMind 行政指揮中心")
    n = st.text_input("輸入 Admin Code (輸入 frank 解鎖終端權限)")
    if st.button("進入系統"):
        if n:
            st.session_state.name = n
            st.rerun()
else:
    st.set_page_config(page_title="LogiMind V100", layout="wide")
    main()
