import streamlit as st
import pandas as pd
import random
import os
import base64
import time
import numpy as np 
import json
from datetime import datetime

# ==================================================
# 0. 系統核心邏輯 (保持不變)
# ==================================================
def init_question_bank():
    # 檢查是否需要生成題庫
    should_generate = False
    if not os.path.exists("questions.txt"):
        should_generate = True
    else:
        with open("questions.txt", "r", encoding="utf-8") as f:
            if len(f.readlines()) < 100:
                should_generate = True

    if should_generate:
        # 如果沒有題庫檔，簡單生成一些範例以免報錯 (建議使用獨立腳本生成完整版)
        with open("questions.txt", "w", encoding="utf-8") as f:
            f.write("SYS-001|1|CityOS 初始化測試題|Pass,Fail|Pass\n")
            for i in range(100):
                f.write(f"AUTO-{i}|1|自動生成題目 {i}|A,B,C,D|A\n")

# ==================================================
# 1. 系統設定與視覺素材
# ==================================================
st.set_page_config(page_title="CityOS V140", layout="wide")
init_question_bank()

SVG_ICONS = {
    "MUX": '''<svg width="120" height="100" viewBox="0 0 120 100" xmlns="http://www.w3.org/2000/svg"><path d="M30,10 L90,25 L90,75 L30,90 Z" fill="none" stroke="currentColor" stroke-width="3"/><text x="45" y="55" fill="currentColor" font-size="14">MUX</text><path d="M10,25 L30,25 M10,40 L30,40 M10,55 L30,55 M10,70 L30,70 M90,50 L110,50 M60,85 L60,95" stroke="currentColor" stroke-width="2"/></svg>''',
    "AND": '''<svg width="100" height="60" viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg"><path d="M10,10 L40,10 C55,10 65,20 65,30 C65,40 55,50 40,50 L10,50 Z" fill="none" stroke="currentColor" stroke-width="3"/><path d="M0,20 L10,20 M0,40 L10,40 M65,30 L80,30" stroke="currentColor" stroke-width="3"/></svg>''',
}

THEMES = {
    "專業暗色 (Night City)": {
        "bg": "#212529", "txt": "#E9ECEF", "btn": "#495057", "btn_txt": "#FFFFFF", "card": "#343A40", 
        "chart": ["#00ADB5", "#EEEEEE", "#FF2E63"]
    },
    "舒適亮色 (Day City)": {
        "bg": "#F8F9FA", "txt": "#343A40", "btn": "#6C757D", "btn_txt": "#FFFFFF", "card": "#FFFFFF", 
        "chart": ["#343A40", "#6C757D", "#ADB5BD"]
    }
}

# Session State 初始化
if "state" not in st.session_state:
    st.session_state.update({
        "state": True, "name": "", "title": "市政執行官", "level": "區域管理員", 
        "used_ids": [], "history": [], "theme_name": "專業暗色 (Night City)",
        "exam_active": False, 
        "quiz_batch": [], # 存放 5 題的陣列
    })

def apply_theme():
    t = THEMES[st.session_state.theme_name]
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {t['bg']} !important; }}
    h1, h2, h3, h4, p, span, div, label, li, .stMarkdown, .stExpander, .stCode {{ color: {t['txt']} !important; font-family: 'Segoe UI', sans-serif; }}
    .stButton>button {{ background-color: {t['btn']} !important; color: {t['btn_txt']} !important; border: none !important; border-radius: 6px !important; padding: 0.5rem 1rem; }}
    div[data-testid="stDataFrame"], div[data-testid="stExpander"] {{ background-color: {t['card']} !important; border: 1px solid rgba(128,128,128,0.2); border-radius: 8px; }}
    [data-testid="stSidebar"] {{ background-color: {t['card']}; border-right: 1px solid rgba(128,128,128,0.1); }}
    </style>
    """, unsafe_allow_html=True)

def get_chart_data():
    # 模擬更高頻的波動
    return pd.DataFrame(
        np.random.randint(20, 90, size=(20, 3)) + np.random.randn(20, 3) * 10,
        columns=['CPU Load', 'Net I/O', 'Sec Level']
    )

def load_qs():
    q_list = []
    if os.path.exists("questions.txt"):
        try:
            with open("questions.txt", "r", encoding="utf-8") as f:
                for l in f:
                    p = l.strip().split("|")
                    if len(p)==5: q_list.append({"id":p[0],"diff":p[1],"q":p[2],"o":p[3].split(","),"a":p[4]})
        except: pass
    return q_list

# ==================================================
# 2. 主程式邏輯
# ==================================================
def main():
    apply_theme()
    t_colors = THEMES[st.session_state.theme_name]["chart"]

    # Sidebar
    with st.sidebar:
        st.title("🏙️ CityOS V140")
        st.caption("Central Command Interface")
        st.divider()
        menu = ["🏙️ 城市儀表板", "🎓 市政學院 (Quiz)", "⚡ 電力設施 (Logic)", "📂 人事檔案"]
        page = st.radio("導航", menu)

    # --- 頁面內容 ---
    if "城市儀表板" in page:
        st.title("🏙️ 城市中控儀表板")
        
        col_main, col_side = st.columns([2, 1])
        
        with col_main:
            # 1. 市政手冊
            st.subheader("📖 市政操作手冊")
            with st.expander("📌 點擊展開：模組功能與戰略描述", expanded=True):
                st.markdown("""
                * **⚡ 電力設施**：監控邏輯閘 (AND/OR/NOT) 運作。
                * **🎓 市政學院**：全新升級 **Batch-5** 考核模式，每組 5 題，連續決策。
                """)

            st.divider()

            # 2. 高頻即時監控 (已加速 + 按鈕)
            c_head, c_btn = st.columns([3, 1])
            with c_head: st.subheader("📡 核心監控 (High-Freq Feed)")
            with c_btn: 
                # [功能 1] 立即刷新按鈕
                if st.button("⚡ 立即刷新", use_container_width=True):
                    st.toast("緩存已清除，數據重置。")
            
            chart_placeholder = st.empty()
            
            # [功能 1] 自動更新速度加快 (Sleep 0.05 -> 0.01)
            for i in range(50):
                new_data = get_chart_data()
                chart_placeholder.area_chart(new_data, color=t_colors, height=250)
                time.sleep(0.01) # 極速模式
            
        with col_side:
            st.subheader("⚠️ 安全公告")
            st.warning("監控頻率已提升至 100Hz。系統負載微幅上升。")
            
            # [功能 3] 版本歷史直接顯示代碼 (不渲染 HTML)
            st.subheader("🛠️ 系統內核日誌 (Raw)")
            
            system_log = {
                "version": "1.4.0",
                "build_date": "2026-01-04",
                "changes": [
                    {"module": "MONITOR", "action": "Overclock refresh rate to 10ms"},
                    {"module": "QUIZ_CORE", "action": "Implement Batch-5 exam logic"},
                    {"module": "UI_RENDER", "action": "Expose raw system logs"},
                    {"module": "SECURITY", "action": "Patch login vulnerability"}
                ],
                "status": "STABLE"
            }
            # 直接顯示 JSON 結構
            st.code(json.dumps(system_log, indent=2), language="json")

    elif "市政學院" in page:
        st.header("🎓 市政管理能力考評 (Batch Mode)")
        
        # 考試未開始狀態
        if not st.session_state.exam_active:
            c1, c2 = st.columns([2, 1])
            with c1:
                st.info("⚠️ 注意：考核模式已升級。")
                st.markdown("""
                **全新考核規則 (V1.4)：**
                1. 系統將一次性下載 **5 道** 戰術決策題。
                2. 您必須完成所有決策後統一提交。
                3. 中途離開將視為任務失敗。
                """)
                if st.button("🚀 啟動 5 連戰考核", type="primary"):
                    qs = load_qs()
                    if len(qs) >= 5:
                        # [功能 2] 隨機抽取 5 題
                        st.session_state.quiz_batch = random.sample(qs, 5)
                        st.session_state.exam_active = True
                        st.rerun()
                    else:
                        st.error(f"題庫不足 (目前 {len(qs)} 題)，請確保 questions.txt 至少有 5 題。")
            with c2: 
                st.metric("題庫狀態", "連線正常", "Ready")

        # 考試進行中狀態
        else:
            st.write(f"### 📝 戰術決策組 (共 5 題)")
            
            # 使用 Form 包裹所有 5 題
            with st.form("batch_exam_form"):
                user_answers = {}
                
                # [功能 2] 迴圈生成 5 題的 UI
                for idx, q in enumerate(st.session_state.quiz_batch):
                    st.markdown(f"**Q{idx+1}. {q['q']}** (ID: {q['id']})")
                    # 使用唯一的 key 避免衝突
                    user_answers[idx] = st.radio(f"決策 {idx+1}", q['o'], key=f"q_{idx}", index=None, label_visibility="collapsed")
                    st.divider()
                
                submitted = st.form_submit_button("🔒 鎖定並提交所有決策")
                
                if submitted:
                    # 檢查是否全部作答
                    if any(a is None for a in user_answers.values()):
                        st.warning("⚠️ 指揮官，尚有未完成的決策！請回答所有問題。")
                    else:
                        # 批次改分邏輯
                        score = 0
                        results = []
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        
                        for idx, q in enumerate(st.session_state.quiz_batch):
                            u_ans = user_answers[idx]
                            is_correct = (u_ans == q['a'])
                            if is_correct: score += 1
                            
                            # 紀錄每一題的結果
                            st.session_state.history.append({
                                "時間": timestamp,
                                "批次": "Batch-5",
                                "題目ID": q['id'],
                                "結果": "✅" if is_correct else "❌"
                            })
                        
                        # 結算畫面
                        if score == 5:
                            st.balloons()
                            st.success(f"完美決策！ 5 題全對。")
                            if st.session_state.level == "區域管理員": st.session_state.level = "城市規劃師"
                        elif score >= 3:
                            st.warning(f"考核通過。答對 {score}/5 題。")
                        else:
                            st.error(f"考核失敗。僅答對 {score}/5 題，請重試。")
                            
                        st.session_state.exam_active = False
                        st.session_state.quiz_batch = []
                        time.sleep(2)
                        st.rerun()

    elif "電力設施" in page:
        # 簡單保留此功能
        st.header("⚡ 電力設施監控")
        st.info("模組運作正常。")
        c1, c2 = st.columns(2)
        with c1: st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/AND_ANSI.svg/200px-AND_ANSI.svg.png", caption="Logic Gate Status: OK")
        with c2: st.metric("電網負載", "42%")

    elif "人事檔案" in page:
        st.header("📂 人事檔案")
        st.text_input("ID", st.session_state.name, disabled=True)
        st.metric("當前權限", st.session_state.level)
        
        if st.button("登出"):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()
            
        st.subheader("📜 近期決策紀錄")
        if st.session_state.history:
            st.dataframe(pd.DataFrame(st.session_state.history)[::-1], use_container_width=True, hide_index=True)

# ==================================================
# 3. 入口 (Clean Login)
# ==================================================
if not st.session_state.name:
    apply_theme()
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.title("🏙️ CityOS V140")
        st.markdown('<div style="text-align:center; color:#888;">System Access Required</div>', unsafe_allow_html=True)
        with st.form("login"):
            n = st.text_input("Commander ID")
            if st.form_submit_button("Initialize"):
                if n: st.session_state.name = n; st.rerun()
else:
    main()
