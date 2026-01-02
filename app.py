import streamlit as st
import pandas as pd
import random
import os
import base64
import time
import numpy as np 
from datetime import datetime

# ==================================================
# 0. 系統核心與題庫 (維持不變)
# ==================================================
def init_question_bank():
    should_generate = False
    if not os.path.exists("questions.txt"): should_generate = True
    elif len(open("questions.txt", "r", encoding="utf-8").readlines()) < 50: should_generate = True

    if should_generate:
        with open("questions.txt", "w", encoding="utf-8") as f:
            gates = ["AND", "OR", "XOR", "NAND"]
            for _ in range(300):
                g = random.choice(gates)
                a, b = random.randint(0, 1), random.randint(0, 1)
                ans = a & b if g == "AND" else (a | b if g == "OR" else (a ^ b if g == "XOR" else 1 - (a & b)))
                f.write(f"LOGIC-{random.randint(1000,9999)}|1|輸入 A={a}, B={b}, {g} 閘輸出為何？|0,1,Z,X|{ans}\n")
            for _ in range(200):
                val = random.randint(1, 15)
                f.write(f"MATH-{random.randint(1000,9999)}|2|十進制 {val} 的二進制？|{bin(val)[2:]},{bin(val+1)[2:]},0000|{bin(val)[2:]}\n")
            f.write("SYS-001|1|CityOS 核心運算單元？|CPU,GPU,TPU,APU|CPU\n")

# ==================================================
# 1. 系統設定
# ==================================================
st.set_page_config(page_title="CityOS V150", layout="wide", page_icon="🏙️")
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
    init_df = pd.DataFrame(np.random.randint(40, 60, size=(20, 3)), columns=['CPU', 'NET', 'SEC'])
    st.session_state.update({
        "state": True, 
        "name": "", 
        "email": "", # 新增 Email 欄位
        "avatar": "", # 新增頭像欄位
        "title": "市政執行官", 
        "level": "區域管理員", 
        "history": [], 
        "theme_name": "專業暗色 (Night City)",
        "exam_active": False, 
        "quiz_batch": [],
        "monitor_data": init_df
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
    /* Google Button Style */
    .google-btn {{
        background-color: white !important; 
        color: #333 !important; 
        border: 1px solid #ddd !important; 
        display: flex; align-items: center; justify-content: center;
        width: 100%;
        font-weight: 500;
    }}
    </style>
    """, unsafe_allow_html=True)

def render_svg(svg_code):
    svg_black = svg_code.replace('stroke="currentColor"', 'stroke="#000000"').replace('fill="currentColor"', 'fill="#000000"')
    b64 = base64.b64encode(svg_black.encode('utf-8')).decode("utf-8")
    st.markdown(f'''<div style="background-color: #FFFFFF; border-radius: 8px; padding: 20px; margin-bottom: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"><img src="data:image/svg+xml;base64,{b64}" width="200"/></div>''', unsafe_allow_html=True)

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
# 2. 核心邏輯 (含隨機漫步)
# ==================================================
def update_data_random_walk():
    last_row = st.session_state.monitor_data.iloc[-1]
    new_cpu = max(0, min(100, last_row['CPU'] + random.randint(-5, 5)))
    new_net = max(0, min(100, last_row['NET'] + random.randint(-5, 5)))
    new_sec = max(0, min(100, last_row['SEC'] + random.randint(-5, 5)))
    
    new_row = pd.DataFrame([[new_cpu, new_net, new_sec]], columns=['CPU', 'NET', 'SEC'])
    updated_df = pd.concat([st.session_state.monitor_data, new_row], ignore_index=True)
    if len(updated_df) > 30: updated_df = updated_df.iloc[1:]
    st.session_state.monitor_data = updated_df
    return updated_df

# ==================================================
# 3. 主程式
# ==================================================
def main():
    apply_theme()
    t_colors = THEMES[st.session_state.theme_name]["chart"]

    with st.sidebar:
        st.title("🏙️ CityOS V150")
        st.caption("Central Command Interface")
        
        # [更新] 側邊欄顯示 Google 風格使用者資訊
        st.markdown(f"""
        <div style="padding:15px; background:rgba(255,255,255,0.05); border-radius:8px; margin-bottom:15px; border-left: 4px solid #4285F4;">
            <div style="display:flex; align-items:center;">
                <div style="width:40px; height:40px; border-radius:50%; background-color:#4285F4; color:white; display:flex; align-items:center; justify-content:center; font-weight:bold; margin-right:10px;">
                    {st.session_state.name[0].upper() if st.session_state.name else "U"}
                </div>
                <div>
                    <div style="font-size:1.0em; font-weight:bold;">{st.session_state.name}</div>
                    <div style="font-size:0.7em; opacity:0.7;">{st.session_state.email}</div>
                </div>
            </div>
            <div style="font-size:0.8em; margin-top:8px; padding-top:8px; border-top:1px solid rgba(255,255,255,0.1);">
                權限: {st.session_state.level}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        menu = ["🏙️ 城市儀表板", "⚡ 電力設施 (Logic)", "🏦 數據中心 (Math)", "🎓 市政學院 (Quiz)", "🔀 交通調度 (MUX)", "📂 人事檔案"]
        page = st.radio("導航", menu)

    if "城市儀表板" in page:
        st.title("🏙️ 城市中控儀表板")
        col_main, col_side = st.columns([2, 1])
        
        with col_main:
            st.subheader("📖 市政操作手冊")
            with st.expander("📌 V1.5.0 更新說明", expanded=True):
                st.markdown("""
                * **🔐 身份驗證**：系統已升級至 **Google OAuth** 安全標準。
                * **📡 監控優化**：隨機漫步算法 (±5) 穩定運行中。
                """)
            st.divider()
            
            c1, c2 = st.columns([3, 1])
            with c1: st.subheader("📡 系統核心監控 (Live Feed)")
            with c2: 
                if st.button("⚡ 立即刷新", use_container_width=True):
                    update_data_random_walk()
            
            chart_placeholder = st.empty()
            metric_placeholder = st.empty()
            
            for _ in range(15): # 模擬即時
                df = update_data_random_walk()
                chart_placeholder.area_chart(df, color=t_colors, height=280)
                last = df.iloc[-1]
                metric_placeholder.markdown(f"""
                <div style="display:flex; justify-content:space-around; background:rgba(128,128,128,0.1); padding:10px; border-radius:5px;">
                    <div>CPU: <b style="color:#4285F4">{int(last['CPU'])}%</b></div>
                    <div>NET: <b style="color:#34A853">{int(last['NET'])} Mbps</b></div>
                    <div>SEC: <b style="color:#EA4335">{int(last['SEC'])} Lvl</b></div>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(1) 

        with col_side:
            st.subheader("⚠️ 系統狀態")
            st.success(f"已透過 Google 帳戶驗證：\n{st.session_state.email}")
            st.subheader("🛠️ 更新日誌")
            log_data = [
                {"Ver": "V1.5.0", "Action": "Implement Google Login UI"},
                {"Ver": "V1.4.2", "Action": "Random Walk (±5)"},
                {"Ver": "V1.4.1", "Action": "Restore All Modules"},
            ]
            st.dataframe(pd.DataFrame(log_data), use_container_width=True, hide_index=True)

    elif "電力設施" in page:
        st.header("⚡ 電力設施")
        gate = st.selectbox("Gate", ["AND", "OR", "XOR"])
        c1, c2 = st.columns([1, 2])
        with c1: render_svg(SVG_ICONS.get(gate, SVG_ICONS["AND"]))
        with c2: st.info(f"監控 {gate} 閘邏輯狀態正常。")

    elif "數據中心" in page:
        st.header("🏦 數據中心")
        val = st.text_input("Dec Input", "255")
        if val.isdigit(): st.metric("Hex", hex(int(val))[2:].upper())

    elif "交通調度" in page:
        st.header("🔀 交通調度")
        st.info("MUX 線路穩定。")

    elif "市政學院" in page:
        st.header("🎓 市政管理考評")
        if not st.session_state.exam_active:
            if st.button("🚀 啟動考核"):
                qs = load_qs()
                if len(qs)>=5:
                    st.session_state.quiz_batch = random.sample(qs, 5)
                    st.session_state.exam_active = True
                    st.rerun()
        else:
            with st.form("exam"):
                ans = {}
                for i, q in enumerate(st.session_state.quiz_batch):
                    st.write(f"**{i+1}. {q['q']}**")
                    ans[i] = st.radio("", q['o'], key=f"q{i}")
                    st.divider()
                if st.form_submit_button("提交"):
                    score = sum([1 for i in range(5) if ans[i]==st.session_state.quiz_batch[i]['a']])
                    if score==5: st.balloons()
                    st.session_state.exam_active = False
                    time.sleep(1); st.rerun()

    elif "人事檔案" in page:
        st.header("📂 人事檔案 (Google Account)")
        c1, c2 = st.columns([1, 3])
        with c1:
            st.markdown(f"""
            <div style="width:100px; height:100px; border-radius:50%; background-color:#4285F4; color:white; display:flex; align-items:center; justify-content:center; font-size:40px; font-weight:bold; margin:auto;">
                {st.session_state.name[0].upper()}
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.text_input("Google Name", st.session_state.name, disabled=True)
            st.text_input("Google Email", st.session_state.email, disabled=True)
            st.text_input("CityOS Level", st.session_state.level, disabled=True)

        if st.button("登出 Google 帳戶"):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()

# ==================================================
# 4. 入口 (Google Login Simulation)
# ==================================================
if not st.session_state.name:
    apply_theme()
    
    # 這裡使用 CSS 將容器置中，營造登入頁面感
    st.markdown("""
    <style>
    .stApp {
        background-color: #202124 !important; /* Google Dark Mode BG */
    }
    .login-container {
        border: 1px solid #5f6368;
        padding: 40px;
        border-radius: 8px;
        text-align: center;
        max-width: 400px;
        margin: 100px auto;
        background-color: #303134;
    }
    .google-btn-fake {
        background-color: #ffffff;
        color: #1f1f1f;
        border: 1px solid #dadce0;
        border-radius: 4px;
        padding: 10px 20px;
        font-family: 'Roboto', sans-serif;
        font-weight: 500;
        font-size: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: background-color 0.3s;
        margin-top: 20px;
    }
    .google-btn-fake:hover {
        background-color: #f8f9fa;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True) # Spacer
        st.title("CityOS")
        st.markdown('<div style="text-align:center; color:#9aa0a6; margin-bottom:20px;">Sign in to continue to Central Command</div>', unsafe_allow_html=True)
        
        # 建立一個容器來置放登入按鈕
        with st.container(border=True):
            st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Google_%22G%22_logo.svg/150px-Google_%22G%22_logo.svg.png", width=50)
            st.subheader("Sign in with Google")
            
            # 使用 Streamlit 按鈕，但我們在上面用 CSS 試圖美化介面
            # 這裡我們用一個簡單的 checkbox 或 button 觸發登入
            if st.button("G | Sign in with Google (Simulated)", use_container_width=True, type="secondary"):
                with st.spinner("Connecting to accounts.google.com..."):
                    time.sleep(1.5) # 模擬網路延遲
                
                # 登入成功，設定模擬數據
                st.session_state.name = "Frank"
                st.session_state.email = "frank@cityos.gov"
                st.success("Authentication Successful")
                time.sleep(0.5)
                st.rerun()
            
            st.caption("This is a simulated authentication for local testing.")

else:
    main()
