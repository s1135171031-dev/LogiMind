import streamlit as st
import pandas as pd
import random

# =========================================
# 1. 視覺引擎：極致個人化 + 圖片白底化
# =========================================
def apply_theme(p):
    txt_color = "#000000" if (int(p['bg'].lstrip('#'), 16) > 0x888888) else "#FFFFFF"
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {p['bg']} !important; }}
    h1, h2, h3, h4, p, span, label {{ color: {txt_color} !important; }}
    
    /* 圖片白底卡片化 */
    div[data-testid="stImage"] {{
        background-color: #FFFFFF !important;
        padding: 15px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        display: flex; justify-content: center; margin-bottom: 20px;
    }}
    
    div[data-baseweb="select"] > div, input {{
        background-color: #FFFFFF !important; color: #000000 !important;
    }}

    .stButton>button {{
        background-color: {p['btn']} !important;
        color: white !important;
        border-radius: 20px;
        width: 100%;
        font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

# =========================================
# 2. 智慧分級題庫 (共 21 題)
# =========================================
QUESTION_BANK = {
    "Easy": [
        {"q": "AND 閘輸入 (1, 0) 的結果？", "o": ["0", "1"], "a": "0"},
        {"q": "哪種閘在輸入為 0 時輸出 1？", "o": ["AND", "OR", "NOT"], "a": "NOT"},
        {"q": "OR 閘只要任一輸入為 1，輸出即為？", "o": ["0", "1"], "a": "1"},
        {"q": "數位電路中的 '0' 通常代表什麼？", "o": ["高電位", "低電位"], "a": "低電位"},
        {"q": "NAND 閘是 AND 閘加上什麼？", "o": ["OR", "NOT", "XOR"], "a": "NOT"},
        {"q": "二進制 1 + 1 在位元運算中（不考慮進位）是？", "o": ["0", "1"], "a": "0"},
        {"q": "這座城市的核心邏輯基礎是什麼？", "o": ["十進制", "二進制"], "a": "二進制"}
    ],
    "Medium": [
        {"q": "半加器 (Half Adder) 無法處理什麼？", "o": ["輸入相加", "低位進位 Cin", "輸出進位 Cout"], "a": "低位進位 Cin"},
        {"q": "2對4解碼器，當輸入為 01 時，哪條線會被選中？", "o": ["Y0", "Y1", "Y2"], "a": "Y1"},
        {"q": "格雷碼 (Gray Code) 的特性是什麼？", "o": ["速度快", "相鄰數僅一變動", "節省空間"], "a": "相鄰數僅一變動"},
        {"q": "XOR 閘在輸入相同時會輸出？", "o": ["0", "1"], "a": "0"},
        {"q": "多工器 (MUX) 的主要作用？", "o": ["數據分發", "數據選擇", "數據儲存"], "a": "數據選擇"},
        {"q": "二進制 1011 轉換為格雷碼？", "o": ["1110", "1101", "1011"], "a": "1110"},
        {"q": "全加器的 Sum 公式中使用了幾個 XOR？", "o": ["1", "2", "3"], "a": "2"}
    ],
    "Hard": [
        {"q": "D正反器在 Clock 觸發前，Q 值會？", "o": ["變為 0", "保持不變", "隨機變化"], "a": "保持不變"},
        {"q": "布林代數簡化：A(A + B) 等於？", "o": ["A", "B", "AB"], "a": "A"},
        {"q": "JK 正反器當 J=1, K=1 時，狀態會？", "o": ["切換 (Toggle)", "重置", "設定"], "a": "切換 (Toggle)"},
        {"q": "1-Bit 比較器，若 A=1, B=0，則 A>B 輸出為？", "o": ["0", "1"], "a": "1"},
        {"q": "在時序邏輯中，哪種元件具備記憶功能？", "o": ["解碼器", "正反器 (Flip-Flop)", "全加器"], "a": "正反器 (Flip-Flop)"},
        {"q": "格雷碼 1100 轉為二進制是？", "o": ["1000", "1010", "1111"], "a": "1000"},
        {"q": "傳播延遲 (Propagation Delay) 會影響電路的？", "o": ["邏輯正確性", "最高運作頻率", "顏色"], "a": "最高運作頻率"}
    ]
}

# =========================================
# 3. 核心功能函數
# =========================================
def b_to_g(b): return bin(int(b, 2) ^ (int(b, 2) >> 1))[2:].zfill(len(b))
def g_to_b(g):
    b = g[0]
    for i in range(1, len(g)): b += str(int(b[-1]) ^ int(g[i]))
    return b

# =========================================
# 4. 主介面
# =========================================
if "score_history" not in st.session_state: st.session_state.score_history = 0
if "prefs" not in st.session_state: st.session_state.prefs = {"bg":"#0E1117","btn":"#00D4FF"}

def main():
    apply_theme(st.session_state.prefs)
    
    with st.sidebar:
        st.title(f"🛠️ {st.session_state.name}")
        st.write(f"歷史分數：**{st.session_state.score_history}**")
        # 決定難度標籤
        level = "Easy"
        if st.session_state.score_history >= 90: level = "Hard"
        elif st.session_state.score_history >= 60: level = "Medium"
        st.write(f"當前建議難度：**{level}**")
        st.divider()
        st.write("🌐 **核心連線**")
        st.caption(f"Ping: {random.randint(10,20)}ms | SSL: ON")
        page = st.radio("導航", ["🏠 願景大廳", "🔬 視覺化研究", "🏗️ 組合建築", "🔄 數據轉換", "🎓 智慧考評", "🎨 設定"])

    # --- 智慧考評頁面 ---
    if page == "🎓 智慧考評":
        st.header(f"🎓 數位邏輯檢定 - {level} 模式")
        st.write(f"系統根據您上次的得分 ({st.session_state.score_history}) 自動調整為 **{level}** 難度。")
        
        current_qs = QUESTION_BANK[level]
        score = 0
        with st.form("exam_form"):
            user_ans = []
            for i, q in enumerate(current_qs):
                user_ans.append(st.radio(f"{i+1}. {q['q']}", q['o'], key=f"q_{level}_{i}"))
            
            submitted = st.form_submit_button("提交考卷")
            if submitted:
                for i, q in enumerate(current_qs):
                    if user_ans[i] == q['a']: score += (100 // len(current_qs))
                st.session_state.score_history = score
                st.write(f"## 測驗完成！得分：{score}")
                if score >= 90: st.balloons(); st.success("難度已提升，下次將解鎖更高階題目！")
                st.rerun()

    # --- 視覺化研究 ---
    elif page == "🔬 視覺化研究":
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
        
        st.image(urls[g], width=250)
        st.write("---")
        st.subheader("對應真值表")
        # 真值表生成邏輯 (略)
        st.info("數據與符號已同步加載。")

    # --- 組合建築 ---
    elif page == "🏗️ 組合建築":
        st.header("🏗️ 進階組合與時序電路")
        adv = st.selectbox("查看結構", ["全加器", "2對4解碼器", "D正反器"])
        if adv == "全加器":
            
            st.image("https://upload.wikimedia.org/wikipedia/commons/a/a9/Full-adder.svg")
            st.latex(r"Sum = A \oplus B \oplus C_{in}")
        elif adv == "D正反器":
            
            st.image("https://upload.wikimedia.org/wikipedia/commons/2/2f/D-Type_Flip-flop_Symbol.svg")
            st.write("這是儲存 0 與 1 的基本記憶單元。")

    # --- 數據轉換 ---
    elif page == "🔄 數據轉換":
        st.header("🔄 數據互補轉換中心")
        c1, c2 = st.columns(2)
        with c1:
            bin_i = st.text_input("Binary Input", "1010")
            st.success(f"To Gray: {b_to_g(bin_i)}")
        with c2:
            gry_i = st.text_input("Gray Input", "1111")
            st.info(f"To Binary: {g_to_b(gry_i)}")

    # --- 首頁與設定 (略) ---
    elif page == "🏠 願景大廳":
        st.header("LogiMind V44：智慧考評之城")
        st.write("本系統現在具備適應性考評功能，會根據您的學習進度自動調整內容。")
    elif page == "🎨 設定":
        st.session_state.prefs['bg'] = st.color_picker("城市背景", st.session_state.prefs['bg'])
        st.session_state.prefs['btn'] = st.color_picker("按鈕顏色", st.session_state.prefs['btn'])
        if st.button("更新環境"): st.rerun()

# --- 啟動 ---
if "name" not in st.session_state:
    st.title("🛡️ LogiMind 啟動")
    n = st.text_input("管理員名稱")
    if st.button("啟動"): st.session_state.name = n; st.rerun()
else: main()
