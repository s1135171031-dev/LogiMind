# 檔案名稱: app.py
# 用途: Streamlit 介面入口，負責顯示與互動
# 執行指令: streamlit run app.py

import streamlit as st
import random
import time
from config import CITY_EVENTS, MISSIONS, ITEMS, SVG_LIB, CLASSES # 匯入設定
from database import load_db, save_db, init_db, check_mission, get_today_event, get_admin_data, get_npc_data # 匯入邏輯

st.set_page_config(page_title="CityOS V16.5 Evolution", layout="wide", page_icon="🏙️", initial_sidebar_state="expanded")

# --- 介面函數 (Views) ---

def page_cli_os(uid, user):
    st.markdown("""<style>.stTextInput > div > div > input {background-color: #000; color: #00ff00; font-family: 'Courier New', monospace;}</style>""", unsafe_allow_html=True)
    st.title("💻 Terminal Mode (CLI)")
    st.caption("CityOS Kernel v16.0 | Type 'help' for commands.")

    if "cli_history" not in st.session_state: st.session_state.cli_history = ["System initialized..."]
    with st.container(height=400):
        for line in st.session_state.cli_history: st.text(line)

    cmd = st.chat_input("Enter command >>")
    if cmd:
        st.session_state.cli_history.append(f"user@{uid}:~$ {cmd}")
        tokens = cmd.strip().split(); base_cmd = tokens[0].lower() if tokens else ""
        response = ""
        
        if base_cmd == "help": response = "Commands: whoami, bal, scan, buy <item>, clear"
        elif base_cmd == "clear": st.session_state.cli_history = []; st.rerun()
        elif base_cmd == "whoami": response = f"User: {user['name']} | Role: {user['job']}"
        elif base_cmd == "bal": response = f"Cash: ${user['money']:,} | Bank: ${user.get('bank_deposit',0):,}"
        elif base_cmd == "scan":
            targets = [u for u in load_db()["users"].keys() if u != uid and u != "frank"]
            response = "Scanning...\n" + "\n".join([f"[+] Target: {t}" for t in targets])
        elif base_cmd == "buy":
            # 簡化的 CLI 購買邏輯
            if len(tokens) >= 2 and tokens[1] == "virus":
                if user['money'] >= 500:
                    user['money'] -= 500; user.setdefault("inventory", {})["Trojan Virus"] = user["inventory"].get("Trojan Virus", 0) + 1
                    check_mission(uid, user, "shop_buy")
                    response = "Bought Trojan Virus."
                else: response = "Insufficient funds."
            else: response = "Usage: buy virus"
        else: response = f"Unknown command: {base_cmd}"
        
        if response: st.session_state.cli_history.append(response)
        st.rerun()

def page_missions(uid, user):
    st.title("🎯 任務中心")
    completed = user.get("completed_missions", [])
    st.progress(len(completed)/len(MISSIONS), text=f"完成度: {len(completed)}/{len(MISSIONS)}")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🚧 待辦事項")
        for mid, m in MISSIONS.items():
            if mid not in completed:
                with st.container(border=True):
                    st.write(f"**{m['title']}**"); st.caption(m['desc']); st.info(f"報酬: ${m['reward']}")
    with c2:
        st.subheader("✅ 已完成"); st.write(", ".join(completed))

def page_digital_lab(uid, user):
    st.title("🔬 數位邏輯實驗室")
    tab1, tab2, tab3 = st.tabs(["邏輯閘", "卡諾圖 (K-Map)", "格雷碼"])
    
    with tab1: # 邏輯閘
        gate = st.selectbox("元件", list(SVG_LIB.keys()))
        c1, c2 = st.columns(2)
        a = c1.toggle("A (1)", False); b = c2.toggle("B (1)", False)
        res = 1 if (gate=="AND" and a and b) or (gate=="OR" and (a or b)) or (gate=="XOR" and a!=b) or (gate=="NOT" and not a) else 0
        st.markdown(SVG_LIB[gate], unsafe_allow_html=True); st.metric("Output", res)
        if gate and (a or b): check_mission(uid, user, "logic_use")

    with tab2: # K-Map
        st.subheader("2-Var K-Map")
        if "kmap" not in st.session_state: st.session_state.kmap = [0,0,0,0]
        c1, c2 = st.columns(2)
        with c1: 
            st.write("A=0"); 
            if st.button(f"00: {st.session_state.kmap[0]}", key="k0"): st.session_state.kmap[0]^=1; st.rerun()
            if st.button(f"01: {st.session_state.kmap[1]}", key="k1"): st.session_state.kmap[1]^=1; st.rerun()
        with c2: 
            st.write("A=1"); 
            if st.button(f"10: {st.session_state.kmap[2]}", key="k2"): st.session_state.kmap[2]^=1; st.rerun()
            if st.button(f"11: {st.session_state.kmap[3]}", key="k3"): st.session_state.kmap[3]^=1; st.rerun()
        # 簡易 SOP 顯示
        ones = [i for i, x in enumerate(st.session_state.kmap) if x == 1]
        st.code(f"Minterms: {ones}", language="text")

    with tab3: # 格雷碼
        num = st.slider("Decimal", 0, 15, 3)
        st.metric("Gray Code", f"{(num^(num>>1)):04b}", delta="相鄰只變一位")

def page_bank(uid, user):
    st.title("🏦 賽博銀行")
    evt = st.session_state.today_event
    c1, c2 = st.columns(2)
    c1.metric("存款", f"${user.get('bank_deposit',0):,}"); c2.metric("現金", f"${user['money']:,}")
    amt = st.number_input("金額", 0, 10000, 100)
    if st.button("存入") and user['money'] >= amt:
        user['money'] -= amt; user['bank_deposit'] += amt
        if amt >= 100: check_mission(uid, user, "bank_save")
        if uid!="frank": save_db({"users":load_db()["users"]|{uid:user}, "bbs": []})
        st.rerun()

def page_shop(uid, user):
    st.title("🛒 地下黑市")
    evt = st.session_state.today_event
    discount = 0.7 if evt["effect"] == "shop_discount" else 1.0
    cols = st.columns(3)
    idx = 0
    for item, info in ITEMS.items():
        price = int(info['price'] * discount)
        with cols[idx%3].container(border=True):
            st.write(f"**{item}** (${price})"); st.caption(info['desc'])
            if st.button(f"買 {item}", key=item):
                if user['money'] >= price:
                    user['money'] -= price; user.setdefault("inventory", {})[item] = user.get("inventory", {}).get(item, 0) + 1
                    check_mission(uid, user, "shop_buy")
                    if uid!="frank": save_db({"users":load_db()["users"]|{uid:user}, "bbs": []})
                    st.rerun()
        idx+=1

def page_terminal(uid, user):
    st.title("📟 GUI 駭客終端"); st.write("功能開發中..."); check_mission(uid, user, "attack_try")

# --- 主程式 ---
def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    if "today_event" not in st.session_state: st.session_state.today_event = get_today_event()

    if not st.session_state.logged_in:
        st.markdown("<h1 style='text-align: center;'>🏙️ CityOS V16.5 Modular</h1>", unsafe_allow_html=True)
        st.info(f"今日事件: {st.session_state.today_event['name']}")
        u = st.text_input("User"); p = st.text_input("Pass", type="password")
        if st.button("Login"):
            db = load_db()
            if u=="frank" and p=="x": 
                st.session_state.logged_in=True; st.session_state.user_id="frank"; st.session_state.user_data=get_admin_data(); st.rerun()
            elif u in db["users"] and db["users"][u]["password"]==p:
                st.session_state.logged_in=True; st.session_state.user_id=u; st.session_state.user_data=db["users"][u]; st.rerun()
            else: st.error("Fail")
        return

    uid = st.session_state.user_id; user = st.session_state.user_data
    if uid != "frank": user = load_db()["users"].get(uid, user)

    st.sidebar.title(f"🆔 {user['name']}")
    nav = st.sidebar.radio("Nav", ["大廳", "任務", "銀行", "黑市", "實驗室", "CLI", "駭客"])
    if st.sidebar.button("Logout"): st.session_state.logged_in=False; st.rerun()

    if nav == "大廳": st.title("大廳"); st.write(f"事件: {st.session_state.today_event['desc']}")
    elif nav == "任務": page_missions(uid, user)
    elif nav == "銀行": page_bank(uid, user)
    elif nav == "黑市": page_shop(uid, user)
    elif nav == "實驗室": page_digital_lab(uid, user)
    elif nav == "CLI": page_cli_os(uid, user)
    elif nav == "駭客": page_terminal(uid, user)

if __name__ == "__main__":
    main()
