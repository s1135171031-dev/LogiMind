import streamlit as st
import pandas as pd
import random
import os
import base64

# ==================================================
# 1. 內嵌 SVG 圖庫
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
st.set_page_config(page_title="LogiMind V135", layout="wide")

THEMES = {
    "專業暗色 (Pro Dark)": {"bg": "#212529", "txt": "#E9ECEF", "btn": "#495057", "btn_txt": "#FFFFFF", "card": "#343A40"},
    "舒適亮色 (Soft Light)": {"bg": "#F8F9FA", "txt": "#343A40", "btn": "#6C757D", "btn_txt": "#FFFFFF", "card": "#FFFFFF"},
    "海軍藍 (Navy Blue)": {"bg": "#1A2530", "txt": "#DDE1E5", "btn": "#3E5C76", "btn_txt": "#FFFFFF", "card": "#2C3E50"}
}

if "state" not in st.session_state:
    st.session_state.update({"state": True, "name": "", "title": "使用者", "level": "初級管理員", "used_ids": [], "theme_name": "專業暗色 (Pro Dark)"})

# ==================================================
# 3. 視覺渲染引擎 (V135: 移除圖片下方文字)
# ==================================================
def apply_theme():
    t = THEMES[st.session_state.theme_name]
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {t['bg']} !important; }}
    h1, h2, h3, h4, p, span, div, label, li, .stMarkdown {{ color: {t['txt']} !important; font-family: 'Segoe UI', sans-serif; }}
    .stButton>button {{ background-color: {t['btn']} !important; color: {t['btn_txt']} !important; border: none !important; border-radius: 6px !important; padding: 0.5rem 1rem; }}
    div[data-testid="stDataFrame"] {{ background-color: {t['card']} !important; border: 1px solid rgba(128,128,128,0.2); padding: 5px; border-radius: 8px; }}
    [data-testid="stSidebar"] {{ background-color: {t['card']}; border-right: 1px solid rgba(128,128,128,0.1); }}
    </style>
    """, unsafe_allow_html=True)

def render_svg(svg_code):
    """
    V135 修復：移除了 caption 參數與對應的 HTML <p> 標籤。
    圖片下方不再顯示任何文字。
    """
    svg_black = svg_code.replace('stroke="currentColor"', 'stroke="#000000"').replace('fill="currentColor"', 'fill="#000000"')
    b64 = base64.b64encode(svg_black.encode('utf-8')).decode("utf-8")
    
    html = f'''
    <div style="
        background-color: #FFFFFF;
        border-radius: 8px; 
        padding: 20px; 
        margin-bottom: 10px; 
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <img src="data:image/svg+xml;base64,{b64}" width="200"/>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)

# ==================================================
# 4. 輔助功能
# ==================================================
def has_access(rank):
    if st.session_state.name.lower() == "frank": return True
    order = ["初級管理員", "中級管理員", "高級工程師", "終端管理員"]
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
        st.title("🏙️ LogiMind V135")
        st.caption("Clean Visual Edition")
        st.markdown(f"""<div style="padding:10px; background:rgba(255,255,255,0.05); border-radius:8px; margin-bottom:15px;"><div>👤 <b>{st.session_state.title}</b></div><div style="font-size:0.9em; opacity:0.8;">ID: {st.session_state.name}</div></div>""", unsafe_allow_html=True)
        if is_frank: st.success("權限：ROOT")
        else: st.info(f"權限：{st.session_state.level}")
        st.divider()
        menu = ["🏠 系統概覽", "🔬 基礎邏輯", "🔢 數碼運算", "🎓 智慧考評"]
        if is_frank or has_access("中級管理員"): menu.append("🧮 化簡邏輯")
        else: menu.append("🔒 化簡 (鎖定)")
        if is_frank or has_access("高級工程師"): menu.append("🔀 組合邏輯")
        else: menu.append("🔒 組合 (鎖定)")
        if is_frank or has_access("終端管理員"): menu.append("🔄 序向邏輯")
        else: menu.append("🔒 序向 (鎖定)")
        menu.append("🎨 個人化")
        page = st.radio("導航", menu)

    # --- 頁面內容 ---
    if "系統概覽" in page:
        st.header("🏠 系統概覽")
        st.write("V135 更新：移除圖片下方所有說明文字，保持介面極簡。")
        c1, c2, c3 = st.columns(3)
        with c1: render_svg(SVG_ICONS["AND"])
        with c2: render_svg(SVG_ICONS["OR"])
        with c3: render_svg(SVG_ICONS["NOT"])

    elif "基礎邏輯" in page:
        st.header("🔬 基礎邏輯閘")
        gate = st.selectbox("選擇元件", ["AND", "OR", "XOR", "NOT"], index=0)
        c1, c2 = st.columns([1, 1.5])
        with c1:
            render_svg(SVG_ICONS.get(gate, SVG_ICONS["AND"]))
        with c2:
            st.write(f"**{gate} 真值表**")
            d = {"A":[0,0,1,1], "B":[0,1,0,1]}
            if gate=="AND": d["Y"]=[0,0,0,1]
            elif gate=="OR": d["Y"]=[0,1,1,1]
            elif gate=="XOR": d["Y"]=[0,1,1,0]
            elif gate=="NOT": d={"In":[0,1], "Out":[1,0]}
            st.dataframe(pd.DataFrame(d), use_container_width=True, hide_index=True)

    elif "數碼運算" in page:
        st.header("🔢 進制轉換")
        val = st.text_input("輸入十進制數值", "255")
        if val.isdigit():
            v = int(val)
            st.info(f"Binary: {bin(v)[2:]} | Octal: {oct(v)[2:]} | Hex: {hex(v)[2:].upper()}")
        else: st.error("請輸入有效整數")

    elif "化簡" in page:
        if "🔒" in page: st.error("權限不足"); st.stop()
        st.header("🧮 卡諾圖化簡")
        c1, c2 = st.columns(2)
        m0 = c1.checkbox("00", False); m1 = c2.checkbox("01", False)
        m2 = c1.checkbox("10", False); m3 = c2.checkbox("11", False)
        if m0 and m1 and m2 and m3: st.success("Output: 1")
        elif m0 and m1: st.success("Output: A'")
        elif m2 and m3: st.success("Output: A")
        else: st.warning("請選擇相鄰項目")

    elif "組合" in page:
        if "🔒" in page: st.error("權限不足"); st.stop()
        st.header("🔀 MUX 多工器")
        col_img, col_ctrl = st.columns([1, 2])
        with col_img: render_svg(SVG_ICONS["MUX"])
        with col_ctrl:
            s = st.selectbox("Select (S1, S0)", ["00", "01", "10", "11"])
            st.metric("Output Line", f"D{int(s, 2)}")

    elif "序向" in page:
        if "🔒" in page: st.error("權限不足"); st.stop()
        st.header("🔄 JK Flip-Flop")
        col_img, col_ctrl = st.columns([1, 2])
        with col_img: render_svg(SVG_ICONS["FF"])
        with col_ctrl:
            j = st.selectbox("J", [0,1]); k = st.selectbox("K", [0,1])
            if j==0 and k==0: st.write("狀態: 保持 (Hold)")
            elif j==1 and k==1: st.write("狀態: 反轉 (Toggle)")
            elif j==1: st.write("狀態: 設定 (Set 1)")
            else: st.write("狀態: 重置 (Reset 0)")

    elif "智慧考評" in page:
        st.header("🎓 測驗區")
        qs = load_qs()
        if not qs: st.warning("請建立 questions.txt")
        else:
            p = [x for x in qs if x['id'] not in st.session_state.used_ids]
            if not p: st.success("題庫已完成"); st.button("重置", on_click=lambda: st.session_state.update({"used_ids":[]}))
            else:
                q = random.choice(p)
                st.markdown(f"**Question:** {q['q']}")
                ans = st.radio("Select Answer:", q['o'], key=q['id'])
                if st.button("提交答案"):
                    if ans == q['a']:
                        st.balloons(); st.session_state.used_ids.append(q['id'])
                        if st.session_state.level == "初級管理員": st.session_state.level = "中級管理員"
                        st.rerun()
                    else: st.error("回答錯誤")

    elif "個人化" in page:
        st.header("🎨 外觀設定")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("主題選擇")
            sel = st.selectbox("介面風格", list(THEMES.keys()), index=list(THEMES.keys()).index(st.session_state.theme_name))
            if sel != st.session_state.theme_name: st.session_state.theme_name = sel; st.rerun()
            st.subheader("個人資訊")
            st.session_state.title = st.text_input("使用者稱號", st.session_state.title)
        with c2:
            st.subheader("系統操作")
            if st.button("登出系統"):
                for k in list(st.session_state.keys()): del st.session_state[k]
                st.rerun()

# ==================================================
# 6. 入口
# ==================================================
if not st.session_state.name:
    apply_theme()
    st.title("🏙️ LogiMind V135")
    st.markdown("請輸入您的使用者代碼以登入系統。")
    n = st.text_input("User ID", placeholder="e.g., Frank")
    if st.button("登入"):
        if n: st.session_state.name = n; st.rerun()
else:
    main()import streamlit as st
import pandas as pd
import random
import os
import base64

# ==================================================
# 1. 內嵌 SVG 圖庫
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
st.set_page_config(page_title="LogiMind V135", layout="wide")

THEMES = {
    "專業暗色 (Pro Dark)": {"bg": "#212529", "txt": "#E9ECEF", "btn": "#495057", "btn_txt": "#FFFFFF", "card": "#343A40"},
    "舒適亮色 (Soft Light)": {"bg": "#F8F9FA", "txt": "#343A40", "btn": "#6C757D", "btn_txt": "#FFFFFF", "card": "#FFFFFF"},
    "海軍藍 (Navy Blue)": {"bg": "#1A2530", "txt": "#DDE1E5", "btn": "#3E5C76", "btn_txt": "#FFFFFF", "card": "#2C3E50"}
}

if "state" not in st.session_state:
    st.session_state.update({"state": True, "name": "", "title": "使用者", "level": "初級管理員", "used_ids": [], "theme_name": "專業暗色 (Pro Dark)"})

# ==================================================
# 3. 視覺渲染引擎 (V135: 移除圖片下方文字)
# ==================================================
def apply_theme():
    t = THEMES[st.session_state.theme_name]
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {t['bg']} !important; }}
    h1, h2, h3, h4, p, span, div, label, li, .stMarkdown {{ color: {t['txt']} !important; font-family: 'Segoe UI', sans-serif; }}
    .stButton>button {{ background-color: {t['btn']} !important; color: {t['btn_txt']} !important; border: none !important; border-radius: 6px !important; padding: 0.5rem 1rem; }}
    div[data-testid="stDataFrame"] {{ background-color: {t['card']} !important; border: 1px solid rgba(128,128,128,0.2); padding: 5px; border-radius: 8px; }}
    [data-testid="stSidebar"] {{ background-color: {t['card']}; border-right: 1px solid rgba(128,128,128,0.1); }}
    </style>
    """, unsafe_allow_html=True)

def render_svg(svg_code):
    """
    V135 修復：移除了 caption 參數與對應的 HTML <p> 標籤。
    圖片下方不再顯示任何文字。
    """
    svg_black = svg_code.replace('stroke="currentColor"', 'stroke="#000000"').replace('fill="currentColor"', 'fill="#000000"')
    b64 = base64.b64encode(svg_black.encode('utf-8')).decode("utf-8")
    
    html = f'''
    <div style="
        background-color: #FFFFFF;
        border-radius: 8px; 
        padding: 20px; 
        margin-bottom: 10px; 
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <img src="data:image/svg+xml;base64,{b64}" width="200"/>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)

# ==================================================
# 4. 輔助功能
# ==================================================
def has_access(rank):
    if st.session_state.name.lower() == "frank": return True
    order = ["初級管理員", "中級管理員", "高級工程師", "終端管理員"]
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
        st.title("🏙️ LogiMind V135")
        st.caption("Clean Visual Edition")
        st.markdown(f"""<div style="padding:10px; background:rgba(255,255,255,0.05); border-radius:8px; margin-bottom:15px;"><div>👤 <b>{st.session_state.title}</b></div><div style="font-size:0.9em; opacity:0.8;">ID: {st.session_state.name}</div></div>""", unsafe_allow_html=True)
        if is_frank: st.success("權限：ROOT")
        else: st.info(f"權限：{st.session_state.level}")
        st.divider()
        menu = ["🏠 系統概覽", "🔬 基礎邏輯", "🔢 數碼運算", "🎓 智慧考評"]
        if is_frank or has_access("中級管理員"): menu.append("🧮 化簡邏輯")
        else: menu.append("🔒 化簡 (鎖定)")
        if is_frank or has_access("高級工程師"): menu.append("🔀 組合邏輯")
        else: menu.append("🔒 組合 (鎖定)")
        if is_frank or has_access("終端管理員"): menu.append("🔄 序向邏輯")
        else: menu.append("🔒 序向 (鎖定)")
        menu.append("🎨 個人化")
        page = st.radio("導航", menu)

    # --- 頁面內容 ---
    if "系統概覽" in page:
        st.header("🏠 系統概覽")
        st.write("V135 更新：移除圖片下方所有說明文字，保持介面極簡。")
        c1, c2, c3 = st.columns(3)
        with c1: render_svg(SVG_ICONS["AND"])
        with c2: render_svg(SVG_ICONS["OR"])
        with c3: render_svg(SVG_ICONS["NOT"])

    elif "基礎邏輯" in page:
        st.header("🔬 基礎邏輯閘")
        gate = st.selectbox("選擇元件", ["AND", "OR", "XOR", "NOT"], index=0)
        c1, c2 = st.columns([1, 1.5])
        with c1:
            render_svg(SVG_ICONS.get(gate, SVG_ICONS["AND"]))
        with c2:
            st.write(f"**{gate} 真值表**")
            d = {"A":[0,0,1,1], "B":[0,1,0,1]}
            if gate=="AND": d["Y"]=[0,0,0,1]
            elif gate=="OR": d["Y"]=[0,1,1,1]
            elif gate=="XOR": d["Y"]=[0,1,1,0]
            elif gate=="NOT": d={"In":[0,1], "Out":[1,0]}
            st.dataframe(pd.DataFrame(d), use_container_width=True, hide_index=True)

    elif "數碼運算" in page:
        st.header("🔢 進制轉換")
        val = st.text_input("輸入十進制數值", "255")
        if val.isdigit():
            v = int(val)
            st.info(f"Binary: {bin(v)[2:]} | Octal: {oct(v)[2:]} | Hex: {hex(v)[2:].upper()}")
        else: st.error("請輸入有效整數")

    elif "化簡" in page:
        if "🔒" in page: st.error("權限不足"); st.stop()
        st.header("🧮 卡諾圖化簡")
        c1, c2 = st.columns(2)
        m0 = c1.checkbox("00", False); m1 = c2.checkbox("01", False)
        m2 = c1.checkbox("10", False); m3 = c2.checkbox("11", False)
        if m0 and m1 and m2 and m3: st.success("Output: 1")
        elif m0 and m1: st.success("Output: A'")
        elif m2 and m3: st.success("Output: A")
        else: st.warning("請選擇相鄰項目")

    elif "組合" in page:
        if "🔒" in page: st.error("權限不足"); st.stop()
        st.header("🔀 MUX 多工器")
        col_img, col_ctrl = st.columns([1, 2])
        with col_img: render_svg(SVG_ICONS["MUX"])
        with col_ctrl:
            s = st.selectbox("Select (S1, S0)", ["00", "01", "10", "11"])
            st.metric("Output Line", f"D{int(s, 2)}")

    elif "序向" in page:
        if "🔒" in page: st.error("權限不足"); st.stop()
        st.header("🔄 JK Flip-Flop")
        col_img, col_ctrl = st.columns([1, 2])
        with col_img: render_svg(SVG_ICONS["FF"])
        with col_ctrl:
            j = st.selectbox("J", [0,1]); k = st.selectbox("K", [0,1])
            if j==0 and k==0: st.write("狀態: 保持 (Hold)")
            elif j==1 and k==1: st.write("狀態: 反轉 (Toggle)")
            elif j==1: st.write("狀態: 設定 (Set 1)")
            else: st.write("狀態: 重置 (Reset 0)")

    elif "智慧考評" in page:
        st.header("🎓 測驗區")
        qs = load_qs()
        if not qs: st.warning("請建立 questions.txt")
        else:
            p = [x for x in qs if x['id'] not in st.session_state.used_ids]
            if not p: st.success("題庫已完成"); st.button("重置", on_click=lambda: st.session_state.update({"used_ids":[]}))
            else:
                q = random.choice(p)
                st.markdown(f"**Question:** {q['q']}")
                ans = st.radio("Select Answer:", q['o'], key=q['id'])
                if st.button("提交答案"):
                    if ans == q['a']:
                        st.balloons(); st.session_state.used_ids.append(q['id'])
                        if st.session_state.level == "初級管理員": st.session_state.level = "中級管理員"
                        st.rerun()
                    else: st.error("回答錯誤")

    elif "個人化" in page:
        st.header("🎨 外觀設定")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("主題選擇")
            sel = st.selectbox("介面風格", list(THEMES.keys()), index=list(THEMES.keys()).index(st.session_state.theme_name))
            if sel != st.session_state.theme_name: st.session_state.theme_name = sel; st.rerun()
            st.subheader("個人資訊")
            st.session_state.title = st.text_input("使用者稱號", st.session_state.title)
        with c2:
            st.subheader("系統操作")
            if st.button("登出系統"):
                for k in list(st.session_state.keys()): del st.session_state[k]
                st.rerun()

# ==================================================
# 6. 入口
# ==================================================
if not st.session_state.name:
    apply_theme()
    st.title("🏙️ LogiMind V135")
    st.markdown("請輸入您的使用者代碼以登入系統。")
    n = st.text_input("User ID", placeholder="e.g., Frank")
    if st.button("登入"):
        if n: st.session_state.name = n; st.rerun()
else:
    main()

