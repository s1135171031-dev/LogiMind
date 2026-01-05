# ==========================================
# 檔案: app.py (CityOS V25.0 Ultimate Fixed)
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
    HIDDEN_MISSIONS, get_npc_data  # <--- ✅ 關鍵修復：這裡加入了 get_npc_data
)

st.set_page_config(page_title="CityOS V25.0", layout="wide", page_icon="🏙️", initial_sidebar_state="expanded")

# --- CSS 美化 ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #0E1117; }
    .stButton>button { border-radius: 8px; border: 1px solid #333; transition: all 0.3s; }
    .stButton>button:hover { border-color: #00FF00; color: #00FF00; box-shadow: 0 0 10px rgba(0,255,0,0.2); }
    h1, h2, h3 { font-family: 'Courier New', monospace; }
    .stock-up { color: #00FF00; } .stock-down { color: #FF0000; }
</style>
""", unsafe_allow_html=True)

# --- 股市自動更新系統 ---
def update_stock_market():
    # 每 60 秒更新一次
    now = time.time()
    last_update = st.session_state.get("last_stock_update", 0)
    
    if now - last_update > 60:
        prices = {}
        history = st.session_state.get("stock_history", {})
        evt = st.session_state.get("today_event", {})
        
        for code, data in STOCKS_DATA.items():
            # 計算漲跌
            prev = st.session_state.get("stock_prices", {}).get(code, data['base'])
            change = random.uniform(-data['volatility'], data['volatility'])
            
            # 事件影響
            if evt.get("effect") == "mining_boost" and code == "CYBR": change += 0.05
            if evt.get("effect") == "hack_nerf" and code == "CYBR": change -= 0.05
            
            new_price = int(prev * (1 + change))
            new_price = max(1, new_price) # 最低 $1
            prices[code] = new_price
            
            # 更新歷史數據 (用於畫圖)
            if code not in history: history[code] = [data['base']] * 10
            history[code].append(new_price)
            if len(history[code]) > 20: history[code].pop(0) # 只留最近 20 筆
            
        st.session_state.stock_prices = prices
        st.session_state.stock_history = history
        st.session_state.last_stock_update = now

# --- 各頁面功能 ---

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
            if evt['effect']: st.info(f"系統影響: {evt['effect']}")
    
    # 背景執行股市更新
    update_stock_market()
    
    st.markdown("---")
    t1, t2, t3 = st.tabs(["📊 系統監控", "⚙️ 安全設定", "📘 使用手冊"])
    
    with t1:
        if st.checkbox("🔴 啟動數據串流 (Live Stream)"):
            c1, c2 = st.columns(2)
            c1.line_chart(pd.DataFrame(np.random.randint(10,60,(20,1)), columns=["CPU Usage"]), height=200)
            c2.area_chart(pd.DataFrame(np.random.randint(200,900,(20,1)), columns=["Network I/O"]), color="#00FF00", height=200)
        else: st.info("監控系統待命中...")

    with t2:
        st.subheader("🛡️ PVP 防禦設定")
        st.caption("設定防禦密碼，防止他人猜中盜取資金。")
        status = "✅ 已設定" if user.get("defense_code") != "0000" else "⚠️ 預設值 (危險)"
        st.info(f"防禦密碼狀態: {status}")
        
        with st.expander("修改防禦密碼"):
            nc = st.text_input("新密碼 (4位數字)", max_chars=4, type="password")
            if st.button("更新設定"):
                if len(nc)==4 and nc.isdigit():
                    user["defense_code"] = nc
                    save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]})
                    st.success("密碼已更新！安全等級提升。")
                else: st.error("格式錯誤，需為 4 位數字。")
        
        st.write("#### 🎒 防禦道具庫存")
        inv = user.get("inventory", {})
        c1, c2 = st.columns(2)
        c1.metric("🔥 防火牆", inv.get("Firewall", 0), help="被猜中時抵銷爆擊")
        c2.metric("💓 混亂之心", inv.get("Chaos Heart", 0), help="讓攻擊者選項加倍")

    with t3:
        st.markdown("* **股市**: 低買高賣賺價差，每分鐘更新。\n* **PVP**: 購買腳本入侵他人，猜中密碼可偷錢。\n* **任務**: 完成後需至看板手動領獎。")

def page_stock_market(uid, user):
    st.title("💹 夜之城證券交易所 (NCSE)")
    st.caption("市場價格每 60 秒自動波動，無需手動刷新。")
    
    update_stock_market() # 確保有數據
    prices = st.session_state.stock_prices
    history = st.session_state.stock_history
    u_stocks = user.get("stocks", {})

    # 1. 市場看板
    st.subheader("📊 市場行情")
    cols = st.columns(4)
    for i, (code, info) in enumerate(STOCKS_DATA.items()):
        curr = prices.get(code, info['base'])
        base = info['base']
        delta = curr - base
        with cols[i].container(border=True):
            st.metric(info['name'], f"${curr}", f"{delta}")
            st.line_chart(history.get(code, []), height=100)
            st.caption(info['desc'])
    
    st.markdown("---")
    
    # 2. 交易終端
    st.subheader("💻 交易終端")
    sel_code = st.selectbox("選擇股票代碼", list(STOCKS_DATA.keys()))
    price = prices.get(sel_code, 0)
    owned = u_stocks.get(sel_code, 0)
    
    c1, c2 = st.columns(2)
    
    # 買入區
    with c1.container(border=True):
        st.write(f"#### 🔵 買入 {sel_code}")
        st.write(f"單價: **${price}** | 現金: ${user['money']:,}")
        qb = st.number_input("買入股數", 1, 1000, 10, key="buy_q")
        cost = qb * price
        st.write(f"總成本: ${cost:,}")
        
        if st.button("下單買進", type="primary"):
            if user['money'] >= cost:
                user['money'] -= cost
                user.setdefault("stocks", {})[sel_code] = owned + qb
                check_mission(uid, user, "stock_buy")
                save_db({"users": load_db()["users"]|{uid:user}, "bbs":[]})
                st.toast(f"✅ 成交！買入 {qb} 股 {sel_code}")
                time.sleep(0.5); st.rerun()
            else: st.error("❌ 現金不足")
            
    # 賣出區
    with c2.container(border=True):
        st.write(f"#### 🔴 賣出 {sel_code}")
        st.write(f"持有: **{owned}** 股 | 市值: ${owned * price:,}")
        qs = st.number_input("賣出股數", 1, max(1, owned), 1, key="sell_q")
        earn = qs * price
        st.write(f"預計獲利: ${earn:,}")
        
        if st.button("下單賣出"):
            if owned >= qs:
                user['stocks'][sel_code] -= qs
                user['money'] += earn
                if user['stocks'][sel_code] == 0: del user['stocks'][sel_code]
                check_mission(uid, user, "stock_sell")
                save_db({"users": load_db()["users"]|{uid:user}, "bbs":[]})
                st.toast(f"💰 成交！賣出獲得 ${earn}")
                time.sleep(0.5); st.rerun()
            else: st.error("❌ 持倉不足")

    # 3. 資產表
    if u_stocks:
        st.markdown("---")
        st.subheader("💼 我的持倉")
        p_data = []
        for c, q in u_stocks.items():
            curr = prices.get(c, 0)
            p_data.append({"代碼": c, "名稱": STOCKS_DATA[c]['name'], "股數": q, "現價": curr, "市值": q*curr})
        st.dataframe(pd.DataFrame(p_data), use_container_width=True)
        total_val = sum([d["市值"] for d in p_data])
        st.metric("股票總資產", f"${total_val:,}")

def page_missions(uid, user):
    st.title("🎯 任務看板")
    ms = load_missions_from_file()
    
    # 1. 領獎區
    pending = user.get("pending_claims", [])
    if pending:
        st.success(f"🎁 恭喜！你有 {len(pending)} 個任務已完成，請領取獎勵。")
        for mid in pending:
            # 判斷是普通任務還是隱藏成就
            m = ms.get(mid, HIDDEN_MISSIONS.get(mid))
            if not m: continue
            
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{m['title']}**")
                c1.caption(m['desc'])
                c1.write(f"💰 獎勵: **${m['reward']}**")
                
                if c2.button("領取", key=f"clm_{mid}", type="primary"):
                    user["money"] += m['reward']
                    user["exp"] = user.get("exp", 0) + 100
                    user["pending_claims"].remove(mid)
                    user["completed_missions"].append(mid)
                    save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]})
                    # 領完後嘗試補新任務
                    check_mission(uid, user, "none") 
                    st.balloons()
                    st.toast(f"已領取 ${m['reward']}")
                    time.sleep(1); st.rerun()
    
    st.markdown("---")
    
    # 2. 進行中任務 (Max 3)
    st.subheader("📌 進行中任務 (Active)")
    active = user.get("active_missions", [])
    
    if not active:
        st.info("目前看板上沒有任務，請稍後或執行任意動作觸發刷新。")
        check_mission(uid, user, "refresh") # 嘗試觸發
    else:
        cols = st.columns(3)
        for i, mid in enumerate(active):
            if mid in ms:
                m = ms[mid]
                with cols[i%3].container(border=True):
                    st.info(f"任務 #{i+1}")
                    st.write(f"**{m['title']}**")
                    st.caption(m['desc'])
                    st.write(f"報酬: ${m['reward']}")
    
    with st.expander("查看已完成歷史"):
        st.write(f"已完成 {len(user.get('completed_missions',[]))} 個任務")

def page_quiz(uid, user):
    st.title("📝 每日挑戰賽")
    today_str = time.strftime("%Y-%m-%d")
    
    # 檢查是否已完成
    if user.get("last_quiz_date") == today_str:
        st.warning("⛔ 你今天已經挑戰過了！請明天再來。")
        return

    # 狀態機：介紹 -> 答題
    if "quiz_state" not in st.session_state: st.session_state.quiz_state = "intro"
    
    if st.session_state.quiz_state == "intro":
        st.markdown("""
        ### 挑戰規則
        1. **題目**: 隨機 1 題 (程式知識或邏輯)。
        2. **獎勵**: 答對獲得 **$500** + 100 EXP。
        3. **限制**: 每天僅限一次機會，答錯無獎勵。
        """)
        if st.button("🔥 開始挑戰", type="primary"):
            qs = load_quiz_from_file()
            if qs:
                st.session_state.q_curr = random.choice(qs)
                st.session_state.quiz_state = "playing"
                st.rerun()
            else: st.error("❌ 題庫讀取失敗 (questions.txt 未找到)")

    elif st.session_state.quiz_state == "playing":
        q = st.session_state.q_curr
        st.write(f"**Q: {q['q']}**")
        st.caption(f"難度: {q['level']}")
        ans = st.radio("請選擇答案:", q['options'])
        
        if st.button("送出答案"):
            if ans == q['ans']:
                st.balloons()
                st.success("✅ 恭喜答對！獲得 $500")
                user["money"] += 500
                user["exp"] = user.get("exp", 0) + 100
                check_mission(uid, user, "quiz_done")
            else:
                st.error(f"❌ 答錯了！正確答案是: {q['ans']}")
            
            # 記錄今天已做
            user["last_quiz_date"] = today_str
            save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]})
            
            # 清除狀態
            del st.session_state.q_curr
            del st.session_state.quiz_state
            time.sleep(2)
            st.rerun()

def page_lab(uid, user):
    st.title("🔬 邏輯實驗室 V2")
    st.caption("操作輸入開關，觀察邏輯閘輸出。")
    
    t1, t2 = st.tabs(["基礎閘 (Basic)", "進階閘 (Advanced)"])
    
    with t1:
        # AND, OR, NOT
        g = st.selectbox("選擇邏輯閘", ["AND", "OR", "NOT"])
        c1, c2 = st.columns(2)
        a = c1.toggle(f"{g} - Input A")
        b = False
        if g != "NOT": b = c2.toggle(f"{g} - Input B")
        
        st.markdown(SVG_LIB[g], unsafe_allow_html=True)
        
        # 判定
        res = 0
        if g=="AND": res = 1 if a and b else 0
        elif g=="OR": res = 1 if a or b else 0
        elif g=="NOT": res = 0 if a else 1
        
        st.metric("Output", res)
        if g=="AND" and res==1: check_mission(uid, user, "logic_state", "11")
    
    with t2:
        # NAND, NOR, XOR, XNOR, BUFFER
        g2 = st.selectbox("進階邏輯閘", ["NAND", "NOR", "XOR", "XNOR", "BUFFER"])
        c1, c2 = st.columns(2)
        a2 = c1.toggle(f"{g2} - Input A")
        b2 = False
        if g2 != "BUFFER": b2 = c2.toggle(f"{g2} - Input B")
        
        st.markdown(SVG_LIB.get(g2, "<div>SVG Not Found</div>"), unsafe_allow_html=True)
        
        # 判定
        res = 0
        if g2=="NAND": res = 0 if (a2 and b2) else 1
        elif g2=="NOR": res = 0 if (a2 or b2) else 1
        elif g2=="XOR": res = 1 if a2!=b2 else 0
        elif g2=="XNOR": res = 1 if a2==b2 else 0
        elif g2=="BUFFER": res = 1 if a2 else 0
        
        st.metric("Output", res)
        if res == 1: check_mission(uid, user, "logic_use")

def page_crypto(uid, user):
    st.title("🔐 密碼學中心")
    mode = st.selectbox("選擇加密模式", ["Caesar", "Morse", "Base64", "Atbash"])
    txt = st.text_input("輸入要加密的文字 (英文)", "HELLO")
    
    check_mission(uid, user, "crypto_input", txt)
    
    res = ""
    if mode == "Caesar":
        s = st.slider("偏移量 (Shift)", 1, 25, 3)
        res = "".join([chr(ord(c)+s) if c.isalpha() else c for c in txt.upper()])
    elif mode == "Morse":
        res = " ".join([MORSE_CODE_DICT.get(c,c) for c in txt.upper()])
    elif mode == "Base64":
        res = base64.b64encode(txt.encode()).decode()
    elif mode == "Atbash":
        # A<->Z
        res = "".join([chr(ord('Z') - (ord(c) - ord('A'))) if 'A'<=c<='Z' else c for c in txt.upper()])
        
    st.code(res)

def page_shop(uid, user):
    st.title("🛒 地下黑市")
    
    # 特價判定
    disc = 1.0
    if st.session_state.today_event['effect'] == "shop_discount":
        disc = 0.7
        st.success("🔥 今日特價：全館 7 折！")
    
    cols = st.columns(3)
    for i, (key, val) in enumerate(ITEMS.items()):
        price = int(val['price'] * disc)
        
        with cols[i%3].container(border=True):
            st.subheader(key)
            st.caption(val['desc'])
            st.write(f"**${price:,}**")
            
            owned = user.get("inventory", {}).get(key, 0)
            st.caption(f"持有: {owned}")
            
            if st.button("購買", key=f"buy_{key}"):
                if user['money'] >= price:
                    user['money'] -= price
                    user.setdefault("inventory", {})[key] = owned + 1
                    check_mission(uid, user, "shop_buy")
                    save_db({"users":load_db()["users"]|{uid:user}, "bbs":[]})
                    st.toast(f"已購買 {key}")
                    time.sleep(0.5); st.rerun()
                else:
                    st.error("現金不足！")

def page_pvp(uid, user):
    st.title("⚔️ 網路戰 (PVP)")
    db = load_db()
    # 篩選可攻擊目標
    targets = [u for u in db["users"] if u != uid and u != "frank"]
    
    if not targets:
        st.warning("目前網路上沒有其他目標。")
        return

    tid = st.selectbox("選擇入侵 IP", targets)
    t_user = db["users"][tid]
    st.info(f"鎖定目標: {t_user['name']} | Lv.{t_user['level']}")
    
    # 檢查是否有攻擊腳本
    if user.get("inventory", {}).get("Brute Force Script", 0) <= 0:
        st.error("❌ 無法攻擊：缺少 [Brute Force Script]。請至黑市購買。")
        return

    # 攻擊前配置
    with st.expander("🛠️ 攻擊配置 (Loadout)", expanded=True):
        use_neck = False
        if user.get("inventory", {}).get("Clarity Necklace", 0) > 0:
            use_neck = st.checkbox("💎 使用 [Clarity Necklace] (減少干擾選項)")

    # 狀態機
    if "pvp_st" not in st.session_state: st.session_state.pvp_st = "ready"
    
    if st.button("🚀 啟動入侵程序") or st.session_state.pvp_st == "go":
        st.session_state.pvp_st = "go"
        
        # 讀取對手防禦
        has_chaos = t_user.get("inventory", {}).get("Chaos Heart", 0) > 0
        n_opt = 8 if has_chaos else 4
        if use_neck: n_opt = max(2, int(n_opt/2))

        # 生成選項 (只生成一次)
        if "pvp_opts" not in st.session_state:
            real = t_user.get("defense_code", "0000")
            opts = set([real])
            while len(opts) < n_opt: opts.add(f"{random.randint(0,9999):04d}")
            l = list(opts); random.shuffle(l)
            st.session_state.pvp_opts = l
            st.session_state.pvp_real = real
            st.session_state.pvp_neck = use_neck
            st.session_state.pvp_chaos = has_chaos

        st.markdown("### 🔑 正在破解防火牆... 請選擇密碼")
        if has_chaos: st.error("⚠️ 警告：偵測到 [混亂之心]，干擾選項加倍！")
        if use_neck: st.success("💎 [清醒項鍊] 生效中，已過濾無效訊號。")

        cols = st.columns(4)
        for i, code in enumerate(st.session_state.pvp_opts):
            if cols[i%4].button(code, key=f"p_{code}"):
                # 消耗道具
                user["inventory"]["Brute Force Script"] -= 1
                if user["inventory"]["Brute Force Script"]==0: del user["inventory"]["Brute Force Script"]
                
                if st.session_state.pvp_neck:
                    user["inventory"]["Clarity Necklace"]-=1
                    if user["inventory"]["Clarity Necklace"]==0: del user["inventory"]["Clarity Necklace"]
                
                if st.session_state.pvp_chaos:
                    t_user["inventory"]["Chaos Heart"]-=1
                    if t_user["inventory"]["Chaos Heart"]==0: del t_user["inventory"]["Chaos Heart"]

                # 判定結果
                if code == st.session_state.pvp_real:
                    has_fw = t_user.get("inventory", {}).get("Firewall", 0) > 0
                    loot = int(t_user["money"] * (0.1 if has_fw else 0.2))
                    
                    if has_fw:
                        t_user["inventory"]["Firewall"]-=1
                        if t_user["inventory"]["Firewall"]==0: del t_user["inventory"]["Firewall"]
                        st.toast(f"攻擊成功！但被防火牆抵擋，僅搶得 ${loot}", icon="🔥")
                    else:
                        st.balloons()
                        st.toast(f"💥 致命一擊！對方無防備，搶得 ${loot}", icon="💰")
                    
                    t_user["money"] -= loot
                    user["money"] += loot
                    check_mission(uid, user, "pvp_win")
                else:
                    st.error("🚫 密碼錯誤！入侵失敗，警報已觸發。")
                
                # 存檔與清理
                db["users"][uid] = user
                db["users"][tid] = t_user
                save_db(db)
                del st.session_state.pvp_opts
                del st.session_state.pvp_st
                time.sleep(2); st.rerun()

def page_cli(uid, user):
    st.title("💻 駭客終端 (CLI)")
    if "cli_h" not in st.session_state: st.session_state.cli_h = ["System Ready..."]
    
    for l in st.session_state.cli_h[-6:]: st.code(l)
    
    cmd = st.chat_input("輸入指令...")
    if cmd:
        st.session_state.cli_h.append(f"user@cityos:~$ {cmd}")
        check_mission(uid, user, "cli_input", cmd)
        
        res = "OK"
        if cmd == "help": res = "Available: bal, whoami, scan, sudo, clear"
        elif cmd == "bal": res = f"Cash: ${user['money']}"
        elif cmd == "whoami": res = f"User: {user['name']} | Role: {user['job']}"
        elif cmd == "scan": res = "Scanning network... [Found 3 targets]"
        elif cmd == "clear": st.session_state.cli_h = []; st.rerun()
        elif cmd.startswith("sudo"): res = "Permission Denied. (Are you root?)"
        else:
            res = "Error: Command not found."
            st.session_state.cli_err = st.session_state.get("cli_err",0)+1
            check_mission(uid, user, "cli_error", st.session_state.cli_err)
        
        st.session_state.cli_h.append(res)
        st.rerun()

def page_bank(uid, user):
    st.title("🏦 賽博銀行")
    c1, c2 = st.columns(2)
    c1.metric("銀行存款", f"${user.get('bank_deposit',0):,}")
    c2.metric("身上現金", f"${user['money']:,}")
    
    amt = st.number_input("金額", 1, 100000, 100)
    b1, b2 = st.columns(2)
    
    if b1.button("📥 存入"):
        if user['money'] >= amt:
            user['money'] -= amt
            user['bank_deposit'] += amt
            check_mission(uid, user, "bank_save")
            st.rerun()
        else: st.error("現金不足")
            
    if b2.button("📤 提款"):
        if user.get('bank_deposit',0) >= amt:
            user['bank_deposit'] -= amt
            user['money'] += amt
            check_mission(uid, user, "bank_withdraw")
            st.rerun()
        else: st.error("存款不足")

def page_leaderboard(uid, user):
    st.title("🏆 城市名人堂")
    db = load_db()
    data = []
    for u in db['users'].values():
        assets = u['money'] + u.get('bank_deposit',0)
        # 加上股票價值
        stock_val = sum([q * st.session_state.get("stock_prices", {}).get(c, STOCKS_DATA[c]['base']) for c,q in u.get('stocks', {}).items()])
        data.append({
            "User": u['name'], 
            "Job": u['job'], 
            "Total Assets": assets + stock_val
        })
    st.dataframe(pd.DataFrame(data).sort_values("Total Assets", ascending=False), use_container_width=True)

# --- 主程式進入點 ---
def main():
    # 初始化 Session State
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    if "today_event" not in st.session_state: st.session_state.today_event = get_today_event()
    
    # 執行全域更新 (股市)
    update_stock_market()

    # 1. 登入/註冊畫面
    if not st.session_state.logged_in:
        st.title("🏙️ CityOS V25.0")
        t1, t2 = st.tabs(["登入 (Login)", "註冊 (Sign Up)"])
        
        with t1:
            u = st.text_input("帳號"); p = st.text_input("密碼", type="password")
            if st.button("登入"):
                db = load_db()
                if u in db["users"] and db["users"][u]["password"]==p:
                    st.session_state.logged_in=True
                    st.session_state.uid=u
                    st.session_state.user=db["users"][u]
                    
                    # 挖礦結算
                    mine = st.session_state.user.get("inventory",{}).get("Mining GPU",0)*100
                    if st.session_state.today_event['effect']=="mining_boost": mine=int(mine*1.5)
                    if mine>0: 
                        st.session_state.user['money']+=mine
                        st.toast(f"⛏️ 挖礦收益: +${mine}")
                        save_db(db)
                    st.rerun()
                else: 
                    st.error("登入失敗")
                    log_intruder(u)
                    
        with t2:
            nu = st.text_input("新帳號"); np = st.text_input("新密碼", type="password")
            if st.button("註冊"):
                db = load_db()
                if nu not in db["users"]:
                    # 呼叫 database.py 的 get_npc_data 進行初始化
                    db["users"][nu] = get_npc_data(nu, "Novice", 1, 1000)
                    db["users"][nu]["password"] = np
                    save_db(db)
                    st.success("註冊成功！請切換至登入頁面。")
                else: 
                    st.error("帳號已存在")
        return

    # 2. 登入後畫面
    uid = st.session_state.uid
    # 重新讀取 DB 以確保資料最新 (防止多人衝突)
    user = st.session_state.user if uid=="frank" else load_db()["users"].get(uid, st.session_state.user)

    st.sidebar.title(f"🆔 {user['name']}")
    st.sidebar.metric("💵 現金", f"${user['money']:,}")
    
    # 導航選單
    menu = {
        "✨ 系統大廳": "dash", 
        "💹 股市": "stock", 
        "🎯 任務": "miss", 
        "📝 測驗": "quiz", 
        "🔬 實驗": "lab", 
        "🔐 密碼": "cryp", 
        "🛒 黑市": "shop", 
        "🏦 銀行": "bank", 
        "⚔️ PVP": "pvp", 
        "💻 CLI": "cli",
        "🏆 排名": "rank"
    }
    
    selection = st.sidebar.radio("導航", list(menu.keys()))
    pg = menu[selection]

    # 頁面路由
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
    elif pg=="rank": page_leaderboard(uid, user)
    
    if st.sidebar.button("🚪 登出"):
        st.session_state.logged_in=False
        st.rerun()

if __name__ == "__main__":
    main()
