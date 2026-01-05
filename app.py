# ==========================================
# 檔案: app.py (V31.0 Ultimate Merge)
# 功能: 包含毒舌CLI、首頁股市圖、動態任務、以及所有PVP/銀行/存檔功能
# ==========================================
import streamlit as st
import random
import time
import pandas as pd
import numpy as np
import base64
import json
from config import CITY_EVENTS, ITEMS, SVG_LIB, MORSE_CODE_DICT, STOCKS_DATA
from database import (
    load_db, save_db, check_mission, get_today_event, 
    log_intruder, load_quiz_from_file, 
    HIDDEN_MISSIONS, get_npc_data, send_mail
)

# --- 1. 頁面基礎設定 ---
st.set_page_config(page_title="CityOS V31.0", layout="wide", page_icon="🏙️", initial_sidebar_state="expanded")

# --- 2. CSS 美化 ---
st.markdown("""
<style>
    /* 全站深色背景 */
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    
    /* 側邊欄與按鈕 */
    [data-testid="stSidebar"] { background-color: #0E1117; border-right: 1px solid #333; }
    .stButton>button { border-radius: 4px; border: 1px solid #444; transition: all 0.3s; color: #EEE; background-color: #1E1E1E; }
    .stButton>button:hover { border-color: #00FF00; color: #00FF00; box-shadow: 0 0 8px rgba(0,255,0,0.3); }
    
    /* 啟動特效文字 */
    .boot-text { font-family: 'Courier New'; color: #00FF00; font-size: 16px; margin-bottom: 2px; }
    .stProgress > div > div > div > div { background-color: #00FF00; }
    
    /* 訊息樣式 */
    .unread-badge { color: #FF4B4B; font-weight: bold; }
    h1, h2, h3 { font-family: 'Courier New', monospace; letter-spacing: -1px; }
</style>
""", unsafe_allow_html=True)

# --- 3. 系統啟動特效 ---
def play_boot_sequence():
    """模擬系統啟動"""
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown("### 🟢 SYSTEM BOOT SEQUENCE")
            st.markdown("---")
            msg_spot = st.empty()
            bar = st.progress(0, text="Initializing...")
            
            steps = [
                ("Loading Kernel...", 20),
                ("Decrypting User Data...", 40),
                ("Connecting to Night City Net...", 60),
                ("Syncing Stock Market...", 80),
                ("Access Granted.", 100)
            ]
            
            for text, percent in steps:
                time.sleep(random.uniform(0.1, 0.3))
                msg_spot.markdown(f"<p class='boot-text'>> {text}</p>", unsafe_allow_html=True)
                bar.progress(percent, text=text)
            
            time.sleep(0.5)
    placeholder.empty()

# --- 4. 股市更新邏輯 ---
def update_stock_market():
    now = time.time()
    last_update = st.session_state.get("last_stock_update", 0)
    
    # 若尚未初始化，先生成一次數據
    if "stock_prices" not in st.session_state:
        st.session_state.stock_prices = {k: v["base"] for k, v in STOCKS_DATA.items()}
        st.session_state.stock_history = pd.DataFrame(columns=STOCKS_DATA.keys())
        # 預填幾筆資料避免圖表空白
        for _ in range(5):
             new_row = pd.DataFrame([st.session_state.stock_prices])
             st.session_state.stock_history = pd.concat([st.session_state.stock_history, new_row], ignore_index=True)

    # 每 60 秒更新一次
    if now - last_update > 60:
        prices = {}
        history = st.session_state.get("stock_history", pd.DataFrame())
        evt = st.session_state.get("today_event", {})
        
        for code, data in STOCKS_DATA.items():
            prev = st.session_state.get("stock_prices", {}).get(code, data['base'])
            change = random.uniform(-data['volatility'], data['volatility'])
            
            # 事件影響
            if evt.get("effect") == "mining_boost" and code == "CYBR": change += 0.08
            if evt.get("effect") == "hack_nerf" and code == "CYBR": change -= 0.08
            if evt.get("effect") == "tech_boom" and code in ["CYBR", "CHIP"]: change += 0.05
            
            new_price = max(1, int(prev * (1 + change)))
            prices[code] = new_price
            
        st.session_state.stock_prices = prices
        
        # 更新歷史並保持長度
        new_row = pd.DataFrame([prices])
        history = pd.concat([history, new_row], ignore_index=True)
        if len(history) > 50: history = history.iloc[-50:]
        
        st.session_state.stock_history = history
        st.session_state.last_stock_update = now

# --- 5. 各功能頁面 ---

def page_dashboard(uid, user):
    st.title("🏙️ CityOS Dashboard")
    evt = st.session_state.today_event
    
    # 頭條與狀態
    c1, c2 = st.columns([1, 5])
    with c1:
        icon = "📉" if "nerf" in str(evt.get('effect','')) else "📈"
        st.markdown(f"<div style='font-size:50px;text-align:center'>{icon}</div>", unsafe_allow_html=True)
    with c2:
        st.subheader(f"頭條：{evt['name']}")
        st.write(f"📝 {evt['desc']}")
        if evt['effect']: st.info(f"⚡ {evt['effect']}")
    
    update_stock_market()
    
    # 資產概況 (V30 功能)
    st.markdown("---")
    st.subheader("📊 資產監控")
    stock_val = sum([amt * st.session_state.stock_prices.get(code,0) for code, amt in user.get("stocks",{}).items()])
    total = user['money'] + user.get('bank_deposit', 0) + stock_val
    
    m1, m2, m3 = st.columns(3)
    m1.metric("總資產估值", f"${total:,}")
    m2.metric("銀行存款", f"${user.get('bank_deposit', 0):,}")
    m3.metric("股票市值", f"${stock_val:,}")
    
    # 顯示股市走勢圖 (V30 功能)
    if not st.session_state.stock_history.empty:
        st.line_chart(st.session_state.stock_history, height=200)

    # 進行中任務預覽
    st.markdown("---")
    st.subheader("🎯 待辦合約")
    if user.get("active_missions"):
        for m in user["active_missions"]:
            if isinstance(m, dict):
                st.info(f"**{m['title']}**: {m['desc']} (賞金: ${m['reward']})")
    else:
        st.caption("目前無任務。")

def page_mail(uid, user):
    st.title("📧 數位信箱")
    mailbox = user.get("mailbox", [])
    unread = len([m for m in mailbox if not m.get("read", False)])
    t1, t2 = st.tabs([f"📥 收件 ({unread})", "📤 寄件"])
    
    with t1:
        if not mailbox: st.info("無郵件")
        else:
            for i, m in enumerate(mailbox):
                st.text(f"{'🔴' if not m.get('read') else '⚪'} {m['title']} (from: {m['from']})")
                with st.expander("閱讀"):
                    st.write(m['msg'])
                    if st.button("標為已讀", key=f"r_{i}"):
                        user["mailbox"][i]["read"] = True
                        save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]}); st.rerun()
                    if st.button("刪除", key=f"d_{i}"):
                        user["mailbox"].pop(i)
                        save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]}); st.rerun()
    with t2:
        db = load_db()
        to = st.selectbox("收件人", list(db["users"].keys()))
        sub = st.text_input("主旨"); content = st.text_area("內容")
        if st.button("發送"):
            if send_mail(to, uid, sub, content):
                st.success("已發送"); check_mission(uid, user, "send_mail", extra_data=to)
            else: st.error("失敗")

def page_stock_market(uid, user):
    st.title("💹 證券交易所")
    update_stock_market()
    prices = st.session_state.stock_prices
    u_stocks = user.get("stocks", {})
    
    # V30 的看盤風格
    st.line_chart(st.session_state.stock_history)
    
    c1, c2 = st.columns(2)
    sel = st.selectbox("股票代碼", list(STOCKS_DATA.keys()))
    curr = prices.get(sel, 0)
    owned = u_stocks.get(sel, 0)
    
    st.metric(f"{STOCKS_DATA[sel]['name']} ({sel})", f"${curr}")
    st.write(f"持有: {owned} 股")
    
    with c1.container(border=True):
        qb = st.number_input("買入量", 1, 1000, 10)
        if st.button("買入"):
            cost = qb * curr
            if user['money'] >= cost:
                user['money'] -= cost
                user.setdefault("stocks", {})[sel] = owned + qb
                check_mission(uid, user, "stock_buy", extra_data=sel, extra_val=qb)
                save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]}); st.success("成交"); st.rerun()
            else: st.error("資金不足")
            
    with c2.container(border=True):
        qs = st.number_input("賣出量", 1, max(1, owned), 1)
        if st.button("賣出"):
            if owned >= qs:
                user['stocks'][sel] -= qs
                user['money'] += qs * curr
                if user['stocks'][sel] == 0: del user['stocks'][sel]
                check_mission(uid, user, "stock_sell")
                save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]}); st.success("成交"); st.rerun()
            else: st.error("持股不足")

def page_missions(uid, user):
    st.title("🎯 任務中心")
    # 待領取
    pending = user.get("pending_claims", [])
    if pending:
        st.success(f"🎁 有 {len(pending)} 個獎勵待領取！")
        for i, m in enumerate(pending):
            title = m.get("title", "未知") if isinstance(m, dict) else "成就"
            reward = m.get("reward", 0) if isinstance(m, dict) else 100
            desc = m.get("desc", "") if isinstance(m, dict) else ""
            with st.container(border=True):
                c1, c2 = st.columns([4,1])
                c1.write(f"**{title}** (${reward})"); c1.caption(desc)
                if c2.button("領取", key=f"mc_{i}"):
                    user["money"] += reward
                    user["pending_claims"].pop(i)
                    mid = m.get("id","") if isinstance(m, dict) else m
                    user.setdefault("completed_missions", []).append(mid)
                    save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]})
                    check_mission(uid, user, "none"); st.rerun()
    
    st.markdown("---")
    # 進行中 (如果沒有，自動補貨)
    if not user.get("active_missions"):
        check_mission(uid, user, "refresh"); st.rerun()
        
    st.subheader("📋 進行中合約")
    cols = st.columns(3)
    for i, m in enumerate(user.get("active_missions", [])):
        if isinstance(m, dict):
            with cols[i%3].container(border=True):
                st.info(f"MISSION {i+1}")
                st.markdown(f"#### {m['title']}")
                st.write(m['desc'])
                st.metric("賞金", f"${m['reward']}")

def page_quiz(uid, user):
    st.title("📝 每日挑戰")
    today = time.strftime("%Y-%m-%d")
    if user.get("last_quiz_date") == today:
        st.warning("今日已完成")
        return
    
    if "quiz_state" not in st.session_state: st.session_state.quiz_state = "intro"
    
    if st.session_state.quiz_state == "intro":
        if st.button("開始測驗"):
            qs = load_quiz_from_file()
            st.session_state.q_curr = random.choice(qs)
            st.session_state.quiz_state = "play"
            st.rerun()
    elif st.session_state.quiz_state == "play":
        q = st.session_state.q_curr
        st.write(f"**Q: {q['q']}**")
        ans = st.radio("Ans", q['options'])
        if st.button("送出"):
            if ans == q['ans']:
                st.success("Correct! +$10") # 困難模式錢很少
                user["money"] += 10
                check_mission(uid, user, "quiz_done")
            else:
                st.error("Wrong.")
            user["last_quiz_date"] = today
            save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]})
            del st.session_state.quiz_state
            time.sleep(1); st.rerun()

def page_lab(uid, user):
    st.title("🔬 邏輯實驗室")
    g = st.selectbox("Gate", ["AND", "OR", "NOT", "XOR", "NAND"])
    c1, c2 = st.columns(2)
    a = c1.toggle("A"); b = False
    if g!="NOT": b = c2.toggle("B")
    
    st.html(f"<div style='width:150px;margin:auto'>{SVG_LIB.get(g,'')}</div>")
    res = 0
    if g=="AND": res = 1 if a and b else 0
    elif g=="OR": res = 1 if a or b else 0
    elif g=="NOT": res = 1 if not a else 0
    elif g=="XOR": res = 1 if a!=b else 0
    elif g=="NAND": res = 0 if a and b else 1
    
    st.metric("Output", res)
    if res==1: check_mission(uid, user, "logic_use")

def page_crypto(uid, user):
    st.title("🔐 密碼學")
    m = st.selectbox("Mode", ["Caesar", "Morse", "Base64"])
    txt = st.text_input("Text", "HELLO")
    check_mission(uid, user, "crypto_input", extra_data=txt)
    
    res = ""
    if m=="Caesar":
        s = st.slider("Shift", 1, 25, 3)
        res = "".join([chr((ord(c)-65+s)%26+65) if c.isupper() else chr((ord(c)-97+s)%26+97) if c.islower() else c for c in txt])
    elif m=="Morse":
        res = " ".join([MORSE_CODE_DICT.get(c.upper(),c) for c in txt])
    elif m=="Base64":
        try: res = base64.b64encode(txt.encode()).decode()
        except: res = "Error"
    st.code(res)

def page_shop(uid, user):
    st.title("🛒 地下黑市")
    # 折扣事件
    disc = 0.7 if st.session_state.today_event['effect']=="shop_discount" else 1.0
    
    for k, v in ITEMS.items():
        with st.container(border=True):
            c1, c2 = st.columns([3,1])
            c1.write(f"**{k}**"); c1.caption(v['desc'])
            price = int(v['price']*disc)
            if c2.button(f"${price}", key=f"b_{k}"):
                if user['money'] >= price:
                    user['money'] -= price
                    user.setdefault("inventory", {})[k] = user.get("inventory", {}).get(k,0)+1
                    check_mission(uid, user, "shop_buy", extra_data=k)
                    save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]})
                    st.success("Bought"); st.rerun()
                else: st.error("No money")

def page_bank(uid, user):
    st.title("🏦 銀行")
    st.metric("存款", f"${user.get('bank_deposit',0)}")
    amt = st.number_input("金額", 1, 100000)
    c1, c2 = st.columns(2)
    if c1.button("存入"):
        if user['money']>=amt:
            user['money']-=amt; user['bank_deposit'] = user.get('bank_deposit',0)+amt
            check_mission(uid, user, "bank_save", extra_val=amt)
            save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]}); st.rerun()
    if c2.button("提款"):
        if user.get('bank_deposit',0)>=amt:
            user['bank_deposit']-=amt; user['money']+=amt
            save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]}); st.rerun()

def page_pvp(uid, user):
    st.title("⚔️ PVP")
    db = load_db()
    targets = [u for u in db["users"] if u != uid and u != "frank"]
    if not targets: st.warning("No targets"); return
    
    tid = st.selectbox("Target", targets)
    t_user = db["users"][tid]
    
    script_cnt = user.get("inventory",{}).get("Brute Force Script", 0)
    st.write(f"持有 Script: {script_cnt}")
    
    if script_cnt <= 0: st.error("Need Script"); return
    
    if st.button("🚀 Attack"):
        # 簡易版PVP邏輯
        user["inventory"]["Brute Force Script"] -= 1
        if user["inventory"]["Brute Force Script"]==0: del user["inventory"]["Brute Force Script"]
        
        # 30% 機率成功 (Hardcore)
        if random.random() < 0.3:
            loot = int(t_user["money"] * 0.1)
            t_user["money"] -= loot
            user["money"] += loot
            check_mission(uid, user, "pvp_win", extra_val=1)
            st.success(f"Success! Stole ${loot}")
        else:
            st.error("Failed.")
            log_intruder(uid)
            
        db["users"][uid] = user; db["users"][tid] = t_user
        save_db(db); st.rerun()

def page_cli(uid, user):
    # --- 毒舌 CLI (V30 功能) ---
    st.title("💻 終端機 (CLI)")
    sarcastic = [
        "指令錯誤。鍵盤壞了？", "Permission Denied. 你不是神。", 
        "404 Brain Not Found.", "別亂試，我會報警。", "去喝杯咖啡再來。"
    ]
    
    if "cli_h" not in st.session_state: st.session_state.cli_h = ["System initialized..."]
    for l in st.session_state.cli_h[-6:]: st.code(l)
    
    cmd = st.chat_input("user@cityos:~$")
    if cmd:
        st.session_state.cli_h.append(f"$ {cmd}")
        check_mission(uid, user, "cli_input", extra_data=cmd)
        
        if cmd == "help": res = "bal, whoami, scan, sudo, clear"
        elif cmd == "bal": res = f"Cash: ${user['money']} (窮)" if user['money']<100 else f"${user['money']}"
        elif cmd == "whoami": res = f"{user['name']} (Lv.{user['level']})"
        elif cmd == "clear": st.session_state.cli_h=[]; st.rerun()
        elif cmd == "sudo": res = "權限不足。"
        elif cmd == "sudo su": res = "成就解鎖：想得美。"; check_mission(uid, user, "cli_input", extra_data="sudo su")
        else:
            res = f"Error: {random.choice(sarcastic)}"
            check_mission(uid, user, "cli_error", extra_val=st.session_state.get("cli_err",0)+1)
        
        st.session_state.cli_h.append(res)
        st.rerun()

def page_leaderboard(uid, user):
    st.title("🏆 名人堂")
    db = load_db()
    data = []
    prices = st.session_state.get("stock_prices", {})
    for u in db['users'].values():
        val = u['money'] + u.get('bank_deposit',0) + sum([q*prices.get(c,10) for c,q in u.get('stocks',{}).items()])
        data.append({"User":u['name'], "Total":val})
    st.dataframe(pd.DataFrame(data).sort_values("Total", ascending=False))

def page_admin(uid, user):
    st.title("💀 Admin")
    db = load_db()
    with st.expander("Event"):
        evt = st.selectbox("Set Event", [e['name'] for e in CITY_EVENTS])
        if st.button("Set"):
            for e in CITY_EVENTS:
                if e['name'] == evt: st.session_state.today_event = e; st.rerun()

# --- 6. 主程式 ---
def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    if "today_event" not in st.session_state: st.session_state.today_event = get_today_event()
    update_stock_market()
    
    # 登入頁面 (含存檔功能 - V28 功能)
    if not st.session_state.logged_in:
        st.title("🏙️ CityOS V31.0")
        
        with st.expander("💾 存檔管理"):
            c1, c2 = st.columns(2)
            try:
                with open("cityos_users.json", "r", encoding="utf-8") as f:
                    c1.download_button("下載存檔", f, "save.json")
            except: c1.warning("無存檔")
            
            up = c2.file_uploader("上傳存檔", type=["json"])
            if up:
                with open("cityos_users.json", "w", encoding="utf-8") as f:
                    json.dump(json.load(up), f, ensure_ascii=False, indent=4)
                st.success("已恢復"); st.rerun()
        
        t1, t2 = st.tabs(["登入", "註冊"])
        with t1:
            u = st.text_input("ID"); p = st.text_input("PW", type="password")
            if st.button("Login"):
                db = load_db()
                if u in db["users"] and db["users"][u]["password"]==p:
                    play_boot_sequence() # 啟動特效
                    st.session_state.logged_in=True; st.session_state.uid=u; st.session_state.user=db["users"][u]
                    st.rerun()
                else: st.error("Fail"); log_intruder(u)
        with t2:
            nu = st.text_input("New ID"); np = st.text_input("New PW", type="password"); nn = st.text_input("Name")
            if st.button("Reg"):
                if len(np)>4 and nu and nn:
                    db = load_db()
                    if nu not in db["users"]:
                        db["users"][nu] = get_npc_data(nn, "Novice", 1, 500)
                        db["users"][nu]["password"] = np
                        save_db(db); st.success("OK")
                    else: st.error("Exist")
        return

    # 主介面
    uid = st.session_state.uid
    user = st.session_state.user if uid=="frank" else load_db()["users"].get(uid, st.session_state.user)
    
    st.sidebar.title(f"{user['name']}")
    st.sidebar.metric("Cash", f"${user['money']}")
    
    menu = {
        "📊 儀表板": "dash", "📧 信箱": "mail", "💹 股市": "stock", 
        "🎯 任務": "miss", "📝 測驗": "quiz", "🔬 實驗": "lab", 
        "🔐 密碼": "cryp", "🛒 黑市": "shop", "🏦 銀行": "bank", 
        "⚔️ PVP": "pvp", "💻 CLI": "cli", "🏆 排名": "rank"
    }
    if uid == "frank": menu["💀 Admin"] = "admin"
    
    pg = menu[st.sidebar.radio("Nav", list(menu.keys()))]
    
    if pg=="dash": page_dashboard(uid, user)
    elif pg=="mail": page_mail(uid, user)
    elif pg=="stock": page_stock_market(uid, user)
    elif pg=="miss": page_missions(uid, user)
    elif pg=="quiz": page_quiz(uid, user)
    elif pg=="lab": page_lab(uid, user)
    elif pg=="cryp": page_crypto(uid, user)
    elif pg=="shop": page_shop(uid, user)
    elif pg=="bank": page_bank(uid, user)
    elif pg=="pvp": page_pvp(uid, user)
    elif pg=="cli": page_cli(uid, user)
    elif pg=="rank": page_leaderboard(uid, user)
    elif pg=="admin": page_admin(uid, user)
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in=False; st.rerun()

if __name__ == "__main__":
    main()
