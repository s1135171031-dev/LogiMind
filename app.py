import streamlit as st
import pandas as pd
import random
import os

# ==================================================
# 1. 核心系統初始化 (Session State & Config)
# ==================================================
st.set_page_config(page_title="LogiMind V120", layout="wide")

if "init" not in st.session_state:
    st.session_state.update({
        "init": True,
        "name": "",
        "level": "初級管理員",
        "score": 0,
        "used_ids": [], # 記錄已考過的題目ID
        "prefs": {"bg": "#0E1117", "btn": "#FF4B4B", "fs": 18}
    })

# ==================================================
# 2. 權限管理系統 (Frank 特權邏輯)
# ==================================================
def get_user_rank_index(rank):
    ranks = ["初級管理員", "中級管理員", "高級工程師", "終端管理員"]
    if rank in ranks:
        return ranks.index(rank)
    return -1

def has_access(required_rank):
    # Frank 擁有絕對權限
    if st.session_state.name.lower() == "frank":
        return True
    
    user_idx = get_user_rank_index(st.session_state.level)
    req_idx = get_user_rank_index(required_rank)
    return user_idx >= req_idx

# ==================================================
# 3. 視覺防護引擎 (CSS 強制修復 & 對齊)
# ==================================================
def apply_advanced_css():
    p = st.session_state.prefs
    # 亮度計算，決定文字顏色
    bg_hex = p['bg'].lstrip('#')
    r, g, b = tuple(int(bg_hex[i:i+2], 16) for i in (0, 2, 4))
    brightness = (r * 0.299 + g * 0.587 + b * 0.114)
    text_color = "#000000" if brightness > 140 else "#FFFFFF"
    
    st.markdown(f"""
    <style>
    /* 全域設定 */
    .stApp {{
        background-color: {p['bg']} !important;
    }}
    h1, h2, h3, h4, p, label, span, div {{
        color: {text_color} !important;
        font-family: 'Segoe UI', sans-serif;
        font-size: {p['fs']}px !important;
    }}
    
    /* 圖片容器強制白底 (解決透明圖問題) */
    div[data-testid="stImage"] {{
        background-color: #FFFFFF !important;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}

    /* 表格強制修復 (解決白底白字 & 對齊) */
    .stDataFrame, .stTable {{
        width: 100% !important;
    }}
    div[data-testid="stDataFrame"] div[role="grid"] {{
        background-color: #FFFFFF !important;
        color: #000000 !important; /* 強制黑字 */
    }}
    div[data-testid="stDataFrame"] th {{
        background-color: #f0f2f6 !important;
        color: #000000 !important;
        text-align: center !important; /* 標題置中 */
    }}
    div[data-testid="stDataFrame"] td {{
        color: #000000 !important;
        text-align: center !important; /* 內容置中 */
    }}

    /* 按鈕樣式 */
    .stButton > button {{
        background-color: {p['btn']} !important;
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        width: 100%;
        font-weight: bold;
    }}
    
    /* 側邊欄等級框 */
    .rank-badge {{
        padding: 15px;
        border: 2px solid {p['btn']};
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
    }}
    </style>
    """, unsafe_allow_html=True)

# ==================================================
# 4. 題庫讀取引擎
# ==================================================
def load_questions():
    questions = []
    if os.path.exists("questions.txt"):
        try:
            with open("questions.txt", "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split("|")
                    if len(parts) == 5:
                        questions.append({
                            "id": parts[0],
                            "diff": parts[1],
                            "q": parts[2],
                            "o": parts[3].split(","),
                            "a": parts[4]
                        })
        except Exception as e:
            st.error(f"題庫讀取失敗: {e}")
    return questions

# ==================================================
# 5. 各功能模組 (Functions)
# ==================================================

# --- 模組：真值表顯示器 ---
def render_truth_table(gate_type):
    data = {}
    if gate_type == "NOT":
        data = {"Input A": [0, 1], "Output Y": [1, 0]}
    else:
        base_a = [0, 0, 1, 1]
        base_b = [0, 1, 0, 1]
        
        if gate_type == "AND": out = [0, 0, 0, 1]
        elif gate_type == "OR": out = [0, 1, 1, 1]
        elif gate_type == "XOR": out = [0, 1, 1, 0]
        elif gate_type == "NAND": out = [1, 1, 1, 0]
        elif gate_type == "NOR": out = [1, 0, 0, 0]
        else: out = [0, 0, 0, 0]
        
        data = {"Input A": base_a, "Input B": base_b, "Output Y": out}
    
    df = pd.DataFrame(data)
    # 使用 st.dataframe 並強制全寬與隱藏索引，搭配 CSS 置中
    st.dataframe(df, use_container_width=True, hide_index=True)

# --- 模組：卡諾圖邏輯 ---
def solve_kmap_2x2(m0, m1, m2, m3):
    # 簡單的 2x2 卡諾圖化簡邏輯模擬
    ones = []
    if m0: ones.append(0)
    if m1: ones.append(1)
    if m2: ones.append(2)
    if m3: ones.append(3)
    
    if len(ones) == 4: return "1 (全 High)"
    if len(ones) == 0: return "0 (全 Low)"
    
    # 兩項相鄰
    if m0 and m1: return "A' (消除 B)" # 00, 01 -> A=0
    if m2 and m3: return "A (消除 B)"  # 10, 11 -> A=1
    if m0 and m2: return "B' (消除 A)" # 00, 10 -> B=0
    if m1 and m3: return "B (消除 A)"  # 01, 11 -> B=1
    
    return "無法進一步化簡或為互斥項"

# ==================================================
# 6. 主程式介面 (Main Layout)
# ==================================================
def main_app():
    apply_advanced_css()
    is_frank = st.session_state.name.lower() == "frank"
    
    # --- 側邊欄 ---
    with st.sidebar:
        st.title("🏙️ LogiMind V120")
        
        # 等級顯示區 (Frank 要求)
        user_display = "Frank (終端管理員)" if is_frank else f"{st.session_state.name}"
        level_display = "權限：∞ 無限制" if is_frank else f"權限：{st.session_state.level}"
        
        st.markdown(f"""
        <div class="rank-badge">
            <h3>👤 {user_display}</h3>
            <p>{level_display}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # 導航選單 (Frank 模式隱藏鎖定圖示)
        menu_items = {
            "home": "🏠 系統概覽",
            "logic": "🔬 基礎邏輯與真值表",
            "exam": "🎓 智慧考評 (不重複)",
            "convert": "🔢 進制轉換中心",
            "bool": "🧮 布林代數化簡",
            "kmap": "🗺️ 互動卡諾圖",
            "math": "➕ 二進位運算器",
            "settings": "🎨 個人化設定"
        }
        
        # 權限過濾邏輯
        final_menu = []
        final_menu.append(menu_items["home"])
        final_menu.append(menu_items["logic"])
        final_menu.append(menu_items["exam"])
        final_menu.append(menu_items["convert"]) # 恢復功能
        
        # 條件功能
        if is_frank or has_access("中級管理員"):
            final_menu.append(menu_items["bool"])
        else:
            final_menu.append("🔒 布林代數 (需中級)")
            
        if is_frank or has_access("高級工程師"):
            final_menu.append(menu_items["kmap"])
        else:
            final_menu.append("🔒 卡諾圖 (需高級)")
            
        if is_frank or has_access("終端管理員"):
            final_menu.append(menu_items["math"])
        else:
            final_menu.append("🔒 運算器 (需終端)")
            
        final_menu.append(menu_items["settings"])
        
        selection = st.radio("功能導航", final_menu)

    # --- 頁面 1: 系統概覽 (Intro) ---
    if selection == menu_items["home"]:
        st.header("🏠 歡迎來到 LogiMind V120")
        st.markdown("""
        ### 系統狀態：正常運作中
        LogiMind 是一個專為數位邏輯設計的互動式學習終端。本系統已根據管理員 **Frank** 的指示進行了全功能的解鎖與修復。
        
        #### 核心功能：
        * **視覺化邏輯閘**：包含 ANSI 標準符號與精確對齊的真值表。
        * **智慧考評**：支援外部題庫讀取，保證題目不重複出現。
        * **進制轉換**：二進位、八進位、十進位、十六進位即時互轉。
        * **工程工具**：包含卡諾圖求解器與布林代數模擬。
        
        請從左側選單開始您的操作。
        """)

    # --- 頁面 2: 基礎邏輯 (Logic & Truth Table) ---
    elif selection == menu_items["logic"]:
        st.header("🔬 基礎邏輯視覺化")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            gate = st.selectbox("選擇邏輯閘", ["AND", "OR", "NOT", "NAND", "NOR", "XOR"])
            st.info(f"當前選擇：{gate} Gate")
        
        with col2:
            # 圖片顯示
            urls = {
                "AND": "https://upload.wikimedia.org/wikipedia/commons/6/64/AND_ANSI.svg",
                "OR": "https://upload.wikimedia.org/wikipedia/commons/b/b5/OR_ANSI.svg",
                "NOT": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/NOT_ANSI.svg/250px-NOT_ANSI.svg.png",
                "NAND": "https://upload.wikimedia.org/wikipedia/commons/f/f2/NAND_ANSI.svg",
                "NOR": "https://upload.wikimedia.org/wikipedia/commons/6/6c/NOR_ANSI.svg",
                "XOR": "https://upload.wikimedia.org/wikipedia/commons/0/01/XOR_ANSI.svg"
            }
            
            st.image(urls[gate], caption=f"{gate} ANSI Symbol", width=300)

        st.divider()
        st.subheader(f"📊 {gate} 閘真值表")
        # 呼叫真值表渲染函數
        render_truth_table(gate)

    # --- 頁面 3: 智慧考評 (Exam - No Repeats) ---
    elif selection == menu_items["exam"]:
        st.header("🎓 智慧考評中心")
        
        # 讀取題庫
        all_questions = load_questions()
        
        if not all_questions:
            st.error("❌ 找不到 questions.txt，請確認檔案已建立。")
        else:
            # 過濾已做過的題目 ID
            available_pool = [q for q in all_questions if q['id'] not in st.session_state.used_ids]
            
            # 進度條
            total_q = len(all_questions)
            done_q = len(st.session_state.used_ids)
            st.progress(done_q / total_q if total_q > 0 else 0)
            st.caption(f"題庫進度：{done_q} / {total_q}")
            
            if not available_pool:
                st.success("🎉 恭喜！您已完成所有題庫訓練。")
                if st.button("重置題庫紀錄"):
                    st.session_state.used_ids = []
                    st.rerun()
            else:
                st.write("請回答以下題目：")
                with st.form("quiz_form"):
                    # 隨機抽取 1 題 (可改多題)
                    q_now = random.choice(available_pool)
                    
                    st.markdown(f"**題目 ID [{q_now['id']}]: {q_now['q']}**")
                    ans = st.radio("請選擇答案：", q_now['o'], key="exam_radio")
                    
                    submitted = st.form_submit_button("提交答案")
                    if submitted:
                        if ans == q_now['a']:
                            st.balloons()
                            st.success("✅ 回答正確！")
                            # 升級邏輯
                            if st.session_state.level == "初級管理員":
                                st.session_state.level = "中級管理員"
                                st.toast("權限提升：中級管理員")
                        else:
                            st.error(f"❌ 回答錯誤。正確答案是：{q_now['a']}")
                        
                        # 不論對錯，記錄該題 ID 以免重複 (或是只記錄對的，這裡設定為做過就不出現)
                        st.session_state.used_ids.append(q_now['id'])
                        st.rerun()

    # --- 頁面 4: 進制轉換 (Binary Conversion - Restored) ---
    elif selection == menu_items["convert"]:
        st.header("🔢 多功能進制轉換器")
        st.markdown("支援 **2 (Binary)**, **8 (Octal)**, **10 (Decimal)**, **16 (Hex)** 進制互轉。")
        
        col1, col2 = st.columns(2)
        with col1:
            input_val = st.text_input("輸入數值", "10")
            base_from = st.selectbox("來源進制", ["10 (十進制)", "2 (二進制)", "8 (八進制)", "16 (十六進制)"])
        
        with col2:
            st.write("### 轉換結果")
            try:
                # 解析來源進制
                base_map = {"10 (十進制)": 10, "2 (二進制)": 2, "8 (八進制)": 8, "16 (十六進制)": 16}
                dec_val = int(input_val, base_map[base_from])
                
                res_bin = bin(dec_val)[2:]
                res_oct = oct(dec_val)[2:]
                res_dec = str(dec_val)
                res_hex = hex(dec_val)[2:].upper()
                
                st.code(f"Binary (2):  {res_bin}")
                st.code(f"Octal  (8):  {res_oct}")
                st.code(f"Decimal(10): {res_dec}")
                st.code(f"Hex    (16): {res_hex}")
                
            except ValueError:
                st.error("⚠️ 輸入格式錯誤，請檢查數值是否符合所選進制。")

    # --- 頁面 5: 布林代數 (Boolean) ---
    elif selection == menu_items["bool"] or "布林" in selection:
        if "🔒" in selection: st.error("權限不足"); st.stop()
        
        st.header("🧮 布林代數化簡模擬器")
        expr = st.text_input("輸入布林表達式 (支援變數 A, B)", "A + 1")
        
        st.write("---")
        st.subheader("分析結果")
        # 簡單的規則庫模擬
        if "A + 1" in expr.replace(" ", ""):
            st.success("結果：1 (互補律/Annulment Law)")
            st.latex(r"A + 1 = 1")
        elif "A . 0" in expr.replace(" ", "") or "A*0" in expr:
            st.success("結果：0 (互補律/Annulment Law)")
            st.latex(r"A \cdot 0 = 0")
        elif "A + A" in expr:
            st.success("結果：A (艾德波頓律/Idempotent Law)")
            st.latex(r"A + A = A")
        else:
            st.info("系統僅支援基礎定律演示 (A+1, A*0, A+A)。複雜運算請升級至 V130。")

    # --- 頁面 6: 卡諾圖 (K-Map) ---
    elif selection == menu_items["kmap"] or "卡諾圖" in selection:
        if "🔒" in selection: st.error("權限不足"); st.stop()
        
        st.header("🗺️ 2變數卡諾圖 (K-Map)")
        st.write("請勾選方格內的 '1'，系統將自動計算化簡後的布林函式。")
        
         # Contextual
        
        c1, c2 = st.columns(2)
        with c1:
            st.caption("A=0 (Top Row)")
            m0 = st.checkbox("m0 (00)", key="m0")
            m1 = st.checkbox("m1 (01)", key="m1")
        with c2:
            st.caption("A=1 (Bottom Row)")
            m2 = st.checkbox("m2 (10)", key="m2")
            m3 = st.checkbox("m3 (11)", key="m3")
            
        st.divider()
        result = solve_kmap_2x2(m0, m1, m2, m3)
        st.subheader("化簡結果 (F):")
        st.code(result, language="text")

    # --- 頁面 7: 二進位運算器 (Math) ---
    elif selection == menu_items["math"] or "運算器" in selection:
        if "🔒" in selection: st.error("權限不足"); st.stop()
        
        st.header("➕ 二進位算術單元 (ALU)")
        c1, c2 = st.columns(2)
        n1 = c1.text_input("數值 A (Binary)", "1010")
        n2 = c2.text_input("數值 B (Binary)", "0011")
        op = st.radio("運算模式", ["加法 (+)", "減法 (-)"], horizontal=True)
        
        if st.button("執行運算"):
            try:
                i1 = int(n1, 2)
                i2 = int(n2, 2)
                if "加法" in op:
                    res = i1 + i2
                    symbol = "+"
                else:
                    res = i1 - i2
                    symbol = "-"
                
                st.success(f"運算完成：{n1} {symbol} {n2}")
                st.metric("二進制結果", bin(res)[2:])
                st.metric("十進制驗證", res)
            except:
                st.error("輸入錯誤：請確保輸入有效的二進制數字 (0/1)。")

    # --- 頁面 8: 設定 ---
    elif selection == menu_items["settings"]:
        st.header("🎨 介面個人化")
        st.write("自定義您的終端外觀。")
        c1, c2 = st.columns(2)
        new_bg = c1.color_picker("背景顏色", st.session_state.prefs['bg'])
        new_btn = c2.color_picker("按鈕主題色", st.session_state.prefs['btn'])
        new_fs = st.slider("全域字體大小", 12, 32, st.session_state.prefs['fs'])
        
        if st.button("儲存並套用"):
            st.session_state.prefs['bg'] = new_bg
            st.session_state.prefs['btn'] = new_btn
            st.session_state.prefs['fs'] = new_fs
            st.rerun()

# ==================================================
# 7. 程式入口 (Login System)
# ==================================================
if __name__ == "__main__":
    if not st.session_state.name:
        apply_advanced_css() # 登入頁面也要套用樣式
        st.title("🛡️ LogiMind 登入系統")
        st.write("請輸入您的管理員代號。")
        
        col1, col2 = st.columns([3, 1])
        name_input = col1.text_input("Admin Code", placeholder="例如：Frank")
        
        if col2.button("解鎖終端"):
            if name_input.strip():
                st.session_state.name = name_input
                # 如果是 Frank，自動設定高等級 (雖然 has_access 會再次檢查)
                if name_input.lower() == "frank":
                    st.session_state.level = "終端管理員"
                st.rerun()
            else:
                st.warning("請輸入代號。")
    else:
        main_app()
