import streamlit as st
import pandas as pd
import random
import os
import time

# ==================================================
# 1. V130 核心初始化
# ==================================================
st.set_page_config(page_title="LogiMind V130", layout="wide")

if "name" not in st.session_state:
    st.session_state.update({
        "name": "",
        "level": "初級管理員",
        "used_ids": [],
        "prefs": {"bg": "#0E1117", "btn": "#FF4B4B", "fs": 18}
    })

# ==================================================
# 2. 權限與工具函數
# ==================================================
def has_access(rank):
    if st.session_state.name.lower() == "frank": return True
    order = ["初級管理員", "中級管理員", "高級工程師", "終端管理員"]
    try:
        return order.index(st.session_state.level) >= order.index(rank)
    except:
        return False

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# ==================================================
# 3. 視覺防護引擎 (V130 強化版)
# ==================================================
def apply_css():
    p = st.session_state.prefs
    bg_hex = p['bg'].lstrip('#')
    r, g, b = tuple(int(bg_hex[i:i+2], 16) for i in (0, 2, 4))
    txt_color = "#000000" if (r*0.299 + g*0.587 + b*0.114) > 140 else "#FFFFFF"
    
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {p['bg']} !important; color: {txt_color}; }}
    h1, h2, h3, h4, p, span, div, label {{ color: {txt_color} !important; font-size: {p['fs']}px !important; }}
    
    /* 登出按鈕專用樣式 */
    .logout-btn {{ border: 2px solid red; color: red; background: transparent; }}
    
    /* 圖片與表格強制白底黑字 */
    div[data-testid="stImage"] {{ background-color: white !important; padding: 15px; border-radius: 10px; }}
    .stDataFrame, .stTable {{ width: 100% !important; }}
    div[data-testid="stDataFrame"] div[role="grid"], .stTable {{ background-color: white !important; color: black !important; }}
    div[data-testid="stDataFrame"] th, .stTable th {{ background-color: #eee !important; color: black !important; text-align: center !important; }}
    div[data-testid="stDataFrame"] td, .stTable td {{ color: black !important; text-align: center !important; }}
    
    /* 按鈕 */
    .stButton>button {{ background-color: {p['btn']} !important; color: white !important; border-radius: 8px; width: 100%; }}
    </style>
    """, unsafe_allow_html=True)

# ==================================================
# 4. 題庫與邏輯功能庫
# ==================================================
def load_questions():
    q_list = []
    if os.path.exists("questions.txt"):
        try:
            with open("questions.txt", "r", encoding="utf-8") as f:
                for line in f:
                    p = line.strip().split("|")
                    if len(p) == 5: q_list.append({"id": p[0], "diff": p[1], "q": p[2], "o": p[3].split(","), "a": p[4]})
        except: pass
    return q_list

# ==================================================
# 5. 主程式架構
# ==================================================
def main():
    apply_css()
    is_frank = st.session_state.name.lower() == "frank"
    
    with st.sidebar:
        st.title("🏙️ LogiMind V130")
        st.caption(f"User: {st.session_state.name}")
        if is_frank: st.warning("★ 終端特權模式")
        else: st.info(f"等級: {st.session_state.level}")
        st.divider()
        
        # V130 全新導航結構：數位邏輯五大支柱
        m_home = "🏠 系統概覽"
        m_gate = "🔬 1. 基礎邏輯閘 (Gates)"
        m_math = "🔢 2. 數碼運算 (Math)"
        m_simp = "🧮 3. 化簡邏輯 (Simplification)"
        m_comb = "🔀 4. 組合邏輯 (Combinational)" # NEW
        m_seq  = "🔄 5. 序向邏輯 (Sequential)"    # NEW
        m_exam = "🎓 智慧考評 (Exam)"
        m_set  = "🎨 設定與登出"
        
        # 權限過濾
        menu = [m_home, m_gate, m_math, m_exam]
        
        # 中級解鎖：化簡
        if is_frank or has_access("中級管理員"): menu.append(m_simp)
        else: menu.append("🔒 化簡邏輯 (需中級)")
            
        # 高級解鎖：組合邏輯
        if is_frank or has_access("高級工程師"): menu.append(m_comb)
        else: menu.append("🔒 組合邏輯 (需高級)")
            
        # 終端解鎖：序向邏輯
        if is_frank or has_access("終端管理員"): menu.append(m_seq)
        else: menu.append("🔒 序向邏輯 (需終端)")
            
        menu.append(m_set)
        page = st.radio("功能模組", menu)

    # --- 0. 首頁 ---
    if page == m_home:
        st.header("🏠 LogiMind V130 知識架構")
        st.markdown("""
        **V130 更新日誌：** 已整合數位邏輯全領域知識。
        
        * **第一層：基礎閘** (AND, OR, NOT...)
        * **第二層：數碼系統** (二/八/十/十六進制)
        * **第三層：布林代數與卡諾圖** (邏輯化簡)
        * **第四層：組合邏輯** (MUX, DeMUX, Encoder, Decoder)
        * **第五層：序向邏輯** (Flip-Flops, Counters)
        """)
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/AND_ANSI.svg/120px-AND_ANSI.svg.png", width=100)

    # --- 1. 基礎邏輯 ---
    elif page == m_gate:
        st.header("🔬 基礎邏輯閘與真值表")
        g = st.selectbox("選擇元件", ["AND", "OR", "XOR", "NAND", "NOR", "NOT"])
        
        # 動態生成真值表數據
        data = {"A": [0,0,1,1], "B": [0,1,0,1]}
        if g == "AND": data["Y"] = [0,0,0,1]
        elif g == "OR":  data["Y"] = [0,1,1,1]
        elif g == "XOR": data["Y"] = [0,1,1,0]
        elif g == "NAND":data["Y"] = [1,1,1,0]
        elif g == "NOR": data["Y"] = [1,0,0,0]
        elif g == "NOT": data = {"In": [0,1], "Out": [1,0]}
        
        c1, c2 = st.columns(2)
        c1.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
        
        # 圖片映射
        urls = {
            "AND": "https://upload.wikimedia.org/wikipedia/commons/6/64/AND_ANSI.svg",
            "OR": "https://upload.wikimedia.org/wikipedia/commons/b/b5/OR_ANSI.svg",
            "XOR": "https://upload.wikimedia.org/wikipedia/commons/0/01/XOR_ANSI.svg",
            "NAND": "https://upload.wikimedia.org/wikipedia/commons/f/f2/NAND_ANSI.svg",
            "NOR": "https://upload.wikimedia.org/wikipedia/commons/6/6c/NOR_ANSI.svg",
            "NOT": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/NOT_ANSI.svg/250px-NOT_ANSI.svg.png"
        }
        c2.image(urls[g], caption=f"{g} Gate", width=250)

    # --- 2. 數碼運算 ---
    elif page == m_math:
        st.header("🔢 進制轉換與運算")
        tab1, tab2 = st.tabs(["進制轉換", "ALU 運算"])
        
        with tab1:
            val = st.text_input("輸入數值", "1010")
            base = st.selectbox("來源基底", [2, 8, 10, 16])
            try:
                dec = int(val, base)
                st.write(f"Dec (10): {dec}")
                st.write(f"Bin (2):  {bin(dec)[2:]}")
                st.write(f"Hex (16): {hex(dec)[2:].upper()}")
            except: st.error("格式錯誤")
            
        with tab2:
            n1 = st.text_input("Bin A", "10")
            n2 = st.text_input("Bin B", "01")
            if st.button("A + B"):
                res = int(n1, 2) + int(n2, 2)
                st.success(f"結果: {bin(res)[2:]} (Dec: {res})")

    # --- 3. 化簡邏輯 (布林 + KMap) ---
    elif "化簡" in page:
        st.header("🧮 布林代數與卡諾圖")
        st.subheader("De Morgan's Laws (笛摩根定律)")
        st.latex(r"(A + B)' = A' \cdot B'")
        st.latex(r"(AB)' = A' + B'")
        
        st.divider()
        st.subheader("2變數卡諾圖求解")
        c1, c2 = st.columns(2)
        m0 = c1.checkbox("00", False)
        m1 = c2.checkbox("01", False)
        m2 = c1.checkbox("10", False)
        m3 = c2.checkbox("11", False)
        
        st.write("化簡結果：")
        if m0 and m1 and m2 and m3: st.code("1")
        elif m0 and m1: st.code("A'")
        elif m2 and m3: st.code("A")
        elif m0 and m2: st.code("B'")
        elif m1 and m3: st.code("B")
        else: st.write("選取更多相鄰項以化簡...")
        
        

    # --- 4. 組合邏輯 (V130 NEW) ---
    elif "組合" in page:
        st.header("🔀 組合邏輯電路 (Combinational Logic)")
        st.info("輸出僅取決於當前輸入，無記憶功能。")
        
        st.subheader("4-to-1 多工器 (Multiplexer)")
        st.write("MUX 原理：根據選擇線 (S1, S0) 決定哪個資料輸入 (D) 通過。")
        
        col_ctrl, col_data = st.columns([1, 2])
        with col_ctrl:
            s1 = st.selectbox("Select S1", [0, 1])
            s0 = st.selectbox("Select S0", [0, 1])
        with col_data:
            d0 = st.number_input("Data D0", 0, 1, 0)
            d1 = st.number_input("Data D1", 0, 1, 1)
            d2 = st.number_input("Data D2", 0, 1, 0)
            d3 = st.number_input("Data D3", 0, 1, 1)
            
        # MUX Logic
        sel = (s1 << 1) | s0
        inputs = [d0, d1, d2, d3]
        out = inputs[sel]
        
        st.success(f"選擇線 S1S0 = {s1}{s0} (Index {sel})")
        st.metric("MUX 輸出 (Y)", out)
        
        

[Image of 4-to-1 multiplexer circuit diagram]


    # --- 5. 序向邏輯 (V130 NEW) ---
    elif "序向" in page:
        st.header("🔄 序向邏輯電路 (Sequential Logic)")
        st.info("輸出取決於當前輸入與過去狀態 (記憶功能)。")
        
        st.subheader("JK 觸發器 (Flip-Flop) 模擬")
        st.write("狀態表分析：")
        
        # 互動輸入
        c1, c2, c3 = st.columns(3)
        j = c1.selectbox("J Input", [0, 1])
        k = c2.selectbox("K Input", [0, 1])
        q_curr = c3.selectbox("目前狀態 Q(t)", [0, 1])
        
        # JK Logic
        q_next = 0
        status = ""
        if j == 0 and k == 0:
            q_next = q_curr
            status = "保持 (No Change)"
        elif j == 0 and k == 1:
            q_next = 0
            status = "重置 (Reset)"
        elif j == 1 and k == 0:
            q_next = 1
            status = "設定 (Set)"
        elif j == 1 and k == 1:
            q_next = 1 - q_curr
            status = "反轉 (Toggle)"
            
        st.table(pd.DataFrame({
            "J": [j], "K": [k], "Q(t)": [q_curr], 
            "Q(t+1) 下一態": [q_next], "模式": [status]
        }))
        
        

    # --- 6. 考評 ---
    elif page == m_exam:
        st.header("🎓 智慧考評")
        qs = load_questions()
        if not qs: st.warning("請建立 questions.txt")
        else:
            pool = [q for q in qs if q['id'] not in st.session_state.used_ids]
            if not pool: 
                st.success("題庫已完成！")
                if st.button("重置"): st.session_state.used_ids = []; st.rerun()
            else:
                q = random.choice(pool)
                st.write(f"**{q['q']}**")
                ans = st.radio("Ans:", q['o'], key=q['id'])
                if st.button("提交"):
                    if ans == q['a']: 
                        st.success("正確!")
                        if st.session_state.level == "初級管理員": st.session_state.level = "中級管理員"
                    else: st.error(f"錯誤，答案是 {q['a']}")
                    st.session_state.used_ids.append(q['id'])
                    st.rerun()

    # --- 7. 設定與登出 (Frank 要求 2) ---
    elif page == m_set:
        st.header("🎨 個人化與帳戶")
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("介面配色")
            st.session_state.prefs['bg'] = st.color_picker("背景", st.session_state.prefs['bg'])
            st.session_state.prefs['btn'] = st.color_picker("按鈕", st.session_state.prefs['btn'])
            st.session_state.prefs['fs'] = st.slider("字體", 14, 28, st.session_state.prefs['fs'])
            if st.button("套用設定"): st.rerun()
            
        with c2:
            st.subheader("帳戶操作")
            st.warning("登出將清除所有暫存資料並返回首頁。")
            if st.button("🚪 安全登出系統"):
                logout()

# ==================================================
# 6. 入口
# ==================================================
if not st.session_state.name:
    apply_css()
    st.title("🏙️ LogiMind V130 入口")
    n = st.text_input("輸入代碼 (Frank)")
    if st.button("登入"):
        if n: st.session_state.name = n; st.rerun()
else:
    main()
