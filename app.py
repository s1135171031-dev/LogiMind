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
        cols
