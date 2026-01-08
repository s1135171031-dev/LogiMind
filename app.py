import streamlit as st
import random
import time
import pandas as pd
import timeit
import plotly.graph_objects as go
import numpy as np # 用於 FFT 和 PID 計算
from datetime import datetime

# --- 1. 載入設定與資料庫 ---
try:
    from config import ITEMS, STOCKS_DATA, LEVEL_TITLES
except ImportError:
    st.error("❌ 系統錯誤: 找不到 config.py。請確認檔案存在。")
    st.stop()

from database import (
    init_db, get_user, save_user, 
    get_global_stock_state, save_global_stock_state, 
    add_exp, add_log, get_logs
)

# --- 2. 樣式設定 (Cyberpunk / Hacker Style) ---
st.set_page_config(page_title="CityOS: EE Core", layout="wide", page_icon="⚡")

st.markdown("""
<style>
    /* 全域背景：深黑色 */
    .stApp { 
        background-color: #050505; 
        color: #00ff41; 
        font-family: 'Consolas', 'Courier New', monospace; 
    }
    
    /* 按鈕樣式：黑底綠框，懸浮發光 */
    div.stButton > button { 
        background-color: #000; 
        border: 1px solid #00ff41; 
        color: #00ff41; 
        border-radius: 0px; 
        font-weight: bold;
        transition: 0.3s;
    }
    div.stButton > button:hover { 
        background-color: #00ff41; 
        color: #000; 
        box-shadow: 0 0 15px #00ff41;
    }
    
    /* 側邊欄：深灰黑 */
    section[data-testid="stSidebar"] { 
        background-color: #0b1016; 
        border-right: 1px solid #333; 
    }
    
    /* 輸入框：黑底綠字 */
    .stTextInput > div > div > input { 
        color: #00ff41; 
        background-color: #111; 
        border: 1px solid #333; 
    }
    
    /* 標題與文字顏色強制為螢光綠 */
    h1, h2, h3, p, span { color: #00ff41 !important; text-shadow: 0 0 5px #003300; }
    
    /* 進度條 */
    .stProgress > div > div > div > div { background-color: #00ff41; }
    
    /* Metric 卡片修正 */
    div[data-testid="stMetricValue"] { color: #00ff41 !important; }
    div[data-testid="stMetricLabel"] { color: #00cc33 !important; }
</style>
""", unsafe_allow_html=True)

init_db()

# --- 3. 工具函式 ---
def render_logic_gate_svg(gate_type, val_a, val_b, output):
    # 產生不破圖的 SVG
    color = "#00ff41" if output else "#333"
    return f"""
    <svg width="200" height="100" viewBox="0 0 200 100">
        <line x1="10" y1="30" x2="50" y2="30" stroke="{'#00ff41' if val_a else '#555'}" stroke-width="3"/>
        <text x="0" y="35" fill="#00ff41" font-size="12">A={val_a}</text>
        <line x1="10" y1="70" x2="50" y2="70" stroke="{'#00ff41' if val_b else '#555'}" stroke-width="3"/>
        <text x="0" y="75" fill="#00ff41" font-size="12">B={val_b}</text>
        <rect x="50" y="20" width="60" height="60" rx="10" fill="none" stroke="#00ff41" stroke-width="2"/>
        <text x="65" y="55" fill="#00ff41" font-size="20">{gate_type}</text>
        <line x1="110" y1="50" x2="180" y2="50" stroke="{color}" stroke-width="3"/>
        <circle cx="180" cy="50" r="5" fill="{color}"/>
        <text x="185" y="55" fill="{color}" font-size="14">{output}</text>
    </svg>
    """

def update_stock_market():
    global_state = get_global_stock_state()
    now = time.time()
    if now - global_state.get("last_update", 0) > 2.0:
        new_prices = {}
        for code, data in STOCKS_DATA.items():
            prev = global_state["prices"].get(code, data["base"])
            change = random.uniform(-0.03, 0.03)
            new_prices[code] = max(1, int(prev * (1 + change)))
        
        global_state["prices"] = new_prices
        global_state["last_update"] = now
        hist = new_prices.copy()
        hist["_time"] = datetime.now().strftime("%H:%M:%S")
        global_state["history"].append(hist)
        if len(global_state["history"]) > 40: global_state["history"].pop(0)
        save_global_stock_state(global_state)
    st.session_state.stock_prices = global_state["prices"]
    st.session_state.stock_history = pd.DataFrame(global_state["history"])

# --- 4. 核心功能頁面 ---

# 🧠 A: 邏輯設計
def page_logic_lab(uid, user):
    st.title("🧠 邏輯設計 (Digital Logic)")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("元件測試 (Circuit Test)")
        gate_type = st.selectbox("Gate Type", ["AND (及)", "OR (或)", "XOR (互斥或)", "NAND (反及)"])
        input_a = st.toggle("Input A (1/0)", value=True)
        input_b = st.toggle("Input B (1/0)", value=False)
        a_val = 1 if input_a else 0
        b_val = 1 if input_b else 0
        
        if "AND" in gate_type: out = a_val & b_val
        elif "OR" in gate_type: out = a_val | b_val
        elif "XOR" in gate_type: out = a_val ^ b_val
        elif "NAND" in gate_type: out = int(not (a_val & b_val))
        
        st.markdown(render_logic_gate_svg(gate_type.split()[0], a_val, b_val, out), unsafe_allow_html=True)

    with col2:
        st.subheader("隨堂測驗 (Quiz)")
        st.write(f"Q: 若 A=1, B=0, **{gate_type}** 輸出為何？")
        ans = st.radio("Answer", ["0 (Low)", "1 (High)"], key="quiz")
        if st.button("Submit"):
            correct = str(out)
            if ans.startswith(correct):
                st.success("Access Granted. 答案正確。")
                add_exp(uid, 10)
            else: st.error("Access Denied. 答案錯誤。")

# ⚔️ B: 演算法
def page_arena(uid, user):
    st.title("⚔️ 演算法競技場 (Algo Arena)")
    st.caption("目標：降低時間複雜度 (Time Complexity)")
    
    enemy_hp = st.session_state.get("enemy_hp", 100)
    st.progress(enemy_hp / 100, text=f"BOSS HP: {enemy_hp}")

    weapon = st.selectbox("選擇演算法", ["Bubble Sort (O(n^2))", "Python Sort (O(n log n))", "NumPy Sort (Optimized)"])

    if st.button("Execute Code"):
        data = list(range(5000)); random.shuffle(data)
        if "Bubble" in weapon:
            setup = f"d = {data[:300]}" # 縮小數據避免卡死
            code = "for i in range(len(d)): d.sort()" # 模擬慢速
            base_dmg = 10
        elif "Python" in weapon:
            setup = f"d = {data}"
            code = "d.sort()"
            base_dmg = 50
        else:
            setup = "import numpy as np; d = np.random.randint(0,5000,5000)"
            code = "np.sort(d)"
            base_dmg = 80

        try:
            with st.spinner("Compiling..."):
                t = timeit.timeit(stmt=code, setup=setup, number=5)
            st.code(f"Execution Time: {t:.5f} sec", language="bash")
            
            final_dmg = base_dmg * (2 if t < 0.001 else 1)
            enemy_hp = max(0, enemy_hp - final_dmg)
            st.session_state.enemy_hp = enemy_hp
            
            st.success(f"Critical Hit! 造成 {final_dmg} 傷害")
            if enemy_hp == 0:
                st.balloons(); st.success("Target Eliminated!"); user['money'] += 500; add_exp(uid, 100); save_user(uid, user); st.session_state.enemy_hp = 100; time.sleep(2); st.rerun()
        except Exception as e: st.error(f"Runtime Error: {e}")

# 📡 C: 訊號處理
def page_signals(uid, user):
    st.title("📡 訊號攔截 (Signals)")
    if "signal_target" not in st.session_state:
        target = random.choice(["FPGA", "CMOS", "UART", "LINUX"])
        st.session_state.signal_target = target
        st.session_state.signal_hex = target.encode().hex().upper()
        st.session_state.noise = np.random.rand(50)

    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("Oscilloscope (示波器)")
        fig = go.Figure(data=go.Scatter(y=st.session_state.noise, mode='lines', line=dict(color='#00ff41')))
        fig.update_layout(height=200, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#00ff41'), xaxis_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        st.code(f"Received: 0x{st.session_state.signal_hex}")
    with c2:
        ans = st.text_input("Decode to ASCII (UPPERCASE):")
        if st.button("Transmit"):
            if ans == st.session_state.signal_target:
                st.success("Decoded Successfully."); user['money'] += 300; add_exp(uid, 50); save_user(uid, user); del st.session_state['signal_target']; time.sleep(1); st.rerun()
            else: st.error("CRC Error.")

# 🏗️ D: 資料結構
def page_memory(uid, user):
    st.title("🏗️ 記憶體管理 (Memory Stack)")
    if "mem_blocks" not in st.session_state: st.session_state.mem_blocks = []
    
    income = sum([b['value'] for b in st.session_state.mem_blocks])
    st.metric("Memory Yield", f"${income}/cycle")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Alloc Array ($500)"):
            if user['money'] >= 500: user['money'] -= 500; st.session_state.mem_blocks.append({"type": "Arr", "value": 50}); save_user(uid, user); st.rerun()
    with c2:
        if st.button("Alloc Node ($200)"):
            if user['money'] >= 200: user['money'] -= 200; st.session_state.mem_blocks.append({"type": "Node", "value": 20}); save_user(uid, user); st.rerun()
            
    st.write("--- Heap Visualization ---")
    cols = st.columns(10)
    for i, block in enumerate(st.session_state.mem_blocks[-20:]):
        color = "🟩" if block['type'] == "Arr" else "🟧"
        cols[i%10].write(f"{color}")

    if st.button("Garbage Collect (Harvest)"):
        user['money'] += income; save_user(uid, user); st.success(f"Recovered ${income}")

# 🎛️ E: 自動控制 (PID)
def page_control(uid, user):
    st.title("🎛️ PID 控制 (Control Systems)")
    st.caption("調整 Kp, Ki, Kd 以穩定系統")
    
    c1, c2 = st.columns([1, 3])
    with c1:
        kp = st.slider("Kp (Proportional)", 0.0, 5.0, 1.0)
        ki = st.slider("Ki (Integral)", 0.0, 2.0, 0.1)
        kd = st.slider("Kd (Derivative)", 0.0, 5.0, 0.5)
        target = st.slider("Set Point", 0, 100, 80)
        run = st.button("Simulate")
    
    with c2:
        if run:
            history, curr, integral, prev_err = [], 0, 0, 0
            for _ in range(50):
                err = target - curr
                integral += err
                deriv = err - prev_err
                out = (kp*err) + (ki*integral) + (kd*deriv)
                curr += out * 0.1 # 慣性
                history.append(curr)
                prev_err = err
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(y=[target]*50, name="Target", line=dict(dash="dash", color="#555")))
            fig.add_trace(go.Scatter(y=history, name="Output", line=dict(color="#00ff41")))
            fig.update_layout(title="Step Response", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#00ff41'))
            st.plotly_chart(fig, use_container_width=True)
            if abs(history[-1] - target) < 2: st.success("System Stable!"); add_exp(uid, 30)
            else: st.warning("Unstable!")

# 🌊 F: 數位訊號處理 (DSP)
def page_dsp(uid, user):
    st.title("🌊 頻譜分析 (FFT)")
    st.write("合成波形 -> 頻域分析")
    
    c1, c2 = st.columns(2)
    f1 = c1.slider("Freq 1 (Hz)", 1, 50, 5); a1 = c1.slider("Amp 1", 1, 10, 5)
    f2 = c2.slider("Freq 2 (Hz)", 1, 50, 20); a2 = c2.slider("Amp 2", 1, 10, 3)
    
    t = np.linspace(0, 1, 500)
    y = a1 * np.sin(2*np.pi*f1*t) + a2 * np.sin(2*np.pi*f2*t)
    
    fig1 = go.Figure(data=go.Scatter(x=t, y=y, line=dict(color='#00ff41')))
    fig1.update_layout(title="Time Domain", height=200, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#00ff41'))
    st.plotly_chart(fig1, use_container_width=True)
    
    if st.button("Compute FFT"):
        fft_vals = np.fft.fft(y)
        freqs = np.fft.fftfreq(len(t), 1/500)
        mask = freqs > 0
        fig2 = go.Figure(data=go.Bar(x=freqs[mask], y=np.abs(fft_vals)[mask], marker_color='#ff0055'))
        fig2.update_layout(title="Frequency Domain", height=250, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#00ff41'))
        st.plotly_chart(fig2, use_container_width=True)
        add_exp(uid, 50)

# --- 主程式與導航 ---
def page_dashboard(uid, user):
    st.title(f"🖥️ SYSTEM STATUS: {user['name']}")
    st.caption(f"ID: {uid} | {LEVEL_TITLES.get(min(user['level'], 5), 'Unknown')}")
    update_stock_market()
    
    if not st.session_state.stock_history.empty:
        df = st.session_state.stock_history
        fig = go.Figure(data=go.Scatter(x=df['_time'], y=df['TSMC'], mode='lines+markers', line=dict(color='#00ff41')))
        fig.update_layout(title="TSMC Index", height=250, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#00ff41'))
        st.plotly_chart(fig, use_container_width=True)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("CREDITS", f"${user['money']:,}")
    c2.metric("ASSETS", f"${sum(user.get('stocks',{}).values()):,}")
    c3.metric("LEVEL", f"Lv.{user['level']}")

def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        st.title("⚡ EE_DEPT // GATEWAY")
        c1, c2 = st.columns([1,2])
        with c1: st.markdown("<h1 style='font-size:100px'>⚡</h1>", unsafe_allow_html=True)
        with c2:
            u = st.text_input("USER ID (frank)")
            p = st.text_input("PASSWORD (x)", type="password")
            if st.button("CONNECT"):
                user = get_user(u)
                if user and user['password'] == p: st.session_state.logged_in = True; st.session_state.uid = u; st.rerun()
                else: st.error("ACCESS DENIED")
        return

    uid = st.session_state.uid; user = get_user(uid)
    if not user: st.session_state.logged_in = False; st.rerun()

    with st.sidebar:
        st.header("⚡ MODULES")
        st.write(f"OP: {user['name']}")
        nav = st.radio("SELECT:", 
            ["📊 DASHBOARD", "🧠 LOGIC LAB", "⚔️ ALGO ARENA", "📡 SIGNALS", 
             "🏗️ MEMORY", "🎛️ PID CONTROL", "🌊 FFT ANALYZER"])
        st.divider()
        if st.button("LOGOUT"): st.session_state.logged_in = False; st.rerun()

    if "DASHBOARD" in nav: page_dashboard(uid, user)
    elif "LOGIC" in nav: page_logic_lab(uid, user)
    elif "ALGO" in nav: page_arena(uid, user)
    elif "SIGNALS" in nav: page_signals(uid, user)
    elif "MEMORY" in nav: page_memory(uid, user)
    elif "PID" in nav: page_control(uid, user)
    elif "FFT" in nav: page_dsp(uid, user)

if __name__ == "__main__":
    main()
