import streamlit as st
import pandas as pd
import random
import os
import base64
from datetime import datetime

# ==================================================
# 0. 系統常數與日誌
# ==================================================
CHANGELOG = [
    ("V1.3.7", "2026-01-03", "安全升級：考評中心新增啟動確認機制 (防誤觸)"),
    ("V1.3.7", "2026-01-03", "介面更新：首頁新增即時系統監控儀表板"),
    ("V1.3.6", "2026-01-02", "系統全面城市化：介面與用語調整為城市管理風格"),
    ("V1.3.6", "2026-01-02", "新增歷史成績追蹤與市政操作手冊"),
    ("V1.3.5", "2026-01-02", "視覺優化：移除圖片下方干擾文字"),
    ("V1.3.4", "2026-01-02", "修復：SVG 線條強制黑色，解決深色模式隱形問題"),
    ("V1.3.3", "2026-01-01", "降低色彩飽和度，引入莫蘭迪色系"),
    ("V1.3.2", "2025-12-30", "優化 SVG 渲染引擎，加入白底卡片"),
    ("V1.2.0", "2025-12-25", "考評系統上線，支援題庫讀取"),
    ("V1.1.0", "2025-12-20", "基礎邏輯閘視覺化完成"),
]

# ==================================================
# 1. 內嵌 SVG 圖庫
# ==================================================
SVG_ICONS = {
    "MUX": '''<svg width="120" height="100" viewBox="0 0 120 100" xmlns="http://www.w3.org/2000/svg"><path d="M30,10 L90,25 L90,75 L30,90 Z" fill="none" stroke="currentColor" stroke-width="3"/><text x="45" y="55" fill="currentColor" font-size="14">MUX</text><path d="M10,25 L30,25 M10,40 L30,40 M10,55 L30,55 M10,70 L30,70 M90,50 L110,50 M60,85 L60,95" stroke="currentColor" stroke-width="2"/></svg>''',
    "FF": '''<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><rect x="20" y="20" width="60" height="60" fill="none" stroke="currentColor" stroke-width="3"/><text x="35" y="55" fill="currentColor" font-size="14">Flip-Flop</text><path d="M10,30 L20,30 M10,70 L20,70 M80,30 L90,30 M80,70 L90,70" stroke="currentColor" stroke-width="2"/></svg>''',
    "AND": '''<svg width="100" height="60" viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg"><path d="M10,10 L40,10 C55,10 65,20 65,30 C65,40 55,50 40,50 L10,50 Z" fill="none" stroke="currentColor" stroke-width="3"/><path d="M0,20 L10,20 M0,40 L10,40 M65,30 L80,30" stroke="currentColor" stroke-width="3"/></svg>''',
    "OR": '''<svg width="100" height="60" viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg"><path d="M10,10 C10,10 25,10 40,10 C60,10 70,30 70,30 C70,30 60,50 40,50 C25,50 10,50 10,50 C15,40 15,20 10,10" fill="none" stroke="currentColor" stroke-width="3"/><path d="M0,20 L13,20 M0,40 L13,40 M70,30 L80,30" stroke="currentColor" stroke-width="3"/></svg>''',
    "NOT": '''<svg width="100" height="60" viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg"><path d="M20,10 L50,30 L20,50 Z" fill="none" stroke="currentColor" stroke-width="3"/><circle cx="54" cy="30" r="4" fill="none" stroke="currentColor" stroke-width="3"/><path d="M10,30 L20,30 M58,30 L70,30" stroke="currentColor" stroke-width="3"/></svg>''',
}

# ==================================================
# 2. 系統設定
# ==================================================
st.set_page_config(page_title="CityOS V137", layout="wide")

THEMES = {
    "專業暗色 (Night City)": {"bg": "#212529", "txt": "#E9ECEF", "btn": "#495057", "btn_txt": "#FFFFFF", "card": "#343A40"},
    "舒適亮色 (Day City)": {"bg": "#F8F9FA", "txt": "#343A40", "btn": "#6C757D", "btn_txt": "#FFFFFF", "card": "#FFFFFF"},
    "海軍藍 (Port City)": {"bg": "#1A2530", "txt": "#DDE1E5", "btn": "#3E5C76", "btn_txt": "#FFFFFF", "card": "#2C3E50"}
}

if "state" not in st.session_state:
    st.session_state.update({
        "state": True, 
        "name": "", 
        "title": "市政執行官", 
        "level": "區域管理員", 
        "used_ids": [], 
        "history": [],
        "theme_name": "專業暗色 (Night City)",
        "exam_active": False, # 新增：考試啟動狀態
        "current_q": None     # 新增：暫存當前題目
    })

# ==================================================
# 3. 視覺渲染引擎
# ==================================================
def apply_theme():
    t = THEMES[st.session_state.theme_name]
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {t['bg']} !important; }}
    h1, h2, h3, h4, p, span, div, label, li, .stMarkdown, .stExpander {{ color: {t['txt']} !important; font-family: 'Segoe UI', sans-serif; }}
    .stButton>button {{ background-color: {t['btn']} !important; color: {t['btn_txt']} !important; border: none !important; border-radius: 6px !important; padding: 0.5rem 1rem; }}
    div[data-testid="stDataFrame"] {{ background-color: {t['card']} !important; border: 1px solid rgba(128,128,128,0.2); padding: 5px; border-radius: 8px; }}
    [data-testid="stSidebar"] {{ background-color: {t['card']}; border-right: 1px solid rgba(128,128,128,0.1); }}
    .log-entry {{ border-left: 3px solid {t['btn']}; padding-left: 10px; margin-bottom: 8px; font-size: 0.9em; }}
    /* 儀表板數值顏色 */
    [data-testid="stMetricValue"] {{ color: {t['btn']} !important; }}
    </style>
    """, unsafe_allow_html=True)

def render_svg(svg_code):
    svg_black = svg_code.replace('stroke="currentColor"', 'stroke="#000000"').replace('fill="currentColor"', 'fill="#000000"')
    b64 = base64.b64encode(svg_black.encode('utf-8')).decode("utf-8")
    html = f'''<div style="background-color: #FFFFFF; border-radius: 8px; padding: 20px; margin-bottom: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"><img src="data:image/svg+xml;base64,{b64}" width="200"/></div>'''
    st.markdown(html, unsafe_allow_html=True)

# ==================================================
# 4. 輔助功能
# ==================================================
def has_access(rank):
    if st.session_state.name.lower() == "frank": return True
    order = ["區域管理員", "城市規劃師", "系統工程師", "最高指揮官"]
    try: return order.index(st.session_state.level) >= order.index(rank)
    except: return False

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

# ==================================================
# 5. 主程式
# ==================================================
def main():
    apply_theme()
    is_frank = st.session_state.name.lower() == "frank"
    
    with st.sidebar:
        st.title("🏙️ CityOS V137")
        st.caption("Central Command Interface")
        
        # 用戶卡片
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
        if is_frank or has_access("最高指揮官"): menu.append("🔄 時序控制 (Seq)")
        else: menu.append("🔒 時序控制 (鎖定)")
        menu.append("📂 人事檔案")
        
        page = st.radio("導航", menu)

    # --- 頁面內容 ---
    if "城市儀表板" in page:
        st.title("🏙️ 城市中控儀表板 (City Dashboard)")
        st.info("👋 歡迎回來，指揮官。CityOS 系統運轉正常。")
        
        col_intro, col_log = st.columns([1.5, 1])
        
        with col_intro:
            st.subheader("📖 市政操作手冊")
            with st.expander("📌 點擊展開模組說明", expanded=False):
                st.markdown("""
                * **⚡ 電力設施**：邏輯閘訊號監控。
                * **🏦 數據中心**：二進位與十六進位運算。
                * **🎓 市政學院**：管理員晉升考核。
                """)
            
            st.subheader("⚠️ 安全須知")
            st.warning("請勿在未授權狀態下存取 ROOT 節點。考評系統現已啟用雙重確認機制。")

            # --- 修改點 1: 儀表板化 ---
            st.subheader("📡 即時監控數據")
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric(label="核心負載 (CPU)", value="42%", delta="-5%")
            with m2:
                st.metric(label="網路吞吐量 (Net)", value="1.2 GB/s", delta="穩定")
            with m3:
                st.metric(label="資安防護等級", value="A+", delta="Secure")

        with col_log:
            st.subheader("🛠️ 系統更新日誌")
            logs_to_show = CHANGELOG[:10]
            for ver, date, desc in logs_to_show:
                st.markdown(f"""<div class="log-entry"><b>[{ver}]</b> <span style="opacity:0.7">{date}</span><br>{desc}</div>""", unsafe_allow_html=True)

    elif "電力設施" in page:
        st.header("⚡ 電力設施監控")
        gate = st.selectbox("監控節點", ["AND", "OR", "XOR", "NOT"])
        c1, c2 = st.columns([1, 1.5])
        with c1: render_svg(SVG_ICONS.get(gate, SVG_ICONS["AND"]))
        with c2:
            st.write(f"**{gate} 真值表**")
            d = {"In A":[0,0,1,1], "In B":[0,1,0,1]}
            if gate=="AND": d["Out"]=[0,0,0,1]
            elif gate=="OR": d["Out"]=[0,1,1,1]
            elif gate=="XOR": d["Out"]=[0,1,1,0]
            elif gate=="NOT": d={"In":[0,1], "Out":[1,0]}
            st.dataframe(pd.DataFrame(d), use_container_width=True, hide_index=True)

    elif "數據中心" in page:
        st.header("🏦 數據中心")
        val = st.text_input("十進制輸入", "255")
        if val.isdigit():
            v = int(val)
            c1, c2, c3 = st.columns(3)
            c1.metric("Binary", bin(v)[2:])
            c2.metric("Octal", oct(v)[2:])
            c3.metric("Hex", hex(v)[2:].upper())
        else: st.error("無效數據")

    elif "節點優化" in page:
        if "🔒" in page: st.error("權限不足"); st.stop()
        st.header("🧮 邏輯節點優化")
        c1, c2 = st.columns(2)
        m0 = c1.checkbox("00", False); m1 = c2.checkbox("01", False)
        m2 = c1.checkbox("10", False); m3 = c2.checkbox("11", False)
        if m0 and m1 and m2 and m3: st.success("Result: 1")
        elif m0 and m1: st.success("Result: A'")
        elif m2 and m3: st.success("Result: A")
        else: st.warning("請選擇相鄰區域")

    elif "交通調度" in page:
        if "🔒" in page: st.error("權限不足"); st.stop()
        st.header("🔀 數據流交通調度")
        col_img, col_ctrl = st.columns([1, 2])
        with col_img: render_svg(SVG_ICONS["MUX"])
        with col_ctrl:
            s = st.selectbox("S1, S0", ["00", "01", "10", "11"])
            st.metric("導通線路", f"Data {int(s, 2)}")

    elif "時序控制" in page:
        if "🔒" in page: st.error("權限不足"); st.stop()
        st.header("🔄 時序邏輯控制")
        col_img, col_ctrl = st.columns([1, 2])
        with col_img: render_svg(SVG_ICONS["FF"])
        with col_ctrl:
            j = st.selectbox("J", [0,1]); k = st.selectbox("K", [0,1])
            if j==0 and k==0: st.info("保持 (Hold)")
            elif j==1 and k==1: st.warning("反轉 (Toggle)")
            elif j==1: st.success("設定 (Set)")
            else: st.error("重置 (Reset)")

    elif "市政學院" in page:
        st.header("🎓 市政管理能力考評")
        
        # --- 修改點 2: 考試防誤觸機制 ---
        if not st.session_state.exam_active:
            st.info("準備好開始新的考核了嗎？這將影響您的權限評估。")
            st.markdown("""
            **考核規則：**
            1. 題目隨機從資料庫抽取。
            2. 提交後無法修改。
            3. 成績將永久記錄於人事檔案。
            """)
            if st.button("🚀 啟動考核程序", type="primary"):
                qs = load_qs()
                if not qs:
                    st.error("錯誤：題庫連線失敗 (questions.txt 不存在)")
                else:
                    p = [x for x in qs if x['id'] not in st.session_state.used_ids]
                    if not p:
                        st.success("所有現有題庫已考核完畢。")
                        if st.button("重置題庫狀態"):
                            st.session_state.used_ids = []
                            st.rerun()
                    else:
                        st.session_state.current_q = random.choice(p)
                        st.session_state.exam_active = True
                        st.rerun()
        else:
            # 考試進行中
            q = st.session_state.current_q
            st.markdown(f"### 📝 考題 ID-{q['id']}")
            st.write(f"**{q['q']}**")
            
            with st.form("exam_form"):
                ans = st.radio("請選擇處置方案：", q['o'])
                submitted = st.form_submit_button("🔒 確認並提交")
                
                if submitted:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    is_correct = (ans == q['a'])
                    
                    st.session_state.history.append({
                        "時間": timestamp,
                        "題目ID": q['id'],
                        "結果": "✅ 通過" if is_correct else "❌ 失敗"
                    })
                    
                    if is_correct:
                        st.balloons()
                        st.session_state.used_ids.append(q['id'])
                        if st.session_state.level == "區域管理員": st.session_state.level = "城市規劃師"
                        st.success("判定正確！權限積分已累積。")
                    else:
                        st.error(f"判定錯誤。正確方案應為：{q['a']}")
                    
                    # 考完後重置狀態，回到確認頁面
                    st.session_state.exam_active = False
                    st.session_state.current_q = None
                    # 給予一點時間看結果再顯示按鈕 (Streamlit 刷新特性)
                    if st.button("返回考核大廳"):
                        st.rerun()

    elif "人事檔案" in page:
        st.header("📂 管理員人事檔案")
        c1, c2 = st.columns([1, 2])
        with c1:
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
# 6. 入口
# ==================================================
if not st.session_state.name:
    apply_theme()
    st.title("🏙️ CityOS V137")
    n = st.text_input("Admin ID", placeholder="e.g., Frank")
    if st.button("連線"):
        if n: st.session_state.name = n; st.rerun()
else:
    main()
