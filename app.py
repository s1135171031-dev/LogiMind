import streamlit as st
import random
import time
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import timeit # 用於演算法競技場計時

# --- 核心連結 ---
from database import (
    init_db, get_user, save_user, create_user, 
    get_global_stock_state, save_global_stock_state, 
    apply_environmental_hazard, add_exp, add_log, get_logs
)

# --- 資料設定 ---
ITEMS = {
    "Nutri-Paste": {"price": 50, "desc": "噁心的營養膏 (飽食度+10)"},
    "Stim-Pack": {"price": 150, "desc": "興奮劑 (短暫提升能力)"},
    "Cyber-Arm": {"price": 2000, "desc": "軍用義肢 (挖礦/戰鬥效率 UP)"},
    "Trojan Virus": {"price": 300, "desc": "木馬程式 (PVP/攔截專用)"},
    "Anti-Rad Pill": {"price": 500, "desc": "抗輻射藥丸 (清除毒素)"}
}
STOCKS_DATA = {"NVID": {"base": 800}, "TSMC": {"base": 600}, "BTC": {"base": 30000}}

# SVG 素材
SVG_LIB = {
    "AND": '<svg viewBox="0 0 60 40" width="100"><path d="M10,5 L30,5 C45,5 45,35 30,35 L10,35 Z" fill="none" stroke="#00ff41" stroke-width="2"/><path d="M0,10 L10,10 M0,30 L10,30 M45,20 L60,20" stroke="#00ff41" stroke-width="2"/></svg>',
    "OR": '<svg viewBox="0 0 60 40" width="100"><path d="M10,5 C10,5 20,20 10,35 C25,35 50,25 50,20 C50,15 25,5 10,5" fill="none" stroke="#00ff41" stroke-width="2"/><path d="M0,10 L15,10 M0,30 L15,30 M50,20 L60,20" stroke="#00ff41" stroke-width="2"/></svg>',
    "NOT": '<svg viewBox="0 0 60 40" width="100"><path d="M10,5 L40,20 L10,35 Z" fill="none" stroke="#00ff41" stroke-width="2"/><circle cx="45" cy="20" r="3" stroke="#00ff41" stroke-width="2" fill="none"/><path d="M0,20 L10,20 M48,20 L60,20" stroke="#00ff41" stroke-width="2"/></svg>'
}

# --- 初始化與樣式 ---
st.set_page_config(page_title="CityOS: ALL IN", layout="wide", page_icon="☣️")
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00ff41; font-family: 'Courier New', monospace; }
    div.stButton > button { background-color: #000; border: 1px solid #00ff41; color: #00ff41; }
    div.stButton > button:hover { background-color: #00ff41; color: #000; box-shadow: 0 0 15px #00ff41; }
    .stTextInput > div > div > input { color: #00ff41; background-color: #111; border-color: #333; }
    code { color: #e6db74; background-color: #222; }
    h1, h2, h3 { color: #00ff41 !important; text-shadow: 0 0 5px #003300; }
    .stProgress > div > div > div > div { background-color: #00ff41; }
</style>
""", unsafe_allow_html=True)

init_db()

# --- 共用邏輯 ---
def update_stock_market():
    global_state = get_global_stock_state()
    now = time.time()
    if now - global_state.get("last_update", 0) > 2.0:
        new_prices = {}
        for code, data in STOCKS_DATA.items():
            prev = global_state["prices"].get(code, data["base"])
            change = random.uniform(-0.05, 0.05)
            new_prices[code] = max(1, int(prev * (1 + change)))
        global_state["prices"] = new_prices; global_state["last_update"] = now
        hist = new_prices.copy(); hist["_time"] = datetime.now().strftime("%H:%M:%S")
        global_state["history"].append(hist)
        if len(global_state["history"]) > 50: global_state["history"].pop(0)
        save_global_stock_state(global_state)
    st.session_state.stock_prices = global_state["prices"]
    st.session_state.stock_history = pd.DataFrame(global_state["history"])

def render_k_line(symbol):
    if "stock_history" not in st.session_state or st.session_state.stock_history.empty:
        st.write("等待數據..."); return
    df = st.session_state.stock_history
    if symbol in df.columns: st.line_chart(df[symbol])

# ================= 新功能區 =================

# 🆕 功能 1: 演算法競技場 (學習: 時間複雜度)
def page_arena(uid, user):
    st.title("⚔️ 演算法競技場 (Algo-Arena)")
    st.caption("學習點：程式執行速度 (Time Complexity) 決定你的戰鬥力。")
    
    st.write("你的數位鬥士準備出擊。選擇一種「排序演算法」作為武器。程式碼跑得越快，攻擊速度越快！")
    
    # 模擬敵人
    enemy_hp = st.session_state.get("arena_enemy_hp", 100)
    st.metric("🤖 敵人 (Rouge AI) HP", f"{enemy_hp}/100")
    st.progress(enemy_hp / 100)

    algo_choice = st.selectbox("選擇演算法武器", ["Bubble Sort (泡沫排序 - 慢)", "Python Built-in Sort (內建排序 - 快)"])
    
    # 準備測試資料 (亂數陣列)
    test_data = list(range(1000))
    random.shuffle(test_data)
    
    if st.button("⚔️ 發動攻擊"):
        with st.spinner("正在編譯演算法並執行..."):
            # 1. 定義要測試的程式碼
            if "Bubble" in algo_choice:
                # 故意寫一個慢的泡沫排序
                code_to_test = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
bubble_sort(data_copy)
"""
                base_dmg = random.randint(5, 15)
            else:
                # 使用 Python 超快的內建 Timsort
                code_to_test = "data_copy.sort()"
                base_dmg = random.randint(20, 40)

            # 2. 測量執行時間
            setup_code = f"import random; data_copy = {test_data}.copy()"
            try:
                # 執行 10 次取平均時間
                exec_time = timeit.timeit(stmt=code_to_test, setup=setup_code, number=10)
                st.write(f"⚡ 演算法執行耗時: {exec_time:.6f} 秒 (10次平均)")

                # 3. 計算傷害 (裝備加成)
                bonus = 2 if "Cyber-Arm" in user.get('inventory', {}) else 1
                final_dmg = base_dmg * bonus
                
                # 4. 結算
                enemy_hp = max(0, enemy_hp - final_dmg)
                st.session_state.arena_enemy_hp = enemy_hp
                
                if "Bubble" in algo_choice:
                    st.warning(f"攻擊緩慢！造成 {final_dmg} 點傷害。(效率低落 O(n^2))")
                else:
                    st.success(f"極速攻擊！造成 {final_dmg} 點傷害。(效率極高 O(n log n))")
                
                if enemy_hp == 0:
                    reward = random.randint(100, 300)
                    user['money'] += reward
                    add_exp(uid, 50)
                    save_user(uid, user)
                    st.balloons()
                    st.success(f"敵人已殲滅！獲得獎金 ${reward}！")
                    st.session_state.arena_enemy_hp = 100 # 重置敵人
                    time.sleep(2)
                    st.rerun()

            except Exception as e:
                st.error(f"演算法執行錯誤: {e}")

# 🆕 功能 2: 封包攔截站 (學習: Hex/ASCII 編碼)
def page_sniffer(uid, user):
    st.title("🕵️ 封包攔截站 (Packet Sniffer)")
    st.caption("學習點：十六進位 (Hex) 與 ASCII 編碼轉換。")

    if "sniffer_puzzle" not in st.session_state:
        # 生成一個隨機單字並轉成 Hex
        words = ["CITY", "HACK", "DATA", "CORE", "NEON", "BYTE"]
        target = random.choice(words)
        hex_puzzle = target.encode('utf-8').hex().upper()
        st.session_state.sniffer_target = target
        st.session_state.sniffer_hex = hex_puzzle
    
    st.write("你攔截到一段加密的網路封包。它看起來是十六進位 (Hex) 編碼。")
    st.write("請將其解碼為原本的 ASCII 文字以獲取內容。")
    
    st.markdown(f"""
    <div style="background:#111; padding:20px; border:1px dashed #00ff41; font-family:monospace; font-size:24px; text-align:center;">
    Intercepted Data: <span style="color:#ff00ff;">{st.session_state.sniffer_hex}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("提示：每兩個 Hex 數字代表一個字母。例如 '41' = 'A', '42' = 'B'。")

    answer = st.text_input("輸入解碼後的文字 (大寫):")
    
    if st.button("🚀 嘗試解碼"):
        if answer.upper() == st.session_state.sniffer_target:
            reward = random.randint(50, 150)
            user['money'] += reward
            add_exp(uid, 30)
            save_user(uid, user)
            st.balloons()
            st.success(f"解碼成功！獲得情資獎金 ${reward}！")
            # 清除題目以產生新的
            del st.session_state["sniffer_puzzle"]
            time.sleep(1)
            st.rerun()
        else:
            st.error("解碼失敗。封包已銷毀。")
            del st.session_state["sniffer_puzzle"]
            st.rerun()

# 🆕 功能 3: 資料結構摩天樓 (學習: 陣列 vs 鏈結串列)
def page_tower(uid, user):
    st.title("🏗️ 資料結構摩天樓 (Structure Tower)")
    st.caption("學習點：不同資料結構的特性 (Array vs Linked List)。")
    
    if "tower_floors" not in st.session_state: st.session_state.tower_floors = []
    if "tower_income" not in st.session_state: st.session_state.tower_income = 0

    # 計算收入
    total_rent = sum([f["rent"] for f in st.session_state.tower_floors])
    st.session_state.tower_income += total_rent
    
    c1, c2 = st.columns(2)
    c1.metric("目前樓層數", len(st.session_state.tower_floors))
    c2.metric("累積租金收益", f"${st.session_state.tower_income}")
    
    st.divider()
    st.subheader("建造新樓層 (選擇地基)")

    col_arr, col_link = st.columns(2)
    with col_arr:
        st.info("【陣列 (Array) 地基】")
        st.write("- 特性：結構緊密，讀取快，但擴建時需要搬移整個結構。")
        st.write("- 成本：$500 | 租金：$50/次")
        if st.button("建造 (Array)"):
            if user['money'] >= 500:
                user['money'] -= 500
                st.session_state.tower_floors.append({"type": "Array", "rent": 50})
                save_user(uid, user)
                st.success("建造完成！")
                st.rerun()
            else: st.error("沒錢")

    with col_link:
        st.info("【鏈結串列 (Linked List) 地基】")
        st.write("- 特性：結構鬆散，擴建容易，但讀取時要一層層找。")
        st.write("- 成本：$200 | 租金：$20/次")
        if st.button("建造 (Linked)"):
            if user['money'] >= 200:
                user['money'] -= 200
                st.session_state.tower_floors.append({"type": "Linked", "rent": 20})
                save_user(uid, user)
                st.success("建造完成！")
                st.rerun()
            else: st.error("沒錢")
            
    st.divider()
    if st.button("💰 收取累積租金"):
        if st.session_state.tower_income > 0:
            user['money'] += st.session_state.tower_income
            st.session_state.tower_income = 0
            save_user(uid, user)
            st.success("租金已入帳！")
            st.rerun()
        else: st.warning("還沒有租金可收。")

    # 顯示大樓結構
    st.write("--- 大樓結構圖 ---")
    for i, floor in enumerate(reversed(st.session_state.tower_floors)):
        color = "#00ff41" if floor["type"] == "Array" else "#ff00ff"
        st.markdown(f"<div style='border:2px solid {color}; margin:2px; padding:5px; text-align:center;'>{len(st.session_state.tower_floors)-i}F [{floor['type']}]</div>", unsafe_allow_html=True)

# --- 舊功能保留區 ---
def page_dashboard(uid, user):
    st.title(f"🏙️ 儀表板: {user['name']}")
    if apply_environmental_hazard(uid, user): st.toast("警告：環境輻射傷害！", icon="☢️")
    update_stock_market()
    stock_val = sum([amt * st.session_state.stock_prices.get(c, 0) for c, amt in user.get('stocks',{}).items()])
    c1, c2, c3 = st.columns(3)
    c1.metric("現金", f"${user['money']:,}"); c2.metric("股票", f"${stock_val:,}"); c3.metric("等級", f"Lv.{user['level']}")
    st.divider(); st.subheader("📡 廣播"); 
    for log in get_logs()[:5]: st.text(log)

def page_stock(uid, user):
    st.title("📉 交易所"); update_stock_market()
    c1, c2 = st.columns([2, 1])
    with c1: sel = st.selectbox("代碼", list(STOCKS_DATA.keys())); render_k_line(sel)
    with c2:
        curr = st.session_state.stock_prices.get(sel, 0); st.metric(f"{sel} 價格", f"${curr}")
        own = user.get('stocks', {}).get(sel, 0); st.write(f"持有: {own}")
        amt = st.number_input("數量", 1, 1000, 10)
        if st.button("買進"):
            cost = curr * amt
            if user['money'] >= cost: user['money'] -= cost; user.setdefault('stocks', {})[sel] = user['stocks'].get(sel, 0) + amt; save_user(uid, user); add_log(f"💰 {user['name']} 買入 {sel}"); st.success("成功"); st.rerun()
            else: st.error("沒錢")
        if st.button("賣出"):
            if own >= amt: gain = curr * amt; user['money'] += gain; user['stocks'][sel] -= amt; save_user(uid, user); add_log(f"💸 {user['name']} 賣出 {sel}"); st.success("成功"); st.rerun()
            else: st.error("不足")

def page_mining(uid, user):
    st.title("⛏️ 礦場"); st.write("點擊挖掘加密數據...")
    eff = 5 if "Cyber-Arm" in user.get('inventory', {}) else 1
    if "Cyber-Arm" in user.get('inventory', {}): st.info("⚡ Cyber-Arm 效率加成啟動")
    if st.button("⛏️ 挖掘"):
        with st.spinner("..."): time.sleep(0.5); rew = random.randint(10, 50) * eff; user['money'] += rew; add_exp(uid, 5); save_user(uid, user); st.success(f"獲得 ${rew}"); st.rerun()

def page_shop(uid, user):
    st.title("🛒 黑市"); 
    for k, v in ITEMS.items():
        c1, c2 = st.columns([3, 1]); c1.write(f"**{k}** (${v['price']}) - {v['desc']}")
        if c2.button(f"購買 {k}"):
            if user['money']>=v['price']: user['money']-=v['price']; user.setdefault('inventory',{})[k]=user['inventory'].get(k,0)+1; save_user(uid, user); st.success("已購"); st.rerun()
            else: st.error("窮")

def page_linux(uid, user):
    st.title("🐧 終端機"); st.code("root@cityos:~#"); cmd = st.text_input("指令")
    if st.button("執行"): st.write(f"Executing: {cmd}...\nAccess Denied.")

def page_lab(uid, user):
    st.title("🔌 實驗室"); g = st.selectbox("閘", list(SVG_LIB.keys())); st.markdown(SVG_LIB[g], unsafe_allow_html=True)

# --- 主程式 ---
def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    if not st.session_state.logged_in:
        st.title("CITY_OS // LOGIN"); u = st.text_input("ID"); p = st.text_input("PW", type="password")
        if st.button("連線"):
            ud = get_user(u)
            if ud and ud['password'] == p: st.session_state.logged_in = True; st.session_state.uid = u; st.rerun()
            else: st.error("錯誤")
        return

    uid = st.session_state.uid; user = get_user(uid)
    if not user: st.session_state.logged_in = False; st.rerun()

    with st.sidebar:
        # 這裡修復了破圖，改用 Emoji 和文字
        st.markdown("# ⚡ CITY_OS") 
        st.markdown(f"**用戶:** {user['name']}")
        st.progress(user['exp'] / (user['level']*100), text=f"EXP: {user['exp']}/{user['level']*100}")
        st.divider()
        
        # 新舊功能整合的導航列
        nav = st.radio("導航模組", 
            ["📊 儀表板", "📉 交易所", "⛏️ 礦場", "🛒 黑市", "🐧 終端機", "🔌 實驗室", 
             "⚔️ 演算法競技場 (NEW!)", "🕵️ 封包攔截站 (NEW!)", "🏗️ 資料結構塔 (NEW!)"]
        )
        
        st.divider(); st.write("🎒 背包:"); st.write(user.get('inventory', {}))
        if st.button("登出"): st.session_state.logged_in = False; st.rerun()

    if nav == "📊 儀表板": page_dashboard(uid, user)
    elif nav == "📉 交易所": page_stock(uid, user)
    elif nav == "⛏️ 礦場": page_mining(uid, user)
    elif nav == "🛒 黑市": page_shop(uid, user)
    elif nav == "🐧 終端機": page_linux(uid, user)
    elif nav == "🔌 實驗室": page_lab(uid, user)
    # 新功能路由
    elif nav == "⚔️ 演算法競技場 (NEW!)": page_arena(uid, user)
    elif nav == "🕵️ 封包攔截站 (NEW!)": page_sniffer(uid, user)
    elif nav == "🏗️ 資料結構塔 (NEW!)": page_tower(uid, user)

if __name__ == "__main__":
    main()
