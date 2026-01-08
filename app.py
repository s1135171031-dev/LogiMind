import streamlit as st
import random
import time
import pandas as pd
import timeit
import plotly.graph_objects as go
import numpy as np
import sympy as sp
from datetime import datetime

# --- 1. 載入設定與資料庫 ---
try:
    from config import ITEMS, STOCKS_DATA, LEVEL_TITLES
except ImportError:
    st.error("❌ 系統錯誤: 找不到 config.py")
    st.stop()

from database import (
    init_db, get_user, save_user, 
    get_global_stock_state, save_global_stock_state, 
    add_exp, add_log, get_logs
)

# --- 2. 樣式設定 (Cyberpunk Style) ---
st.set_page_config(page_title="CityOS: EE Core", layout="wide", page_icon="⚡")

st.markdown("""
<style>
    /* 全域背景：深黑 */
    .stApp { 
        background-color: #050505; 
        color: #00ff41; 
        font-family: 'Consolas', 'Microsoft JhengHei', monospace; 
    }
    
    /* 按鈕：黑底綠框，懸浮發光 */
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
    
    /* 文字顏色強制螢光綠 */
    h1, h2, h3, p, span { color: #00ff41 !important; text-shadow: 0 0 5px #003300; }
    
    /* Metric 卡片 */
    div[data-testid="stMetricValue"] { color: #00ff41 !important; }
    div[data-testid="stMetricLabel"] { color: #00cc33 !important; }
</style>
""", unsafe_allow_html=True)

init_db()

# --- 3. 工具函式 ---
def render_logic_gate_svg(gate_type, val_a, val_b, output):
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

# --- 4. 核心功能模組 ---

# 🧠 A: 邏輯設計
def page_logic_lab(uid, user):
    st.title("🧠 邏輯設計 (Logic Design)")
    st.caption("課程：布林代數與邏輯閘 (Boolean Algebra)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("電路模擬 (Circuit Sim)")
        gate_type = st.selectbox("選擇元件 (Component)", ["AND (及閘)", "OR (或閘)", "XOR (互斥或)", "NAND (反及)"])
        input_a = st.toggle("輸入 A (Input A)", value=True)
        input_b = st.toggle("輸入 B (Input B)", value=False)
        a_val = 1 if input_a else 0
        b_val = 1 if input_b else 0
        
        gate_key = gate_type.split()[0]
        if "AND" in gate_type: out = a_val & b_val
        elif "OR" in gate_type: out = a_val | b_val
        elif "XOR" in gate_type: out = a_val ^ b_val
        elif "NAND" in gate_type: out = int(not (a_val & b_val))
        
        st.markdown(render_logic_gate_svg(gate_key, a_val, b_val, out), unsafe_allow_html=True)

    with col2:
        st.subheader("隨堂測驗 (Quiz)")
        st.write(f"Q: 當 A={a_val}, B={b_val} 時，**{gate_key}** 的輸出為何？")
        ans = st.radio("你的答案 (Answer)", ["0 (Low)", "1 (High)"], key="quiz")
        if st.button("提交 (Submit)"):
            correct = str(out)
            if ans.startswith(correct):
                st.success("Access Granted. 邏輯正確。")
                add_exp(uid, 10)
            else: st.error("Access Denied. 邏輯錯誤。")

# ⚔️ B: 演算法
def page_arena(uid, user):
    st.title("⚔️ 演算法競技場 (Algo Arena)")
    st.caption("課程：資料結構與複雜度 (Data Structures & Big O)")
    
    enemy_hp = st.session_state.get("enemy_hp", 100)
    st.progress(enemy_hp / 100, text=f"BUG 怪獸血量 (HP): {enemy_hp}")

    weapon = st.selectbox("選擇演算法武器 (Algorithm)", 
        ["氣泡排序 (Bubble Sort) - O(n^2) 傷害低", 
         "Python 內建排序 (Timsort) - O(n log n) 傷害高", 
         "NumPy 極速排序 (Optimized) - 暴擊傷害"])

    if st.button("編譯並執行 (Compile & Run)"):
        data = list(range(5000)); random.shuffle(data)
        if "Bubble" in weapon:
            setup = f"d = {data[:300]}" 
            code = "for i in range(len(d)): d.sort()" 
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
            with st.spinner("CPU 運算中 (Processing)..."):
                t = timeit.timeit(stmt=code, setup=setup, number=5)
            st.code(f"Execution Time: {t:.5f} sec", language="bash")
            
            final_dmg = base_dmg * (2 if t < 0.001 else 1)
            enemy_hp = max(0, enemy_hp - final_dmg)
            st.session_state.enemy_hp = enemy_hp
            
            st.success(f"命中！造成 {final_dmg} 點傷害 (基於運算速度)")
            if enemy_hp == 0:
                st.balloons()
                st.success("Bug 修復完成 (Target Eliminated)！")
                user['money'] += 500
                add_exp(uid, 100)
                save_user(uid, user)
                st.session_state.enemy_hp = 100
                time.sleep(2)
                st.rerun()
        except Exception as e: st.error(f"Runtime Error: {e}")

# 📡 C: 訊號處理
def page_signals(uid, user):
    st.title("📡 訊號攔截 (Signal Interception)")
    st.caption("課程：數位編碼 (Hex/Binary Encoding)")
    
    if "signal_target" not in st.session_state:
        target = random.choice(["FPGA", "CMOS", "UART", "KERNEL", "BIOS"])
        st.session_state.signal_target = target
        st.session_state.signal_hex = target.encode().hex().upper()
        st.session_state.noise = np.random.rand(50)

    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("示波器畫面 (Oscilloscope)")
        fig = go.Figure(data=go.Scatter(y=st.session_state.noise, mode='lines', line=dict(color='#00ff41')))
        fig.update_layout(height=200, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#00ff41'), xaxis_visible=False, yaxis_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        st.code(f"接收訊號 (Hex): 0x{st.session_state.signal_hex}")
    with c2:
        ans = st.text_input("解碼為 ASCII (全大寫):")
        if st.button("傳送 (Transmit)"):
            if ans == st.session_state.signal_target:
                st.success("解碼成功 (Decoded Successfully)！")
                user['money'] += 300
                add_exp(uid, 50)
                save_user(uid, user)
                del st.session_state['signal_target']
                time.sleep(1)
                st.rerun()
            else: st.error("驗證失敗 (CRC Error)。")

# 🏗️ D: 記憶體管理
def page_memory(uid, user):
    st.title("🏗️ 記憶體堆疊 (Memory Stack)")
    st.caption("課程：陣列與鏈結串列 (Array vs Linked List)")
    
    if "mem_blocks" not in st.session_state: st.session_state.mem_blocks = []
    
    income = sum([b['value'] for b in st.session_state.mem_blocks])
    st.metric("記憶體收益 (Memory Yield)", f"${income}/cycle")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("配置陣列 Array ($500)"):
            if user['money'] >= 500: 
                user['money'] -= 500
                st.session_state.mem_blocks.append({"type": "Arr", "value": 50})
                save_user(uid, user); st.rerun()
    with c2:
        if st.button("配置節點 Node ($200)"):
            if user['money'] >= 200: 
                user['money'] -= 200
                st.session_state.mem_blocks.append({"type": "Node", "value": 20})
                save_user(uid, user); st.rerun()
            
    st.write("--- Heap 視覺化 (Visualization) ---")
    cols = st.columns(10)
    for i, block in enumerate(st.session_state.mem_blocks[-20:]):
        color = "🟩" if block['type'] == "Arr" else "🟧"
        cols[i%10].write(f"{color}")

    if st.button("執行垃圾回收 (Garbage Collection)"):
        user['money'] += income
        save_user(uid, user)
        st.success(f"記憶體釋放完成。獲得收益：${income}")

# 🎛️ E: 自動控制 (PID)
def page_control(uid, user):
    st.title("🎛️ PID 控制實驗室 (Control Lab)")
    st.caption("課程：回授控制系統 (Feedback Control Systems)")
    
    c1, c2 = st.columns([1, 3])
    with c1:
        st.subheader("參數調校 (Tuning)")
        kp = st.slider("Kp (比例)", 0.0, 5.0, 1.0)
        ki = st.slider("Ki (積分)", 0.0, 2.0, 0.1)
        kd = st.slider("Kd (微分)", 0.0, 5.0, 0.5)
        target = st.slider("目標值 (Set Point)", 0, 100, 80)
        run = st.button("啟動模擬 (Simulate)")
    
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
            fig.add_trace(go.Scatter(y=[target]*50, name="目標 (Target)", line=dict(dash="dash", color="#555")))
            fig.add_trace(go.Scatter(y=history, name="響應 (Response)", line=dict(color="#00ff41")))
            fig.update_layout(title="步階響應圖 (Step Response)", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#00ff41'))
            st.plotly_chart(fig, use_container_width=True)
            
            if abs(history[-1] - target) < 2: 
                st.success("系統穩定 (Stable)！獲得獎勵。")
                add_exp(uid, 30)
            else: st.warning("系統震盪 (Unstable)！請重新調整。")

# 🌊 F: 數位訊號處理 (FFT)
def page_dsp(uid, user):
    st.title("🌊 頻譜分析儀 (FFT Analyzer)")
    st.caption("課程：數位訊號處理 (DSP)")
    
    c1, c2 = st.columns(2)
    f1 = c1.slider("頻率 1 (Freq 1 Hz)", 1, 50, 5); a1 = c1.slider("振幅 1 (Amp 1)", 1, 10, 5)
    f2 = c2.slider("頻率 2 (Freq 2 Hz)", 1, 50, 20); a2 = c2.slider("振幅 2 (Amp 2)", 1, 10, 3)
    
    t = np.linspace(0, 1, 500)
    y = a1 * np.sin(2*np.pi*f1*t) + a2 * np.sin(2*np.pi*f2*t)
    
    fig1 = go.Figure(data=go.Scatter(x=t, y=y, line=dict(color='#00ff41')))
    fig1.update_layout(title="時域波形 (Time Domain)", height=200, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#00ff41'))
    st.plotly_chart(fig1, use_container_width=True)
    
    if st.button("執行傅立葉轉換 (Compute FFT)"):
        fft_vals = np.fft.fft(y)
        freqs = np.fft.fftfreq(len(t), 1/500)
        mask = freqs > 0
        fig2 = go.Figure(data=go.Bar(x=freqs[mask], y=np.abs(fft_vals)[mask], marker_color='#ff0055'))
        fig2.update_layout(title="頻域分析 (Frequency Domain)", height=250, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#00ff41'))
        st.plotly_chart(fig2, use_container_width=True)
        add_exp(uid, 50)

# 🧮 G: 工程運算核心 (Math)
def page_calculator(uid, user):
    st.title("🧮 工程運算核心 (Math Kernel)")
    st.caption("課程：工程數學與微積分 (Calculus)")
    
    st.info("語法提示：`2*x`, `x**2` (平方), `sin(x)`")
    
    c1, c2 = st.columns([3, 1])
    expr_str = c1.text_input("輸入函數 f(x):", value="sin(x) + 0.5*x")
    x_range = c2.slider("X 軸範圍 (Range)", 5, 50, 10)
    
    x = sp.symbols('x')
    try:
        expr = sp.sympify(expr_str)
        deriv = sp.diff(expr, x)
        integ = sp.integrate(expr, x)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("f(x) 原式", f"${sp.latex(expr)}$")
        c2.metric("f'(x) 微分", f"${sp.latex(deriv)}$")
        c3.metric("∫ f(x) 積分", f"${sp.latex(integ)}$")
        
        f_lambda = sp.lambdify(x, expr, "numpy")
        x_vals = np.linspace(-x_range, x_range, 400)
        
        try:
            y_vals = f_lambda(x_vals)
            if isinstance(y_vals, (int, float)): y_vals = np.full_like(x_vals, y_vals)
            
            fig = go.Figure(data=go.Scatter(x=x_vals, y=y_vals, line=dict(color='#00ff41', width=2)))
            fig.update_layout(title=f"函數繪圖 (Plot): y = {expr_str}", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#00ff41'))
            st.plotly_chart(fig, use_container_width=True)
            
            if st.button("上傳運算結果 (Upload Result)"):
                st.success("運算數據已同步雲端。")
                add_exp(uid, 20)
        except Exception as e: st.warning(f"繪圖錯誤: {e}")
            
    except Exception as e: st.error(f"語法錯誤 (Syntax Error): {e}")

# --- 主控台與儀表板 ---
def page_dashboard(uid, user):
    st.title(f"🖥️ 系統狀態: {user['name']}")
    st.caption(f"ID: {uid} | 等級: {LEVEL_TITLES.get(min(user['level'], 5), 'Unknown')}")
    update_stock_market()
    
    if not st.session_state.stock_history.empty:
        df = st.session_state.stock_history
        fig = go.Figure(data=go.Scatter(x=df['_time'], y=df['TSMC'], mode='lines+markers', line=dict(color='#00ff41')))
        fig.update_layout(title="台積電指數 (TSMC Index)", height=250, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#00ff41'))
        st.plotly_chart(fig, use_container_width=True)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("持有資金 (Credits)", f"${user['money']:,}")
    c2.metric("股票資產 (Assets)", f"${sum(user.get('stocks',{}).values()):,}")
    c3.metric("目前等級 (Level)", f"Lv.{user['level']}")
    
    st.subheader("📡 系統日誌 (System Logs)")
    for l in get_logs()[:3]: st.text(l)

def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        st.title("⚡ CITY_OS // GATEWAY")
        c1, c2 = st.columns([1,2])
        with c1: st.markdown("<h1 style='font-size:100px; text-align:center'>⚡</h1>", unsafe_allow_html=True)
        with c2:
            st.write("需要安全連線 (Secure Connection Required)")
            u = st.text_input("使用者 ID (frank)", value="frank")
            p = st.text_input("密碼 (x)", type="password", value="x")
            if st.button("建立連線 (CONNECT)"):
                user = get_user(u)
                if user and user['password'] == p: st.session_state.logged_in = True; st.session_state.uid = u; st.rerun()
                else: st.error("拒絕存取 (ACCESS DENIED)")
        return

    uid = st.session_state.uid; user = get_user(uid)
    if not user: st.session_state.logged_in = False; st.rerun()

    with st.sidebar:
        st.header("⚡ 功能模組 (MODULES)")
        st.write(f"操作員: {user['name']}")
        nav = st.radio("選擇功能:", 
            ["📊 儀表板 (Dashboard)", 
             "🧠 邏輯設計 (Logic Lab)", 
             "⚔️ 演算法 (Algo Arena)", 
             "📡 訊號攔截 (Signals)", 
             "🏗️ 記憶體 (Memory)", 
             "🎛️ 自動控制 (PID)", 
             "🌊 頻譜分析 (FFT)", 
             "🧮 工程運算 (Math)"])
        
        st.divider()
        if st.button("登出系統 (LOGOUT)"): st.session_state.logged_in = False; st.rerun()

    if "儀表板" in nav: page_dashboard(uid, user)
    elif "邏輯" in nav: page_logic_lab(uid, user)
    elif "演算法" in nav: page_arena(uid, user)
    elif "訊號" in nav: page_signals(uid, user)
    elif "記憶體" in nav: page_memory(uid, user)
    elif "控制" in nav: page_control(uid, user)
    elif "頻譜" in nav: page_dsp(uid, user)
    elif "運算" in nav: page_calculator(uid, user)

if __name__ == "__main__":
    main()
