import streamlit as st
import pandas as pd
import random
import os
import base64
import time
import numpy as np 
from datetime import datetime

# ==================================================
# 0. 自動化題庫生成系統
# ==================================================
def init_question_bank():
    should_generate = False
    if not os.path.exists("questions.txt"):
        should_generate = True
    else:
        with open("questions.txt", "r", encoding="utf-8") as f:
            if len(f.readlines()) < 100:
                should_generate = True

    if should_generate:
        with st.spinner("正在初始化市政題庫 (生成 1000 題)..."):
            with open("questions.txt", "w", encoding="utf-8") as f:
                gates = ["AND", "OR", "XOR", "NAND"]
                for _ in range(400):
                    g = random.choice(gates)
                    a = random.randint(0, 1)
                    b = random.randint(0, 1)
                    ans = 0
                    if g == "AND": ans = a & b
                    elif g == "OR": ans = a | b
                    elif g == "XOR": ans = a ^ b
                    elif g == "NAND": ans = 1 - (a & b)
                    line = f"LOGIC-{random.randint(1000,9999)}|1|若輸入 A={a}, B={b}, 經過 {g} 閘後的輸出為何？|0,1,High Z,Unknown|{ans}\n"
                    f.write(line)
                
                for _ in range(300):
                    val = random.randint(1, 15)
                    line = f"MATH-{random.randint(1000,9999)}|2|十進制數值 {val} 的二進制表示為何？|{bin(val)[2:]},{bin(val+1)[2:]},{bin(val-1)[2:]},0000|{bin(val)[2:]}\n"
                    f.write(line)
                
                base_qs = [
                    "SYS-001|1|CityOS 的核心邏輯運算單元是什麼？|CPU,GPU,APU,TPU|CPU",
                    "SYS-002|1|在 MUX 多工器中，若有 4 條輸入線，需要幾條選擇線？|1,2,4,8|2",
                    "SYS-003|2|JK 正反器當 J=1, K=1 時的狀態為何？|保持,重置,設定,反轉 (Toggle)|反轉 (Toggle)",
                    "SYS-004|3|卡諾圖 (K-Map) 主要用於什麼用途？|加密數據,壓縮影像,化簡布林代數,增加冗餘|化簡布林代數"
                ]
                for _ in range(300):
                    q = random.choice(base_qs)
                    parts = q.strip().split("|")
                    parts[0] = f"{parts[0]}-{random.randint(100,999)}" 
                    f.write("|".join(parts) + "\n")

# ==================================================
# 1. 系統設定與素材
# ==================================================
st.set_page_config(page_title="CityOS V139", layout="wide")
init_question_bank()

SVG_ICONS = {
    "MUX": '''<svg width="120" height="100" viewBox="0 0 120 100" xmlns="http://www.w3.org/2000/svg"><path d="M30,10 L90,25 L90,75 L30,90 Z" fill="none" stroke="currentColor" stroke-width="3"/><text x="45" y="55" fill="currentColor" font-size="14">MUX</text><path d="M10,25 L30,25 M10,40 L30,40 M10,55 L30,55 M10,70 L30,70 M90,50 L110,50 M60,85 L60,95" stroke="currentColor" stroke-width="2"/></svg>''',
    "FF": '''<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><rect x="20" y="20" width="60" height="60" fill="none" stroke="currentColor" stroke-width="3"/><text x="35" y="55" fill="currentColor" font-size="14">Flip-Flop</text><path d="M10,30 L20,30 M10,70 L20,70 M80,30 L90,30 M80,70 L90,70" stroke="currentColor" stroke-width="2"/></svg>''',
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
        "exam_active": False, "current_q": None
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
    .log-entry {{ border-left: 2px solid {t['btn']}; padding-left: 10px; margin-bottom: 8px; font-size: 0.85em; }}
    </style>
    """, unsafe_allow_html=True)

def render_svg(svg_code):
    svg_black = svg_code.replace('stroke="currentColor"', 'stroke="#000000"').replace('fill="currentColor"', 'fill="#000000"')
    b64 = base64.b64encode(svg_black.encode('utf-8')).decode("utf-8")
    st.markdown(f'''<div style="background-color: #FFFFFF; border-radius: 8px; padding: 20px; margin-bottom: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"><img src="data:image/svg+xml;base64,{b64}" width="200"/></div>''', unsafe_allow_html=True)

def get_chart_data():
    # 模擬隨機波動的數據
    return pd.DataFrame(
        np.random.randint(20, 80, size=(20, 3)) + np.random.randn(20, 3) * 5,
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
# 3. 主程式邏輯
# ==================================================
def main():
    apply_theme()
    is_frank = st.session_state.name.lower() == "frank"
    t_colors = THEMES[st.session_state.theme_name]["chart"]

    with st.sidebar:
        st.title("🏙️ CityOS V139")
        st.caption("Central Command Interface")
        st.markdown(f"""
        <div style="padding:15px; background:rgba(255,255,255,0.05); border-radius:8px; margin-bottom:15px; border-left: 4px solid #4CAF50;">
            <div style="font-size:1.1em;">👤 <b>{st.session_state.title}</b></div>
            <div style="font-size:0.9em; opacity:0.8;">ID: {st.session_state.name}</div>
            <div style="font-size:0.8em; margin-top:5px;">權限等級: {st.session_state.level if not is_frank else 'ROOT (最高指揮官)'}</div>
        </div>
        """, unsafe_allow_html=True)
        st.divider()
        menu = ["🏙️ 城市儀表板", "⚡ 電力設施 (Logic)", "🏦 數據中心 (Math)", "🎓 市政學院 (Quiz)"]
        if is_frank or has_access("城市規劃師"): menu.append("🧮 節點優化 (Map)")
        else: menu.append("🔒 節點優化 (鎖定)")
        if is_frank or has_access("系統工程師"): menu.append("🔀 交通調度 (MUX)")
        else: menu.append("🔒 交通調度 (鎖定)")
        menu.append("📂 人事檔案")
        page = st.radio("導航", menu)

    # --- 頁面內容 ---
    if "城市儀表板" in page:
        st.title("🏙️ 城市中控儀表板 (City Dashboard)")
        st.info(f"👋 歡迎回來，{st.session_state.title}。系統運轉正常，請指示。")
        
        col_main, col_side = st.columns([2, 1])
        
        with col_main:
            # 1. 市政操作手冊 (置頂)
            st.subheader("📖 市政操作手冊")
            with st.expander("📌 點擊展開：模組功能與戰略描述", expanded=True):
                st.markdown("""
                ### 1. 基礎設施層
                * **⚡ 電力設施 (Logic Gates)**：
                    * **核心邏輯**：負責城市最底層的訊號判斷。
                    * **應用場景**：AND(核彈發射雙人確認)、OR(緊急災難多重觸發)、NOT(訊號反轉與加密)。
                
                ### 2. 運算核心層
                * **🏦 數據中心 (Math)**：
                    * **核心邏輯**：處理所有進制轉換 (Bin/Hex/Dec)。
                    * **應用場景**：記憶體位置定址、網路遮罩計算、權限代碼解析。

                ### 3. 人才晉升層
                * **🎓 市政學院 (Quiz)**：
                    * **核心邏輯**：自動化適性測驗系統。
                    * **應用場景**：**唯一晉升管道**。累積足夠積分後，系統將自動解鎖高階功能模組。
                """)

            st.divider()

            # 2. 即時監控數據 (下移 + 自動運作)
            st.subheader("📡 系統核心即時監控 (Live Feed)")
            st.caption("正在連線至市政傳感器網路... (模擬即時資料流)")
            
            # 建立一個空容器來放置圖表
            chart_placeholder = st.empty()
            
            # 自動運行迴圈 (讓圖表動起來)
            # 注意：Streamlit 機制限制，這裡跑 50 幀讓使用者感覺它在動，隨後停止以節省資源
            for i in range(50):
                new_data = get_chart_data()
                chart_placeholder.area_chart(new_data, color=t_colors, height=250)
                time.sleep(0.05) # 控制更新速度
            
            st.caption("✅ 即時連線穩定。監控週期結束。")

        with col_side:
            st.subheader("⚠️ 安全公告")
            st.warning("偵測到來自 Sector-7 的異常流量。建議加強防火牆設定。")
            
            # 3. 擴充版更新日誌
            st.subheader("🛠️ 系統版本歷史")
            changelog = [
                ("V1.3.9", "2026-01-04", "介面重構：圖表位置優化，登入頁面極簡化"),
                ("V1.3.9", "2026-01-04", "核心更新：引入 Live Feed 自動刷新技術"),
                ("V1.3.8", "2026-01-03", "資料庫：擴充題庫至 1000+ 筆"),
                ("V1.3.8", "2026-01-03", "視覺優化：動態監控圖表上線 (修復配色錯誤)"),
                ("V1.3.7", "2026-01-03", "安全補丁：考評中心新增『防誤觸』雙重驗證"),
                ("V1.3.6", "2026-01-02", "UI/UX：全面城市化風格 (Night/Day City)"),
                ("V1.3.5", "2026-01-02", "底層優化：移除冗餘 SVG 代碼，提升渲染速度"),
                ("V1.3.0", "2025-12-30", "新功能：K-Map 邏輯節點優化模組上線"),
                ("V1.2.0", "2025-12-25", "新功能：MUX 交通調度系統上線"),
                ("V1.0.0", "2025-12-01", "CityOS 創始版本發布：基礎邏輯閘功能"),
            ]
            
            # 使用 HTML 渲染長列表，增加捲動感
            log_html = '<div style="height: 400px; overflow-y: scroll;">'
            for ver, date, desc in changelog:
                log_html += f"""
                <div class="log-entry">
                    <div style="font-weight:bold; color:{THEMES[st.session_state.theme_name]['btn']}">[{ver}] <span style="font-weight:normal; opacity:0.6; font-size:0.8em;">{date}</span></div>
                    <div style="margin-top:2px;">{desc}</div>
                </div>
                """
            log_html += '</div>'
            st.markdown(log_html, unsafe_allow_html=True)

    elif "電力設施" in page:
        st.header("⚡ 電力設施監控")
        gate = st.selectbox("監控節點", ["AND", "OR", "XOR", "NOT"])
        c1, c2, c3 = st.columns([1, 1.5, 1.5])
        with c1: render_svg(SVG_ICONS.get(gate, SVG_ICONS["AND"]))
        with c2:
            st.subheader("訊號真值表")
            d = {"In A":[0,0,1,1], "In B":[0,1,0,1]}
            if gate=="AND": d["Out"]=[0,0,0,1]
            elif gate=="OR": d["Out"]=[0,1,1,1]
            elif gate=="XOR": d["Out"]=[0,1,1,0]
            elif gate=="NOT": d={"In":[0,1], "Out":[1,0]}
            st.dataframe(pd.DataFrame(d), use_container_width=True, hide_index=True)
        with c3:
            st.info("技術規格：所有邏輯閘皆採用軍規級半導體製程，誤差率低於 0.001%。")
            st.metric("節點運作效率", f"{random.randint(95,100)}%")

    elif "數據中心" in page:
        st.header("🏦 數據中心 (Data Center)")
        c_input, c_info = st.columns([1, 1])
        with c_input:
            val = st.text_input("輸入十進制資源數值 (0-9999)", "255")
            if val.isdigit():
                v = int(val)
                st.markdown("#### 轉換結果")
                c1, c2 = st.columns(2)
                c1.metric("Binary (二進制)", bin(v)[2:])
                c2.metric("Hex (十六進制)", hex(v)[2:].upper())
                st.divider()
                st.metric("Octal (八進制)", oct(v)[2:])
            else: st.error("錯誤：請輸入有效整數")
        with c_info:
            st.subheader("常用對照速查表")
            ref_data = {"Power of 2": ["2^0", "2^1", "2^2", "2^3", "2^4", "2^5"], "Decimal": [1, 2, 4, 8, 16, 32], "Hex": ["01", "02", "04", "08", "10", "20"]}
            st.dataframe(pd.DataFrame(ref_data), use_container_width=True, hide_index=True)

    elif "節點優化" in page:
        if "🔒" in page: st.error("權限不足"); st.stop()
        st.header("🧮 邏輯節點優化 (K-Map)")
        c1, c2 = st.columns([1, 1])
        with c1:
            st.write("勾選 High (1) 輸出區域：")
            cc1, cc2 = st.columns(2)
            m0 = cc1.checkbox("Cell 00", False); m1 = cc2.checkbox("Cell 01", False)
            m2 = cc1.checkbox("Cell 10", False); m3 = cc2.checkbox("Cell 11", False)
        with c2:
            if m0 and m1 and m2 and m3: st.success("邏輯結果: 1")
            elif m0 and m1: st.success("邏輯結果: A'")
            elif m2 and m3: st.success("邏輯結果: A")
            elif m0 and m2: st.success("邏輯結果: B'")
            elif m1 and m3: st.success("邏輯結果: B")
            else: st.warning("未檢測到可化簡群組")

    elif "交通調度" in page:
        if "🔒" in page: st.error("權限不足"); st.stop()
        st.header("🔀 數據流交通調度 (MUX)")
        col_img, col_ctrl, col_desc = st.columns([1, 1, 1])
        with col_img: render_svg(SVG_ICONS["MUX"])
        with col_ctrl:
            s = st.selectbox("選擇通道 (S1, S0)", ["00", "01", "10", "11"])
            st.metric("當前導通線路", f"Data Line {int(s, 2)}")
        with col_desc: st.write("根據 S1, S0 的控制訊號，決定哪一條輸入線路 (D0-D3) 的資料可以通過。")

    elif "市政學院" in page:
        st.header("🎓 市政管理能力考評")
        if not st.session_state.exam_active:
            c1, c2 = st.columns([2, 1])
            with c1:
                st.info("準備好開始新的考核了嗎？這將影響您的權限評估。")
                if st.button("🚀 啟動考核程序", type="primary"):
                    qs = load_qs()
                    if qs: st.session_state.current_q = random.choice(qs); st.session_state.exam_active = True; st.rerun()
                    else: st.error("題庫連線失敗")
            with c2: st.metric("題庫總量", "1000+", "充足")
        else:
            q = st.session_state.current_q
            st.markdown(f"### 📝 考題 ID-{q['id']}")
            st.write(f"**{q['q']}**")
            with st.form("exam_form"):
                ans = st.radio("請選擇處置方案：", q['o'], index=None)
                if st.form_submit_button("🔒 確認並提交"):
                    if ans:
                        is_correct = (ans == q['a'])
                        st.session_state.history.append({"時間": datetime.now().strftime("%H:%M:%S"), "題目ID": q['id'], "結果": "✅ 通過" if is_correct else "❌ 失敗"})
                        if is_correct: 
                            st.balloons()
                            if st.session_state.level == "區域管理員": st.session_state.level = "城市規劃師"
                            st.success("判定正確！")
                        else: st.error(f"判定錯誤。答案：{q['a']}")
                        st.session_state.exam_active = False; st.session_state.current_q = None; time.sleep(1.5); st.rerun()
                    else: st.warning("請選擇答案")

    elif "人事檔案" in page:
        st.header("📂 管理員人事檔案")
        c1, c2 = st.columns([1, 2])
        with c1:
            st.image("https://api.dicebear.com/7.x/bottts/svg?seed="+st.session_state.name, width=150)
            st.text_input("代碼", st.session_state.name, disabled=True)
            new_title = st.text_input("職稱", st.session_state.title)
            if new_title != st.session_state.title: st.session_state.title = new_title; st.rerun()
            sel = st.selectbox("主題", list(THEMES.keys()), index=list(THEMES.keys()).index(st.session_state.theme_name))
            if sel != st.session_state.theme_name: st.session_state.theme_name = sel; st.rerun()
            if st.button("登出指揮系統"):
                for k in list(st.session_state.keys()): del st.session_state[k]
                st.rerun()
        with c2:
            st.subheader("📜 歷史績效")
            if st.session_state.history: st.dataframe(pd.DataFrame(st.session_state.history)[::-1], use_container_width=True, hide_index=True)
            else: st.info("無紀錄")

# ==================================================
# 4. 入口 (Clean Login)
# ==================================================
if not st.session_state.name:
    apply_theme()
    # 登入頁面：極簡化，移除所有圖表
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.title("🏙️ CityOS V139")
        st.markdown("""
        <div style="text-align: center; color: #888; margin-bottom: 20px;">
        Authorized Access Only <br> 城市核心控制終端
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            n = st.text_input("Admin ID", placeholder="Enter Commander Name (e.g., Frank)")
            if st.form_submit_button("連線接入", type="primary"):
                if n: st.session_state.name = n; st.rerun()
else:
    main()
