# app.py
# 用途: 系統核心 UI 與業務邏輯 (支援新版題庫格式)

import streamlit as st
import random
import time
import pandas as pd
from datetime import datetime, date
import os 

# --- 引用自訂模組 ---
# 確保這些檔案存在於同目錄下
try:
    from config import ITEMS, STOCKS_DATA, CITY_EVENTS, SVG_LIB 
    from database import (init_db, get_user, save_user, create_user, check_mission, 
                          send_mail, get_all_users, get_global_stock_state, save_global_stock_state)
except ImportError:
    st.error("⚠️ 檔案遺失！請確保 app.py, config.py, database.py 都在同目錄下。")
    st.stop()

# --- [修改重點] 讀取題庫函數 (支援 5 欄位格式) ---
def load_quiz_from_file():
    questions = []
    default_q = [{"q": "系統提示: 請檢查 questions.txt", "options": ["好", "了解"], "ans": "好"}]
    file_path = "questions.txt"

    # 1. 檔案不存在時建立範例 (更新為新格式範例)
    if not os.path.exists(file_path):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("# ID|Level|題目|選項|答案\n")
                f.write("LOGIC-001|1|Python的作者是誰?|吉多,伊隆馬斯克,賈伯斯|吉多\n")
                f.write("LOGIC-002|1|CityOS的核心是什麼?|數據,金錢,控制|數據\n")
                f.write("LOGIC-003|2|輸入 A=1, B=1 , 經過 [NAND] 閘輸出？|0,1,Z,X|0\n")
            st.toast("⚠️ 已建立範例 questions.txt")
        except Exception as e:
            st.error(f"無法建立題庫檔案: {e}")
            return default_q

    # 2. 嘗試讀取檔案 (處理編碼)
    lines = []
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f: # 優先嘗試 utf-8-sig
            lines = f.readlines()
    except UnicodeDecodeError:
        try:
            with open(file_path, "r", encoding="cp950") as f: # 備用: big5/cp950
                lines = f.readlines()
        except:
            st.error("❌ 題庫編碼錯誤，請確保使用 UTF-8 存檔。")
            return default_q

    # 3. 解析每一行
    for line_num, line in enumerate(lines):
        line = line.strip()
        if not line or line.startswith("#"): continue
            
        parts = line.split("|")
        
        q_text = ""
        options = []
        ans = ""

        # --- [關鍵修改] 判斷格式 ---
        if len(parts) >= 5:
            # 新格式: ID | Level | 題目 | 選項 | 答案
            # 例如: LOGIC-31437|1|題目...|選項...|答案
            q_text = parts[2].strip()
            options = [o.strip() for o in parts[3].split(",")]
            ans = parts[4].strip()
        elif len(parts) == 3:
            # 舊格式相容: 題目 | 選項 | 答案
            q_text = parts[0].strip()
            options = [o.strip() for o in parts[1].split(",")]
            ans = parts[2].strip()
        else:
            # 格式不符跳過
            continue

        # 4. 資料驗證與防呆
        if not q_text or not options or not ans:
            continue

        # 確保答案在選項中
        if ans not in options:
            options.append(ans)
            random.shuffle(options)

        questions.append({"q": q_text, "options": options, "ans": ans})

    if not questions:
        st.warning("⚠️ 讀取不到題目，載入預設題。")
        return default_q

    return questions

# --- 頁面設定 ---
st.set_page_config(page_title="CityOS V32.1 Logic", layout="wide", page_icon="📟", initial_sidebar_state="expanded")

# --- CSS ---
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00ff41; }
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stButton button, input, textarea, .stSelectbox div, .stRadio div {
        font-family: 'Courier New', monospace !important;
        text-shadow: 0 0 2px rgba(0, 255, 65, 0.3);
    }
    .stButton > button {
        background-color: #000 !important; color: #00ff41 !important;
        border: 1px solid #00ff41 !important;
    }
    .stButton > button:hover { box-shadow: 0 0 15px #00ff41; background-color: #001a05 !important; }
    .stTextInput > div > div > input { background-color: #111 !important; color: #00ff41 !important; }
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #00ff41; }
</style>
""", unsafe_allow_html=True)

# --- 系統初始化 ---
init_db()

# --- 每日事件 ---
def get_today_event():
    seed = int(date.today().strftime("%Y%m%d"))
    random.seed(seed)
    evt = random.choice(CITY_EVENTS)
    random.seed()
    return evt

if "today_event" not in st.session_state:
    st.session_state.today_event = get_today_event()

# --- 🔥 核心股市邏輯 (多人同步版) ---
def update_stock_market():
    global_state = get_global_stock_state()
    if not global_state: return

    now = time.time()
    last_update = global_state.get("last_update", 0)
    
    # 若超過 5 秒沒更新，由當前使用者觸發更新
    if now - last_update > 5:
        evt = st.session_state.today_event
        new_prices = {}
        for code, data in STOCKS_DATA.items():
            prev = global_state["prices"].get(code, data["base"])
            vol = data["volatility"] * 2.0
            
            if evt["effect"] == "crash": change = random.uniform(-0.3, -0.05)
            elif evt["effect"] == "tech_boom" and code in ["CYBR", "AI"]: change = random.uniform(0.05, 0.2)
            else: change = random.uniform(-vol, vol)
            
            new_p = int(prev * (1 + change))
            new_p = max(5, min(3000, new_p))
            new_prices[code] = new_p
            
        global_state["prices"] = new_prices
        global_state["last_update"] = now
        
        hist_entry = new_prices.copy()
        hist_entry["_time"] = datetime.now().strftime("%H:%M:%S")
        global_state["history"].append(hist_entry)
        if len(global_state["history"]) > 30: global_state["history"].pop(0)
        
        save_global_stock_state(global_state)

    st.session_state.stock_prices = global_state["prices"]
    st.session_state.stock_history = pd.DataFrame(global_state["history"])

# --- 功能頁面 ---

def page_dashboard(uid, user):
    st.title("🏙️ DASHBOARD")
    evt = st.session_state.today_event
    st.info(f"📢 今日狀態: {evt['name']} | {evt['desc']}")
    
    update_stock_market()
    
    stock_val = sum([amt * st.session_state.stock_prices.get(c, 0) for c, amt in user.get('stocks',{}).items()])
    total = user['money'] + stock_val
    
    c1, c2, c3 = st.columns(3)
    c1.metric("總資產", f"${total:,}")
    c2.metric("現金", f"${user['money']:,}")
    c3.metric("股票市值", f"${stock_val:,}")
    
    if not st.session_state.stock_history.empty:
        st.subheader("📉 市場走勢")
        chart_data = st.session_state.stock_history.drop(columns=["_time"], errors="ignore")
        st.line_chart(chart_data, height=300)

def page_stock(uid, user):
    st.title("💹 證券交易所")
    update_stock_market()
    prices = st.session_state.stock_prices
    
    t1, t2 = st.tabs(["買入", "賣出"])
    with t1:
        code = st.selectbox("選擇股票", list(STOCKS_DATA.keys()))
        curr = prices.get(code, 0)
        st.metric(f"{STOCKS_DATA[code]['name']}", f"${curr}")
        qty = st.number_input("數量", 1, 1000, 10, key="buy_qty")
        cost = qty * curr
        if st.button(f"買進 (${cost:,})"):
            if user['money'] >= cost:
                user['money'] -= cost
                user.setdefault('stocks', {})[code] = user['stocks'].get(code, 0) + qty
                check_mission(uid, user, "stock_buy")
                save_user(uid, user)
                st.success("交易成功！"); time.sleep(0.5); st.rerun()
            else: st.error("資金不足")
    with t2:
        my_stocks = user.get('stocks', {})
        if my_stocks:
            s_code = st.selectbox("賣出股票", list(my_stocks.keys()))
            owned = my_stocks[s_code]
            curr = prices.get(s_code, 0)
            st.write(f"持有: {owned} | 現價: ${curr}")
            s_qty = st.number_input("賣出數量", 1, owned, 1, key="sell_qty")
            income = s_qty * curr
            if st.button(f"賣出 (獲利 ${income:,})"):
                user['stocks'][s_code] -= s_qty
                user['money'] += income
                if user['stocks'][s_code] == 0: del user['stocks'][s_code]
                save_user(uid, user)
                st.success("交易成功！"); time.sleep(0.5); st.rerun()
        else: st.info("無持倉股票")

def page_pvp(uid, user):
    st.title("⚔️ 網路攻防戰")
    last_hack = user.get("last_hack", 0)
    cooldown = 60
    remaining = int(cooldown - (time.time() - last_hack))
    
    if remaining > 0:
        st.warning(f"⚠️ 系統追蹤中，請等待冷卻: {remaining} 秒")
        return

    all_users = get_all_users()
    targets = [u for u in all_users.keys() if u != uid and u != "admin"]
    if not targets:
        st.info("無目標 IP。")
        return
        
    target_uid = st.selectbox("鎖定目標", targets)
    has_virus = user.get("inventory", {}).get("Trojan Virus", 0) > 0
    st.write(f"病毒狀態: {'✅ 就緒' if has_virus else '❌ 未持有'}")
    
    if st.button("🔴 EXECUTE", disabled=not has_virus):
        user["inventory"]["Trojan Virus"] -= 1
        if user["inventory"]["Trojan Virus"] <= 0: del user["inventory"]["Trojan Virus"]
        
        success_rate = 0.5
        if user.get("inventory", {}).get("Brute Force Script", 0) > 0: success_rate = 0.8
        
        if random.random() < success_rate:
            victim = get_user(target_uid)
            loot = random.randint(100, 500)
            if victim.get("inventory", {}).get("Firewall", 0) > 0:
                victim["inventory"]["Firewall"] -= 1
                if victim["inventory"]["Firewall"] <= 0: del victim["inventory"]["Firewall"]
                save_user(target_uid, victim)
                save_user(uid, user)
                st.error("攻擊被防火牆攔截！")
                send_mail(target_uid, "System", "🛡️ 防禦通知", f"{uid} 攻擊被你的防火牆擋下了。")
            else:
                actual_loot = min(victim['money'], loot)
                victim['money'] -= actual_loot
                user['money'] += actual_loot
                user['last_hack'] = time.time()
                save_user(target_uid, victim)
                save_user(uid, user)
                send_mail(target_uid, "System", "🚨 入侵警報", f"你遭到 {uid} 攻擊，損失 ${actual_loot}")
                st.balloons()
                st.success(f"攻擊成功！竊取 ${actual_loot}")
        else:
            penalty = 100
            user['money'] = max(0, user['money'] - penalty)
            user['last_hack'] = time.time()
            save_user(uid, user)
            st.error(f"攻擊失敗！反向追蹤罰款 ${penalty}")

def page_shop(uid, user):
    st.title("🛒 地下黑市")
    discount = 0.7 if st.session_state.today_event['effect'] == "shop_discount" else 1.0
    if discount < 1.0: st.success("🔥 特賣中！")
    
    cols = st.columns(3)
    for i, (k, v) in enumerate(ITEMS.items()):
        price = int(v['price'] * discount)
        with cols[i % 3].container(border=True):
            st.subheader(k)
            st.caption(v['desc'])
            st.write(f"**${price:,}**")
            if st.button("購買", key=f"buy_{i}"):
                if user['money'] >= price:
                    user['money'] -= price
                    user.setdefault("inventory", {})[k] = user.get("inventory", {}).get(k, 0) + 1
                    check_mission(uid, user, "shop_buy")
                    save_user(uid, user)
                    st.toast(f"已購買 {k}"); time.sleep(0.5); st.rerun()
                else: st.error("資金不足")

def page_quiz(uid, user):
    st.title("📝 知識庫測驗")
    
    with st.expander("⚙️ 題庫設定"):
        if st.button("🔄 重新載入題庫"):
            st.cache_data.clear()
            if "quiz_questions" in st.session_state: del st.session_state["quiz_questions"]
            st.session_state.q_idx = 0
            st.success("題庫已更新！"); time.sleep(0.5); st.rerun()

    if "quiz_questions" not in st.session_state or not st.session_state.quiz_questions:
        st.session_state.quiz_questions = load_quiz_from_file()
        st.session_state.q_idx = 0
        
    questions = st.session_state.quiz_questions
    if not questions: st.error("無題目"); return

    if st.session_state.q_idx >= len(questions): st.session_state.q_idx = 0

    current_q = questions[st.session_state.q_idx]
    
    st.progress((st.session_state.q_idx + 1) / len(questions), text=f"Q {st.session_state.q_idx + 1} / {len(questions)}")
    st.markdown(f"### ❓ {current_q['q']}")
    
    with st.form("quiz_form"):
        user_ans = st.radio("請選擇:", current_q['options'], key=f"q_{st.session_state.q_idx}")
        if st.form_submit_button("確認"):
            if user_ans == current_q['ans']:
                st.balloons()
                st.success("✅ 正確！ +$50")
                user['money'] += 50
                check_mission(uid, user, "quiz_done")
                save_user(uid, user)
                time.sleep(1.0)
                st.session_state.q_idx = (st.session_state.q_idx + 1) % len(questions)
                st.rerun()
            else:
                st.error(f"❌ 錯誤，答案是：{current_q['ans']}")
                time.sleep(1.5)
                st.session_state.q_idx = (st.session_state.q_idx + 1) % len(questions)
                st.rerun()

def page_cli(uid, user):
    st.title("💻 終端機")
    if "cli_log" not in st.session_state: st.session_state.cli_log = ["System connected..."]
    
    with st.container(height=300):
        for l in st.session_state.cli_log: st.text(l)
    
    cmd = st.chat_input(f"{uid}@cityos:~$")
    if cmd:
        st.session_state.cli_log.append(f"{uid}@cityos:~$ {cmd}")
        base = cmd.split()[0].lower()
        resp = "Unknown command."
        if base == "help": resp = "bal, whoami, clear, date, scan"
        elif base == "bal": resp = f"Cash: ${user['money']}"
        elif base == "whoami": resp = f"User: {user['name']}"
        elif base == "clear": st.session_state.cli_log = []; st.rerun()
        elif base == "date": resp = datetime.now().strftime("%Y-%m-%d")
        elif base == "scan": resp = f"Nodes found: {len(get_all_users())}"
        
        st.session_state.cli_log.append(resp)
        check_mission(uid, user, "cli_input")
        st.rerun()

def page_lab(uid, user):
    st.title("🔬 邏輯實驗室")
    gate = st.selectbox("Gate", list(SVG_LIB.keys()))
    c1, c2 = st.columns(2)
    i1 = c1.toggle("Input A")
    i2 = c2.toggle("Input B", disabled=(gate=="NOT"))
    
    st.markdown(SVG_LIB.get(gate, "SVG Error"), unsafe_allow_html=True)
    out = False
    if gate == "AND": out = i1 and i2
    elif gate == "OR": out = i1 or i2
    elif gate == "NOT": out = not i1
    elif gate == "XOR": out = i1 != i2
    st.metric("Output", "HIGH (1)" if out else "LOW (0)")

def page_missions(uid, user):
    st.title("🎯 任務中心")
    if user.get("pending_claims"):
        st.success("🎁 有獎勵可領取！")
        for i, m in enumerate(user["pending_claims"]):
            if st.button(f"領取 ${m['reward']}", key=f"c_{i}"):
                user['money'] += m['reward']
                user['pending_claims'].pop(i)
                save_user(uid, user)
                st.rerun()
    st.divider()
    for m in user.get('active_missions', []):
        st.write(f"- {m['title']}: {m['desc']} (${m['reward']})")

# --- 主程式 ---
def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        st.title("🏙️ CityOS Login")
        t1, t2 = st.tabs(["登入", "註冊"])
        with t1:
            u = st.text_input("帳號")
            p = st.text_input("密碼", type="password")
            if st.button("連線"):
                user_data = get_user(u)
                if user_data and user_data['password'] == p:
                    st.session_state.logged_in = True
                    st.session_state.uid = u
                    st.rerun()
                else: st.error("失敗")
        with t2:
            nu, np, nn = st.text_input("新帳號"), st.text_input("新密碼", type="password"), st.text_input("暱稱")
            if st.button("註冊"):
                if create_user(nu, np, nn): st.success("OK"); st.rerun()
                else: st.error("ID已存在")
        return

    uid = st.session_state.uid
    user = get_user(uid)
    
    with st.sidebar:
        st.title(f"👤 {user['name']}")
        st.caption(f"ID: {uid}")
        st.metric("資金", f"${user['money']:,}")
        nav = st.radio("導航", ["儀表板", "股市", "任務", "黑市", "PVP", "CLI", "邏輯實驗室", "測驗"])
        if st.button("登出"): st.session_state.logged_in = False; st.rerun()

    if nav == "儀表板": page_dashboard(uid, user)
    elif nav == "股市": page_stock(uid, user)
    elif nav == "任務": page_missions(uid, user)
    elif nav == "黑市": page_shop(uid, user)
    elif nav == "PVP": page_pvp(uid, user)
    elif nav == "CLI": page_cli(uid, user)
    elif nav == "邏輯實驗室": page_lab(uid, user)
    elif nav == "測驗": page_quiz(uid, user)

if __name__ == "__main__":
    main()
