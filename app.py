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
    ("V1.3.6", "2026-01-02", "系統全面城市化：介面與用語調整為城市管理風格"),
    ("V1.3.6", "2026-01-02", "新增歷史成績追蹤功能"),
    ("V1.3.6", "2026-01-02", "新增市政操作手冊與安全須知"),
    ("V1.3.5", "2026-01-02", "視覺優化：移除圖片下方干擾文字 (Clean Visual)"),
    ("V1.3.4", "2026-01-02", "修復：SVG 線條強制黑色，解決深色模式隱形問題"),
    ("V1.3.3", "2026-01-01", "降低色彩飽和度，引入莫蘭迪色系"),
    ("V1.3.2", "2025-12-30", "優化 SVG 渲染引擎，加入白底卡片"),
    ("V1.3.1", "2025-12-28", "新增 MUX 與 Flip-Flop 進階邏輯元件"),
    ("V1.2.0", "2025-12-25", "考評系統上線，支援題庫讀取"),
    ("V1.1.0", "2025-12-20", "基礎邏輯閘視覺化完成"),
]

# ==================================================
# 1. 內嵌 SVG 圖庫 (維持 V135 強制黑線邏輯)
# ==================================================
SVG_ICONS = {
    "AND": '''<svg width="100" height="60" viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg"><path d="M10,10 L40,10 C55,10 65,20 65,30 C65,40 55,50 40,50 L10,50 Z" fill="none" stroke="currentColor" stroke-width="3"/><path d="M0,20 L10,20 M0,40 L10,40 M65,30 L80,30" stroke="currentColor" stroke-width="3"/></svg>''',
    "OR": '''<svg width="100" height="60" viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg"><path d="M10,10 C10,10 25,10 40,10 C60,10 70,30 70,30 C70,30 60,50 40,50 C25,50 10,50 10,50 C15,40 15,20 10,10" fill="none" stroke="currentColor" stroke-width="3"/><path d="M0,20 L13,20 M0,40 L13,40 M70,30 L80,30" stroke="currentColor" stroke-width="3"/></svg>''',
    "NOT": '''<svg width="100" height="60" viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg"><path d="M20,10 L50,30 L20,50 Z" fill="none" stroke="currentColor" stroke-width="3"/><circle cx="54" cy="30" r="4" fill="none" stroke="currentColor" stroke-width="3"/><path d="M10,30 L20,30 M58,30 L70,30" stroke="currentColor" stroke-width="3"/></svg>''',
    "XOR": '''<svg width="100" height="60" viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg"><path d="M15,10 C15,10 30,10 45,10 C65,10 75,30 75,30 C75,30 65,50 45,50 C30,50 15,50 15,50 C20,40 20,20 15,10" fill="none" stroke="currentColor" stroke-width="3"/><path d="M5,10 C10,20 10,40 5,50" fill="none" stroke="currentColor" stroke-width="3"/><path d="M0,20 L13,20 M0,40 L13,40 M75,30 L85,30" stroke="currentColor" stroke-width="3"/></svg>''',
    "MUX": '''<svg width="120" height="100" viewBox="0 0 120 100" xmlns="http://www.w3.org/2000/svg"><path d="M30,10 L90,25 L90,75 L30,90 Z" fill="none" stroke="currentColor" stroke-width="3"/><text x="45" y="55" fill="currentColor" font-size="14">MUX</text><path d="M10,25 L30,25 M10,40 L30,40 M10,55 L30,55 M10,70 L30,70 M90,50 L110,50 M60,85 L60,95" stroke="currentColor" stroke-width="2"/></svg>''',
    "FF": '''<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><rect x="20" y="20" width="60" height="60" fill="none" stroke="currentColor" stroke-width="3"/><text x="35" y="55" fill="currentColor" font-size="14">Flip-Flop</text><path d="M10,30 L20,30 M10,70 L20,70 M80,30 L90,30 M80,70 L90,70" stroke="currentColor" stroke-width="2"/></svg>'''
}

# ==================================================
# 2. 系統設定
# ==================================================
st.set_page_config(page_title="CityOS V136", layout="wide")

THEMES = {
    "專業暗色 (Night City)": {"bg": "#212529", "txt": "#E9ECEF", "btn": "#495057", "btn_txt": "#FFFFFF", "card": "#343A40"},
    "舒適亮色 (Day City)": {"bg": "#F8F9FA", "txt": "#343A40", "btn": "#6C757D", "btn_txt": "#FFFFFF", "card": "#FFFFFF"},
    "海軍藍 (Port City)": {"bg": "#1A2530", "txt": "#DDE1E5", "btn": "#3E5C76", "btn_txt": "#FFFFFF", "card": "#2C3E50"}
}

# 初始化 Session State
if "state" not in st.session_state:
    st.session_state.update({
        "state": True, 
        "name": "", 
        "title": "市政執行官", 
        "level": "區域管理員", 
        "used_ids": [], 
        "history": [], # 新增歷史成績
        "theme_name": "專業暗色 (Night City)"
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
    /* 特殊樣式：日誌區塊 */
    .log-entry {{ border-left: 3px solid {t['btn']}; padding-left: 10px; margin-bottom: 8px; font-size: 0.9em; }}
    </style>
    """, unsafe_allow_html=True)

def render_svg(svg_code):
    svg_black = svg_code.replace('stroke="currentColor"', 'stroke="#000000"').replace('fill="currentColor"', 'fill="#000000"')
    b64 = base64.b64encode(svg_black.encode('utf-8')).decode("utf-8")
    html = f'''
    <div style="background-color: #FFFFFF; border-radius: 8px; padding: 20px; margin-bottom: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <img src="data:image/svg+xml;base64,{b64}" width="200"/>
    </div>'''
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
        st.title("🏙️ CityOS V136")
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
        
        # 1. 系統介紹
        st.info("👋 歡迎回來，指揮官。CityOS 是本市的核心邏輯控制系統，負責維護數位基礎設施的運作。")
        
        col_intro, col_log = st.columns([1.5, 1])
        
        with col_intro:
            st.subheader("📖 市政操作手冊")
            with st.expander("📌 系統模組說明 (點擊展開)", expanded=True):
                st.markdown("""
                * **⚡ 電力設施 (Logic Gates)**：檢視與維護基礎邏輯閘（AND, OR, NOT），確保訊號傳輸正確。
                * **🏦 數據中心 (Math)**：執行二進制、十六進制等底層數據轉換運算。
                * **🎓 市政學院 (Quiz)**：進行模擬考核，提升您的管理權限等級。
                * **🧮 節點優化 (K-Map)**：(進階) 使用卡諾圖化簡複雜的邏輯電路。
                * **🔀 交通調度 (MUX)**：(進階) 控制多工器進行數據分流。
                """)
            
            st.subheader("⚠️ 安全須知")
            st.warning("""
            1. **權限分級**：請勿嘗試存取超越您當前職級的模組，否則將觸發警報。
            2. **數據完整性**：在進行「考評」時，請確保連線穩定，成績將即時寫入人事檔案。
            3. **視覺保護**：系統預設啟用「視覺保護模式」，請依環境光線調整主題。
            """)

            # 視覺展示
            st.subheader("📡 系統狀態監控")
            c1, c2, c3 = st.columns(3)
            with c1: render_svg(SVG_ICONS["AND"])
            with c2: render_svg(SVG_ICONS["OR"])
            with c3: render_svg(SVG_ICONS["NOT"])

        with col_log:
            st.subheader("🛠️ 系統更新日誌")
            st.markdown("顯示最近 10 筆核心更新：")
            logs_to_show = CHANGELOG[:10]
            for ver, date, desc in logs_to_show:
                st.markdown(f"""
                <div class="log-entry">
                    <b>[{ver}]</b> <span style="opacity:0.7">{date}</span><br>
                    {desc}
                </div>
                """, unsafe_allow_html=True)

    elif "電力設施" in page:
        st.header("⚡ 電力設施監控 (Basic Logic)")
        gate = st.selectbox("選擇監控節點", ["AND", "OR", "XOR", "NOT"], index=0)
        c1, c2 = st.columns([1, 1.5])
        with c1:
            render_svg(SVG_ICONS.get(gate, SVG_ICONS["AND"]))
        with c2:
            st.write(f"**{gate} 訊號真值表**")
            d = {"Input A":[0,0,1,1], "Input B":[0,1,0,1]}
            if gate=="AND": d["Output"]=[0,0,0,1]
            elif gate=="OR": d["Output"]=[0,1,1,1]
            elif gate=="XOR": d["Output"]=[0,1,1,0]
            elif gate=="NOT": d={"Input":[0,1], "Output":[1,0]}
            st.dataframe(pd.DataFrame(d), use_container_width=True, hide_index=True)

    elif "數據中心" in page:
        st.header("🏦 數據中心 (Data Center)")
        val = st.text_input("輸入十進制資源數值", "255")
        if val.isdigit():
            v = int(val)
            c1, c2, c3 = st.columns(3)
            c1.metric("Binary (二進制)", bin(v)[2:])
            c2.metric("Octal (八進制)", oct(v)[2:])
            c3.metric("Hex (十六進制)", hex(v)[2:].upper())
        else: st.error("錯誤：請輸入有效整數數據")

    elif "節點優化" in page:
        if "🔒" in page: st.error("權限不足：需要 [城市規劃師] 權限"); st.stop()
        st.header("🧮 邏輯節點優化 (K-Map)")
        c1, c2 = st.columns(2)
        m0 = c1.checkbox("區域 00", False); m1 = c2.checkbox("區域 01", False)
        m2 = c1.checkbox("區域 10", False); m3 = c2.checkbox("區域 11", False)
        if m0 and m1 and m2 and m3: st.success("優化結果: 恆定輸出 1")
        elif m0 and m1: st.success("優化結果: A' (反相 A)")
        elif m2 and m3: st.success("優化結果: A (正相 A)")
        else: st.warning("系統提示：請選擇相鄰區域以進行化簡")

    elif "交通調度" in page:
        if "🔒" in page: st.error("權限不足：需要 [系統工程師] 權限"); st.stop()
        st.header("🔀 數據流交通調度 (MUX)")
        col_img, col_ctrl = st.columns([1, 2])
        with col_img: render_svg(SVG_ICONS["MUX"])
        with col_ctrl:
            s = st.selectbox("通道選擇訊號 (S1, S0)", ["00", "01", "10", "11"])
            st.metric("當前導通線路", f"Data Line {int(s, 2)}")

    elif "時序控制" in page:
        if "🔒" in page: st.error("權限不足：需要 [最高指揮官] 權限"); st.stop()
        st.header("🔄 時序邏輯控制 (Flip-Flop)")
        col_img, col_ctrl = st.columns([1, 2])
        with col_img: render_svg(SVG_ICONS["FF"])
        with col_ctrl:
            j = st.selectbox("J 輸入", [0,1]); k = st.selectbox("K 輸入", [0,1])
            if j==0 and k==0: st.info("狀態: 保持 (Hold) - 系統穩定")
            elif j==1 and k==1: st.warning("狀態: 反轉 (Toggle) - 訊號震盪")
            elif j==1: st.success("狀態: 設定 (Set 1) - 啟動")
            else: st.error("狀態: 重置 (Reset 0) - 關閉")

    elif "市政學院" in page:
        st.header("🎓 市政管理能力考評 (Academy)")
        qs = load_qs()
        if not qs: st.warning("系統警告：題庫資料庫 (questions.txt) 遺失")
        else:
            p = [x for x in qs if x['id'] not in st.session_state.used_ids]
            if not p: 
                st.success("恭喜：所有考評項目已完成")
                st.button("重置考評紀錄", on_click=lambda: st.session_state.update({"used_ids":[]}))
            else:
                q = random.choice(p)
                st.markdown(f"**考題:** {q['q']}")
                ans = st.radio("請選擇最佳處置方案:", q['o'], key=q['id'])
                
                if st.button("提交方案"):
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    is_correct = (ans == q['a'])
                    
                    # 紀錄歷史
                    record = {
                        "時間": timestamp,
                        "題目ID": q['id'],
                        "您的答案": ans,
                        "結果": "✅ 通過" if is_correct else "❌ 失敗"
                    }
                    st.session_state.history.append(record)

                    if is_correct:
                        st.balloons()
                        st.session_state.used_ids.append(q['id'])
                        if st.session_state.level == "區域管理員": st.session_state.level = "城市規劃師"
                        st.success("判定：方案正確。權限積分已累積。")
                        st.rerun()
                    else: 
                        st.error("判定：方案錯誤。請重新審視邏輯。")

    elif "人事檔案" in page:
        st.header("📂 管理員人事檔案 (Profile)")
        
        c1, c2 = st.columns([1, 2])
        with c1:
            st.subheader("基本資料")
            st.text_input("使用者代碼", st.session_state.name, disabled=True)
            new_title = st.text_input("職稱 (Title)", st.session_state.title)
            if new_title != st.session_state.title:
                st.session_state.title = new_title
                st.rerun()
            
            st.subheader("介面風格")
            sel = st.selectbox("City Theme", list(THEMES.keys()), index=list(THEMES.keys()).index(st.session_state.theme_name))
            if sel != st.session_state.theme_name: st.session_state.theme_name = sel; st.rerun()

            st.divider()
            if st.button("登出指揮系統", type="primary"):
                for k in list(st.session_state.keys()): del st.session_state[k]
                st.rerun()

        with c2:
            st.subheader("📜 歷史考評績效")
            if not st.session_state.history:
                st.info("尚無考評紀錄")
            else:
                # 轉為 DataFrame 顯示，並倒序排列
                df = pd.DataFrame(st.session_state.history)
                df = df[::-1] # 最新在最上面
                st.dataframe(
                    df, 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "時間": st.column_config.TextColumn("時間", width="medium"),
                        "結果": st.column_config.TextColumn("考核結果", width="small"),
                    }
                )

# ==================================================
# 6. 入口
# ==================================================
if not st.session_state.name:
    apply_theme()
    st.title("🏙️ CityOS V136")
    st.markdown("### 城市核心控制終端")
    st.markdown("請輸入您的 **管理員 ID** 以存取系統。")
    n = st.text_input("Admin ID", placeholder="e.g., Frank")
    if st.button("連線"):
        if n: st.session_state.name = n; st.rerun()
else:
    main()
