import streamlit as st
import pandas as pd
import random
import os
import base64
import time
import numpy as np 
from datetime import datetime

# ==================================================
# 0. 自動化題庫生成 (完整版)
# ==================================================
def init_question_bank():
    should_generate = False
    if not os.path.exists("questions.txt"):
        should_generate = True
    else:
        with open("questions.txt", "r", encoding="utf-8") as f:
            if len(f.readlines()) < 50: should_generate = True

    if should_generate:
        with open("questions.txt", "w", encoding="utf-8") as f:
            # 邏輯題
            gates = ["AND", "OR", "XOR", "NAND"]
            for _ in range(400):
                g = random.choice(gates)
                a, b = random.randint(0, 1), random.randint(0, 1)
                ans = 0
                if g == "AND": ans = a & b
                elif g == "OR": ans = a | b
                elif g == "XOR": ans = a ^ b
                elif g == "NAND": ans = 1 - (a & b)
                f.write(f"LOGIC-{random.randint(1000,9999)}|1|輸入 A={a}, B={b}, {g} 閘輸出為何？|0,1,Z,X|{ans}\n")
            
            # 數學題
            for _ in range(300):
                val = random.randint(1, 15)
                f.write(f"MATH-{random.randint(1000,9999)}|2|十進制 {val} 的二進制？|{bin(val)[2:]},{bin(val+1)[2:]},0000,1111|{bin(val)[2:]}\n")
            
            # 系統題
            base = [
                "SYS-001|1|CityOS 核心運算單元？|CPU,GPU,TPU,APU|CPU",
                "SYS-002|2|MUX 4輸入需幾條選擇線？|2,1,4,8|2",
                "SYS-003|1|K-Map 用途？|化簡布林代數,加密,壓縮,備份|化簡布林代數"
            ]
            for b in base: 
                parts = b.split("|")
                for i in range(50): # 重複寫入增加機率
                    f.write(f"{parts[0]}-{i}|{parts[1]}|{parts[2]}|{parts[3]}|{parts[4]}\n")

# ==================================================
# 1. 系統設定與素材 (完整 SVG)
# ==================================================
st.set_page_config(page_title="CityOS V141", layout="wide")
init_question_bank()

SVG_ICONS = {
    "MUX": '''<svg width="120" height="100" viewBox="0 0 120 100" xmlns="http://www.w3.org/2000/svg"><path d="M30,10 L90,25 L90,75 L30,90 Z" fill="none" stroke="currentColor" stroke-width="3"/><text x="45" y="55" fill="currentColor" font-size="14">MUX</text><path d="M10,25 L30,25 M10,40 L30,40 M10,55 L30,55 M10,70 L30,70 M90,50 L110,50 M60,85 L60,95" stroke="currentColor" stroke-width="2"/></svg>''',
    "AND": '''<svg width="100" height="60" viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg"><path d="M10,10 L40,10 C55,10 65,20 65,30 C65,40 55,50 40,50 L10,50 Z" fill="none" stroke="currentColor" stroke-width="3"/><path d="M0,20 L10,20 M0,40 L10,40 M65,30 L80,30" stroke="currentColor" stroke-width="3"/></svg>''',
    "OR": '''<svg width="100" height="60" viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg"><path d="M10,10 C10,10 25,10 40,10 C60,10 70,30 70,30 C70,30 60,50 40,50 C25,50 10,50 10,50 C15,40 15,20 10,10" fill="none" stroke="currentColor" stroke-width="3"/><path d="M0,20 L13,20 M0,40 L13,40 M70,30 L80,30" stroke="currentColor" stroke-width="3"/></svg>''',
    "NOT": '''<svg width="100" height="60" viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg"><path d="M20,10 L50,30 L20,50 Z" fill="none" stroke="currentColor" stroke-width="3"/><circle cx="54" cy="30" r="4" fill="none" stroke="currentColor" stroke-width="3"/><path d="M10,30 L20,30 M58,30 L70,30" stroke="currentColor" stroke-width="3"/></svg>''',
    "XOR": '''<svg width="100" height="60" viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg"><path d="M15,10 C15,10 30,10 45,10 C65,10 75,30 75,30 C75,30 65,50 45,50 C30,50 15,50 15,50 C20,40 20,20 15,10" fill="none" stroke="currentColor" stroke-width="3"/><path d="M5,10 C10,20 10,40 5,50" fill="none" stroke="currentColor" stroke-width="3"/><path d="M0,20 L13,20 M0,40 L13,40 M75,30 L85,30" stroke="currentColor" stroke-width="3"/></svg>'''
}

THEMES = {
    "專業暗色 (Night City)": {
        "bg": "#212529", "txt": "#E9ECEF", "btn": "#495057", "btn_txt": "#FFFFFF", "card": "#343A40", 
        "chart": ["#00ADB5", "#EEEEEE", "#FF2E63"]
    },
    "舒適亮色 (Day City)": {
        "bg": "#F8F9FA", "txt": "#343A40", "btn": "#6C757D", "btn_txt": "#FFFFFF", "card": "#FFFFFF", 
        "chart": ["#343A40", "#6C757D", "#ADB5BD"]
    },
    "海軍藍 (Port City)": {
        "bg": "#1A2530", "txt": "#DDE1E5", "btn": "#3E5C76", "btn_txt": "#FFFFFF", "card": "#2C3E50", 
        "chart": ["#66FCF1", "#45A29E", "#1F2833"]
    }
}

if "state" not in st.session_state:
    st.session_state.update({
        "state": True, "name": "", "title": "市政執行官", "level": "區域管理員", 
        "used_ids": [], "history": [], "theme_name": "專業暗色 (Night City)",
        "exam_active": False, "quiz_batch": []
    })

def apply_theme():
    t = THEMES[st.session_state.theme_name]
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {t['bg']} !important; }}
    h1, h2, h3, h4, p, span, div, label, li, .stMarkdown, .stExpander {{ color: {t['txt']} !important; font-family: 'Segoe UI', sans-serif; }}
    .stButton>button {{ background-color: {t['btn']} !important; color: {t['btn_txt']} !important; border: none !important; border-radius: 6px !important; padding: 0.5rem 1rem; }}
    div[data-testid="stDataFrame"], div[data-testid="stExpander"] {{ background-color: {t['card']} !important; border: 1px solid rgba(128,128,128,0.2); border-radius: 8px; }}
    [data-testid="stSidebar"] {{ background-color: {t['card']}; border-right: 1px solid rgba(128,128,128,0.1); }}
    </style>
    """, unsafe_allow_html=True)

def render_svg(svg_code):
    svg_black = svg_code.replace('stroke="currentColor"', 'stroke="#000000"').replace('fill="currentColor"', 'fill="#000000"')
    b64 = base64.b64encode(svg_black.encode('utf-8')).decode("utf-8")
    st.markdown(f'''<div style="background-color: #FFFFFF; border-radius: 8px; padding: 20px; margin-bottom: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"><img src="data:image/svg+xml;base64,{b64}" width="200"/></div>''', unsafe_allow_html=True)

def get_chart_data():
    return pd.DataFrame(
        np.random.randint(20, 90, size=(20, 3)) + np.random.randn(20, 3) * 8,
        columns=['CPU Load', 'Net I/O', 'Sec Level']
    )

def load_qs():
    q = []
    if os.path.exists("questions.txt"):
        try:
            with open("questions.txt", "r", encoding="utf-8") as f:
                for l in f:
                    p = l.strip().split("|")
                    if len(p)==5: q.append({"id":p[0],"diff":p[1],"q":p[2],"o":p[3].split(","),"a":p[4]})
        except: pass
    return q

def has_access(rank):
    if st.session_state.name.lower() == "frank": return True
    order = ["區域管理員", "城市規劃師", "系統工程師", "最高指揮官"]
    try: return order.index(st.session_state.level) >= order.index(rank)
    except: return False

# ==================================================
# 2. 主程式
# ==================================================
def main():
    apply_theme()
    is_frank = st.session_state.name.lower() == "frank"
    t_colors = THEMES[st.session_state.theme_name]["chart"]

    with st.sidebar:
        st.title("🏙️ CityOS V141")
        st.caption("Central Command Interface")
        st.markdown(f"""
        <div style="padding:15px; background:rgba(255,255,255,0.05); border-radius:8px; margin-bottom:15px; border-left: 4px solid #4CAF50;">
            <div style="font-size:1.1em;">👤 <b>{st.session_state.title}</b></div>
            <div style="font-size:0.9em; opacity:0.8;">ID: {st.session_state.name}</div>
            <div style="font-size:0.8em; margin-top:5px;">權限等級: {st.session_state.level if not is_frank else 'ROOT (最高指揮官)'}</div>
        </div>
        """, unsafe_allow_html=True)
        st.divider()
        # [恢復] 完整選單
        menu = ["🏙️ 城市儀表板", "⚡ 電力設施 (Logic)", "🏦 數據中心 (Math)", "🎓 市政學院 (Quiz)"]
        if is_frank or has_access("城市規劃師"): menu.append("🧮 節點優化 (Map)")
        else: menu.append("🔒 節點優化 (鎖定)")
        if is_frank or has_access("系統工程師"): menu.append("🔀 交通調度 (MUX)")
        else: menu.append("🔒 交通調度 (鎖定)")
        menu.append("📂 人事檔案")
        page = st.radio("導航", menu)

    # --- 頁面內容 ---
    if "城市儀表板" in page:
        st.title("🏙️ 城市中控儀表板 (Dashboard)")
        
        col_main, col_side = st.columns([2, 1])
        
        with col_main:
            st.subheader("📖 市政操作手冊")
            with st.expander("📌 模組功能總覽", expanded=True):
                st.markdown("""
                * **⚡ 電力設施**：監控 AND/OR/XOR 等邏輯閘運作。
                * **🏦 數據中心**：進制轉換運算 (Bin/Hex/Dec)。
                * **🎓 市政學院**：Batch-5 連鎖考核模式。
                * **🔀 交通調度**：MUX 多工器線路模擬。
                """)
            
            st.divider()
            
            # [功能] 高速圖表 + 按鈕
            c1, c2 = st.columns([3,1])
            with c1: st.subheader("📡 系統即時監控 (100Hz Live)")
            with c2: 
                if st.button("⚡ 立即刷新", use_container_width=True):
                    st.toast("數據緩衝已清除")

            chart_placeholder = st.empty()
            for i in range(50):
                new_data = get_chart_data()
                chart_placeholder.area_chart(new_data, color=t_colors, height=250)
                time.sleep(0.01) # 加速
            
        with col_side:
            st.subheader("⚠️ 安全公告")
            st.warning("所有子系統 (Math, Map, MUX) 連線已恢復。")
            
            # [更新] 日誌表格化
            st.subheader("🛠️ 系統更新日誌")
            log_data = [
                {"版本": "V1.4.1", "日期": "2026-01-04", "內容": "功能復原：Math/MUX/Map 重新上線"},
                {"版本": "V1.4.1", "日期": "2026-01-04", "內容": "UI 優化：日誌改為表格顯示"},
                {"版本": "V1.4.0", "日期": "2026-01-04", "內容": "核心升級：監控圖表加速 (0.01s)"},
                {"版本": "V1.4.0", "日期": "2026-01-04", "內容": "考核升級：5題連鎖 (Batch-5)"},
                {"版本": "V1.3.9", "日期": "2026-01-03", "內容": "介面重構：登入頁面極簡化"},
            ]
            df_log = pd.DataFrame(log_data)
            st.dataframe(df_log, use_container_width=True, hide_index=True)

    elif "電力設施" in page:
        st.header("⚡ 電力設施監控")
        gate = st.selectbox("監控節點", ["AND", "OR", "XOR", "NOT"])
        c1, c2 = st.columns([1, 2])
        with c1: render_svg(SVG_ICONS.get(gate, SVG_ICONS["AND"]))
        with c2:
            st.subheader("邏輯真值表")
            d = {"Input A":[0,0,1,1], "Input B":[0,1,0,1]}
            if gate=="AND": d["Out"]=[0,0,0,1]
            elif gate=="OR": d["Out"]=[0,1,1,1]
            elif gate=="XOR": d["Out"]=[0,1,1,0]
            elif gate=="NOT": d={"Input":[0,1], "Out":[1,0]}
            st.dataframe(pd.DataFrame(d), use_container_width=True, hide_index=True)

    elif "數據中心" in page:
        st.header("🏦 數據中心 (Data Center)")
        c1, c2 = st.columns(2)
        with c1:
            val = st.text_input("輸入十進制數值 (0-9999)", "255")
            if val.isdigit():
                v = int(val)
                st.metric("Binary (二進制)", bin(v)[2:])
                st.metric("Hex (十六進制)", hex(v)[2:].upper())
        with c2:
            st.info("此模組負責將人類指令轉換為機器碼。")

    elif "節點優化" in page:
        if "🔒" in page: st.error("權限不足"); st.stop()
        st.header("🧮 K-Map 邏輯優化")
        c1, c2 = st.columns(2)
        with c1:
            st.write("輸入狀態 High (1):")
            cc1, cc2 = st.columns(2)
            m0 = cc1.checkbox("00", False); m1 = cc2.checkbox("01", False)
            m2 = cc1.checkbox("10", False); m3 = cc2.checkbox("11", False)
        with c2:
            if m0 and m1 and m2 and m3: st.success("Result: 1")
            elif m0 and m1: st.success("Result: A'")
            elif m2 and m3: st.success("Result: A")
            elif m0 and m2: st.success("Result: B'")
            elif m1 and m3: st.success("Result: B")
            else: st.warning("無簡化可能")

    elif "交通調度" in page:
        if "🔒" in page: st.error("權限不足"); st.stop()
        st.header("🔀 MUX 數據流調度")
        c1, c2 = st.columns(2)
        with c1: render_svg(SVG_ICONS["MUX"])
        with c2:
            s = st.selectbox("選擇通道 (S1, S0)", ["00", "01", "10", "11"])
            st.metric("導通線路", f"Line {int(s, 2)}")

    elif "市政學院" in page:
        st.header("🎓 市政管理能力考評 (Batch-5)")
        
        if not st.session_state.exam_active:
            st.info("本次考核將連續發布 5 道指令。請做好準備。")
            if st.button("🚀 啟動 5 連戰", type="primary"):
                qs = load_qs()
                if len(qs) >= 5:
                    st.session_state.quiz_batch = random.sample(qs, 5)
                    st.session_state.exam_active = True
                    st.rerun()
                else: st.error("題庫連線中斷 (題目不足)")
        else:
            with st.form("exam_form"):
                user_ans = {}
                for i, q in enumerate(st.session_state.quiz_batch):
                    st.markdown(f"**{i+1}. {q['q']}**")
                    user_ans[i] = st.radio(f"Ans {i}", q['o'], key=f"q{i}", index=None, label_visibility="collapsed")
                    st.divider()
                
                if st.form_submit_button("🔒 提交決策"):
                    if any(a is None for a in user_ans.values()):
                        st.warning("請完成所有決策")
                    else:
                        score = 0
                        for i, q in enumerate(st.session_state.quiz_batch):
                            if user_ans[i] == q['a']: score += 1
                            st.session_state.history.append({"時間":datetime.now().strftime("%H:%M"), "結果": "✅" if user_ans[i]==q['a'] else "❌", "ID":q['id']})
                        
                        if score==5: 
                            st.balloons(); st.success("完美決策！(5/5)")
                            if st.session_state.level == "區域管理員": st.session_state.level = "城市規劃師"
                        else: st.error(f"考核結束。得分：{score}/5")
                        st.session_state.exam_active = False
                        time.sleep(2)
                        st.rerun()

    elif "人事檔案" in page:
        st.header("📂 人事檔案")
        st.text_input("ID", st.session_state.name, disabled=True)
        st.selectbox("主題", list(THEMES.keys()), key="theme_name")
        if st.button("登出"):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()
        st.subheader("📜 歷史紀錄")
        if st.session_state.history:
            st.dataframe(pd.DataFrame(st.session_state.history)[::-1], use_container_width=True, hide_index=True)

# ==================================================
# 3. 入口
# ==================================================
if not st.session_state.name:
    apply_theme()
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.title("🏙️ CityOS V141")
        st.markdown('<div style="text-align:center; color:#888;">System Access Required</div>', unsafe_allow_html=True)
        with st.form("login"):
            n = st.text_input("Commander ID")
            if st.form_submit_button("Initialize"):
                if n: st.session_state.name = n; st.rerun()
else:
    main()
