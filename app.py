# ==========================================
# 檔案: app.py (CityOS V25.0)
# ==========================================
import streamlit as st
import random
import time
import pandas as pd
import numpy as np
import base64
from config import CITY_EVENTS, ITEMS, SVG_LIB, MORSE_CODE_DICT, STOCKS_DATA
from database import (
    load_db, save_db, check_mission, get_today_event, 
    log_intruder, load_quiz_from_file, load_missions_from_file, 
    HIDDEN_MISSIONS, get_npc_data  # <--- 🔥 關鍵修復：這裡加入了 get_npc_data
)

st.set_page_config(page_title="CityOS V25.0", layout="wide", page_icon="🏙️", initial_sidebar_state="expanded")

# --- CSS ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #0E1117; }
    .stButton>button { border-radius: 8px; border: 1px solid #333; transition: all 0.3s; }
    .stButton>button:hover { border-color: #00FF00; color: #00FF00; box-shadow: 0 0 10px rgba(0,255,0,0.2); }
    h1, h2, h3 { font-family: 'Courier New', monospace; }
</style>
""", unsafe_allow_html=True)

# --- 股市自動更新 ---
def update_stock_market():
    now = time.time()
    last_update = st.session_state.get("last_stock_update", 0)
    if now - last_update > 60:
        prices = {}
        history = st.session_state.get("stock_history", {})
        evt = st.session_state.get("today_event", {})
        for code, data in STOCKS_DATA.items():
            prev = st.session_state.get("stock_prices", {}).get(code, data['base'])
            change = random.uniform(-data['volatility'], data['volatility'])
            if evt.get("effect") == "mining_boost" and code == "CYBR": change += 0.05
            if evt.get("effect") == "hack_nerf" and code == "CYBR": change -= 0.05
            new_price = max(1, int(prev * (1 + change)))
            prices[code] = new_price
            if code not in history: history[code] = [data['base']] * 10
            history[code].append(new_price)
            if len(history[code]) > 20: history[code].pop(0)
        st.session_state.stock_prices = prices
        st.session_state.stock_history = history
        st.session_state.last_stock_update = now

# --- 頁面 ---
def page_dashboard(uid, user):
    st.title("🏙️ CityOS 中央控制台")
    evt = st.session_state.today_event
    icon = "📉" if "nerf" in str(evt['effect']) else "📈"
    with st.container(border=True):
        c1, c2 = st.columns([1, 6])
        c1.markdown(f"<div style='font-size:50px;text-align:center'>{icon}</div>", unsafe_allow_html=True)
        with c2:
            st.subheader(f"頭條：{evt['name']}")
            st.write(evt['desc'])
            if evt['effect']: st.info(f"影響: {evt['effect']}")
    update_stock_market()
    st.markdown("---")
    t1, t2 = st.tabs(["📊 監控", "⚙️ 安全"])
    with t1:
        if st.checkbox("🔴 啟動數據串流"):
            c1, c2 = st.columns(2)
            c1.line_chart(pd.DataFrame(np.random.randint(10,60,(20,1)), columns=["CPU"]))
            c2.area_chart(pd.DataFrame(np.random.randint(200,900,(20,1)), columns=["NET"]), color="#00FF00")
        else: st.info("待命...")
    with t2:
        st.info(f"防禦密碼: {'✅ 已設定' if user.get('defense_code')!='0000' else '⚠️ 預設'}")
        with st.expander("修改密碼"):
            nc = st.text_input("新密碼 (4位)", max_chars=4, type="password")
            if st.button("更新"):
                if len(nc)==4 and nc.isdigit():
                    user["defense_code"] = nc
                    save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]})
                    st.success("OK")

def page_stock_market(uid, user):
    st.title("💹 夜之城證券交易所")
    st.caption("每 60 秒自動更新。")
    update_stock_market()
    prices = st.session_state.stock_prices
    history = st.session_state.stock_history
    u_stocks = user.get("stocks", {})
    
    cols = st.columns(4)
    for i, (code, info) in enumerate(STOCKS_DATA.items()):
        curr = prices.get(code, info['base'])
        delta = curr - info['base']
        with cols[i].container(border=True):
            st.metric(info['name'], f"${curr}", f"{delta}")
            st.line_chart(history.get(code, []), height=100)
    
    st.markdown("---")
    st.subheader("💻 交易")
    sel = st.selectbox("股票", list(STOCKS_DATA.keys()))
    price = prices.get(sel, 0)
    owned = u_stocks.get(sel, 0)
    
    c1, c2 = st.columns(2)
    with c1.container(border=True):
        st.write(f"**買入** @ ${price}")
        qb = st.number_input("股數", 1, 1000, 10, key="qb")
        cost = qb * price
        if st.button("買入"):
            if user['money']>=cost:
                user['money']-=cost
                user.setdefault("stocks",{})[sel] = owned+qb
                check_mission(uid, user, "stock_buy")
                save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]})
                st.toast("成交！"); time.sleep(0.5); st.rerun()
            else: st.error("沒錢")
    with c2.container(border=True):
        st.write(f"**賣出** (持: {owned})")
        qs = st.number_input("股數", 1, max(1, owned), 1, key="qs")
        earn = qs * price
        if st.button("賣出"):
            if owned>=qs:
                user['stocks'][sel]-=qs
                user['money']+=earn
                if user['stocks'][sel]==0: del user['stocks'][sel]
                check_mission(uid, user, "stock_sell")
                save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]})
                st.toast("成交！"); time.sleep(0.5); st.rerun()
            else: st.error("不足")

def page_missions(uid, user):
    st.title("🎯 任務看板")
    ms = load_missions_from_file()
    pending = user.get("pending_claims", [])
    if pending:
        st.success(f"🎁 有 {len(pending)} 個任務完成！")
        for mid in pending:
            m = ms.get(mid, HIDDEN_MISSIONS.get(mid))
            if not m: continue
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{m['title']}** - 💰 ${m['reward']}")
                if c2.button("領取", key=f"clm_{mid}"):
                    user["money"] += m['reward']
                    user["pending_claims"].remove(mid)
                    user["completed_missions"].append(mid)
                    save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]})
                    check_mission(uid, user, "none") 
                    st.rerun()
    st.markdown("---")
    st.subheader("📌 進行中 (Max 3)")
    active = user.get("active_missions", [])
    if not active:
        st.info("暫無任務，請稍後。")
        check_mission(uid, user, "refresh")
    else:
        cols = st.columns(3)
        for i, mid in enumerate(active):
            if mid in ms:
                m = ms[mid]
                with cols[i%3].container(border=True):
                    st.info(f"任務 {i+1}")
                    st.write(f"**{m['title']}**")
                    st.caption(m['desc'])
                    st.write(f"報酬: ${m['reward']}")
    with st.expander("歷史紀錄"):
        st.write(f"已完成: {len(user.get('completed_missions',[]))}")

def page_quiz(uid, user):
    st.title("📝 每日挑戰")
    today = time.strftime("%Y-%m-%d")
    if user.get("last_quiz_date") == today:
        st.warning("⛔ 今天已挑戰過。")
        return
    if "quiz_state" not in st.session_state: st.session_state.quiz_state = "intro"
    if st.session_state.quiz_state == "intro":
        st.write("答對獲 $500，每天限一次。")
        if st.button("開始"):
            qs = load_quiz_from_file()
            if qs: st.session_state.q_curr = random.choice(qs); st.session_state.quiz_state = "playing"; st.rerun()
            else: st.error("無題庫")
    elif st.session_state.quiz_state == "playing":
        q = st.session_state.q_curr
        st.write(f"**Q: {q['q']}**")
        ans = st.radio("Ans", q['options'])
        if st.button("送出"):
            if ans == q['ans']:
                st.balloons(); st.success("✅ 正確！+$500")
                user["money"]+=500; user["exp"]=user.get("exp",0)+100
                check_mission(uid, user, "quiz_done")
            else: st.error(f"❌ 錯誤。答案是 {q['ans']}")
            user["last_quiz_date"] = today
            save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]})
            del st.session_state.q_curr; del st.session_state.quiz_state
            time.sleep(2); st.rerun()

def page_lab(uid, user):
    st.title("🔬 邏輯實驗室")
    t1, t2 = st.tabs(["基礎", "進階"])
    with t1:
        g = st.selectbox("Gate", ["AND", "OR", "NOT"])
        c1, c2 = st.columns(2)
        a = c1.toggle(f"{g} A"); b = False
        if g!="NOT": b = c2.toggle(f"{g} B")
        st.markdown(SVG_LIB[g], unsafe_allow_html=True)
        if g=="AND" and a and b: check_mission(uid, user, "logic_state", "11")
    with t2:
        g2 = st.selectbox("Adv Gate", ["NAND", "NOR", "XOR", "XNOR", "BUFFER"])
        c1, c2 = st.columns(2)
        a2 = c1.toggle(f"{g2} A"); b2 = False
        if g2!="BUFFER": b2 = c2.toggle(f"{g2} B")
        st.markdown(SVG_LIB.get(g2, "<div>SVG Missing</div>"), unsafe_allow_html=True)
        res = 0
        if g2=="NAND": res = 0 if (a2 and b2) else 1
        elif g2=="NOR": res = 0 if (a2 or b2) else 1
        elif g2=="XOR": res = 1 if a2!=b2 else 0
        elif g2=="XNOR": res = 1 if a2==b2 else 0
        elif g2=="BUFFER": res = 1 if a2 else 0
        st.metric("Out", res)
        if res==1: check_mission(uid, user, "logic_use")

def page_crypto(uid, user):
    st.title("🔐 密碼學")
    m = st.selectbox("Mode", ["Caesar", "Morse", "Base64", "Atbash"])
    txt = st.text_input("Input", "HELLO")
    check_mission(uid, user, "crypto_input", txt)
    if m=="Caesar":
        s = st.slider("Shift", 1, 25, 3)
        res = "".join([chr(ord(c)+s) if c.isalpha() else c for c in txt.upper()])
    elif m=="Morse": res = " ".join([MORSE_CODE_DICT.get(c,c) for c in txt.upper()])
    elif m=="Base64": res = base64.b64encode(txt.encode()).decode()
    elif m=="Atbash":
        res = "".join([chr(ord('Z')-(ord(c)-ord('A'))) if 'A'<=c<='Z' else c for c in txt.upper()])
    st.code(res)

def page_shop(uid, user):
    st.title("🛒 黑市")
    disc = 0.7 if st.session_state.today_event['effect']=="shop_discount" else 1.0
    cols = st.columns(3)
    for i, (k,v) in enumerate(ITEMS.items()):
        p = int(v['price']*disc)
        with cols[i%3].container(border=True):
            st.write(f"**{k}** (${p})"); st.caption(v['desc'])
            if st.button("Buy", key=k):
                if user['money']>=p:
                    user['money']-=p
                    user.setdefault("inventory",{})[k]=user.get("inventory",{}).get(k,0)+1
                    check_mission(uid, user, "shop_buy")
                    save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]})
                    st.rerun()
                else: st.error("No $")

def page_pvp(uid, user):
    st.title("⚔️ PVP")
    db = load_db()
    targets = [u for u in db["users"] if u != uid and u != "frank"]
    if not targets: st.warning("No targets"); return
    tid = st.selectbox("Target", targets)
    t_user = db["users"][tid]
    
    if user.get("inventory", {}).get("Brute Force Script", 0) <= 0:
        st.error("需要 Brute Force Script"); return

    with st.expander("配置", expanded=True):
        use_neck = False
        if user.get("inventory", {}).get("Clarity Necklace", 0) > 0:
            use_neck = st.checkbox("用項鍊")

    if "pvp_st" not in st.session_state: st.session_state.pvp_st = "ready"
    if st.button("入侵") or st.session_state.pvp_st == "go":
        st.session_state.pvp_st = "go"
        has_chaos = t_user.get("inventory", {}).get("Chaos Heart", 0) > 0
        n_opt = 8 if has_chaos else 4
        if use_neck: n_opt = max(2, int(n_opt/2))

        if "pvp_opts" not in st.session_state:
            real = t_user.get("defense_code", "0000")
            opts = set([real])
            while len(opts) < n_opt: opts.add(f"{random.randint(0,9999):04d}")
            l = list(opts); random.shuffle(l)
            st.session_state.pvp_opts = l
            st.session_state.pvp_real = real
            st.session_state.pvp_neck = use_neck
            st.session_state.pvp_chaos = has_chaos

        st.markdown("### 🔑 破解")
        cols = st.columns(4)
        for i, code in enumerate(st.session_state.pvp_opts):
            if cols[i%4].button(code, key=f"p_{code}"):
                user["inventory"]["Brute Force Script"] -= 1
                if user["inventory"]["Brute Force Script"]==0: del user["inventory"]["Brute Force Script"]
                if st.session_state.pvp_neck:
                    user["inventory"]["Clarity Necklace"]-=1
                    if user["inventory"]["Clarity Necklace"]==0: del user["inventory"]["Clarity Necklace"]
                if st.session_state.pvp_chaos:
                    t_user["inventory"]["Chaos Heart"]-=1
                    if t_user["inventory"]["Chaos Heart"]==0: del t_user["inventory"]["Chaos Heart"]

                if code == st.session_state.pvp_real:
                    has_fw = t_user.get("inventory", {}).get("Firewall", 0) > 0
                    loot = int(t_user["money"] * (0.1 if has_fw else 0.2))
                    if has_fw:
                        t_user["inventory"]["Firewall"]-=1
                        if t_user["inventory"]["Firewall"]==0: del t_user["inventory"]["Firewall"]
                        st.toast(f"成功(被擋) +${loot}", icon="🔥")
                    else: st.balloons(); st.toast(f"爆擊 +${loot}", icon="💰")
                    t_user["money"] -= loot; user["money"] += loot
                    check_mission(uid, user, "pvp_win")
                else: st.error("失敗")
                
                db["users"][uid] = user; db["users"][tid] = t_user
                save_db(db)
                del st.session_state.pvp_opts; del st.session_state.pvp_st
                time.sleep(2); st.rerun()

def page_cli(uid, user):
    st.title("💻 CLI")
    if "cli_h" not in st.session_state: st.session_state.cli_h = []
    for l in st.session_state.cli_h[-5:]: st.code(l)
    cmd = st.chat_input("Cmd...")
    if cmd:
        st.session_state.cli_h.append(f"> {cmd}")
        check_mission(uid, user, "cli_input", cmd)
        if cmd not in ["help", "bal", "scan", "sudo"]:
            st.session_state.cli_err = st.session_state.get("cli_err",0)+1
            check_mission(uid, user, "cli_error", st.session_state.cli_err)
        st.session_state.cli_h.append("Done")
        st.rerun()

def page_bank(uid, user):
    st.title("🏦 銀行")
    c1, c2 = st.columns(2)
    c1.metric("存", user.get('bank_deposit',0)); c2.metric("現", user['money'])
    amt = st.number_input("$", 1, 100000)
    if st.button("存") and user['money']>=amt:
        user['money']-=amt; user['bank_deposit']+=amt; check_mission(uid, user, "bank_save"); st.rerun()
    if st.button("取") and user.get('bank_deposit',0)>=amt:
        user['bank_deposit']-=amt; user['money']+=amt; check_mission(uid, user, "bank_withdraw"); st.rerun()

# --- Main ---
def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    if "today_event" not in st.session_state: st.session_state.today_event = get_today_event()
    update_stock_market()

    if not st.session_state.logged_in:
        st.title("🏙️ CityOS V25.0")
        t1, t2 = st.tabs(["Login", "Register"])
        with t1:
            u = st.text_input("User"); p = st.text_input("Pass", type="password")
            if st.button("Login"):
                db = load_db()
                if u in db["users"] and db["users"][u]["password"]==p:
                    st.session_state.logged_in=True; st.session_state.uid=u; st.session_state.user=db["users"][u]
                    st.rerun()
                else: st.error("Fail")
        with t2:
            nu = st.text_input("New User"); np = st.text_input("New Pass", type="password")
            if st.button("Sign Up"):
                db = load_db()
                if nu not in db["users"]:
                    # 這裡原本會報錯，現在修復了
                    db["users"][nu] = get_npc_data(nu, "Novice", 1, 1000)
                    db["users"][nu]["password"] = np
                    save_db(db); st.success("OK! Login please.")
                else: st.error("Exists")
        return

    uid = st.session_state.uid
    user = st.session_state.user if uid=="frank" else load_db()["users"].get(uid, st.session_state.user)

    st.sidebar.title(f"🆔 {user['name']}")
    menu = {"✨ 大廳":"dash", "💹 股市":"stock", "🎯 任務":"miss", "📝 測驗":"quiz", "🔬 實驗":"lab", "🔐 密碼":"cryp", "🛒 黑市":"shop", "🏦 銀行":"bank", "⚔️ PVP":"pvp", "💻 CLI":"cli"}
    pg = menu[st.sidebar.radio("Nav", list(menu.keys()))]

    if pg=="dash": page_dashboard(uid, user)
    elif pg=="stock": page_stock_market(uid, user)
    elif pg=="miss": page_missions(uid, user)
    elif pg=="quiz": page_quiz(uid, user)
    elif pg=="lab": page_lab(uid, user)
    elif pg=="cryp": page_crypto(uid, user)
    elif pg=="shop": page_shop(uid, user)
    elif pg=="bank": page_bank(uid, user)
    elif pg=="pvp": page_pvp(uid, user)
    elif pg=="cli": page_cli(uid, user)
    
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in=False; st.rerun()

if __name__ == "__main__":
    main()
