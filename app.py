import streamlit as st
import pandas as pd
import random
import os
import base64

# ==================================================
# 1. 內嵌 SVG 圖庫 (解決破圖問題的核心)
#    這些代碼會直接由瀏覽器繪製，不需外部網路
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
# 2. 系統初始化與主題定義
# ==================================================
st.set_page_config(page_title="LogiMind V132", layout="wide")

THEMES = {
    "駭客黑 (Matrix)": {"bg": "#000000", "txt": "#00FF41", "btn": "#003B00", "card": "#111111"},
    "深海藍 (Cyberpunk)": {"bg": "#0E1117", "txt": "#00FFFF", "btn": "#FF00FF", "card": "#1A1C24"},
    "實驗室 (Lab)": {"bg": "#FFFFFF", "txt": "#000000", "btn": "#2E86C1", "card": "#F0F2F6"}
}

if "state" not in st.session_state:
    st.session_state.update({
        "state": True,
        "name": "",
        "title": "終端操作員", # 新增稱號
        "level": "初級管理員",
        "used_ids": [],
        "theme_name": "深海藍 (Cyberpunk)" # 預設主題
    })

# ==================================================
# 3. 權限與核心邏輯
# ==================================================
def has_access(rank):
    if st.session_state.name.lower() == "frank": return True
    order = ["初級管理員", "中級管理員", "高級工程師", "終端管理員"]
    try:
        return order.index(st.session_state.level) >= order.index(rank)
    except: return False

def logout():
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()

def reset_data():
    st.session_state.level = "初級管理員"
    st.session_state.used_ids = []
    st.toast("系統數據已重置")

# ==================================================
# 4. 視覺引擎 (解決白底白字)
# ==================================================
def apply_theme():
    t = THEMES[st.session_state.theme_name]
    
    st.markdown(f"""
    <style>
    /* 全域變數強制覆蓋 */
    .stApp {{ background-color: {t['bg']} !important; }}
    
    /* 文字顏色強制繼承 */
    h1, h2, h3, p, span, div, label, li, .stMarkdown {{ 
        color: {t['txt']} !important; 
        font-family: 'Consolas', 'Courier New', monospace;
    }}
    
    /* 解決真值表白底白字：強制表格區域有獨立的黑白配色或跟隨主題 */
    div[data-testid="stDataFrame"] {{
        background-color: {t['card']} !important;
        border: 1px solid {t['btn']};
        padding: 5px;
        border-radius: 5px;
    }}
    div[data-testid="stDataFrame"] * {{
        color: {t['txt']} !important;
        background-color: {t['card']} !important;
    }}
    
    /* 按鈕樣式 */
    .stButton>button {{
        background-color: {t['btn']} !important;
        color: {t['bg']} !important; /* 按鈕文字反白 */
        font-weight: bold;
        border: 1px solid {t['txt']};
        border-radius: 0px; /* 駭客風格方角 */
    }}
    
    /* 輸入框優化 */
    .stTextInput>div>div>input {{
        color: {t['txt']} !important;
        background-color: {t['card']} !important;
        border-color: {t['btn']} !important;
    }}
    
    /* SVG 圖示顏色自動適應文字顏色 */
    svg path, svg circle, svg rect, svg text {{
        stroke: {t['txt']} !important;
        fill: {t['txt']} !important;
    }}
    svg {{ fill: none !important; }} /* 修正填充 */
    </style>
    """, unsafe_allow_html=True)

# 顯示 SVG 的輔助函數
def render_svg(svg_code, caption=""):
    # 將 SVG 轉為 Base64 以便在 img 標籤顯示，或直接用 HTML
    b64 = base64.b64encode(svg_code.encode('utf-8')).decode("utf-8")
    html = f'<div style="text-align: center;"><img src="data:image/svg+xml;base64,{b64}" width="200"/><p>{caption}</p></div>'
    st.markdown(html, unsafe_allow_html=True)

# ==================================================
# 5. 題庫讀取
# ==================================================
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
# 6. 主程式
# ==================================================
def main():
    apply_theme()
    is_frank = st.session_state.name.lower() == "frank"
    
    with st.sidebar:
        st.title("🏙️ LogiMind V132")
        # 個人化顯示
        st.markdown(f"### 👤 {st.session_state.title}: {st.session_state.name}")
        
        if is_frank: st.success("權限：ROOT (Frank)")
        else: st.info(f"權限：{st.session_state.level}")
        st.divider()
        
        # 導航
        menu = ["🏠 系統概覽", "🔬 基礎邏輯", "🔢 數碼運算", "🎓 智慧考評"]
        
        if is_frank or has_access("中級管理員"): menu.append("🧮 化簡邏輯")
        else: menu.append("🔒 化簡 (鎖定)")
            
        if is_frank or has_access("高級工程師"): menu.append("🔀 組合邏輯")
        else: menu.append("🔒 組合 (鎖定)")
            
        if is_frank or has_access("終端管理員"): menu.append("🔄 序向邏輯")
        else: menu.append("🔒 序向 (鎖定)")
            
        menu.append("🎨 個人化中心")
        page = st.radio("導航", menu)

    # --- 頁面邏輯 ---
    if "系統概覽" in page:
        st.header("🏠 LogiMind V132")
        st.markdown("""
        **V132 更新日誌：**
        1. **SVG 向量引擎**：圖示不再破圖，由程式碼即時繪製。
        2. **高對比主題**：徹底解決文字看不清的問題。
        3. **深度個人化**：可自訂稱號與切換主題風格。
        """)
        render_svg(SVG_ICONS["AND"], "System Check: OK")

    elif "基礎邏輯" in page:
        st.header("🔬 基礎邏輯閘")
        gate = st.selectbox("選擇元件", ["AND", "OR", "XOR", "NOT"])
        
        c1, c2 = st.columns(2)
        with c1:
            render_svg(SVG_ICONS.get(gate, SVG_ICONS["AND"]), f"{gate} Gate Symbol")
        with c2:
            st.write(f"**{gate} Truth Table**")
            # 建立資料
            d = {"A":[0,0,1,1], "B":[0,1,0,1]}
            if gate=="AND": d["Y"]=[0,0,0,1]
            elif gate=="OR": d["Y"]=[0,1,1,1]
            elif gate=="XOR": d["Y"]=[0,1,1,0]
            elif gate=="NOT": d={"In":[0,1], "Out":[1,0]}
            st.dataframe(pd.DataFrame(d), use_container_width=True, hide_index=True)

    elif "數碼運算" in page:
        st.header("🔢 進制轉換")
        val = st.text_input("輸入十進制數字", "10")
        try:
            v = int(val)
            st.code(f"Binary: {bin(v)[2:]}\nOctal:  {oct(v)[2:]}\nHex:    {hex(v)[2:].upper()}")
        except: st.error("請輸入數字")

    elif "化簡" in page:
        if "🔒" in page: st.error("權限不足"); st.stop()
        st.header("🧮 布林化簡 (K-Map)")
        st.info("請勾選為 1 的方格：")
        c1, c2 = st.columns(2)
        m0 = c1.checkbox("00", False); m1 = c2.checkbox("01", False)
        m2 = c1.checkbox("10", False); m3 = c2.checkbox("11", False)
        if m0 and m1 and m2 and m3: st.success("F = 1")
        elif m0 and m1: st.success("F = A'")
        elif m2 and m3: st.success("F = A")
        else: st.warning("選取更多以化簡")

    elif "組合" in page:
        if "🔒" in page: st.error("權限不足"); st.stop()
        st.header("🔀 MUX 多工器")
        render_svg(SVG_ICONS["MUX"], "4-to-1 Multiplexer")
        s = st.selectbox("選擇線 S1S0", ["00", "01", "10", "11"])
        st.write(f"通道 **D{int(s,2)}** 被選中輸出。")

    elif "序向" in page:
        if "🔒" in page: st.error("權限不足"); st.stop()
        st.header("🔄 Flip-Flop 記憶單元")
        render_svg(SVG_ICONS["FF"], "JK Flip-Flop")
        j = st.selectbox("J", [0, 1]); k = st.selectbox("K", [0, 1])
        if j==0 and k==0: st.info("保持 (Hold)")
        elif j==1 and k==1: st.info("反轉 (Toggle)")
        elif j==1: st.info("設定 (Set 1)")
        else: st.info("重置 (Reset 0)")

    elif "智慧考評" in page:
        st.header("🎓 考評中心")
        qs = load_qs()
        if not qs: st.warning("請建立 questions.txt")
        else:
            p = [x for x in qs if x['id'] not in st.session_state.used_ids]
            if not p: st.success("題庫已完成"); st.button("重置紀錄", on_click=reset_data)
            else:
                q = random.choice(p)
                st.write(f"Q: {q['q']}")
                ans = st.radio("Ans", q['o'], key=q['id'])
                if st.button("提交"):
                    if ans == q['a']:
                        st.balloons(); st.session_state.level = "中級管理員"
                        st.session_state.used_ids.append(q['id'])
                        st.rerun()
                    else: st.error("錯誤")

    elif "個人化" in page:
        st.header("🎨 個人化控制台 (V132 新增)")
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("主題風格")
            # 這裡解決個人化太少的問題
            sel_theme = st.selectbox("選擇介面風格", list(THEMES.keys()), index=list(THEMES.keys()).index(st.session_state.theme_name))
            if sel_theme != st.session_state.theme_name:
                st.session_state.theme_name = sel_theme
                st.rerun()
                
            st.subheader("使用者資訊")
            new_title = st.text_input("自訂您的稱號", st.session_state.title)
            if st.button("更新稱號"):
                st.session_state.title = new_title
                st.rerun()

        with c2:
            st.subheader("危險區域")
            if st.button("🔄 重置所有學習進度"):
                reset_data()
                st.rerun()
            st.write("")
            if st.button("🚪 安全登出", key="logout_btn"):
                logout()

# ==================================================
# 7. 入口
# ==================================================
if not st.session_state.name:
    apply_theme() # 登入畫面也套用主題
    st.title("🏙️ LogiMind V132 登入")
    st.markdown("---")
    c1, c2 = st.columns([3, 1])
    n = c1.text_input("輸入代碼 (Frank)", placeholder="Name")
    if c2.button("連線"):
        if n: st.session_state.name = n; st.rerun()
else:
    main()
