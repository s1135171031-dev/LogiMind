# ==========================================
# 檔案名稱: app.py
# 版本: CityOS V21.0 (Complete Edition)
# 功能: 整合 V19 所有豐富功能 + V20 PVP 網路戰系統
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

# --- 頁面設定 ---
st.set_page_config(
    page_title="CityOS V21.0", 
    layout="wide", 
    page_icon="🏙️", 
    initial_sidebar_state="expanded"
)

# --- CSS 美化 ---
st.markdown("""
<style>
    /* 側欄與背景 */
    [data-testid="stSidebar"] { background-color: #0E1117; }
    
    /* 按鈕特效 */
    .stButton>button { 
        border-radius: 8px; 
        border: 1px solid #333; 
        transition: all 0.3s;
    }
    .stButton>button:hover {
        border-color: #00FF00;
        color: #00FF00;
        box-shadow: 0 0 10px rgba(0, 255, 0, 0.2);
    }
    
    /* 標題字型 */
    h1, h2, h3 { font-family: 'Courier New', monospace; }
    
    /* 進度條 */
    .stProgress > div > div > div > div { background-color: #00FF00; }
</style>
""", unsafe_allow_html=True)

# --- 功能模組 ---

def page_dashboard(uid, user):
    st.title("🏙️ CityOS 中央控制台")
    
    # --- 📰 每日快報 ---
    st.markdown("### 📰 每日快報 (Daily News)")
    evt = st.session_state.today_event
    
    msg_type = "info"
    icon = "📢"
    if evt['effect']:
        if "boost" in evt['effect'] or "discount" in evt['effect']:
            msg_type = "success"; icon = "📈"
        elif "nerf" in evt['effect'] or "attack" in evt['effect']:
            msg_type = "error"; icon = "📉"
    
    with st.container(border=True):
        col_icon, col_text = st.columns([1, 6])
        with col_icon:
            st.markdown(f"<div style='font-size: 50px; text-align: center;'>{icon}</div>", unsafe_allow_html=True)
        with col_text:
            st.subheader(f"頭條：{evt['name']}")
            st.write(f"{evt['desc']}")
            if evt['effect']:
                note = f"⚠️ 系統影響: {evt['effect']}"
                if msg_type == "success": st.success(note)
                elif msg_type == "error": st.error(note)
                else: st.info(note)

    st.markdown("---")

    # --- 儀表板分頁 (含安全設定) ---
    st.caption(f"User: {user['name']} | Status: Online | Role: {user['job']}")
    tab1, tab2, tab3, tab4 = st.tabs(["📊 系統監控", "⚙️ 安全設定 (PVP)", "📖 系統介紹", "📘 使用手冊"])

    with tab1:
        st.subheader("📡 即時數據監控")
        run_monitor = st.checkbox("🔴 啟動數據串流")
        c1, c2, c3 = st.columns(3)
        with c1: chart1 = st.empty()
        with c2: chart2 = st.empty()
        with c3: chart3 = st.empty()
        
        if run_monitor:
            while run_monitor:
                cpu = pd.DataFrame(np.random.randint(10, 60, size=(20, 1)), columns=["CPU%"])
                ram = pd.DataFrame(np.random.randint(40, 80, size=(20, 1)), columns=["RAM%"])
                net = pd.DataFrame(np.random.randint(200, 900, size=(20, 1)), columns=["Net"])
                chart1.line_chart(cpu, height=150)
                chart2.area_chart(ram, height=150, color="#00FF00")
                chart3.bar_chart(net, height=150, color="#FF0000")
                time.sleep(0.8)
        else:
            chart1.metric("CPU", "Idle", "0%")
            chart2.metric("RAM", "Stable", "4.2GB")
            chart3.metric("Network", "Connected", "1Gbps")

    with tab2:
        st.subheader("🛡️ 安全防禦設定")
        st.caption("設定您的 [防禦密碼]。當其他駭客 (PVP) 攻擊您時，必須猜中此密碼才能盜取資金。")
        
        # 顯示當前狀態
        st.info(f"當前防禦密碼: **** (隱藏中)")
        
        with st.form("set_defense_code"):
            new_code = st.text_input("輸入新防禦密碼 (4位數字)", max_chars=4, type="password")
            if st.form_submit_button("更新設定"):
                if len(new_code) == 4 and new_code.isdigit():
                    user["defense_code"] = new_code
                    save_db({"users": load_db()["users"] | {uid: user}, "bbs": load_db().get("bbs", [])})
                    st.success("防禦密碼已更新！系統安全性提升。")
                else:
                    st.error("格式錯誤：請輸入 4 位數字。")
                    
        st.markdown("---")
        st.write("#### 🎒 防禦庫存")
        inv = user.get("inventory", {})
        c1, c2 = st.columns(2)
        c1.metric("🔥 防火牆", inv.get("Firewall", 0), help="被猜中時抵銷爆擊傷害")
        c2.metric("💓 混亂之心", inv.get("Chaos Heart", 0), help="讓攻擊者選項加倍")

    with tab3:
        st.markdown("### 關於 CityOS V21.0")
        st.write("結合賽博龐克風格的作業系統，具備經濟、教育、任務與 **PVP 對戰** 功能。")

    with tab4:
        st.markdown("""
        ### 📘 攻略指南
        * **PVP 對戰**: 購買 `Brute Force Script` 入侵他人，猜對密碼即可偷錢。
        * **防守**: 購買 `Firewall` (減傷) 與 `Chaos Heart` (增加對手難度)。
        * **賺錢**: 每日挖礦、完成任務、每日測驗。
        * **彩蛋**: 嘗試尋找隱藏的指令或輸入特殊的數字。
        """)

def page_pvp(uid, user):
    st.title("⚔️ 網路戰 (Cyber Warfare)")
    st.caption("掃描網路節點，破解防禦密碼，獲取非法收益。")
    
    db = load_db()
    
    # 1. 掃描目標
    st.subheader("📡 網路掃描")
    targets = [u for u in db["users"] if u != uid and u != "frank"]
    
    if not targets:
        st.warning("⚠️ 網路上無其他可攻擊目標。")
        return

    target_uid = st.selectbox("鎖定目標 IP", targets)
    target_user = db["users"][target_uid]
    
    col_info, col_tool = st.columns(2)
    with col_info:
        st.info(f"目標: {target_user['name']} | 職業: {target_user['job']} | Lv.{target_user['level']}")
    
    with col_tool:
        # 檢查攻擊道具
        has_script = user.get("inventory", {}).get("Brute Force Script", 0) > 0
        if has_script:
            st.success(f"✅ 攻擊腳本就緒 (剩餘: {user['inventory']['Brute Force Script']})")
        else:
            st.error("❌ 缺少 [Brute Force Script]，無法發動攻擊。")
            if st.button("前往黑市購買"): st.switch_page("app.py") # 簡單導引，或讓使用者自己切換
            return

    # 2. 攻擊準備
    with st.expander("🛠️ 攻擊配置 (Loadout)", expanded=True):
        use_necklace = False
        has_necklace = user.get("inventory", {}).get("Clarity Necklace", 0) > 0
        
        if has_necklace:
            use_necklace = st.checkbox("💎 使用 [Clarity Necklace] (減少干擾選項)")
        else:
            st.caption("🔒 無 [Clarity Necklace] 可用")

    # 3. 執行入侵
    if "pvp_stage" not in st.session_state: st.session_state.pvp_stage = "ready"
    
    start_btn = st.button("🚀 啟動入侵程序 (Consume Script)")
    if start_btn or st.session_state.pvp_stage == "guessing":
        st.session_state.pvp_stage = "guessing"
        
        # 讀取防守方狀態
        has_chaos = target_user.get("inventory", {}).get("Chaos Heart", 0) > 0
        
        # 計算選項數量
        num_options = 4
        if has_chaos: num_options *= 2
        if use_necklace: num_options = max(2, int(num_options / 2))
        
        # 生成選項 (只生成一次)
        if "pvp_options" not in st.session_state:
            real_code = target_user.get("defense_code", "0000")
            options = set([real_code])
            while len(options) < num_options:
                options.add(f"{random.randint(0, 9999):04d}")
            
            opt_list = list(options)
            random.shuffle(opt_list)
            st.session_state.pvp_options = opt_list
            st.session_state.pvp_target_real = real_code
            st.session_state.pvp_use_necklace = use_necklace
            st.session_state.pvp_has_chaos = has_chaos

        st.markdown(f"### 🔑 正在破解防火牆... 請選擇密碼")
        if has_chaos: st.error("⚠️ 警告: 目標裝備了 [混亂之心]，選項數量加倍！")
        if use_necklace: st.success("💎 [清醒項鍊] 生效中，選項已過濾。")

        cols = st.columns(4)
        for idx, code in enumerate(st.session_state.pvp_options):
            if cols[idx % 4].button(code, key=f"guess_{code}"):
                # === 結算邏輯 ===
                
                # 1. 扣除攻擊者道具
                user["inventory"]["Brute Force Script"] -= 1
                if user["inventory"]["Brute Force Script"] <= 0: del user["inventory"]["Brute Force Script"]
                
                if st.session_state.pvp_use_necklace:
                    user["inventory"]["Clarity Necklace"] -= 1
                    if user["inventory"]["Clarity Necklace"] <= 0: del user["inventory"]["Clarity Necklace"]

                # 2. 扣除防守方道具
                if st.session_state.pvp_has_chaos:
                    target_user["inventory"]["Chaos Heart"] -= 1
                    if target_user["inventory"]["Chaos Heart"] <= 0: del target_user["inventory"]["Chaos Heart"]

                # 3. 判斷勝負
                if code == st.session_state.pvp_target_real:
                    has_firewall = target_user.get("inventory", {}).get("Firewall", 0) > 0
                    loot = 0
                    
                    if has_firewall:
                        loot = int(target_user["money"] * 0.1)
                        target_user["inventory"]["Firewall"] -= 1
                        if target_user["inventory"]["Firewall"] <= 0: del target_user["inventory"]["Firewall"]
                        st.toast(f"攻擊成功！對方防火牆吸收了傷害。獲得 ${loot}", icon="🔥")
                    else:
                        loot = int(target_user["money"] * 0.2)
                        st.balloons()
                        st.toast(f"💥 致命一擊！雙倍獎勵！獲得 ${loot}", icon="💰")
                    
                    target_user["money"] -= loot
                    user["money"] += loot
                    check_mission(uid, user, "pvp_win")
                else:
                    st.error("🚫 密碼錯誤！入侵失敗，警報已觸發。")
                    st.toast("攻擊失敗，道具已消耗。", icon="💀")

                # 4. 存檔與重置
                db["users"][uid] = user
                db["users"][target_uid] = target_user
                save_db(db)
                
                del st.session_state.pvp_options
                del st.session_state.pvp_stage
                time.sleep(2)
                st.rerun()

def page_missions(uid, user):
    st.title("🎯 任務中心")
    missions = load_missions_from_file()
    done = user.get("completed_missions", [])
    
    # 計算進度
    valid_done = [m for m in done if m in missions]
    total = len(missions)
    progress = len(valid_done)/total if total > 0 else 0
    st.progress(progress, text=f"一般任務完成度: {int(progress*100)}%")
    
    tab_n, tab_h = st.tabs(["📋 一般任務", "🏆 隱藏成就"])
    
    with tab_n:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🚧 待執行")
            count = 0
            for mid, m in missions.items():
                if mid not in done and count < 8:
                    with st.container(border=True):
                        st.write(f"**{m['title']}**")
                        st.caption(m['desc'])
                        st.write(f"💰 ${m['reward']}")
                    count += 1
        with col2:
            st.subheader("✅ 已完成")
            for mid in reversed(done):
                if mid in missions:
                    m = missions[mid]
                    with st.container(border=True):
                        st.write(f"~~{m['title']}~~")
                        st.caption(f"已領取 ${m['reward']}")
    
    with tab_h:
        st.subheader("🕵️ 傳奇隱藏成就")
        hidden_done = [mid for mid in done if mid.startswith("H_")]
        if not hidden_done:
            st.info("尚無隱藏成就。提示：嘗試讓錢歸零、亂打指令、或在PVP中獲勝。")
        else:
            for mid in hidden_done:
                if mid in HIDDEN_MISSIONS:
                    m = HIDDEN_MISSIONS[mid]
                    st.success(f"【{m['title']}】\n{m['desc']} (獎金 ${m['reward']})")

def page_quiz(uid, user):
    st.title("📝 每日工程測驗")
    if "quiz_today_done" not in st.session_state: st.session_state.quiz_today_done = False
    
    if st.session_state.quiz_today_done:
        st.info("✅ 今日測驗已完成，請明日再來。")
        return

    if "current_question" not in st.session_state:
        qs = load_quiz_from_file()
        if not qs: st.error("找不到題庫 (questions.txt)。"); return
        st.session_state.current_question = random.choice(qs)

    q = st.session_state.current_question
    st.write(f"### Q: {q['q']}")
    st.caption(f"Level: {q['level']} | ID: {q['id']}")
    choice = st.radio("Answer:", q['options'], key="quiz_opt")
    
    if st.button("提交"):
        if choice == q['ans']:
            st.balloons(); st.success("正確！ +$300")
            user["money"]+=300; user["exp"]+=50
            check_mission(uid, user, "quiz_done")
            save_db({"users": load_db()["users"]|{uid:user}, "bbs":[]})
            st.session_state.quiz_today_done=True
            del st.session_state.current_question
            st.rerun()
        else:
            st.error("錯誤！系統鎖定。")
            st.session_state.quiz_today_done=True
            del st.session_state.current_question
            st.rerun()

def page_digital_lab(uid, user):
    st.title("🔬 數位邏輯實驗室")
    t1, t2, t3 = st.tabs(["邏輯閘", "K-Map", "格雷碼"])
    
    with t1:
        g = st.selectbox("Gate", list(SVG_LIB.keys()))
        c1, c2 = st.columns(2)
        a = c1.toggle("Input A", False); b = c2.toggle("Input B", False)
        st.markdown(SVG_LIB[g], unsafe_allow_html=True)
        
        if a and b: check_mission(uid, user, "logic_state", extra_data="11")
        elif g and (a or b): check_mission(uid, user, "logic_use")
            
    with t2:
        st.write("2-Var K-Map 互動板")
        if "kmap" not in st.session_state: st.session_state.kmap=[0,0,0,0]
        c1, c2 = st.columns(2)
        c1.write("A=0"); c2.write("A=1")
        if c1.button(f"00: {st.session_state.kmap[0]}", key="k0"): st.session_state.kmap[0]^=1; st.rerun()
        if c1.button(f"01: {st.session_state.kmap[1]}", key="k1"): st.session_state.kmap[1]^=1; st.rerun()
        if c2.button(f"10: {st.session_state.kmap[2]}", key="k2"): st.session_state.kmap[2]^=1; st.rerun()
        if c2.button(f"11: {st.session_state.kmap[3]}", key="k3"): st.session_state.kmap[3]^=1; st.rerun()

    with t3:
        n = st.slider("Decimal Number", 0, 15, 5)
        gray = n ^ (n >> 1)
        st.metric("Gray Code", f"{gray:04b}")
        st.caption(f"Binary: {n:04b}")

def page_bank(uid, user):
    st.title("🏦 賽博銀行")
    c1, c2 = st.columns(2)
    c1.metric("銀行存款", f"${user.get('bank_deposit',0):,}")
    c2.metric("身上現金", f"${user['money']:,}")
    
    with st.expander("ATM 操作", expanded=True):
        amt = st.number_input("金額", 0, 1000000, 100)
        b1, b2 = st.columns(2)
        if b1.button("📥 存入") and user['money']>=amt:
            user['money']-=amt; user['bank_deposit']+=amt
            check_mission(uid, user, "bank_save"); st.rerun()
        if b2.button("📤 提款") and user['bank_deposit']>=amt:
            user['bank_deposit']-=amt; user['money']+=amt
            check_mission(uid, user, "bank_withdraw"); st.rerun()

def page_shop(uid, user):
    st.title("🛒 地下黑市")
    evt = st.session_state.today_event
    discount = 0.7 if evt["effect"] == "shop_discount" else 1.0
    if discount < 1: st.success("🔥 限時特價中 (7折)！")

    cols = st.columns(3)
    idx = 0
    for k, v in ITEMS.items():
        price = int(v['price'] * discount)
        with cols[idx%3].container(border=True):
            st.subheader(k)
            st.caption(v['desc'])
            st.write(f"**${price:,}**")
            
            # 顯示庫存
            owned = user.get("inventory", {}).get(k, 0)
            st.caption(f"持有: {owned}")
            
            if st.button("購買", key=f"buy_{k}"):
                if user['money']>=price:
                    user['money']-=price
                    user.setdefault("inventory", {})[k] = owned + 1
                    check_mission(uid, user, "shop_buy")
                    st.toast(f"已購買 {k}")
                    time.sleep(0.5); st.rerun()
                else: st.error("現金不足")
        idx+=1

def page_crypto(uid, user):
    st.title("🔐 密碼學中心")
    t1, t2 = st.tabs(["凱薩密碼", "摩斯電碼"])
    with t1:
        txt = st.text_input("輸入文字/數字", "HELLO")
        s = st.slider("偏移量", 1, 10, 3)
        check_mission(uid, user, "crypto_input", extra_data=txt)
        res = "".join([chr(ord(c)+s) if c.isalpha() else c for c in txt.upper()])
        st.success(f"加密結果: {res}")
    with t2:
        mt = st.text_input("輸入英文 (A-Z, 0-9)", "SOS").upper()
        res = " ".join([MORSE_CODE_DICT.get(c,c) for c in mt])
        st.code(res)

def page_leaderboard(uid, user):
    st.title("🏆 城市名人堂")
    db = load_db()
    data = []
    for u_id, u_data in db["users"].items():
        total = u_data.get("money",0) + u_data.get("bank_deposit",0)
        data.append({
            "User": u_data["name"], 
            "Job": u_data["job"], 
            "Level": u_data["level"],
            "Total Assets": total
        })
    df = pd.DataFrame(data).sort_values(by="Total Assets", ascending=False).reset_index(drop=True)
    df.index += 1
    st.dataframe(df, use_container_width=True)

def page_cli_os(uid, user):
    st.title("💻 駭客終端 (CLI)")
    st.markdown("---")
    
    if "cli_hist" not in st.session_state: 
        st.session_state.cli_hist = ["System Initialized...", "Type 'help' for commands."]
    
    # 顯示歷史
    for l in st.session_state.cli_hist[-8:]: st.code(l, language="bash")
    
    cmd = st.chat_input("輸入指令...")
    if cmd:
        st.session_state.cli_hist.append(f"user@cityos:~$ {cmd}")
        t = cmd.split()
        res = "Unknown command."
        
        check_mission(uid, user, "cli_input", extra_data=cmd)
        
        valid_cmds = ["help", "clear", "bal", "whoami", "scan", "sudo", "buy"]
        
        if t[0] not in valid_cmds:
            if "cli_err_cnt" not in st.session_state: st.session_state.cli_err_cnt = 0
            st.session_state.cli_err_cnt += 1
            check_mission(uid, user, "cli_error", extra_data=st.session_state.cli_err_cnt)
            res = f"Error: Command not found. (Fail count: {st.session_state.cli_err_cnt})"
        else:
            st.session_state.cli_err_cnt = 0
            if t[0]=="help": res = "Available: whoami, bal, scan, clear, sudo"
            elif t[0]=="clear": st.session_state.cli_hist=[]; st.rerun()
            elif t[0]=="bal": res = f"Cash: ${user['money']} | Bank: ${user.get('bank_deposit',0)}"
            elif t[0]=="whoami": res = f"User: {user['name']} | Job: {user['job']} | Level: {user['level']}"
            elif t[0]=="scan": res = "Scanning network... Found: Alice, Bob, Frank(Admin)"
            elif t[0]=="sudo" and len(t)>1 and t[1]=="su": res = "ACCESS DENIED... (Hidden Achievement Unlocked?)"
        
        st.session_state.cli_hist.append(res); st.rerun()

# --- 主程式 ---
def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    if "today_event" not in st.session_state: st.session_state.today_event = get_today_event()

    # --- 登入畫面 (恢復註冊分頁) ---
    if not st.session_state.logged_in:
        st.markdown("<h1 style='text-align: center;'>🏙️ CityOS V21.0</h1>", unsafe_allow_html=True)
        st.info(f"📅 今日狀態: {st.session_state.today_event['name']}")
        
        t1, t2 = st.tabs(["登入", "註冊"])
        with t1:
            u = st.text_input("帳號"); p = st.text_input("密碼", type="password")
            if st.button("登入"):
                db = load_db()
                if u in db["users"] and db["users"][u]["password"]==p:
                    st.session_state.logged_in=True
                    st.session_state.user_id=u
                    st.session_state.user_data=db["users"][u]
                    
                    # 挖礦獎勵
                    if "Mining GPU" in st.session_state.user_data.get("inventory", {}):
                        gpu_count = st.session_state.user_data["inventory"]["Mining GPU"]
                        bonus = gpu_count * 100
                        if st.session_state.today_event['effect'] == "mining_boost":
                            bonus = int(bonus * 1.5)
                        st.session_state.user_data["money"] += bonus
                        st.toast(f"⛏️ 挖礦收益: +${bonus}")
                        save_db(db)
                    st.rerun()
                else: st.error("登入失敗"); log_intruder(u)
        with t2:
            nu = st.text_input("新帳號"); np = st.text_input("新密碼", type="password")
            if st.button("註冊"):
                db = load_db()
                if nu not in db["users"]:
                    # 新註冊預設帶有 defense_code
                    db["users"][nu] = {
                        "password": np, "name": nu, "job": "Novice", 
                        "money": 1000, "level": 1, "exp": 0, "bank_deposit": 0, 
                        "defense_code": "0000",
                        "inventory": {}, "completed_missions": []
                    }
                    save_db(db); st.success("註冊成功！請登入。")
                else: st.error("帳號已存在")
        return

    # --- 登入後邏輯 ---
    uid = st.session_state.user_id
    user = st.session_state.user_data if uid == "frank" else load_db()["users"].get(uid, st.session_state.user_data)

    st.sidebar.title(f"🆔 {user['name']}")
    st.sidebar.caption(f"職業: {user['job']} | Lv.{user.get('level',1)}")
    st.sidebar.markdown("---")
    
    # 完整選單
    menu = {
        "✨ 系統大廳": "dashboard",
        "⚔️ 網路戰 (PVP)": "pvp",
        "🎯 任務中心": "missions",
        "📝 每日測驗": "quiz",
        "🏦 賽博銀行": "bank",
        "🛒 地下黑市": "shop",
        "🔬 邏輯實驗": "lab",
        "🔐 密碼學": "crypto",
        "💻 駭客終端": "cli",
        "🏆 名人堂": "leaderboard"
    }
    
    selection = st.sidebar.radio("導航選單", list(menu.keys()))
    page = menu[selection]

    if st.sidebar.button("🚪 安全登出"):
        st.session_state.logged_in=False; st.rerun()

    if page == "dashboard": page_dashboard(uid, user)
    elif page == "pvp": page_pvp(uid, user)
    elif page == "missions": page_missions(uid, user)
    elif page == "quiz": page_quiz(uid, user)
    elif page == "bank": page_bank(uid, user)
    elif page == "shop": page_shop(uid, user)
    elif page == "lab": page_digital_lab(uid, user)
    elif page == "crypto": page_crypto(uid, user)
    elif page == "cli": page_cli_os(uid, user)
    elif page == "leaderboard": page_leaderboard(uid, user)

if __name__ == "__main__":
    main()
