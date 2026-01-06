# app.py
# 用途: 系統核心 (Toxic UI + Job System + 5-Col Quiz)

import streamlit as st
import random
import time
import pandas as pd
from datetime import datetime, date
import os 

try:
    from config import ITEMS, STOCKS_DATA, CITY_EVENTS, SVG_LIB 
    from database import (init_db, get_user, save_user, create_user, check_mission, 
                          send_mail, get_all_users, get_global_stock_state, save_global_stock_state)
except ImportError:
    st.error("⚠️ 檔案遺失！請確保 app.py, config.py, database.py 都在同目錄下。")
    st.stop()

# --- 讀取題庫 (支援 ID|Level|Q|Opts|Ans 格式) ---
def load_quiz_from_file():
    questions = []
    default_q = [{"q": "系統錯誤: 題庫損毀", "options": ["...", "???"], "ans": "..."}]
    file_path = "questions.txt"

    if not os.path.exists(file_path):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("# ID|Level|題目|選項|答案\n")
                f.write("LOGIC-001|1|Python的作者是誰?|吉多,伊隆馬斯克,賈伯斯|吉多\n")
                f.write("LOGIC-002|1|CityOS的核心是什麼?|數據,金錢,控制|數據\n")
        except: return default_q

    lines = []
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f: lines = f.readlines()
    except:
        try:
            with open(file_path, "r", encoding="cp950") as f: lines = f.readlines()
        except: return default_q

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"): continue
        parts = line.split("|")
        
        q_text, options, ans = "", [], ""
        if len(parts) >= 5:
            q_text, options, ans = parts[2].strip(), [o.strip() for o in parts[3].split(",")], parts[4].strip()
        elif len(parts) == 3:
            q_text, options, ans = parts[0].strip(), [o.strip() for o in parts[1].split(",")], parts[2].strip()
        else: continue

        if not q_text or not options or not ans: continue
        if ans not in options: options.append(ans); random.shuffle(options)
        questions.append({"q": q_text, "options": options, "ans": ans})

    return questions if questions else default_q

# --- 頁面設定 ---
st.set_page_config(page_title="CityOS V32.1 Toxic", layout="wide", page_icon="☣️", initial_sidebar_state="expanded")

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

init_db()

def get_today_event():
    seed = int(date.today().strftime("%Y%m%d"))
    random.seed(seed)
    evt = random.choice(CITY_EVENTS)
    random.seed()
    return evt

if "today_event" not in st.session_state:
    st.session_state.today_event = get_today_event()

def update_stock_market():
    global_state = get_global_stock_state()
    if not global_state: return

    now = time.time()
    last_update = global_state.get("last_update", 0)
    
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
    c1.metric("你的身價 (低得可憐)", f"${total:,}")
    c2.metric("現金 (快花光了)", f"${user['money']:,}")
    c3.metric("股票 (廢紙堆)", f"${stock_val:,}")
    
    if not st.session_state.stock_history.empty:
        st.subheader("📉 資本家收割曲線 (Global)")
        chart_data = st.session_state.stock_history.drop(columns=["_time"], errors="ignore")
        st.line_chart(chart_data, height=300)

def page_stock(uid, user):
    st.title("💹 韭菜交易所")
    update_stock_market()
    prices = st.session_state.stock_prices
    
    t1, t2 = st.tabs(["繳智商稅 (買)", "認賠殺出 (賣)"])
    with t1:
        code = st.selectbox("選擇哪支垃圾股", list(STOCKS_DATA.keys()))
        curr = prices.get(code, 0)
        st.metric(f"{STOCKS_DATA[code]['name']}", f"${curr}")
        qty = st.number_input("數量", 1, 1000, 10, key="buy_qty")
        cost = qty * curr
        if st.button(f"買進 (浪費 ${cost:,})"):
            if user['money'] >= cost:
                user['money'] -= cost
                user.setdefault('stocks', {})[code] = user['stocks'].get(code, 0) + qty
                check_mission(uid, user, "stock_buy")
                save_user(uid, user)
                st.success("交易成功。你現在更窮了，但擁有了夢想。"); time.sleep(0.5); st.rerun()
            else: st.error("沒錢還想玩股票？滾去打工。")
    with t2:
        my_stocks = user.get('stocks', {})
        if my_stocks:
            s_code = st.selectbox("賣出", list(my_stocks.keys()))
            owned = my_stocks[s_code]
            curr = prices.get(s_code, 0)
            st.write(f"持有: {owned} | 現價: ${curr}")
            s_qty = st.number_input("賣出數量", 1, owned, 1, key="sell_qty")
            income = s_qty * curr
            if st.button(f"賣出 (回收 ${income:,})"):
                user['stocks'][s_code] -= s_qty
                user['money'] += income
                if user['stocks'][s_code] == 0: del user['stocks'][s_code]
                save_user(uid, user)
                st.success("賣掉了。希望你沒虧太多。"); time.sleep(0.5); st.rerun()
        else: st.info("你沒有股票。就像你沒有未來一樣。")

def page_pvp(uid, user):
    st.title("⚔️ 互害社會 (PVP)")
    last_hack = user.get("last_hack", 0)
    cooldown = 60
    remaining = int(cooldown - (time.time() - last_hack))
    
    if remaining > 0:
        st.warning(f"⚠️ 網警正在盯著你，冷卻中: {remaining} 秒")
        return

    all_users = get_all_users()
    targets = [u for u in all_users.keys() if u != uid and u != "admin"]
    if not targets:
        st.info("這附近沒人。你是孤獨的。")
        return
        
    target_uid = st.selectbox("選擇受害者", targets)
    has_virus = user.get("inventory", {}).get("Trojan Virus", 0) > 0
    st.write(f"作案工具: {'✅ 病毒就緒' if has_virus else '❌ 兩手空空'}")
    
    if st.button("🔴 執行攻擊 (EXECUTE)", disabled=not has_virus):
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
                st.error("對面有防火牆！你的病毒像傻瓜一樣被擋在外面。")
                send_mail(target_uid, "System", "嘲諷通知", f"{uid} 想攻擊你，但撞到了你的防火牆。真丟臉。")
            else:
                actual_loot = min(victim['money'], loot)
                victim['money'] -= actual_loot
                user['money'] += actual_loot
                user['last_hack'] = time.time()
                save_user(target_uid, victim)
                save_user(uid, user)
                send_mail(target_uid, "System", "悲慘通知", f"你的錢被 {uid} 偷走了 ${actual_loot}。報警也沒用。")
                st.balloons()
                st.success(f"哈哈！你搶走了 ${actual_loot}。這種快感無可取代。")
        else:
            penalty = 100
            user['money'] = max(0, user['money'] - penalty)
            user['last_hack'] = time.time()
            save_user(uid, user)
            st.error(f"手滑了！攻擊失敗，反被追蹤罰款 ${penalty}。真笨。")

def page_shop(uid, user):
    st.title("🛒 詐騙黑市")
    discount = 0.7 if st.session_state.today_event['effect'] == "shop_discount" else 1.0
    
    cols = st.columns(3)
    for i, (k, v) in enumerate(ITEMS.items()):
        price = int(v['price'] * discount)
        with cols[i % 3].container(border=True):
            st.subheader(k)
            st.caption(v['desc'])
            st.write(f"**${price:,}**")
            if st.button("買這個廢物", key=f"buy_{i}"):
                if user['money'] >= price:
                    user['money'] -= price
                    user.setdefault("inventory", {})[k] = user.get("inventory", {}).get(k, 0) + 1
                    check_mission(uid, user, "shop_buy")
                    save_user(uid, user)
                    st.toast(f"恭喜，你浪費了錢買了 {k}"); time.sleep(0.5); st.rerun()
                else: st.error("餘額不足。窮鬼。")

def page_quiz(uid, user):
    st.title("📝 智力測驗 (賺取微薄薪水)")
    
    with st.expander("⚙️ 題庫"):
        if st.button("🔄 重新載入"):
            st.cache_data.clear()
            if "quiz_questions" in st.session_state: del st.session_state["quiz_questions"]
            st.session_state.q_idx = 0
            st.rerun()

    if "quiz_questions" not in st.session_state or not st.session_state.quiz_questions:
        st.session_state.quiz_questions = load_quiz_from_file()
        st.session_state.q_idx = 0
        
    questions = st.session_state.quiz_questions
    if not questions: st.error("沒題目"); return

    if st.session_state.q_idx >= len(questions): st.session_state.q_idx = 0
    current_q = questions[st.session_state.q_idx]
    
    st.progress((st.session_state.q_idx + 1) / len(questions), text=f"Q {st.session_state.q_idx + 1}")
    st.markdown(f"### ❓ {current_q['q']}")
    
    with st.form("quiz_form"):
        user_ans = st.radio("選一個吧:", current_q['options'], key=f"q_{st.session_state.q_idx}")
        if st.form_submit_button("送出"):
            # 獎勵強制設定為 50
            reward = 50
            if user_ans == current_q['ans']:
                st.balloons()
                st.success(f"竟然對了？ 獲得微薄的 +${reward}")
                user['money'] += reward
                check_mission(uid, user, "quiz_done")
                save_user(uid, user)
                time.sleep(1.0)
                st.session_state.q_idx = (st.session_state.q_idx + 1) % len(questions)
                st.rerun()
            else:
                st.error(f"錯得離譜。正確答案是：{current_q['ans']}")
                time.sleep(1.5)
                st.session_state.q_idx = (st.session_state.q_idx + 1) % len(questions)
                st.rerun()

def page_cli(uid, user):
    st.title("💻 沒禮貌的終端機")
    if "cli_log" not in st.session_state: st.session_state.cli_log = ["System connected... Waiting for input..."]
    
    with st.container(height=300):
        for l in st.session_state.cli_log: st.text(l)
    
    cmd = st.chat_input(f"{uid}@cityos:~$")
    if cmd:
        st.session_state.cli_log.append(f"{uid}@cityos:~$ {cmd}")
        base = cmd.split()[0].lower()
        resp = ""
        
        # 毒舌回應邏輯
        if base == "help": 
            resp = "不會用嗎？真沒用。試試: bal, whoami, clear, date, scan"
        elif base == "bal": 
            resp = f"你的餘額少得可憐: ${user['money']}"
        elif base == "whoami": 
            resp = f"你就是個代碼: {uid} (也就是 {user['name']})"
        elif base == "clear": 
            st.session_state.cli_log = []; st.rerun()
        elif base == "date": 
            resp = f"現在時間: {datetime.now().strftime('%Y-%m-%d')}。你的生命正在倒數。"
        elif base == "scan": 
            resp = f"掃描到 {len(get_all_users())} 個可悲的靈魂在線上。"
        else: 
            resp = f"指令 '{base}' 錯誤。你在亂打什麼？手指抽筋嗎？"
        
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
    st.title("🎯 奴隸任務中心")
    if user.get("pending_claims"):
        st.success("🎁 終於做完了？領錢吧。")
        for i, m in enumerate(user["pending_claims"]):
            if st.button(f"領取乞丐般的賞金 ${m['reward']}", key=f"c_{i}"):
                user['money'] += m['reward']
                user['pending_claims'].pop(i)
                save_user(uid, user)
                st.rerun()
    st.divider()
    st.subheader("未完成的工作")
    for m in user.get('active_missions', []):
        st.write(f"- **{m['title']}**: {m['desc']} (賞金: ${m['reward']})")

# --- 主程式 ---
def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        st.title("🏙️ CityOS Access Denied")
        t1, t2 = st.tabs(["登入", "註冊公民ID"])
        with t1:
            u = st.text_input("帳號")
            p = st.text_input("密碼", type="password")
            if st.button("連線"):
                user_data = get_user(u)
                if user_data and user_data['password'] == p:
                    st.session_state.logged_in = True
                    st.session_state.uid = u
                    st.rerun()
                else: st.error("密碼錯誤。連這都記不住？")
        with t2:
            nu, np, nn = st.text_input("新帳號"), st.text_input("新密碼", type="password"), st.text_input("暱稱")
            if st.button("建立"):
                if create_user(nu, np, nn): st.success("註冊成功。歡迎來到地獄。"); st.rerun()
                else: st.error("這 ID 有人用了。換一個。")
        return

    uid = st.session_state.uid
    user = get_user(uid)
    
    # --- Sidebar 顯示職業 ---
    with st.sidebar:
        st.title(f"👤 {user['name']}")
        
        job_title = user.get("job", "Unknown")
        st.caption(f"ID: {uid} | Class: {job_title}")
        
        st.metric("資金", f"${user['money']:,}")
        
        if job_title == "Gamemaster":
            st.warning("⚠️ 開發者模式")

        nav = st.radio("選單", ["儀表板", "股市", "任務", "黑市", "PVP", "CLI", "邏輯實驗室", "測驗"])
        if st.button("斷開連線"): st.session_state.logged_in = False; st.rerun()

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
