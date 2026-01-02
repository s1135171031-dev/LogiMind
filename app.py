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
st.set_page_config(page_title="CityOS V142", layout="wide")
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
    # 初始化一個起始數據 (20筆)，讓圖表一開始有東西
    init_df = pd.DataFrame(np.random.randint(40, 60, size=(20, 3)), columns=['CPU', 'NET', 'SEC'])
    
    st.session_state.update({
        "state": True, "name": "", "title": "市政執行官", "level": "區域管理員", 
        "history": [], "theme_name": "專業暗色 (Night City)",
        "exam_active": False, "quiz_batch": [],
        "monitor_data": init_df, # 用來存儲連續數據
        "run_monitor": False     # 控制監控開關
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
# 2. 核心邏輯：隨機漫步產生器
# ==================================================
def update_data_random_walk():
    # 取得當前數據庫的最後一筆資料
    last_row = st.session_state.monitor_data.iloc[-1]
    
    # 產生新數據：上一筆 + 隨機波動 (-5 到 5)
    new_cpu = last_row['CPU'] + random.randint(-5, 5)
    new_net = last_row['NET'] + random.randint(-5, 5)
    new_sec = last_row['SEC'] + random.randint(-5, 5)
    
    # 邊界檢查 (Clip)：確保數值不會超出 0-100 或變成負數
    new_cpu = max(0, min(100, new_cpu))
    new_net = max(0, min(100, new_net))
    new_sec = max(0, min(100, new_sec))
    
    # 建立新的一行
    new_row = pd.DataFrame([[new_cpu, new_net, new_sec]], columns=['CPU', 'NET', 'SEC'])
    
    # 合併到主數據，並保持只留最後 30 筆以維持圖表簡潔
    updated_df = pd.concat([st.session_state.monitor_data, new_row], ignore_index=True)
    if len(updated_df) > 30:
        updated_df = updated_df.iloc[1:] # 刪除最舊的一筆
        
    st.session_state.monitor_data = updated_df
    return updated_df

# ==================================================
# 3. 主程式
# ==================================================
def main():
    apply_theme()
    t_colors = THEMES[st.session_state.theme_name]["chart"]

    with st.sidebar:
        st.title("🏙️ CityOS V142")
        st.caption("Central Command Interface")
        st.markdown(f"""
        <div style="padding:15px; background:rgba(255,255,255,0.05); border-radius:8px; margin-bottom:15px; border-left: 4px solid #4CAF50;">
            <div style="font-size:1.1em;">👤 <b>{st.session_state.title}</b></div>
            <div style="font-size:0.9em; opacity:0.8;">ID: {st.session_state.name}</div>
        </div>
        """, unsafe_allow_html=True)
        st.divider()
        menu = ["🏙️ 城市儀表板", "⚡ 電力設施 (Logic)", "🏦 數據中心 (Math)", "🎓 市政學院 (Quiz)", "🔀 交通調度 (MUX)", "📂 人事檔案"]
        page = st.radio("導航", menu)

    if "城市儀表板" in page:
        st.title("🏙️ 城市中控儀表板 (Dashboard)")
        
        col_main, col_side = st.columns([2, 1])
        
        with col_main:
            st.subheader("📖 市政操作手冊")
            with st.expander("📌 模組說明", expanded=True):
                st.markdown("* **V1.4.2 更新**：即時監控圖表現在採用「隨機漫步算法」，每次變動幅度不超過 ±5。")

            st.divider()
            
            # --- 監控區域 ---
            c1, c2 = st.columns([3, 1])
            with c1: st.subheader("📡 系統核心監控 (Live Feed)")
            with c2: 
                # 按鈕控制
                if st.button("⚡ 立即刷新數據流", use_container_width=True):
                    # 手動觸發一次更新
                    update_data_random_walk()
            
            # 圖表容器
            chart_placeholder = st.empty()
            metric_placeholder = st.empty()
            
            # 自動運行迴圈 (模擬即時效果)
            # 這裡設定跑 20 次循環，每次間隔 1 秒，符合您要求的「每1秒產生一次」
            for _ in range(20):
                # 1. 更新數據 (核心邏輯：誤差 < 5)
                df = update_data_random_walk()
                
                # 2. 繪製圖表
                chart_placeholder.area_chart(df, color=t_colors, height=280)
                
                # 3. 顯示最新數值 (讓使用者看清楚數值變化)
                last = df.iloc[-1]
                metric_placeholder.markdown(f"""
                <div style="display:flex; justify-content:space-around; background:rgba(128,128,128,0.1); padding:10px; border-radius:5px;">
                    <div>CPU: <b>{int(last['CPU'])}%</b></div>
                    <div>NET: <b>{int(last['NET'])} Mbps</b></div>
                    <div>SEC: <b>{int(last['SEC'])} Lvl</b></div>
                </div>
                """, unsafe_allow_html=True)
                
                # 4. 等待 1 秒
                time.sleep(1) 

        with col_side:
            st.subheader("⚠️ 安全公告")
            st.warning("監控數據流已穩定。波動幅度鎖定於 ±5。")
            
            st.subheader("🛠️ 系統更新日誌")
            # 使用表格顯示
            log_data = [
                {"版本": "V1.4.2", "日期": "2026-01-04", "項目": "監控邏輯：隨機誤差限制 (±5)"},
                {"版本": "V1.4.2", "日期": "2026-01-04", "項目": "更新頻率：調整為 1.0 秒"},
                {"版本": "V1.4.1", "日期": "2026-01-04", "項目": "全功能復原：Math/MUX/Map"},
                {"版本": "V1.4.1", "日期": "2026-01-04", "項目": "UI 優化：日誌表格化"},
                {"版本": "V1.4.0", "日期": "2026-01-04", "項目": "核心：Batch-5 連鎖考核"},
            ]
            st.dataframe(pd.DataFrame(log_data), use_container_width=True, hide_index=True)

    elif "電力設施" in page:
        st.header("⚡ 電力設施監控")
        gate = st.selectbox("監控節點", ["AND", "OR", "XOR"])
        c1, c2 = st.columns([1, 2])
        with c1: render_svg(SVG_ICONS.get(gate, SVG_ICONS["AND"]))
        with c2:
            st.subheader("邏輯真值表")
            d = {"In A":[0,0,1,1], "In B":[0,1,0,1]}
            if gate=="AND": d["Out"]=[0,0,0,1]
            elif gate=="OR": d["Out"]=[0,1,1,1]
            elif gate=="XOR": d["Out"]=[0,1,1,0]
            st.dataframe(pd.DataFrame(d), use_container_width=True, hide_index=True)

    elif "數據中心" in page:
        st.header("🏦 數據中心")
        val = st.text_input("輸入十進制數值", "128")
        if val.isdigit():
            v = int(val)
            c1, c2 = st.columns(2)
            c1.metric("Binary", bin(v)[2:])
            c2.metric("Hex", hex(v)[2:].upper())

    elif "交通調度" in page:
        st.header("🔀 交通調度 (MUX)")
        c1, c2 = st.columns(2)
        with c1: render_svg(SVG_ICONS["MUX"])
        with c2:
            s = st.selectbox("選擇通道", ["00", "01", "10", "11"])
            st.info(f"當前導通：Line {int(s, 2)}")

    elif "市政學院" in page:
        st.header("🎓 市政管理能力考評 (Batch-5)")
        if not st.session_state.exam_active:
            if st.button("🚀 啟動考核", type="primary"):
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
                    ans[i] = st.radio(f"Opt {i}", q['o'], key=f"q{i}", label_visibility="collapsed")
                    st.divider()
                if st.form_submit_button("提交"):
                    score = sum([1 for i in range(5) if ans[i]==st.session_state.quiz_batch[i]['a']])
                    if score==5: 
                        st.balloons(); st.success("完美通過！")
                        if st.session_state.level == "區域管理員": st.session_state.level = "城市規劃師"
                    else: st.error(f"得分：{score}/5")
                    st.session_state.history.append({"時間": datetime.now().strftime("%H:%M"), "結果": f"{score}/5"})
                    st.session_state.exam_active = False
                    time.sleep(2); st.rerun()

    elif "人事檔案" in page:
        st.header("📂 人事檔案")
        st.text_input("ID", st.session_state.name, disabled=True)
        st.selectbox("主題", list(THEMES.keys()), key="theme_name")
        if st.button("登出"):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()
        st.subheader("紀錄")
        if st.session_state.history: st.dataframe(st.session_state.history)

# ==================================================
# 4. 入口
# ==================================================
if not st.session_state.name:
    apply_theme()
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.title("🏙️ CityOS V142")
        st.markdown('<div style="text-align:center; color:#888;">System Access Required</div>', unsafe_allow_html=True)
        with st.form("login"):
            n = st.text_input("Commander ID")
            if st.form_submit_button("Initialize"):
                if n: st.session_state.name = n; st.rerun()
else:
    main()
