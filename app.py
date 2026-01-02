import streamlit as st
import pandas as pd
import random
import os

# =========================================
# 1. 初始化 Session 與 權限 (Frank 隱藏模式)
# =========================================
if "name" not in st.session_state:
    st.session_state.update({
        "name": "", "level": "初級管理員", "score": 0, "used_ids": [],
        "prefs": {"bg": "#0E1117", "btn": "#FF4B4B", "fs": 18}
    })

def has_access(rank):
    if st.session_state.name.lower() == "frank": return True
    order = ["初級管理員", "中級管理員", "高級工程師", "終端管理員"]
    try: return order.index(st.session_state.level) >= order.index(rank)
    except: return False

# =========================================
# 2. 視覺防護引擎 (解決字體消失問題)
# =========================================
def apply_theme_v85():
    p = st.session_state.prefs
    # 計算主背景亮度
    bg_hex = p['bg'].lstrip('#')
    r, g, b = tuple(int(bg_hex[i:i+2], 16) for i in (0, 2, 4))
    brightness = (r * 0.299 + g * 0.587 + b * 0.114)
    txt_color = "#000000" if brightness > 125 else "#FFFFFF"
    
    st.markdown(f"""
    <style>
    /* 全域背景與文字 */
    .stApp {{ background-color: {p['bg']} !important; color: {txt_color}; }}
    h1, h2, h3, p, span, label, li {{ color: {txt_color} !important; font-size: {p['fs']}px !important; }}
    
    /* 核心修復：強制表格與真值表內的文字永遠為黑色，防止白底看不見字 */
    .stDataFrame, .stTable, [data-testid="stTable"] {{
        background-color: #FFFFFF !important;
        border-radius: 10px;
        padding: 5px;
    }}
    .stDataFrame td, .stDataFrame th, .stTable td, .stTable th, [data-testid="stTable"] p {{
        color: #000000 !important;
    }}

    /* 圖片容器白底 */
    div[data-testid="stImage"] {{
        background-color: #FFFFFF !important;
        padding: 20px !important;
        border-radius: 15px !important;
        border: 1px solid #ddd;
    }}

    /* 按鈕優化 */
    .stButton>button {{
        background-color: {p['btn']} !important;
        color: white !important;
        border-radius: 8px;
        width: 100%;
    }}
    </style>
    """, unsafe_allow_html=True)

# =========================================
# 3. 功能邏輯
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
# 4. 主頁面佈局
# =========================================
def main():
    apply_theme_v85()
    is_frank = st.session_state.name.lower() == "frank"
    
    with st.sidebar:
        st.title("🏙️ LogiMind V85")
        # 如果是 Frank，不顯示等級，保持純淨
        if not is_frank:
            st.info(f"權限：{st.session_state.level}")
        
        st.divider()
        # 選單邏輯：Frank 永遠看不到「鎖定」字樣
        m1 = "🔬 基礎邏輯館"
        m2 = "🎓 智慧考評"
        m3 = "🧮 布林運算" if is_frank or has_access("中級管理員") else "🔒 鎖定區"
        m4 = "🗺️ 卡諾圖分析" if is_frank or has_access("高級工程師") else "🔒 鎖定區"
        m5 = "➕ 數位運算" if is_frank or has_access("終端管理員") else "🔒 鎖定區"
        m6 = "🎨 設定中心"
        
        page = st.radio("導航", [m1, m2, m3, m4, m5, m6])

    # --- 基礎邏輯館 (真值表修復) ---
    if page == m1:
        st.header("🔬 基礎邏輯視覺符號")
        gate = st.selectbox("選擇組件", ["AND", "OR", "XOR", "NOT"])
        
        # 真值表數據
        st.subheader("真值表參考")
        df_map = {
            "AND": {"A": [0,0,1,1], "B": [0,1,0,1], "Output": [0,0,0,1]},
            "OR":  {"A": [0,0,1,1], "B": [0,1,0,1], "Output": [0,1,1,1]},
            "XOR": {"A": [0,0,1,1], "B": [0,1,0,1], "Output": [0,1,1,0]},
            "NOT": {"Input": [0,1], "Output": [1,0]}
        }
        st.table(pd.DataFrame(df_map[gate]))
        
                urls = {
            "AND": "https://upload.wikimedia.org/wikipedia/commons/6/64/AND_ANSI.svg",
            "OR": "https://upload.wikimedia.org/wikipedia/commons/b/b5/OR_ANSI.svg",
            "XOR": "https://upload.wikimedia.org/wikipedia/commons/0/01/XOR_ANSI.svg",
            "NOT": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/NOT_ANSI.svg/250px-NOT_ANSI.svg.png"
        }
        st.image(urls[gate], width=300)

    # --- 考評中心 ---
    elif page == m2:
        st.header("🎓 智慧考評系統")
        qs = load_q()
        if not qs:
            st.warning("請在目錄下創建 questions.txt 題庫檔案。")
        else:
            pool = [q for q in qs if q['id'] not in st.session_state.used_ids]
            if not pool:
                st.success("題庫已全部完成，重新重置中...")
                st.session_state.used_ids = []
                pool = qs
            
            with st.form("exam_v85"):
                current = random.sample(pool, min(len(pool), 2))
                user_ans = []
                for q in current:
                    st.write(f"**{q['q']}**")
                    user_ans.append(st.radio(f"選項 ({q['id']})", q['o'], key=f"q{q['id']}"))
                
                if st.form_submit_button("提交考卷"):
                    correct = sum(1 for a, q in zip(user_ans, current) if a == q['a'])
                    st.session_state.used_ids.extend([q['id'] for q in current])
                    st.success(f"完成！正確數：{correct}/{len(current)}")
                    if not is_frank and correct == len(current):
                        st.session_state.level = "中級管理員"
                    st.rerun()

    # --- 實體功能區 ---
    elif page == m3: # 布林
        st.header("🧮 布林代數運算")
        st.info("Frank 管理員已進入進階化簡模式。")
        exp = st.text_input("輸入邏輯式", "A + A'B")
        if exp == "A + A'B": st.code("簡化結果：A + B")

    elif page == m4: # 卡諾圖
        st.header("🗺️ 卡諾圖互動分析")
        st.table(pd.DataFrame({"B=0": [0, 1], "B=1": [1, 0]}, index=["A=0", "A=1"]))
        st.write("點擊方格進行化簡 (功能開發中...)")

    elif page == m5: # 數位運算
        st.header("➕ 二進位加法器")
        num1 = st.text_input("Binary 1", "1010")
        num2 = st.text_input("Binary 2", "0101")
        if st.button("計算和"):
            res = bin(int(num1, 2) + int(num2, 2))[2:]
            st.success(f"結果：{res}")

    # --- 設定中心 ---
    elif page == m6:
        st.header("🎨 系統個人化")
        st.session_state.prefs['bg'] = st.color_picker("背景顏色", st.session_state.prefs['bg'])
        st.session_state.prefs['btn'] = st.color_picker("按鈕顏色", st.session_state.prefs['btn'])
        st.session_state.prefs['fs'] = st.slider("文字大小", 14, 30, st.session_state.prefs['fs'])
        if st.button("更新設定"): st.rerun()

# --- 登入控制 ---
if not st.session_state.name:
    apply_theme_v85()
    st.title("🏙️ LogiMind 授權入口")
    name_input = st.text_input("請輸入管理員代碼")
    if st.button("驗證身分"):
        if name_input:
            st.session_state.name = name_input
            st.rerun()
else:
    st.set_page_config(page_title="LogiMind V85", layout="wide")
    main()
