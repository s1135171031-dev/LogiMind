# ==========================================
# 檔案: app.py (完整整合版 V28.4)
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
st.set_page_config(page_title="CityOS V28.4", layout="wide", page_icon="🏙️", initial_sidebar_state="expanded")

# --- 2. CSS 美化與防閃爍 ---
st.markdown("""
<style>
    /* 全站深色背景，防止重新整理閃白光 */
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    
    /* 側邊欄與區塊設定 */
    [data-testid="stSidebar"] { background-color: #0E1117; border-right: 1px solid #333; }
    .stButton>button { border-radius: 4px; border: 1px solid #444; transition: all 0.3s; color: #EEE; background-color: #1E1E1E; }
    .stButton>button:hover { border-color: #00FF00; color: #00FF00; box-shadow: 0 0 8px rgba(0,255,0,0.3); }
    
    /* 字體設定 */
    h1, h2, h3 { font-family: 'Courier New', monospace; letter-spacing: -1px; }
    
    /* 啟動畫面特效文字 */
    .boot-text { font-family: 'Courier New'; color: #00FF00; font-size: 16px; margin-bottom: 2px; }
    
    /* 進度條顏色 (綠色駭客風) */
    .stProgress > div > div > div > div { background-color: #00FF00; }
    
    /* 其他細節 */
    .unread-badge { color: #FF4B4B; font-weight: bold; }
    .log-text { font-size: 12px; color: #888; font-family: monospace; border-left: 2px solid #333; padding-left: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 3. 系統啟動特效函式 ---
def play_boot_sequence():
    """模擬系統啟動的動畫"""
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown("### 🟢 SYSTEM BOOT SEQUENCE INITIATED")
            st.markdown("---")
            msg_spot = st.empty()
            bar = st.progress(0, text="Checking Hardware Integrity...")
            
            steps = [
                ("Loading Kernel Modules...", 15),
                ("Mounting Virtual File System...", 30),
                ("Decrypting User Profile...", 50),
                ("Establishing Neural Net Connection...", 70),
                ("Syncing Market Data Streams...", 85),
                ("Access Granted. Welcome back.", 100)
            ]
            
            for text, percent in steps:
                time.sleep(random.uniform(0.1, 0.4)) # 隨機延遲更有真實感
                msg_spot.markdown(f"<p class='boot-text'>> {text}</p>", unsafe_allow_html=True)
                bar.progress(percent, text=text)
            
            time.sleep(0.5)
    placeholder.empty()

# --- 4. 股市更新邏輯 ---
def update_stock_market():
    now = time.time()
    last_update = st.session_state.get("last_stock_update", 0)
    # 每 60 秒更新一次股價
    if now - last_update > 60:
        prices = {}
        history = st.session_state.get("stock_history", {})
        evt = st.session_state.get("today_event", {})
        
        for code, data in STOCKS_DATA.items():
            prev = st.session_state.get("stock_prices", {}).get(code, data['base'])
            
            # 隨機波動
            change = random.uniform(-data['volatility'], data['volatility'])
            
            # 事件影響
            if evt.get("effect") == "mining_boost" and code == "CYBR": change += 0.08
            if evt.get("effect") == "hack_nerf" and code == "CYBR": change -= 0.08
            if evt.get("effect") == "tech_boom" and code in ["CYBR", "CHIP"]: change += 0.05
            
            new_price = max(1, int(prev * (1 + change)))
            prices[code] = new_price
            
            # 記錄歷史走勢
            if code not in history: history[code] = [data['base']] * 10
            history[code].append(new_price)
            if len(history[code]) > 20: history[code].pop(0)
            
        st.session_state.stock_prices = prices
        st.session_state.stock_history = history
        st.session_state.last_stock_update = now

# --- 5. 各功能頁面 ---

def page_dashboard(uid, user):
    st.title("🏙️ CityOS 中央控制台")
    evt = st.session_state.today_event
    
    # 頂部狀態列
    c1, c2, c3 = st.columns([1, 4, 2])
    with c1:
        icon = "📉" if "nerf" in str(evt.get('effect','')) else "📈"
        st.markdown(f"<div style='font-size:50px;text-align:center'>{icon}</div>", unsafe_allow_html=True)
    with c2:
        st.subheader(f"今日頭條：{evt['name']}")
        st.write(f"📝 {evt['desc']}")
    with c3:
        if evt['effect']: st.info(f"⚡ 系統影響: {evt['effect']}")
    
    update_stock_market()
    st.markdown("---")
    
    # 儀表板下半部
    c_left, c_right = st.columns(2)
    with c_left:
        with st.expander("📜 系統更新日誌", expanded=True):
            st.markdown("""
            <div class="log-text">
            <b>[System V28.4] Stable Release</b><br>
            - Core: Dynamic Mission System Online.<br>
            - UI: Enhanced Dark Mode & Boot FX.<br>
            - Security: NPC Passwords Reset (Static).<br>
            - Network: Connection Stable.<br>
            </div>
            """, unsafe_allow_html=True)
    with c_right:
        with st.expander("📘 新手指引"):
            st.markdown("""
            1. **賺取第一桶金**: 參加 `每日挑戰` 或完成 `任務`。
            2. **投資理財**: 在 `股市` 低買高賣。
            3. **自我防衛**: 在 `PVP` 設置防禦密碼，購買防火牆。
            4. **安全登出**: 離開前請到登入頁面 `下載存檔`。
            """)
            
    if st.checkbox("🔴 顯示即時數據流", value=False):
        c1, c2 = st.columns(2)
        c1.line_chart(pd.DataFrame(np.random.randint(10,60,(20,1)), columns=["CPU Usage"]), height=150)
        c2.area_chart(pd.DataFrame(np.random.randint(200,900,(20,1)), columns=["Network I/O"]), color="#00FF00", height=150)

def page_mail(uid, user):
    st.title("📧 數位信箱")
    mailbox = user.get("mailbox", [])
    unread_count = len([m for m in mailbox if not m.get("read", False)])
    
    t1, t2 = st.tabs([f"📥 收件匣 ({unread_count})", "📤 撰寫郵件"])
    
    with t1:
        if not mailbox:
            st.info("📭 目前沒有郵件。")
        else:
            for i, mail in enumerate(mailbox):
                status = "🔴" if not mail.get("read") else "⚪"
                sender = mail.get('from', 'Unknown')
                with st.expander(f"{status} {mail['title']} (from: {sender})"):
                    st.caption(f"時間: {mail['time']}")
                    st.write(mail['msg'])
                    c1, c2 = st.columns([1, 5])
                    
                    if not mail.get("read"):
                        if c1.button("標為已讀", key=f"read_{i}"):
                            user["mailbox"][i]["read"] = True
                            save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]})
                            st.rerun()
                    
                    if c2.button("🗑️ 刪除", key=f"del_{i}"):
                        user["mailbox"].pop(i)
                        save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]})
                        st.rerun()
    with t2:
        db = load_db()
        targets = list(db["users"].keys())
        st.write("發送加密訊息給其他使用者。")
        to_who = st.selectbox("收件人 ID", targets)
        title = st.text_input("主旨")
        msg = st.text_area("內容")
        
        if st.button("🚀 發送傳輸"):
            if title and msg:
                if send_mail(to_who, uid, title, msg):
                    st.success("已發送！")
                    check_mission(uid, user, "send_mail", extra_data=to_who) # 觸發任務
                else:
                    st.error("發送失敗：使用者不存在。")
            else:
                st.warning("請填寫完整內容。")

def page_stock_market(uid, user):
    st.title("💹 證券交易所")
    update_stock_market()
    
    prices = st.session_state.stock_prices
    history = st.session_state.stock_history
    u_stocks = user.get("stocks", {})
    
    # 顯示行情看板
    cols = st.columns(4)
    for i, (code, info) in enumerate(STOCKS_DATA.items()):
        curr = prices.get(code, info['base'])
        base = info['base']
        delta = curr - base
        color = "normal"
        if delta > 0: color = "normal" 
        
        with cols[i].container(border=True):
            st.metric(info['name'], f"${curr}", f"{delta}")
            st.line_chart(history.get(code, []), height=80)
    
    st.markdown("---")
    
    # 交易操作區
    c1, c2 = st.columns(2)
    sel = st.selectbox("選擇股票代碼", list(STOCKS_DATA.keys()))
    price = prices.get(sel, 0)
    owned = u_stocks.get(sel, 0)
    
    st.write(f"目前持有 **{sel}**: {owned} 股 | 當前單價: **${price}**")
    
    with c1.container(border=True):
        st.subheader("買入")
        qb = st.number_input("數量", 1, 1000, 10, key="qb")
        cost = qb * price
        st.caption(f"總花費: ${cost}")
        if st.button("確認買入"):
            if user['money'] >= cost:
                user['money'] -= cost
                user.setdefault("stocks", {})[sel] = owned + qb
                # --- 動態任務觸發點 ---
                check_mission(uid, user, "stock_buy", extra_data=sel, extra_val=qb)
                # --------------------
                save_db({"users":load_db()["users"]|{uid:user},"bbs":[]})
                st.toast("✅ 交易成功!")
                st.rerun()
            else:
                st.error("餘額不足！")
                
    with c2.container(border=True):
        st.subheader("賣出")
        qs = st.number_input("數量", 1, max(1, owned), 1, key="qs")
        earn = qs * price
        st.caption(f"預計收入: ${earn}")
        if st.button("確認賣出"):
            if owned >= qs:
                user['stocks'][sel] -= qs
                user['money'] += earn
                if user['stocks'][sel] == 0: del user['stocks'][sel]
                check_mission(uid, user, "stock_sell")
                save_db({"users":load_db()["users"]|{uid:user},"bbs":[]})
                st.toast("✅ 交易成功!")
                st.rerun()
            else:
                st.error("持股不足")

def page_missions(uid, user):
    st.title("🎯 任務中心")
    
    # 1. 待領取獎勵區
    pending = user.get("pending_claims", [])
    if pending:
        st.success(f"🎁 你有 {len(pending)} 個獎勵待領取！")
        for i, m in enumerate(pending):
            # 相容舊版ID字串與新版字典物件
            title = m.get("title", "未知任務") if isinstance(m, dict) else "任務完成"
            reward = m.get("reward", 0) if isinstance(m, dict) else 100
            desc = m.get("desc", "") if isinstance(m, dict) else ""
            
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                c1.markdown(f"**{title}**")
                c1.caption(f"{desc} | 獎勵: ${reward}")
                
                if c2.button("領取賞金", key=f"clm_{i}"):
                    user["money"] += reward
                    user["pending_claims"].pop(i) # 移除
                    
                    # 記錄完成
                    mid = m.get("id", "old_id") if isinstance(m, dict) else m
                    user.setdefault("completed_missions", []).append(mid)
                    
                    # 存檔並刷新
                    save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]})
                    check_mission(uid, user, "none") # 觸發補貨檢查
                    st.toast(f"獲得 ${reward}")
                    st.rerun()
    
    st.markdown("---")
    
    # 2. 進行中任務
    active = user.get("active_missions", [])
    
    # 若無任務，嘗試刷新
    if not active:
        check_mission(uid, user, "refresh")
        st.rerun()
    
    st.subheader("📋 進行中合約")
    cols = st.columns(3)
    for i, m in enumerate(active):
        if isinstance(m, dict):
            with cols[i % 3].container(border=True):
                st.info(f"MISSION - {i+1}")
                st.markdown(f"#### {m['title']}")
                st.write(m['desc'])
                st.caption(f"目標代碼: `{m['target']}`")
                st.metric("賞金", f"${m['reward']}")

def page_quiz(uid, user):
    st.title("📝 每日技術挑戰")
    today = time.strftime("%Y-%m-%d")
    
    if user.get("last_quiz_date") == today:
        st.warning("⛔ 您今天已經完成挑戰，請明日再來。")
        return
        
    if "quiz_state" not in st.session_state:
        st.session_state.quiz_state = "intro"
        
    if st.session_state.quiz_state == "intro":
        st.write("回答一題電腦科學相關問題，答對即可獲得獎金。")
        if st.button("開始測驗"):
            qs = load_quiz_from_file()
            st.session_state.q_curr = random.choice(qs)
            st.session_state.quiz_state = "playing"
            st.rerun()
            
    elif st.session_state.quiz_state == "playing":
        q = st.session_state.q_curr
        st.markdown(f"### Q: {q['q']}")
        ans = st.radio("請選擇答案:", q['options'])
        
        if st.button("送出答案"):
            if ans == q['ans']:
                st.balloons()
                st.success("✅ 正確！獎金 +$50")
                user["money"] += 50
                check_mission(uid, user, "quiz_done")
            else:
                st.error(f"❌ 錯誤。正確答案是 {q['ans']}")
            
            user["last_quiz_date"] = today
            save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]})
            
            # 清理狀態
            del st.session_state.q_curr
            del st.session_state.quiz_state
            time.sleep(1.5)
            st.rerun()

def page_lab(uid, user):
    st.title("🔬 邏輯閘實驗室")
    st.caption("透過調整開關來理解數位邏輯。")
    
    t1, t2 = st.tabs(["基礎邏輯", "進階邏輯"])
    
    with t1:
        g = st.selectbox("選擇邏輯閘", ["AND", "OR", "NOT"])
        c1, c2 = st.columns(2)
        a = c1.toggle(f"Input A")
        b = False
        if g != "NOT":
            b = c2.toggle(f"Input B")
            
        st.html(f"<div style='width:200px;margin:auto;padding:20px'>{SVG_LIB[g]}</div>")
        
        res = 0
        if g == "AND": res = 1 if (a and b) else 0
        elif g == "OR": res = 1 if (a or b) else 0
        elif g == "NOT": res = 1 if not a else 0
        
        st.metric("Output Result", str(res), delta="High (1)" if res else "Low (0)")
        if g=="AND" and a and b: check_mission(uid, user, "logic_state", "11")

    with t2:
        g2 = st.selectbox("進階元件", ["NAND", "NOR", "XOR", "XNOR", "BUFFER"])
        c1, c2 = st.columns(2)
        a2 = c1.toggle(f"In A")
        b2 = False
        if g2 != "BUFFER":
            b2 = c2.toggle(f"In B")
            
        st.html(f"<div style='width:200px;margin:auto;padding:20px'>{SVG_LIB.get(g2,'')}</div>")
        
        res = 0
        if g2=="NAND": res = 0 if (a2 and b2) else 1
        elif g2=="NOR": res = 0 if (a2 or b2) else 1
        elif g2=="XOR": res = 1 if a2!=b2 else 0
        elif g2=="XNOR": res = 1 if a2==b2 else 0
        elif g2=="BUFFER": res = 1 if a2 else 0
        
        st.metric("Output Result", str(res), delta="High (1)" if res else "Low (0)")
        if res == 1: check_mission(uid, user, "logic_use")

def page_crypto(uid, user):
    st.title("🔐 密碼學解碼器")
    m = st.selectbox("加密模式", ["Caesar", "Morse", "Base64", "Atbash"])
    txt = st.text_input("輸入文字", "HELLO")
    
    # 觸發任務
    check_mission(uid, user, "crypto_input", txt)
    
    res = ""
    if m == "Caesar":
        s = st.slider("位移量 (Shift)", 1, 25, 3)
        temp_res = []
        for c in txt:
            if c.isalpha():
                base = ord('A') if c.isupper() else ord('a')
                temp_res.append(chr((ord(c) - base + s) % 26 + base))
            else:
                temp_res.append(c)
        res = "".join(temp_res)
        
    elif m == "Morse":
        res = " ".join([MORSE_CODE_DICT.get(c, c) for c in txt.upper()])
        
    elif m == "Base64":
        try:
            res = base64.b64encode(txt.encode()).decode()
        except:
            res = "Error"
            
    elif m == "Atbash":
        res = "".join([chr(ord('Z')-(ord(c)-ord('A'))) if 'A'<=c<='Z' else c for c in txt.upper()])
        
    st.code(res, language="text")

def page_shop(uid, user):
    st.title("🛒 地下黑市")
    st.write("購買非法駭客工具與防禦軟體。")
    
    # 事件折扣
    discount = 0.7 if st.session_state.today_event['effect'] == "shop_discount" else 1.0
    if discount < 1.0: st.success("🔥 黑色星期五：全館 7 折！")
    
    cols = st.columns(3)
    for i, (item_name, info) in enumerate(ITEMS.items()):
        price = int(info['price'] * discount)
        
        with cols[i % 3].container(border=True):
            st.write(f"**{item_name}**")
            st.caption(info['desc'])
            st.write(f"💲 {price}")
            
            if st.button("購買", key=f"buy_{item_name}"):
                if user['money'] >= price:
                    user['money'] -= price
                    user.setdefault("inventory", {})[item_name] = user.get("inventory", {}).get(item_name, 0) + 1
                    
                    # 觸發任務
                    check_mission(uid, user, "shop_buy", extra_data=item_name)
                    
                    save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]})
                    st.toast(f"已購買 {item_name}!")
                    st.rerun()
                else:
                    st.error("資金不足")

def page_pvp(uid, user):
    st.title("⚔️ 網路戰 (PVP)")
    st.caption("入侵其他使用者的系統以竊取資金。需要 'Brute Force Script'。")
    
    db = load_db()
    targets = [u for u in db["users"] if u != uid and u != "frank"]
    
    if not targets:
        st.warning("目前沒有可攻擊的目標。")
        return
        
    tid = st.selectbox("選擇目標 IP", targets)
    t_user = db["users"][tid]
    
    # 檢查道具
    scripts = user.get("inventory", {}).get("Brute Force Script", 0)
    st.write(f"持有入侵腳本: {scripts} 個")
    
    if scripts <= 0:
        st.error("❌ 你需要 'Brute Force Script' 才能發動攻擊。請去黑市購買。")
        return
    
    use_neck = False
    if user.get("inventory", {}).get("Clarity Necklace", 0) > 0:
        use_neck = st.checkbox("使用 Clarity Necklace (移除一半錯誤選項)")
        
    # 狀態機管理
    if "pvp_st" not in st.session_state:
        st.session_state.pvp_st = "ready"
        
    if st.button("🚀 啟動入侵程序") or st.session_state.pvp_st == "go":
        st.session_state.pvp_st = "go"
        
        # 讀取防守方資訊
        has_chaos = t_user.get("inventory", {}).get("Chaos Heart", 0) > 0
        n_opt = 8 if has_chaos else 4
        if use_neck: n_opt = max(2, int(n_opt/2))
        
        # 取得真實密碼 (NPC固定，玩家自訂)
        real_code = t_user.get("defense_code", "0000")
        
        # 生成選項 (只在第一次生成)
        if "pvp_opts" not in st.session_state:
            opts = set([real_code])
            while len(opts) < n_opt:
                opts.add(f"{random.randint(0,9999):04d}")
            
            l = list(opts)
            random.shuffle(l)
            
            # 存入 session
            st.session_state.pvp_opts = l
            st.session_state.pvp_real = real_code
            st.session_state.pvp_neck = use_neck
            st.session_state.pvp_chaos = has_chaos
            
            # 模擬運算延遲
            with st.spinner("正在暴力破解防火牆..."):
                time.sleep(1.0)
            
        st.write("### ⚠️ 防火牆回應中，請選擇正確密鑰：")
        cols = st.columns(4)
        
        for i, code in enumerate(st.session_state.pvp_opts):
            if cols[i % 4].button(code, key=f"p_{code}"):
                # 消耗道具
                user["inventory"]["Brute Force Script"] -= 1
                if user["inventory"]["Brute Force Script"] == 0: del user["inventory"]["Brute Force Script"]
                
                if st.session_state.pvp_neck and user.get("inventory", {}).get("Clarity Necklace", 0) > 0:
                     user["inventory"]["Clarity Necklace"] -= 1
                     if user["inventory"]["Clarity Necklace"] == 0: del user["inventory"]["Clarity Necklace"]
                
                if st.session_state.pvp_chaos and t_user.get("inventory", {}).get("Chaos Heart", 0) > 0:
                     t_user["inventory"]["Chaos Heart"] -= 1
                     if t_user["inventory"]["Chaos Heart"] == 0: del t_user["inventory"]["Chaos Heart"]
                
                # 判定結果
                if code == st.session_state.pvp_real:
                    has_fw = t_user.get("inventory", {}).get("Firewall", 0) > 0
                    loot_ratio = 0.1 if has_fw else 0.2
                    loot = int(t_user["money"] * loot_ratio)
                    
                    t_user["money"] -= loot
                    user["money"] += loot
                    
                    if has_fw:
                        t_user["inventory"]["Firewall"] -= 1
                        if t_user["inventory"]["Firewall"] == 0: del t_user["inventory"]["Firewall"]
                        st.toast(f"對方防火牆啟動，僅搶得 ${loot}")
                    else:
                        st.balloons()
                        st.toast(f"入侵成功！搶得 ${loot}")
                        
                    check_mission(uid, user, "pvp_win")
                else:
                    st.error("⛔ 密碼錯誤！入侵失敗。")
                    log_intruder(uid)
                
                # 存檔與重置
                db["users"][uid] = user
                db["users"][tid] = t_user
                save_db(db)
                
                del st.session_state.pvp_opts
                del st.session_state.pvp_st
                time.sleep(2)
                st.rerun()

def page_cli(uid, user):
    st.title("💻 終端機 (CLI)")
    st.markdown("模擬 Linux 終端機環境。輸入 `help` 查看指令。")
    
    if "cli_h" not in st.session_state:
        st.session_state.cli_h = ["CityOS Kernel v28.4 initialized...", "Type 'help' for commands."]
        
    # 顯示歷史紀錄 (最後 6 行)
    for l in st.session_state.cli_h[-6:]:
        st.code(l, language="bash")
        
    cmd = st.chat_input("user@cityos:~$")
    
    if cmd:
        st.session_state.cli_h.append(f"user@cityos:~$ {cmd}")
        check_mission(uid, user, "cli_input", extra_data=cmd)
        
        res = "OK"
        if cmd == "help": res = "Available commands: bal, whoami, scan, sudo, clear, exit"
        elif cmd == "bal": res = f"Current Balance: ${user['money']}"
        elif cmd == "whoami": res = f"User: {user['name']} | Level: {user['level']}"
        elif cmd == "scan": res = "Scanning network... No immediate threats found."
        elif cmd == "clear": 
            st.session_state.cli_h = []
            st.rerun()
        elif cmd.startswith("sudo"): 
            res = "Permission Denied: User is not in the sudoers file."
            if cmd == "sudo su": check_mission(uid, user, "cli_input", extra_data="sudo su")
        else: 
            res = f"bash: {cmd}: command not found"
            check_mission(uid, user, "cli_error", extra_val=st.session_state.get("cli_err",0)+1)
            
        st.session_state.cli_h.append(res)
        st.rerun()

def page_bank(uid, user):
    st.title("🏦 城市銀行")
    
    c1, c2 = st.columns(2)
    c1.metric("銀行存款", f"${user.get('bank_deposit',0):,}")
    c2.metric("身上現金", f"${user['money']:,}")
    
    st.write("存款可避免被駭客搶奪，但無法用於黑市交易。")
    
    amt = st.number_input("交易金額", 1, 100000, 100)
    
    b1, b2 = st.columns(2)
    
    if b1.button("存入現金"):
        if user['money'] >= amt:
            user['money'] -= amt
            user['bank_deposit'] = user.get('bank_deposit', 0) + amt
            # 觸發任務
            check_mission(uid, user, "bank_save", extra_val=amt)
            save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]})
            st.success("存入成功")
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("現金不足")
            
    if b2.button("提款"):
        if user.get('bank_deposit', 0) >= amt:
            user['bank_deposit'] -= amt
            user['money'] += amt
            check_mission(uid, user, "bank_withdraw")
            save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]})
            st.success("提款成功")
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("存款不足")

def page_leaderboard(uid, user):
    st.title("🏆 名人堂")
    db = load_db()
    data = []
    prices = st.session_state.get("stock_prices", {})
    
    for u in db['users'].values():
        assets = u['money'] + u.get('bank_deposit',0)
        # 計算股票價值
        stock_val = sum([q * prices.get(c, STOCKS_DATA[c]['base']) for c,q in u.get('stocks', {}).items()])
        total_assets = assets + stock_val
        
        data.append({
            "玩家": u['name'], 
            "職業": u['job'], 
            "總資產": total_assets,
            "等級": u['level']
        })
        
    df = pd.DataFrame(data).sort_values("總資產", ascending=False).reset_index(drop=True)
    st.dataframe(df, use_container_width=True)

def page_admin(uid, user):
    st.title("💀 管理員後台")
    st.warning("⚠️ 此區域僅限授權人員進入")
    
    db = load_db()
    all_users = db["users"]
    
    with st.expander("事件控制"):
        sel_evt = st.selectbox("強制觸發事件", [e['name'] for e in CITY_EVENTS])
        if st.button("設定事件"):
            for e in CITY_EVENTS:
                if e['name'] == sel_evt:
                    st.session_state.today_event = e
                    st.success(f"事件已更換為: {sel_evt}")
                    st.rerun()
                    
    with st.expander("廣播系統"):
        bc_msg = st.text_input("廣播訊息內容")
        if st.button("發送全域廣播"):
            for u in all_users:
                send_mail(u, "System Admin", "📢 系統緊急廣播", bc_msg)
            st.success("已發送至所有用戶信箱")

# --- 6. 主程式進入點 ---
def main():
    # 初始化 Session State
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    if "today_event" not in st.session_state: st.session_state.today_event = get_today_event()
    update_stock_market()

    # --- 登入頁面 ---
    if not st.session_state.logged_in:
        st.title("🏙️ CityOS V28.4 (Secure Boot)")
        
        # 存檔管理區
        with st.expander("💾 遊戲存檔管理 (備份/還原)", expanded=False):
            c1, c2 = st.columns(2)
            with c1:
                st.write("🔽 **備份存檔**")
                try:
                    with open("cityos_users.json", "r", encoding="utf-8") as f:
                        st.download_button("下載 .json 檔案", f, "cityos_save.json", "application/json")
                except:
                    st.warning("尚無資料庫檔案")
            with c2:
                st.write("🔼 **恢復存檔**")
                uploaded_file = st.file_uploader("上傳 .json", type=["json"])
                if uploaded_file is not None:
                    try:
                        data = json.load(uploaded_file)
                        with open("cityos_users.json", "w", encoding="utf-8") as f:
                            json.dump(data, f, ensure_ascii=False, indent=4)
                        st.success("✅ 存檔已恢復！請重新登入。")
                        time.sleep(1)
                        st.rerun()
                    except:
                        st.error("❌ 檔案格式錯誤")
        
        st.markdown("---")
        
        # 登入/註冊 Tabs
        t1, t2 = st.tabs(["🔑 使用者登入", "📝 新用戶註冊"])
        
        with t1:
            u = st.text_input("帳號 (ID)")
            p = st.text_input("密碼", type="password")
            if st.button("連線登入", type="primary"):
                db = load_db()
                if u in db["users"] and db["users"][u]["password"] == p:
                    # === 播放啟動特效 ===
                    play_boot_sequence()
                    # ==================
                    st.session_state.logged_in = True
                    st.session_state.uid = u
                    st.session_state.user = db["users"][u]
                    st.rerun()
                else:
                    st.error("⛔ 登入失敗：帳號或密碼錯誤")
                    log_intruder(u)
                    
        with t2:
            nu = st.text_input("設定新帳號")
            np = st.text_input("設定新密碼", type="password")
            nn = st.text_input("設定顯示暱稱")
            if st.button("建立帳戶"):
                if len(np) <= 4:
                    st.error("密碼長度需大於 4 碼")
                elif nu and nn:
                    db = load_db()
                    if nu not in db["users"]:
                        db["users"][nu] = get_npc_data(nn, "Novice", 1, 500)
                        db["users"][nu]["password"] = np
                        save_db(db)
                        st.success("✅ 註冊成功！請切換至登入頁籤。")
                    else:
                        st.error("此帳號已被使用")
        return

    # --- 登入後的主介面 ---
    uid = st.session_state.uid
    # 重新讀取最新的 User 資料 (確保金錢等狀態同步)
    user = st.session_state.user if uid == "frank" else load_db()["users"].get(uid, st.session_state.user)
    
    # 側邊欄
    unread = len([m for m in user.get("mailbox", []) if not m.get("read")])
    noti = f"🔴{unread}" if unread > 0 else ""
    
    st.sidebar.title(f"🆔 {user['name']}")
    st.sidebar.caption(f"Level: {user['level']} | Job: {user['job']}")
    st.sidebar.metric("現金餘額", f"${user['money']:,}")
    
    menu = {
        "✨ 中央大廳": "dash",
        f"📧 信箱 {noti}": "mail",
        "💹 證券交易所": "stock",
        "🎯 任務中心": "miss",
        "📝 每日挑戰": "quiz",
        "🔬 邏輯實驗室": "lab",
        "🔐 密碼學": "cryp",
        "🛒 地下黑市": "shop",
        "🏦 城市銀行": "bank",
        "⚔️ 網路戰 PVP": "pvp",
        "💻 終端機 CLI": "cli",
        "🏆 名人堂": "rank"
    }
    
    if uid == "frank":
        menu["💀 系統管理"] = "admin"
        
    selection = st.sidebar.radio("導航選單", list(menu.keys()))
    pg = menu[selection]

    # 頁面路由
    if pg == "dash": page_dashboard(uid, user)
    elif pg == "mail": page_mail(uid, user)
    elif pg == "stock": page_stock_market(uid, user)
    elif pg == "miss": page_missions(uid, user)
    elif pg == "quiz": page_quiz(uid, user)
    elif pg == "lab": page_lab(uid, user)
    elif pg == "cryp": page_crypto(uid, user)
    elif pg == "shop": page_shop(uid, user)
    elif pg == "bank": page_bank(uid, user)
    elif pg == "pvp": page_pvp(uid, user)
    elif pg == "cli": page_cli(uid, user)
    elif pg == "rank": page_leaderboard(uid, user)
    elif pg == "admin": page_admin(uid, user)
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 安全登出"):
        st.session_state.logged_in = False
        st.session_state.clear()
        st.rerun()

if __name__ == "__main__":
    main()

