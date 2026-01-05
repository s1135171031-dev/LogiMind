# ==========================================
# 檔案: app.py (CityOS V22.0)
# ==========================================
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

st.set_page_config(page_title="CityOS V22.0", layout="wide", page_icon="🏙️", initial_sidebar_state="expanded")

# --- CSS ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #0E1117; }
    .stButton>button { border-radius: 8px; border: 1px solid #333; transition: all 0.3s; }
    .stButton>button:hover { border-color: #00FF00; color: #00FF00; box-shadow: 0 0 10px rgba(0,255,0,0.2); }
    h1, h2, h3 { font-family: 'Courier New', monospace; }
</style>
""", unsafe_allow_html=True)

# --- 頁面模組 ---

def page_dashboard(uid, user):
    st.title("🏙️ CityOS 中央控制台")
    
    # 每日快報
    evt = st.session_state.today_event
    icon = "📉" if "nerf" in str(evt['effect']) else "📈"
    msg_type = "error" if "nerf" in str(evt['effect']) else "success"
    
    with st.container(border=True):
        c1, c2 = st.columns([1, 6])
        c1.markdown(f"<div style='font-size:50px;text-align:center'>{icon}</div>", unsafe_allow_html=True)
        with c2:
            st.subheader(f"頭條：{evt['name']}")
            st.write(evt['desc'])
            if evt['effect']: 
                if msg_type=="success": st.success(f"系統影響: {evt['effect']}")
                else: st.error(f"系統影響: {evt['effect']}")

    st.markdown("---")
    t1, t2, t3 = st.tabs(["📊 系統監控", "⚙️ 安全設定", "📘 使用手冊"])

    with t1:
        if st.checkbox("🔴 啟動數據串流"):
            c1,c2 = st.columns(2)
            c1.line_chart(pd.DataFrame(np.random.randint(10,60,(20,1)), columns=["CPU"]))
            c2.bar_chart(pd.DataFrame(np.random.randint(200,900,(20,1)), columns=["NET"]))
        else: st.info("監控待命。")
            
    with t2:
        st.subheader("🛡️ 安全防禦設定 (PVP)")
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
        c1.metric("🔥 防火牆", inv.get("Firewall", 0), help="抵銷爆擊")
        c2.metric("💓 混亂之心", inv.get("Chaos Heart", 0), help="選項加倍")

    with t3:
        st.markdown("* **PVP**: 買腳本攻人，買牆防守。\n* **任務**: 完成後記得去領獎。")

def page_pvp(uid, user):
    st.title("⚔️ 網路戰 (Cyber Warfare)")
    db = load_db()
    targets = [u for u in db["users"] if u != uid and u != "frank"]
    
    if not targets: st.warning("無目標。"); return

    tid = st.selectbox("選擇目標 IP", targets)
    t_user = db["users"][tid]
    st.info(f"目標: {t_user['name']} | Lv.{t_user['level']}")
    
    has_script = user.get("inventory", {}).get("Brute Force Script", 0) > 0
    if not has_script:
        st.error("❌ 需要 [Brute Force Script] (請至黑市購買)。"); return

    with st.expander("攻擊配置", expanded=True):
        use_neck = False
        if user.get("inventory", {}).get("Clarity Necklace", 0) > 0:
            use_neck = st.checkbox("💎 使用 [Clarity Necklace] (選項減半)")

    if "pvp_stage" not in st.session_state: st.session_state.pvp_stage = "ready"
    
    if st.button("🚀 啟動入侵") or st.session_state.pvp_stage == "guessing":
        st.session_state.pvp_stage = "guessing"
        
        has_chaos = t_user.get("inventory", {}).get("Chaos Heart", 0) > 0
        n_opt = 4
        if has_chaos: n_opt *= 2
        if use_neck: n_opt = max(2, int(n_opt/2))
        
        if "pvp_opts" not in st.session_state:
            real = t_user.get("defense_code", "0000")
            opts = set([real])
            while len(opts) < n_opt: opts.add(f"{random.randint(0,9999):04d}")
            lst = list(opts); random.shuffle(lst)
            st.session_state.pvp_opts = lst
            st.session_state.pvp_real = real
            st.session_state.pvp_neck = use_neck
            st.session_state.pvp_chaos = has_chaos

        st.markdown(f"### 🔑 破解防禦層")
        if has_chaos: st.error("⚠️ 對方有 [混亂之心]！選項加倍！")
        if use_neck: st.success("💎 [清醒項鍊] 生效中。")
        
        cols = st.columns(4)
        for i, code in enumerate(st.session_state.pvp_opts):
            if cols[i%4].button(code, key=f"p_{code}"):
                # 消耗
                user["inventory"]["Brute Force Script"] -= 1
                if user["inventory"]["Brute Force Script"] <= 0: del user["inventory"]["Brute Force Script"]
                if st.session_state.pvp_neck:
                    user["inventory"]["Clarity Necklace"] -= 1
                    if user["inventory"]["Clarity Necklace"]<=0: del user["inventory"]["Clarity Necklace"]
                if st.session_state.pvp_chaos:
                    t_user["inventory"]["Chaos Heart"] -= 1
                    if t_user["inventory"]["Chaos Heart"]<=0: del t_user["inventory"]["Chaos Heart"]

                if code == st.session_state.pvp_real:
                    has_fw = t_user.get("inventory", {}).get("Firewall", 0) > 0
                    if has_fw:
                        loot = int(t_user["money"]*0.1)
                        t_user["inventory"]["Firewall"]-=1
                        if t_user["inventory"]["Firewall"]<=0: del t_user["inventory"]["Firewall"]
                        st.toast(f"攻擊成功(防火牆抵擋)！獲得 ${loot}", icon="🔥")
                    else:
                        loot = int(t_user["money"]*0.2)
                        st.balloons()
                        st.toast(f"💥 致命一擊！獲得 ${loot}", icon="💰")
                    t_user["money"] -= loot; user["money"] += loot
                    check_mission(uid, user, "pvp_win")
                else:
                    st.error("🚫 密碼錯誤！入侵失敗。")
                
                db["users"][uid] = user; db["users"][tid] = t_user
                save_db(db)
                del st.session_state.pvp_opts; del st.session_state.pvp_stage
                time.sleep(2); st.rerun()

def page_missions(uid, user):
    st.title("🎯 任務中心")
    st.caption("完成任務後，請務必點擊領取按鈕。")
    
    ms = load_missions_from_file()
    done = user.get("completed_missions", [])
    pending = user.get("pending_claims", [])
    
    # 1. 待領取區 (New!)
    if pending:
        st.markdown("### 🎁 待領取獎勵")
        st.info(f"你有 {len(pending)} 個任務已達成！")
        for mid in pending:
            if mid in ms: m = ms[mid]
            elif mid in HIDDEN_MISSIONS: m = HIDDEN_MISSIONS[mid]
            else: continue
            
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.write(f"**{m['title']}**"); c1.caption(m['desc']); c1.write(f"💰 ${m['reward']}")
                if c2.button("領取", key=f"clm_{mid}", type="primary"):
                    user["money"] += m['reward']
                    user["exp"] = user.get("exp", 0) + 100
                    user["pending_claims"].remove(mid)
                    user["completed_missions"].append(mid)
                    save_db({"users": load_db()["users"]|{uid:user}, "bbs":[]})
                    st.balloons(); st.toast(f"已領取 ${m['reward']}"); time.sleep(1); st.rerun()
        st.markdown("---")

    # 2. 任務列表
    t1, t2 = st.tabs(["🚧 進行中", "✅ 已完成"])
    with t1:
        cnt = 0
        for mid, m in ms.items():
            if mid not in done and mid not in pending and cnt<8:
                with st.container(border=True):
                    st.write(f"**{m['title']}**")
                    st.caption(m['desc'])
                    st.write(f"報酬: ${m['reward']}")
                cnt+=1
        if cnt==0: st.info("無可接取任務。")
    
    with t2:
        for mid in reversed(done):
            title = ""
            if mid in ms: title = ms[mid]['title']
            elif mid in HIDDEN_MISSIONS: title = HIDDEN_MISSIONS[mid]['title']
            if title: st.caption(f"✅ {title} (已完成)")

def page_shop(uid, user):
    st.title("🛒 地下黑市")
    disc = 0.7 if st.session_state.today_event["effect"]=="shop_discount" else 1.0
    if disc<1: st.success("🔥 限時 7 折！")

    cols = st.columns(3)
    for i, (k, v) in enumerate(ITEMS.items()):
        p = int(v['price']*disc)
        with cols[i%3].container(border=True):
            st.subheader(k)
            st.caption(v['desc'])
            st.write(f"**${p:,}**")
            st.caption(f"持有: {user.get('inventory',{}).get(k,0)}")
            if st.button("購買", key=f"b_{k}"):
                if user['money']>=p:
                    user['money']-=p
                    user.setdefault("inventory",{})[k] = user.get("inventory",{}).get(k,0)+1
                    check_mission(uid, user, "shop_buy")
                    st.toast(f"已購買 {k}"); time.sleep(0.5); st.rerun()
                else: st.error("資金不足")

def page_bank(uid, user):
    st.title("🏦 銀行")
    c1, c2 = st.columns(2)
    c1.metric("存款", f"${user.get('bank_deposit',0):,}"); c2.metric("現金", f"${user['money']:,}")
    amt = st.number_input("金額", 0, 100000)
    b1, b2 = st.columns(2)
    if b1.button("存入") and user['money']>=amt:
        user['money']-=amt; user['bank_deposit']+=amt
        check_mission(uid, user, "bank_save"); st.rerun()
    if b2.button("提款") and user['bank_deposit']>=amt:
        user['bank_deposit']-=amt; user['money']+=amt
        check_mission(uid, user, "bank_withdraw"); st.rerun()

def page_quiz(uid, user):
    st.title("📝 每日測驗")
    if st.session_state.get("quiz_done"): st.info("今日已完成"); return
    if "q_curr" not in st.session_state:
        qs = load_quiz_from_file()
        st.session_state.q_curr = random.choice(qs) if qs else None
    
    if not st.session_state.q_curr: st.error("無題庫"); return
    q = st.session_state.q_curr
    st.write(f"**Q: {q['q']}**")
    ans = st.radio("Ans", q['options'])
    if st.button("送出"):
        if ans == q['ans']:
            st.balloons(); user["money"]+=300; check_mission(uid, user, "quiz_done")
            st.session_state.quiz_done = True
            save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]})
            st.rerun()
        else: st.error("錯誤"); st.session_state.quiz_done=True; st.rerun()

def page_lab(uid, user):
    st.title("🔬 邏輯實驗室")
    g = st.selectbox("Gate", list(SVG_LIB.keys()))
    c1, c2 = st.columns(2)
    a = c1.toggle("In A"); b = c2.toggle("In B")
    st.markdown(SVG_LIB[g], unsafe_allow_html=True)
    if a and b: check_mission(uid, user, "logic_state", "11")

def page_crypto(uid, user):
    st.title("🔐 密碼學")
    txt = st.text_input("輸入文字", "ABC")
    check_mission(uid, user, "crypto_input", txt)
    st.code("".join([chr(ord(c)+3) if c.isalpha() else c for c in txt.upper()]))

def page_cli(uid, user):
    st.title("💻 CLI")
    if "hist" not in st.session_state: st.session_state.hist=[]
    for l in st.session_state.hist[-5:]: st.code(l)
    cmd = st.chat_input("cmd...")
    if cmd:
        st.session_state.hist.append(f"> {cmd}")
        check_mission(uid, user, "cli_input", cmd)
        if cmd not in ["help", "bal", "scan", "sudo"]:
            st.session_state.err_cnt = st.session_state.get("err_cnt", 0) + 1
            check_mission(uid, user, "cli_error", st.session_state.err_cnt)
            st.session_state.hist.append("Error")
        else: st.session_state.err_cnt=0; st.session_state.hist.append("OK")
        st.rerun()

def page_leaderboard(uid, user):
    st.title("🏆 名人堂")
    db = load_db()
    data = [{"User":u['name'], "Job":u['job'], "Assets":u['money']+u.get('bank_deposit',0)} for u in db['users'].values()]
    st.dataframe(pd.DataFrame(data).sort_values("Assets", ascending=False), use_container_width=True)

# --- Main ---
def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    if "today_event" not in st.session_state: st.session_state.today_event = get_today_event()

    if not st.session_state.logged_in:
        st.title("🏙️ CityOS V22.0")
        t1, t2 = st.tabs(["登入", "註冊"])
        with t1:
            u = st.text_input("User"); p = st.text_input("Pass", type="password")
            if st.button("Login"):
                db = load_db()
                if u in db["users"] and db["users"][u]["password"]==p:
                    st.session_state.logged_in=True; st.session_state.uid=u; st.session_state.user=db["users"][u]
                    # 挖礦結算
                    mine = st.session_state.user.get("inventory",{}).get("Mining GPU",0)*100
                    if mine>0: 
                        if st.session_state.today_event['effect']=="mining_boost": mine=int(mine*1.5)
                        st.session_state.user['money']+=mine; st.toast(f"⛏️ 挖礦: +${mine}")
                    st.rerun()
                else: st.error("Fail"); log_intruder(u)
        with t2:
            nu = st.text_input("New User"); np = st.text_input("New Pass", type="password")
            if st.button("Sign Up"):
                db = load_db()
                if nu not in db["users"]:
                    db["users"][nu] = {"password":np, "name":nu, "job":"Novice", "money":1000, "level":1, "exp":0, "bank_deposit":0, "inventory":{}, "completed_missions":[], "pending_claims":[], "defense_code":"0000"}
                    save_db(db); st.success("OK! Please Login.")
                else: st.error("Exists")
        return

    uid = st.session_state.uid
    user = st.session_state.user if uid=="frank" else load_db()["users"].get(uid, st.session_state.user)
    
    st.sidebar.title(f"🆔 {user['name']}")
    menu = {"✨ 大廳":"dash", "⚔️ 網路戰":"pvp", "🎯 任務":"miss", "🛒 黑市":"shop", "🏦 銀行":"bank", "📝 測驗":"quiz", "🔬 實驗":"lab", "🔐 密碼":"cryp", "💻 CLI":"cli", "🏆 排名":"rank"}
    sel = st.sidebar.radio("Menu", list(menu.keys()))
    
    pg = menu[sel]
    if pg=="dash": page_dashboard(uid, user)
    elif pg=="pvp": page_pvp(uid, user)
    elif pg=="miss": page_missions(uid, user)
    elif pg=="shop": page_shop(uid, user)
    elif pg=="bank": page_bank(uid, user)
    elif pg=="quiz": page_quiz(uid, user)
    elif pg=="lab": page_lab(uid, user)
    elif pg=="cryp": page_crypto(uid, user)
    elif pg=="cli": page_cli(uid, user)
    elif pg=="rank": page_leaderboard(uid, user)

if __name__ == "__main__":
    main()
