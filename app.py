import streamlit as st
import random
import time
import pandas as pd
import timeit
import plotly.graph_objects as go # 需要 pip install plotly
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

# --- 2. 樣式設定 (Cyberpunk / 電子電路風) ---
st.set_page_config(page_title="CityOS: EE Core", layout="wide", page_icon="⚡")
st.markdown("""
<style>
    .stApp { background-color: #020a12; color: #00ff41; font-family: 'Consolas', monospace; }
    div.stButton > button { background-color: #000; border: 1px solid #00ff41; color: #00ff41; border-radius: 0px; }
    div.stButton > button:hover { background-color: #00ff41; color: #000; box-shadow: 0 0 10px #00ff41; }
    h1, h2, h3 { color: #00ff41 !important; text-shadow: 0 0 5px #003300; }
    .stProgress > div > div > div > div { background-color: #00ff41; }
    /* 讓側邊欄看起來像電路板 */
    section[data-testid="stSidebar"] { background-color: #0b1016; border-right: 1px solid #333; }
</style>
""", unsafe_allow_html=True)

init_db()

# --- 3. 工具函式 ---
def render_logic_gate_svg(gate_type, val_a, val_b, output):
    # 這裡用程式碼畫 SVG，保證不破圖，且極度精細
    color = "#00ff41" if output else "#333"
    return f"""
    <svg width="200" height="100" viewBox="0 0 200 100">
        <line x1="10" y1="30" x2="50" y2="30" stroke="{'#00ff41' if val_a else '#555'}" stroke-width="3"/>
        <text x="0" y="35" fill="white" font-size="12">A={val_a}</text>
        <line x1="10" y1="70" x2="50" y2="70" stroke="{'#00ff41' if val_b else '#555'}" stroke-width="3"/>
        <text x="0" y="75" fill="white" font-size="12">B={val_b}</text>
        
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
            change = random.uniform(-0.03, 0.03) # 波動
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

# 🧠 功能 A: 邏輯設計實驗室 (Digital Logic)
def page_logic_lab(uid, user):
    st.title("🧠 邏輯設計實驗室 (Logic Design)")
    st.caption("課程目標：熟悉布林代數與邏輯閘 (Boolean Algebra)")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🛠️ 電路模擬區")
        gate_type = st.selectbox("選擇元件", ["AND (及)", "OR (或)", "XOR (互斥或)", "NAND (反及)"])
        
        # 讓使用者控制輸入電位
        input_a = st.toggle("Input A (High/Low)", value=True)
        input_b = st.toggle("Input B (High/Low)", value=False)
        
        # 邏輯運算
        a_val = 1 if input_a else 0
        b_val = 1 if input_b else 0
        
        if "AND" in gate_type: out = a_val & b_val
        elif "OR" in gate_type: out = a_val | b_val
        elif "XOR" in gate_type: out = a_val ^ b_val
        elif "NAND" in gate_type: out = not (a_val & b_val)
        
        st.markdown(render_logic_gate_svg(gate_type.split()[0], a_val, b_val, int(out)), unsafe_allow_html=True)

    with col2:
        st.subheader("📝 真值表測驗 (Truth Table)")
        st.write(f"題目：當 A=1, B=0 時，**{gate_type}** 的輸出為何？")
        ans = st.radio("你的答案", ["0 (Low)", "1 (High)"], key="logic_quiz")
        
        if st.button("提交驗證"):
            correct = "1" if out else "0"
            if ans.startswith(correct):
                st.success("Correct! 邏輯正確。")
                add_exp(uid, 10)
            else:
                st.error("Segmentation Fault. 答案錯誤。")

# ⚔️ 功能 B: 演算法競技場 (Data Structures & Algo)
def page_arena(uid, user):
    st.title("⚔️ 演算法競技場 (Algo-Arena)")
    st.caption("課程目標：時間複雜度 (Big O) 與程式效能分析")
    
    st.info("說明：選擇一段程式碼作為攻擊手段。執行速度越快 (Time Complexity 越低)，造成的傷害越高！")
    
    enemy_hp = st.session_state.get("enemy_hp", 100)
    st.progress(enemy_hp / 100, text=f"Bug Monster HP: {enemy_hp}")

    # 選擇武器 (其實是選擇排序法)
    weapon = st.selectbox("選擇演算法武器", 
        ["Bubble Sort (O(n^2)) - 攻擊力低", 
         "Python Built-in Sort (O(n log n)) - 攻擊力高",
         "NumPy Sort (C-Optimized) - 攻擊力極高"])

    if st.button("⚡ 編譯並執行 (Run Code)"):
        # 準備測試資料 (模擬大量運算)
        data = list(range(5000))
        random.shuffle(data)
        
        # 定義不同演算法
        if "Bubble" in weapon:
            # 故意縮小數據量以免卡死，模擬慢速
            setup_code = f"d = {data[:500]}"
            run_code = """
for i in range(len(d)):
    for j in range(0, len(d)-i-1):
        if d[j] > d[j+1]: d[j], d[j+1] = d[j+1], d[j]
"""
            base_dmg = 10
        elif "Built-in" in weapon:
            setup_code = f"d = {data}"
            run_code = "d.sort()"
            base_dmg = 50
        else: # NumPy 模擬
            setup_code = "import random; d = list(range(5000)); random.shuffle(d)"
            run_code = "sorted(d)" # 簡化模擬
            base_dmg = 80

        # 真實測量時間
        try:
            with st.spinner("CPU 運算中..."):
                t = timeit.timeit(stmt=run_code, setup=setup_code, number=5)
            
            st.code(f"Execution Time: {t:.5f} sec", language="bash")
            
            # 計算傷害
            final_dmg = base_dmg
            if t < 0.001: final_dmg *= 2 # 暴擊
            
            enemy_hp = max(0, enemy_hp - final_dmg)
            st.session_state.enemy_hp = enemy_hp
            
            st.success(f"造成 {final_dmg} 點物理傷害！(基於真實運算速度)")
            
            if enemy_hp == 0:
                st.balloons()
                st.write("🎉 Bug 已修復 (Enemy Defeated)！")
                user['money'] += 500
                add_exp(uid, 100)
                save_user(uid, user)
                st.session_state.enemy_hp = 100
                time.sleep(2)
                st.rerun()

        except Exception as e:
            st.error(f"Runtime Error: {e}")

# 🕵️ 功能 C: 訊號與系統 (Signals & Systems) - Hex 解碼
def page_signals(uid, user):
    st.title("📡 訊號攔截站 (Signal Processing)")
    st.caption("課程目標：資料編碼 (ASCII/Hex/Binary) 與訊號處理")
    
    if "signal_target" not in st.session_state:
        # 生成隨機 Hex 題目
        words = ["FPGA", "CMOS", "UART", "HDMI", "WIFI"]
        target = random.choice(words)
        st.session_state.signal_target = target
        st.session_state.signal_hex = target.encode().hex().upper()
        # 產生一點雜訊 (模擬真實訊號)
        st.session_state.signal_noise = [random.randint(0, 9) for _ in range(10)]

    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("接收到的原始波形 (Raw Signal)")
        # 畫一個簡單的波形圖模擬示波器
        fig = go.Figure(data=go.Scatter(y=st.session_state.signal_noise + [5,5,5] + st.session_state.signal_noise, mode='lines', line=dict(color='#00ff41')))
        fig.update_layout(height=200, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis_visible=False, yaxis_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("解調變後的 Hex 資料")
        st.code(f"0x{st.session_state.signal_hex}", language="c")
        
    with c2:
        st.write("請將 Hex 轉回 ASCII 文字：")
        ans = st.text_input("輸入解碼結果 (大寫)", key="hex_input")
        if st.button("送出 (Transmit)"):
            if ans == st.session_state.signal_target:
                st.success("訊號解析成功！訊號雜訊比 (SNR) 良好。")
                user['money'] += 300
                add_exp(uid, 50)
                save_user(uid, user)
                del st.session_state['signal_target'] # 重置
                time.sleep(1)
                st.rerun()
            else:
                st.error("解碼錯誤 (CRC Check Failed)。")

# 🏗️ 功能 D: 記憶體管理摩天樓 (Data Structures)
def page_memory(uid, user):
    st.title("🏗️ 記憶體堆疊 (Memory Stack)")
    st.caption("課程目標：了解 Array (陣列) 與 Linked List (鏈結串列) 的成本差異")
    
    if "mem_blocks" not in st.session_state: st.session_state.mem_blocks = []
    
    # 計算當前租金 (模擬記憶體回收效率)
    income = sum([b['value'] for b in st.session_state.mem_blocks])
    st.metric("Memory Yield (收益/週期)", f"${income}")
    
    c1, c2 = st.columns(2)
    with c1:
        st.info("🔹 Static Array (靜態陣列)")
        st.write("特性：存取快 O(1)，但建造成本高。")
        if st.button("Allocate Array ($500)"):
            if user['money'] >= 500:
                user['money'] -= 500
                st.session_state.mem_blocks.append({"type": "Array", "value": 50})
                save_user(uid, user); st.rerun()
    with c2:
        st.info("🔸 Linked List (鏈結串列)")
        st.write("特性：插入快 O(1)，建造成本低，收益較低。")
        if st.button("Insert Node ($200)"):
            if user['money'] >= 200:
                user['money'] -= 200
                st.session_state.mem_blocks.append({"type": "Node", "value": 20})
                save_user(uid, user); st.rerun()
                
    st.divider()
    # 視覺化記憶體區塊
    st.write("--- Heap Memory Visualization ---")
    cols = st.columns(10)
    for i, block in enumerate(st.session_state.mem_blocks[-20:]): # 只顯示最近20個
        color = "🟩" if block['type'] == "Array" else "🟧"
        cols[i % 10].write(f"{color} {block['type']}")

    if st.button("Garbage Collection (回收收益)"):
        user['money'] += income
        save_user(uid, user)
        st.toast(f"記憶體釋放完成，獲得 ${income}")

# --- 主儀表板與共用區 ---
def page_dashboard(uid, user):
    st.title(f"🖥️ System Status: {user['name']}")
    title_name = LEVEL_TITLES.get(min(user['level'], 5), "Unknown")
    st.caption(f"Class: {title_name} | ID: {uid}")
    
    update_stock_market()
    
    # K線圖 (用 Plotly 畫精細的圖)
    if not st.session_state.stock_history.empty:
        df = st.session_state.stock_history
        fig = go.Figure(data=go.Scatter(x=df['_time'], y=df['TSMC'], mode='lines+markers', line=dict(color='#00ff41')))
        fig.update_layout(title="TSMC Real-time Clock", height=300, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#00ff41'))
        st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Credits (Money)", f"${user['money']:,}")
    c2.metric("Stock Assets", f"${sum(user.get('stocks', {}).values()):,}")
    c3.metric("Academic Level", f"Lv.{user['level']}")
    
    st.subheader("🎒 Hardware Inventory")
    inv = user.get('inventory', {})
    if not inv: st.write("No hardware detected.")
    else:
        for k, v in inv.items(): st.write(f"- {k}: {v} units")

def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        st.title("⚡ EE_DEPT // LOGIN SYSTEM")
        c1, c2 = st.columns([1,2])
        with c1: st.image("https://placehold.co/200x200/000000/00ff41?text=EE", caption="Department of Electronic Engineering")
        with c2:
            u = st.text_input("Student ID (Admin: frank)")
            p = st.text_input
