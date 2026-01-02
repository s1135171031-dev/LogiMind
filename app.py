import streamlit as st
import pandas as pd
import random
import os

# =========================================
# 1. 核心狀態初始化
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
# 2. 視覺防護系統 (確保表格與文字對齊)
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
    
    /* 表格視覺優化與強制黑色字體 (對齊核心) */
    .stTable, [data-testid="stTable"], .stDataFrame {{
        background-color: #FFFFFF !important;
        border: 2px solid #444;
        border-radius: 8px;
    }}
    .stTable td, .stTable th, [data-testid="stTable"] p, .stDataFrame td, .stDataFrame th {{
        color: #000000 !important;
        text-align: center !important; /* 強制對齊 */
        font-family: 'Courier New', monospace;
    }}
    
    /* 側邊欄等級顯示優化 */
    .level-box {{
        padding: 10px;
        border: 1px solid {p['btn']};
        border-radius: 5px;
        text-align: center;
        background: rgba(255, 75, 75, 0.1);
    }}
    </style>
    """, unsafe_allow_html=True)

# =========================================
# 3. 核心功能分頁
# =========================================
def main():
    apply_style()
    is_frank = st.session_state.name.lower() == "frank"
    
    with st.sidebar:
        st.title("🏙️ LogiMind V110")
        
        # --- 2. 管理員等級回歸 ---
        st.markdown(f'<div class="level-box">系統使用者：{st.session_state.name}</div>', unsafe_allow_html=True)
        if is_frank:
            st.warning("★ 終端特權模式已啟動")
        else:
            st.info(f"當前權限：{st.session_state.level}")
        
        st.divider()
        
        # 功能清單 (Frank 不顯示鎖定)
        m0 = "🏠 系統概覽與介紹"
        m1 = "🔬 基礎邏輯中心"
        m2 = "🎓 智慧考評中心"
        m3 = "🔢 進制轉換中心" # --- 1. 二進位轉換回歸 ---
        m4 = "🧮 布林化簡" if is_frank or has_access("中級管理員") else "🔒 鎖定"
        m5 = "🗺️ 卡諾圖實驗室" if is_frank or has_access("高級工程師") else "🔒 鎖定"
        m6 = "🎨 介面設定"
        
        page = st.radio("導航選單", [m0, m1, m2, m3, m4, m5, m6])

    # --- 3. 介紹頁面回歸 ---
    if page == m0:
        st.header("🏠 LogiMind 系統概覽")
        st.write("""
        歡迎來到 LogiMind 數位邏輯教育系統。
        本系統旨在提供最直觀的數位電路學習體驗：
        - **視覺化閘電路**：透過 ANSI 標準符號學習基礎元件。
        - **實時真值表**：精確對齊的邏輯演算參考。
        - **智慧考評**：不重複題庫，隨著您的答題自動提升權限。
        """)
        st.info("系統版本：V110 | 開發者：Frank")

    # --- 4. 基礎邏輯 (真值表對齊優化) ---
    elif page == m1:
        st.header("🔬 基礎邏輯與真值表")
        gate = st.selectbox("選擇邏輯閘", ["AND", "OR", "XOR", "NOT", "NAND", "NOR"])
        
        df_map = {
            "AND": {"A": [0,0,1,1], "B": [0,1,0,1], "Y": [0,0,0,1]},
            "OR":  {"A": [0,0,1,1], "B": [0,1,0,1], "Y": [0,1,1,1]},
            "XOR": {"A": [0,0,1,1], "B": [0,1,0,1], "Y": [0,1,1,0]},
            "NAND": {"A": [0,0,1,1], "B": [0,1,0,1], "Y": [1,1,1,0]},
            "NOR":  {"A": [0,0,1,1], "B": [0,1,0,1], "Y": [1,0,0,0]},
            "NOT": {"Input": [0,1], "Output": [1,0]}
        }
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("標準真值表")
            st.dataframe(pd.DataFrame(df_map[gate]), use_container_width=True) # 使用 dataframe 確保對齊
        with col2:
            st.subheader("物理符號")
            urls = {
                "AND": "https://upload.wikimedia.org/wikipedia/commons/6/64/AND_ANSI.svg",
                "OR": "https://upload.wikimedia.org/wikipedia/commons/b/b5/OR_ANSI.svg",
                "XOR": "https://upload.wikimedia.org/wikipedia/commons/0/01/XOR_ANSI.svg",
                "NAND": "https://upload.wikimedia.org/wikipedia/commons/f/f2/NAND_ANSI.svg",
                "NOR": "https://upload.wikimedia.org/wikipedia/commons/6/6c/NOR_ANSI.svg",
                "NOT": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/NOT_ANSI.svg/250px-NOT_ANSI.svg.png"
            }
            st.image(urls[gate], width=200)

    # --- 1. 二進位轉換功能回歸 ---
    elif page == m3:
        st.header("🔢 進制轉換中心")
        val = st.text_input("輸入數值", "10")
        from_base = st.selectbox("原始進制", [10, 2, 16, 8])
        if st.button("轉換"):
            try:
                dec = int(val, from_base)
                st.success(f"十進制：{dec}")
                st.success(f"二進制：{bin(dec)[2:]}")
                st.success(f"十六進制：{hex(dec)[2:].upper()}")
                st.success(f"八進制：{oct(dec)[2:]}")
            except:
                st.error("輸入格式有誤，請檢查進制。")

    # --- 其他功能保持原樣但確保縮排正確 ---
    elif page == m2:
        st.header("🎓 智慧考評中心")
        st.write("題庫系統已準備就緒，點擊開始測驗以提升等級。")
        # (這裡可依照 V100 的邏輯繼續加入題庫讀取)

    elif "介面設定" in page:
        st.header("🎨 介面個人化")
        st.session_state.prefs['bg'] = st.color_picker("系統背景", st.session_state.prefs['bg'])
        st.session_state.prefs['fs'] = st.slider("字體大小", 14, 32, st.session_state.prefs['fs'])
        if st.button("重新加載系統"): st.rerun()

# --- 登入控制 ---
if not st.session_state.name:
    apply_style()
    st.title("🏙️ LogiMind 登入")
    n = st.text_input("管理員代碼")
    if st.button("解鎖"):
        st.session_state.name = n
        st.rerun()
else:
    st.set_page_config(page_title="LogiMind V110", layout="wide")
    main()
