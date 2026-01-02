import streamlit as st
import pandas as pd
import random
import os
import base64
import time
import numpy as np # 新增 numpy 用於生成圖表數據
from datetime import datetime

# ==================================================
# 0. 自動化題庫生成系統 (首次運行自動建立 1000 題)
# ==================================================
def init_question_bank():
    if not os.path.exists("questions.txt"):
        with st.spinner("正在初始化市政題庫 (生成 1000 題)..."):
            with open("questions.txt", "w", encoding="utf-8") as f:
                # 1. 邏輯閘題目生成
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
                
                # 2. 進制轉換題目生成
                for _ in range(300):
                    val = random.randint(1, 15)
                    line = f"MATH-{random.randint(1000,9999)}|2|十進制數值 {val} 的二進制表示為何？|{bin(val)[2:]},{bin(val+1)[2:]},{bin(val-1)[2:]},0000|{bin(val)[2:]}\n"
                    f.write(line)
                
                # 3. 系統管理常識
                base_qs = [
                    "SYS-001|1|CityOS 的核心邏輯運算單元是什麼？|CPU,GPU,APU,TPU|CPU",
                    "SYS-002|1|在 MUX 多工器中，若有 4 條輸入線，需要幾條選擇線？|1,2,4,8|2",
                    "SYS-003|2|JK 正反器當 J=1, K=1 時的狀態為何？|保持,重置,設定,反轉 (Toggle)|反轉 (Toggle)",
                    "SYS-004|3|卡諾圖 (K-Map) 主要用於什麼用途？|加密數據,壓縮影像,化簡布林代數,增加冗餘|化簡布林代數"
                ]
                # 複製常識題補滿剩餘
                for _ in range(300):
                    q = random.choice(base_qs)
                    # 加上隨機後綴避免 ID 重複
                    parts = q.strip().split("|")
                    parts[0] = f"{parts[0]}-{random.randint(100,999)}" 
                    f.write("|".join(parts) + "\n")
            st.success("✅ 題庫初始化完成：已生成 1000 道考題。")

# ==================================================
# 1. 系統設定與圖庫
# ==================================================
st.set_page_config(page_title="CityOS V138", layout="wide")

# 初始化題庫
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
    "專業暗色 (Night City)": {"bg": "#212529", "txt": "#E9ECEF", "btn": "#495057", "btn_txt": "#FFFFFF", "card": "#343A40", "chart": ["#00ADB5", "#EEEEEE"]},
    "舒適亮色 (Day City)": {"bg": "#F8F9FA", "txt": "#343A40", "btn": "#6C757D", "btn_txt": "#FFFFFF", "card": "#FFFFFF", "chart": ["#343A40", "#6C757D"]},
    "海軍藍 (Port City)": {"bg": "#1A2530", "txt": "#DDE1E5", "btn": "#3E5C76", "btn_txt": "#FFFFFF", "card": "#2C3E50", "chart": ["#66FCF1", "#45A29E"]}
}

if "state" not in st.session_state:
    st.session_state.update({
        "state": True, "name": "", "title": "市政執行官", "level": "區域管理員", 
        "used_ids": [], "history": [], "theme_name": "專業暗色 (Night City)",
        "exam_active": False, "current_q": None
    })

# ==================================================
# 2. 視覺渲染引擎
# ==================================================
def apply_theme():
    t = THEMES[st.session_state.theme_name]
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {t['bg']} !important; }}
    h1, h2, h3, h4, p, span, div, label, li, .stMarkdown, .stExpander {{ color: {t['txt']} !important; font-family: 'Segoe UI', sans-serif; }}
    .stButton>button {{ background-color: {t['btn']} !important; color: {t['btn_txt']} !important; border: none !important; border-radius: 6px !important; padding: 0.5rem 1rem; }}
    div[data-testid="stDataFrame"], div[data-testid="stExpander"] {{ background-color: {t['card']} !important; border: 1px solid rgba(128,128,128,0.2); border-radius: 8px; }}
    [data-testid="stSidebar"] {{ background-color: {t['card']}; border-right: 1px solid rgba(128,128,128,0.1); }}
    .info-box {{ background-color: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 3px solid {t['btn']}; }}
    </style>
    """, unsafe_allow_html=True)

def render_svg(svg_code):
    svg_black = svg_code.replace('stroke="currentColor"', 'stroke="#000000"').replace('fill="currentColor"', 'fill="#000000"')
    b64 = base64.b64encode(svg_black.encode('utf-8')).decode("utf-8")
    st.markdown(f'''<div style="background-color: #FFFFFF; border-radius: 8px; padding: 20px; margin-bottom: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"><img src="data:image/svg+xml;base64,{b64}" width="200"/></div>''', unsafe_allow_html=True)

# 輔助：生成動態數據
def get_chart_data():
    return pd.DataFrame(
        np.random.randint(10, 90, size=(20, 3)),
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
# 3. 主程式
# ==================================================
def main():
    apply_theme()
    is_frank = st.session_state.name.lower() == "frank"
    t_colors = THEMES[st.session_state.theme_name]["chart"]

    with st.sidebar:
        st.title("🏙️ CityOS V138")
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
        st.info(f"👋 歡迎回來，{st.session_state.title}。系統即時監控模組已上線。")
        
        col_main, col_side = st.columns([2, 1])
        
        with col_main:
            st.subheader("📡 即時系統流量 (Real-time Metric)")
            # 生成動態圖表
            chart_data = get_chart_data()
            st.area_chart(chart_data, color=t_colors)
            st.caption("※ 數據來源：虛擬市政傳感器網路 (模擬即時波動)")

            st.subheader("📖 市政操作手冊 (詳盡版)")
            with st.expander("📌 點擊展開：模組功能與戰略描述", expanded=True):
                st.markdown("""
                ### 1. 基礎設施層
                * **⚡ 電力設施 (Logic Gates)**：
                    * **功能**：監控邏輯閘的輸入與輸出狀態。
                    * **戰略意義**：這是城市運作的基石。AND 閘用於「雙重認證」，OR 閘用於「備援系統」，NOT 閘用於「訊號反轉」。
                
                ### 2. 運算核心層
                * **🏦 數據中心 (Math)**：
                    * **功能**：執行十進制與二進制/十六進制的快速轉換。
                    * **戰略意義**：底層機械碼溝通的橋樑。IP 地址配置與記憶體定址皆依賴此模組。

                ### 3. 人才晉升層
                * **🎓 市政學院 (Quiz)**：
                    * **功能**：提供 1000+ 題隨機變化的專業考核。
                    * **戰略意義**：這是唯一提升您「管理員權限等級」的途徑。答對累積積分，答錯則需重新學習。
                """)

        with col_side:
            st.subheader("⚠️ 安全公告")
            st.warning("近期檢測到未授權的 Port 掃描。請各位指揮官在進行考評時，務必確認自身權限。")
            
            st.subheader("🛠️ 更新日誌")
            st.markdown("""
            <div class="log-entry"><b>[V1.3.8]</b> 題庫擴充至 1000 題<br>監控圖表全面動態化</div>
            <div class="log-entry"><b>[V1.3.7]</b> 新增考評確認機制</div>
            <div class="log-entry"><b>[V1.3.6]</b> 介面城市化風格更新</div>
            """, unsafe_allow_html=True)

    elif "電力設施" in page:
        st.header("⚡ 電力設施監控")
        gate = st.selectbox("監控節點", ["AND", "OR", "XOR", "NOT"])
        
        c1, c2, c3 = st.columns([1, 1.5, 1.5])
        with c1: 
            render_svg(SVG_ICONS.get(gate, SVG_ICONS["AND"]))
        with c2:
            st.subheader("訊號真值表")
            d = {"In A":[0,0,1,1], "In B":[0,1,0,1]}
            if gate=="AND": d["Out"]=[0,0,0,1]
            elif gate=="OR": d["Out"]=[0,1,1,1]
            elif gate=="XOR": d["Out"]=[0,1,1,0]
            elif gate=="NOT": d={"In":[0,1], "Out":[1,0]}
            st.dataframe(pd.DataFrame(d), use_container_width=True, hide_index=True)
        with c3:
            st.subheader("技術規格說明")
            desc = ""
            if gate == "AND": desc = "所有輸入皆為 High 時，輸出才為 High。常用於『安全聯鎖機制』(如：鑰匙A + 鑰匙B 同時插入才能發射)。"
            elif gate == "OR": desc = "任一輸入為 High 時，輸出即為 High。常用於『警報觸發系統』(如：火災 OR 地震 皆觸發警鈴)。"
            elif gate == "XOR": desc = "輸入狀態相異時輸出為 High。常用於『數據加密』與『奇偶校驗』(Parity Check)。"
            elif gate == "NOT": desc = "訊號反相器。將 1 變 0，0 變 1。是構成所有複雜數位電路的原子元件。"
            st.info(desc)
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
            ref_data = {
                "Power of 2": ["2^0", "2^1", "2^2", "2^3", "2^4", "2^5", "2^6", "2^7", "2^8"],
                "Decimal": [1, 2, 4, 8, 16, 32, 64, 128, 256],
                "Hex": ["01", "02", "04", "08", "10", "20", "40", "80", "100"]
            }
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
            st.markdown("#### 優化分析報告")
            if m0 and m1 and m2 and m3: st.success("邏輯結果: 常數 1 (恆導通)")
            elif m0 and m1: st.success("邏輯結果: A' (僅與 A 相關)")
            elif m2 and m3: st.success("邏輯結果: A (僅與 A 相關)")
            elif m0 and m2: st.success("邏輯結果: B' (僅與 B 相關)")
            elif m1 and m3: st.success("邏輯結果: B (僅與 B 相關)")
            else: st.warning("未檢測到可化簡的相鄰群組 (Grouping)")
            
            st.info("K-Map 優化可減少邏輯閘數量，降低系統功耗與延遲。")

    elif "交通調度" in page:
        if "🔒" in page: st.error("權限不足"); st.stop()
        st.header("🔀 數據流交通調度 (MUX)")
        col_img, col_ctrl, col_desc = st.columns([1, 1, 1])
        with col_img: render_svg(SVG_ICONS["MUX"])
        with col_ctrl:
            s = st.selectbox("選擇通道 (S1, S0)", ["00", "01", "10", "11"])
            st.metric("當前導通線路", f"Data Line {int(s, 2)}")
        with col_desc:
            st.markdown("#### 運作原理")
            st.write("多工器 (Multiplexer) 就像是鐵軌的轉轍器。根據 S1, S0 的控制訊號，決定哪一條輸入線路 (D0-D3) 的資料可以通過傳送到唯一的輸出端。")

    elif "市政學院" in page:
        st.header("🎓 市政管理能力考評")
        
        if not st.session_state.exam_active:
            c1, c2 = st.columns([2, 1])
            with c1:
                st.info("準備好開始新的考核了嗎？這將影響您的權限評估。")
                st.markdown("""
                **考核規則：**
                1. 題目由系統從 1000 題庫中隨機抽取。
                2. 選項不再預設，請謹慎選擇。
                3. 提交後即時判分。
                """)
                if st.button("🚀 啟動考核程序", type="primary"):
                    qs = load_qs()
                    if not qs:
                        st.error("錯誤：題庫連線失敗")
                    else:
                        st.session_state.current_q = random.choice(qs)
                        st.session_state.exam_active = True
                        st.rerun()
            with c2:
                 st.metric("題庫總量", "1000+", "充足")
                 st.metric("歷史答題數", len(st.session_state.history))

        else:
            q = st.session_state.current_q
            st.markdown(f"### 📝 考題 ID-{q['id']}")
            st.write(f"**{q['q']}**")
            
            with st.form("exam_form"):
                # 重要修改：index=None 不預先選答案
                ans = st.radio("請選擇處置方案：", q['o'], index=None) 
                submitted = st.form_submit_button("🔒 確認並提交")
                
                if submitted:
                    if ans is None:
                        st.warning("⚠️ 請先選擇一個答案再提交。")
                    else:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        is_correct = (ans == q['a'])
                        
                        st.session_state.history.append({
                            "時間": timestamp,
                            "題目ID": q['id'],
                            "結果": "✅ 通過" if is_correct else "❌ 失敗"
                        })
                        
                        if is_correct:
                            st.balloons()
                            if st.session_state.level == "區域管理員": st.session_state.level = "城市規劃師"
                            st.success("判定正確！權限積分已累積。")
                        else:
                            st.error(f"判定錯誤。正確方案應為：{q['a']}")
                        
                        st.session_state.exam_active = False
                        st.session_state.current_q = None
                        time.sleep(1.5) # 稍作停留
                        st.rerun()

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
            if not st.session_state.history: st.info("無紀錄")
            else:
                df = pd.DataFrame(st.session_state.history)[::-1]
                st.dataframe(df, use_container_width=True, hide_index=True)

# ==================================================
# 4. 入口
# ==================================================
if not st.session_state.name:
    apply_theme()
    st.title("🏙️ CityOS V138")
    c1, c2 = st.columns([1,1])
    with c1:
        st.markdown("### 城市核心控制終端")
        st.markdown("請輸入您的 **管理員 ID** 以存取系統。")
        n = st.text_input("Admin ID", placeholder="e.g., Frank")
        if st.button("連線"):
            if n: st.session_state.name = n; st.rerun()
    with c2:
        # 首頁也放個動態圖裝飾
        st.line_chart(np.random.randn(20, 2), height=200)

else:
    main()
