import streamlit as st
import random
import time
import pandas as pd
import timeit
from datetime import datetime

# --- 匯入本地模組 (使用 config) ---
try:
    from config import ITEMS, STOCKS_DATA, LEVEL_TITLES
except ImportError:
    st.error("找不到 config.py！請確認第一步有建立檔案。")
    st.stop()

from database import (
    init_db, get_user, save_user, create_user, 
    get_global_stock_state, save_global_stock_state, 
    apply_environmental_hazard, add_exp, add_log, get_logs
)

# --- 初始化設定 ---
st.set_page_config(page_title="CityOS: LogiMind", layout="wide", page_icon="☣️")
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00ff41; font-family: 'Courier New', monospace; }
    div.stButton > button { background-color: #000; border: 1px solid #00ff41; color: #00ff41; }
    div.stButton > button:hover { background-color: #00ff41; color: #000; box-shadow: 0 0 15px #00ff41; }
    .stTextInput > div > div > input { color: #00ff41; background-color: #111; border-color: #333; }
    code { color: #e6db74; background-color: #222; }
    .stProgress > div > div > div > div { background-color: #00ff41; }
</style>
""", unsafe_allow_html=True)

init_db()

# --- 核心邏輯 ---
def update_stock_market():
    global_state = get_global_stock_state()
    now = time.time()
    if now - global_state.get("last_update", 0) > 3.0:
        new_prices = {}
        for code, data in STOCKS_DATA.items():
            prev = global_state["prices"].get(code, data["base"])
            change = random.uniform(-0.05, 0.05)
            new_prices[code] = max(1, int(prev * (1 + change)))
        
        global_state["prices"] = new_prices
        global_state["last_update"] = now
        hist = new_prices.copy()
        hist["_time"] = datetime.now().strftime("%H:%M:%S")
        global_state["history"].append(hist)
        if len(global_state["history"]) > 30: global_state["history"].pop(0)
        save_global_stock_state(global_state)
    st.session_state.stock_prices = global_state["prices"]
    st.session_state.stock_history = pd.DataFrame(global_state["history"])

def render_k_line(symbol):
    if "stock_history" not in st.session_state or st.session_state.stock_history.empty:
        st.write(">> 等待市場數據連線...")
        return
    df = st.session_state.stock_history
    if symbol in df.columns: st.line_chart(df[symbol])

# --- 遊戲頁面 ---

def page_arena(uid, user):
    st.title("⚔️ 演算法競技場")
    st.caption("目標：優化你的攻擊代碼 (Time Complexity)")
    enemy_hp = st.session_state.get("arena_hp", 100)
    st.progress(enemy_hp / 100, text=f"敵人 HP: {enemy_hp}")
    
    algo = st.selectbox("選擇武器 (演算法)", ["Bubble Sort (暴力攻擊)", "Python Timsort (精準打擊)"])
    
    if st.button("執行攻擊"):
        data = list(range(2000)); random.shuffle(data)
        if "Bubble" in algo:
            test_code = """
for i in range(len(d)):
    for j in range(0, len(d)-i-1):
        if d[j] > d[j+1]: d[j], d[j+1] = d[j+1], d[j]
"""
            setup = f"d = {data[:200]}"
            base_dmg = 10
        else:
            test_code = "d.sort()"
            setup = f"d = {data}"
            base_dmg = 40

        try:
            t = timeit.timeit(stmt=test_code, setup=setup, number=10)
            st.write(f"⏱️ 耗時: {t:.5f} 秒")
            final_dmg = base_dmg * (5 if "Cyber-Arm" in user.get('inventory', {}) else 1)
            enemy_hp = max(0, enemy_hp - final_dmg)
            st.session_state.arena_hp = enemy_hp
            
            if "Bubble" in algo: st.warning(f"攻擊效率低落... 造成 {final_dmg} 傷害")
            else: st.success(f"高效能攻擊！造成 {final_dmg} 傷害")
            
            if enemy_hp == 0:
                st.balloons()
                user['money'] += 500
                add_exp(uid, 50)
                save_user(uid, user)
                st.success("敵人殲滅！獲得 $500")
                st.session_state.arena_hp = 100
                time.sleep(2)
                st.rerun()
        except Exception as e: st.error(f"編譯錯誤: {e}")

def page_sniffer(uid, user):
    st.title("🕵️ 封包攔截站")
    st.write("任務：將 Hex (十六進位) 解碼為 ASCII 文字。")
    if "sniff_ans" not in st.session_state:
        words = ["SYSTEM", "LINUX", "PYTHON", "CYBER", "FRANK"]
        target = random.choice(words)
        st.session_state.sniff_ans = target
        st.session_state.sniff_hex = target.encode().hex().upper()
    
    st.code(f"Intercepted: {st.session_state.sniff_hex}")
    ans = st.text_input("輸入解碼結果 (大寫):")
    if st.button("解密"):
        if ans == st.session_state.sniff_ans:
            st.success("解密成功！"); user['money'] += 200; add_exp(uid, 20); save_user(uid, user); del st.session_state['sniff_ans']; time.sleep(1); st.rerun()
        else: st.error("密鑰錯誤！")

def page_tower(uid, user):
    st.title("🏗️ 資料結構摩天樓")
    if "tower" not in st.session_state: st.session_state.tower = []
    rent = sum([f['rent'] for f in st.session_state.tower])
    st.metric("當前租金收益", f"${rent}/輪")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("建造 Array 層 ($500)"):
            if user['money'] >= 500: user['money'] -= 500; st.session_state.tower.append({"type": "Array", "rent": 50}); save_user(uid, user); st.rerun()
    with c2:
        if st.button("收取租金"): user['money'] += rent; save_user(uid, user); st.success(f"收到 ${rent}"); st.rerun()
    for i, f in enumerate(reversed(st.session_state.tower)):
        st.info(f"{len(st.session_state.tower)-i}F [{f['type']}] - Rent: ${f['rent']}")

def page_dashboard(uid, user):
    st.title(f"🏙️ {user['name']}")
    title_name = LEVEL_TITLES.get(min(user['level'], 5), "Unknown")
    st.caption(f"身份: {title_name} | ID: {uid}")
    if apply_environmental_hazard(uid, user): st.toast("警告：輻射外洩！", icon="☢️")
    update_stock_market()
    stock_val = sum([amt * st.session_state.stock_prices.get(c, 0) for c, amt in user.get('stocks',{}).items()])
    c1, c2, c3 = st.columns(3)
    c1.metric("現金", f"${user['money']:,}"); c2.metric("股票資產", f"${stock_val:,}"); c3.metric("等級", f"Lv.{user['level']}")
    st.divider(); st.write("📡 系統日誌"); 
    for l in get_logs()[:5]: st.text(l)

def page_stock(uid, user):
    st.title("📉 紐約證交所"); update_stock_market()
    c1, c2 = st.columns([2, 1])
    with c1: sel = st.selectbox("股票", list(STOCKS_DATA.keys())); render_k_line(sel)
    with c2:
        curr = st.session_state.stock_prices.get(sel, 0); st.metric("現價", f"${curr}")
        own = user.get('stocks', {}).get(sel, 0); st.write(f"持有: {own}")
        amt = st.number_input("數量", 1, 1000, 10)
        if st.button("買進"):
            cost = curr * amt
            if user['money'] >= cost: user['money'] -= cost; user.setdefault('stocks', {})[sel] = user['stocks'].get(sel, 0) + amt; save_user(uid, user); st.success("成交"); st.rerun()
        if st.button("賣出"):
            if own >= amt: user['money'] += curr * amt; user['stocks'][sel] -= amt; save_user(uid, user); st.success("成交"); st.rerun()

def page_shop(uid, user):
    st.title("🛒 地下黑市")
    for name, info in ITEMS.items():
        c1, c2 = st.columns([3,1])
        c1.write(f"**{name}** (${info['price']})"); c1.caption(info['desc'])
        if c2.button(f"購買 {name}"):
            if user['money'] >= info['price']: user['money'] -= info['price']; user.setdefault('inventory', {})[name] = user['inventory'].get(name, 0) + 1; save_user(uid, user); st.success("成功"); st.rerun()
            else: st.error("資金不足")

def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    if not st.session_state.logged_in:
        st.title("CITY_OS // LOGIN"); u = st.text_input("ID"); p = st.text_input("Password", type="password")
        if st.button("Connect"):
            user = get_user(u)
            if user and user['password'] == p: st.session_state.logged_in = True; st.session_state.uid = u; st.rerun()
            else: st.error("Access Denied")
        return

    uid = st.session_state.uid; user = get_user(uid)
    if not user: st.session_state.logged_in = False; st.rerun()

    with st.sidebar:
        st.header("⚡ LOGIMIND"); st.write(f"User: {user['name']}")
        with st.expander("🎒 背包"):
            for k, v in user.get('inventory', {}).items(): st.write(f"{k} x{v}")
        nav = st.radio("導航", ["📊 儀表板", "📉 交易所", "🛒 黑市", "⚔️ 競技場", "🕵️ 攔截站", "🏗️ 摩天樓"])
        if st.button("登出"): st.session_state.logged_in = False; st.rerun()

    if nav == "📊 儀表板": page_dashboard(uid, user)
    elif nav == "📉 交易所": page_stock(uid, user)
    elif nav == "🛒 黑市": page_shop(uid, user)
    elif nav == "⚔️ 競技場": page_arena(uid, user)
    elif nav == "🕵️ 攔截站": page_sniffer(uid, user)
    elif nav == "🏗️ 摩天樓": page_tower(uid, user)

if __name__ == "__main__":
    main()
