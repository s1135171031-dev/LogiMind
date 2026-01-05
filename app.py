# app.py
# CityOS V20.0 - Ultimate Edition (PVP Update)

import streamlit as st
import random
import time
import pandas as pd
import numpy as np
from config import CITY_EVENTS, ITEMS, SVG_LIB, MORSE_CODE_DICT
from database import (
    load_db, save_db, check_mission, get_today_event, 
    log_intruder, load_quiz_from_file, load_missions_from_file, 
    HIDDEN_MISSIONS
)

st.set_page_config(page_title="CityOS V20", layout="wide", page_icon="🏙️")

# --- CSS Style ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #0E1117; }
    .stButton>button { border-radius: 6px; transition: all 0.3s; }
    .stButton>button:hover { border-color: #00FF00; color: #00FF00; }
    h1, h2, h3 { font-family: 'Courier New', monospace; }
</style>
""", unsafe_allow_html=True)

# --- Pages ---

def page_dashboard(uid, user):
    st.title("🏙️ CityOS 中央控制台")
    
    # 每日快報
    st.markdown("### 📰 每日快報")
    evt = st.session_state.today_event
    icon = "📉" if "nerf" in str(evt['effect']) else "📈"
    msg_type = "error" if "nerf" in str(evt['effect']) else "success"
    
    with st.container(border=True):
        c1, c2 = st.columns([1, 6])
        with c1: st.markdown(f"<h1 style='text-align:center'>{icon}</h1>", unsafe_allow_html=True)
        with c2:
            st.subheader(f"頭條：{evt['name']}")
            st.write(evt['desc'])
            if evt['effect']: 
                if msg_type=="success": st.success(f"系統影響: {evt['effect']}")
                else: st.error(f"系統影響: {evt['effect']}")

    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["📊 系統監控", "⚙️ 安全設定", "📘 使用手冊"])

    with tab1:
        st.subheader("📡 即時數據流")
        if st.checkbox("🔴 啟動監控"):
            c1,c2 = st.columns(2)
            c1.line_chart(pd.DataFrame(np.random.randint(10,60,(20,1)), columns=["CPU"]))
            c2.bar_chart(pd.DataFrame(np.random.randint(200,900,(20,1)), columns=["Network"]))
        else:
            st.info("監控待命。")
            
    with tab2:
        st.subheader("🛡️ 防禦設定 (PVP)")
        st.caption("設定防禦密碼，防止他人猜中盜取資金。")
        st.info("當前密碼: **** (隱藏)")
        
        with st.form("def_code"):
            nc = st.text_input("新防禦密碼 (4位數字)", max_chars=4, type="password")
            if st.form_submit_button("更新"):
                if len(nc)==4 and nc.isdigit():
                    user["defense_code"] = nc
                    save_db({"users": load_db()["users"]|{uid:user}, "bbs":[]})
                    st.success("更新成功！")
                else: st.error("需為4位數字。")
        
        st.write("#### 🎒 防禦庫存")
        inv = user.get("inventory", {})
        c1, c2 = st.columns(2)
        c1.metric("🔥 防火牆", inv.get("Firewall", 0), help="被猜中時抵銷爆擊")
        c2.metric("💓 混亂之心", inv.get("Chaos Heart", 0), help="讓攻擊者選項加倍")

    with tab3:
        st.markdown("### 📘 攻略\n* **PVP**: 購買腳本攻擊他人，猜對密碼即可偷錢。\n* **防守**: 購買防火牆與混亂之心。")

def page_pvp(uid, user):
    st.title("⚔️ 網路戰 (Cyber Warfare)")
    db = load_db()
    targets = [u for u in db["users"] if u != uid and u != "frank"]
    
    if not targets:
        st.warning("無可用目標。"); return

    # 1. 選擇目標
    tid = st.selectbox("選擇目標", targets)
    t_user = db["users"][tid]
    st.info(f"目標: {t_user['name']} | Lv.{t_user['level']}")
    
    # 2. 檢查道具
    has_script = user.get("inventory", {}).get("Brute Force Script", 0) > 0
    if not has_script:
        st.error("❌ 需要 [Brute Force Script] 才能攻擊。請至黑市購買。")
        return

    # 3. 準備階段
    with st.expander("攻擊配置", expanded=True):
        use_neck = False
        if user.get("inventory", {}).get("Clarity Necklace", 0) > 0:
            use_neck = st.checkbox("💎 使用 [Clarity Necklace] (選項減半)")
        else:
            st.caption("🔒 無項鍊可用")

    # 4. 遊戲邏輯
    if "pvp_stage" not in st.session_state: st.session_state.pvp_stage = "ready"
    
    if st.button("🚀 啟動入侵") or st.session_state.pvp_stage == "guessing":
        st.session_state.pvp_stage = "guessing"
        
        # 計算選項
        has_chaos = t_user.get("inventory", {}).get("Chaos Heart", 0) > 0
        n_opt = 4
        if has_chaos: n_opt *= 2
        if use_neck: n_opt = max(2, int(n_opt/2))
        
        # 生成選項
        if "pvp_opts" not in st.session_state:
            real = t_user.get("defense_code", "0000")
            opts = set([real])
            while len(opts) < n_opt:
                opts.add(f"{random.randint(0,9999):04d}")
            lst = list(opts); random.shuffle(lst)
            st.session_state.pvp_opts = lst
            st.session_state.pvp_real = real
            st.session_state.pvp_neck = use_neck
            st.session_state.pvp_chaos = has_chaos

        st.markdown(f"### 🔑 破解防禦層")
        if has_chaos: st.error("⚠️ 對方裝備了 [混亂之心]！選項加倍！")
        if use_neck: st.success("💎 [清醒項鍊] 生效中。")
        
        cols = st.columns(4)
        for i, code in enumerate(st.session_state.pvp_opts):
            if cols[i%4].button(code, key=f"p_{code}"):
                # 消耗道具
                user["inventory"]["Brute Force Script"] -= 1
                if user["inventory"]["Brute Force Script"] <= 0: del user["inventory"]["Brute Force Script"]
                
                if st.session_state.pvp_neck:
                    user["inventory"]["Clarity Necklace"] -= 1
                    if user["inventory"]["Clarity Necklace"]<=0: del user["inventory"]["Clarity Necklace"]
                
                if st.session_state.pvp_chaos:
                    t_user["inventory"]["Chaos Heart"] -= 1
                    if t_user["inventory"]["Chaos Heart"]<=0: del t_user["inventory"]["Chaos Heart"]

                # 判斷
                if code == st.session_state.pvp_real:
                    has_fw = t_user.get("inventory", {}).get("Firewall", 0) > 0
                    if has_fw:
                        loot = int(t_user["money"]*0.1)
                        t_user["inventory"]["Firewall"]-=1
                        if t_user["inventory"]["Firewall"]<=0: del t_user["inventory"]["Firewall"]
                        st.toast(f"攻擊成功！對方防火牆吸收了傷害。獲得 ${loot}", icon="🔥")
                    else:
                        loot = int(t_user["money"]*0.2)
                        st.balloons()
                        st.toast(f"💥 致命一擊！雙倍獎勵！獲得 ${loot}", icon="💰")
                    
                    t_user["money"] -= loot
                    user["money"] += loot
                    check_mission(uid, user, "pvp_win")
                else:
                    st.error("🚫 密碼錯誤！入侵失敗。")
                
                # 結算與存檔
                db["users"][uid] = user
                db["users"][tid] = t_user
                save_db(db)
                del st.session_state.pvp_opts
                del st.session_state.pvp_stage
                time.sleep(2); st.rerun()

def page_shop(uid, user):
    st.title("🛒 地下黑市")
    evt = st.session_state.today_event
    disc = 0.7 if evt["effect"]=="shop_discount" else 1.0
    if disc<1: st.success("🔥 限時特價 (7折)！")

    cols = st.columns(3)
    idx = 0
    for k, v in ITEMS.items():
        p = int(v['price']*disc)
        with cols[idx%3].container(border=True):
            st.subheader(k)
            st.caption(v['desc'])
            st.write(f"**${p:,}**")
            if st.button("購買", key=f"b_{k}"):
                if user['money']>=p:
                    user['money']-=p
                    user.setdefault("inventory",{})[k] = user.get("inventory",{}).get(k,0)+1
                    check_mission(uid, user, "shop_buy")
                    st.toast(f"已購買 {k}"); time.sleep(0.5); st.rerun()
                else: st.error("資金不足")
        idx+=1

def page_missions(uid, user):
    st.title("🎯 任務中心")
    ms = load_missions_from_file()
    done = user.get("completed_missions", [])
    
    t1, t2 = st.tabs(["一般任務", "🏆 成就"])
    with t1:
        cnt = 0
        for mid, m in ms.items():
            if mid not in done and cnt<5:
                st.info(f"**{m['title']}**: {m['desc']} (${m['reward']})")
                cnt+=1
    with t2:
        for mid in done:
            if mid.startswith("H_") and mid in HIDDEN_MISSIONS:
                hm = HIDDEN_MISSIONS[mid]
                st.success(f"【{hm['title']}】 {hm['desc']}")

def page_quiz(uid, user):
    st.title("📝 每日測驗")
    if "quiz_done" not in st.session_state: st.session_state.quiz_done = False
    if st.session_state.quiz_done: st.info("今日已完成"); return

    if "q_curr" not in st.session_state:
        qs = load_quiz_from_file()
        if qs: st.session_state.q_curr = random.choice(qs)
        else: st.error("無題庫"); return

    q = st.session_state.q_curr
    st.write(f"**Q: {q['q']}**")
    ans = st.radio("Ans", q['options'])
    if st.button("Submit"):
        if ans == q['ans']:
            st.balloons(); user["money"]+=300; check_mission(uid, user, "quiz_done")
            st.session_state.quiz_done = True
            save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]})
            st.rerun()
        else: st.error("Wrong"); st.session_state.quiz_done=True; st.rerun()

def page_lab(uid, user):
    st.title("🔬 邏輯實驗室")
    g = st.selectbox("Gate", list(SVG_LIB.keys()))
    c1, c2 = st.columns(2)
    a = c1.toggle("In A"); b = c2.toggle("In B")
    st.markdown(SVG_LIB[g], unsafe_allow_html=True)
    if a and b: check_mission(uid, user, "logic_state", "11")
    elif a or b: check_mission(uid, user, "logic_use")

def page_crypto(uid, user):
    st.title("🔐 密碼學")
    txt = st.text_input("Input", "123")
    check_mission(uid, user, "crypto_input", txt)
    st.write(f"Len: {len(txt)}")

def page_cli(uid, user):
    st.title("💻 CLI")
    if "hist" not in st.session_state: st.session_state.hist=[]
    for l in st.session_state.hist[-5:]: st.code(l)
    cmd = st.chat_input("cmd...")
    if cmd:
        st.session_state.hist.append(f"> {cmd}")
        check_mission(uid, user, "cli_input", cmd)
        valid = ["help", "bal", "scan", "sudo"]
        if cmd.split()[0] not in valid:
            if "err_cnt" not in st.session_state: st.session_state.err_cnt=0
            st.session_state.err_cnt+=1
            check_mission(uid, user, "cli_error", st.session_state.err_cnt)
            st.session_state.hist.append("Error")
        else:
            st.session_state.err_cnt=0
            st.session_state.hist.append("OK")
        st.rerun()

def page_bank(uid, user):
    st.title("🏦 銀行")
    st.metric("Cash", user['money']); st.metric("Bank", user.get('bank_deposit',0))
    amt = st.number_input("Amount", 1, 10000)
    if st.button("Deposit"):
        if user['money']>=amt:
            user['money']-=amt; user['bank_deposit']+=amt
            check_mission(uid, user, "bank_save"); st.rerun()
    if st.button("Withdraw"):
        if user['bank_deposit']>=amt:
            user['bank_deposit']-=amt; user['money']+=amt
            check_mission(uid, user, "bank_withdraw"); st.rerun()

# --- Main ---
def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    if "today_event" not in st.session_state: st.session_state.today_event = get_today_event()

    if not st.session_state.logged_in:
        st.title("🏙️ CityOS V20.0")
        u = st.text_input("User"); p = st.text_input("Pass", type="password")
        if st.button("Login"):
            db = load_db()
            if u in db["users"] and db["users"][u]["password"]==p:
                st.session_state.logged_in=True
                st.session_state.uid=u
                st.session_state.user=db["users"][u]
                st.rerun()
            else: st.error("Fail")
        return

    uid = st.session_state.uid
    user = st.session_state.user if uid=="frank" else load_db()["users"][uid]
    
    st.sidebar.title(f"🆔 {user['name']}")
    menu = {
        "✨ 大廳": "dash", "⚔️ 網路戰": "pvp", "🎯 任務": "miss", 
        "🛒 黑市": "shop", "🏦 銀行": "bank", "📝 測驗": "quiz",
        "🔬 實驗": "lab", "🔐 密碼": "cryp", "💻 CLI": "cli"
    }
    sel = st.sidebar.radio("Menu", list(menu.keys()))
    
    if menu[sel]=="dash": page_dashboard(uid, user)
    elif menu[sel]=="pvp": page_pvp(uid, user)
    elif menu[sel]=="shop": page_shop(uid, user)
    elif menu[sel]=="miss": page_missions(uid, user)
    elif menu[sel]=="quiz": page_quiz(uid, user)
    elif menu[sel]=="lab": page_lab(uid, user)
    elif menu[sel]=="cryp": page_crypto(uid, user)
    elif menu[sel]=="cli": page_cli(uid, user)
    elif menu[sel]=="bank": page_bank(uid, user)

if __name__ == "__main__":
    main()
