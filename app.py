# ==========================================
# 檔案: app.py (CityOS V23.0 Ultimate)
# ==========================================
import streamlit as st
import random
import time
import pandas as pd
import numpy as np
from config import CITY_EVENTS, ITEMS, SVG_LIB, MORSE_CODE_DICT, STOCKS_DATA
from database import (
    load_db, save_db, check_mission, get_today_event, 
    log_intruder, load_quiz_from_file, load_missions_from_file, 
    HIDDEN_MISSIONS
)

st.set_page_config(page_title="CityOS V23.0", layout="wide", page_icon="🏙️", initial_sidebar_state="expanded")

# --- CSS 美化 ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #0E1117; }
    .stButton>button { border-radius: 8px; border: 1px solid #333; transition: all 0.3s; }
    .stButton>button:hover { border-color: #00FF00; color: #00FF00; box-shadow: 0 0 10px rgba(0,255,0,0.2); }
    h1, h2, h3 { font-family: 'Courier New', monospace; }
</style>
""", unsafe_allow_html=True)

# --- 輔助函式: 股市生成 ---
def generate_market_data():
    if "stock_prices" not in st.session_state:
        prices = {}
        history = {}
        evt = st.session_state.get("today_event", {})
        for code, data in STOCKS_DATA.items():
            change = random.uniform(-data['volatility'], data['volatility'])
            # 事件影響
            if evt.get("effect") == "mining_boost" and code == "CYBR": change += 0.1
            if evt.get("effect") == "hack_nerf" and code == "CYBR": change -= 0.1
            
            cp = int(data['base'] * (1 + change))
            prices[code] = max(1, cp)
            
            # 假歷史
            hist = []
            cur = data['base']
            for _ in range(15):
                cur = cur * (1 + random.uniform(-0.05, 0.05))
                hist.append(cur)
            hist.append(cp)
            history[code] = hist
        st.session_state.stock_prices = prices
        st.session_state.stock_history = history

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
    
    st.markdown("---")
    t1, t2, t3 = st.tabs(["📊 監控", "⚙️ 安全設定", "📘 指南"])
    
    with t1:
        if st.checkbox("🔴 啟動數據串流"):
            c1, c2 = st.columns(2)
            c1.line_chart(pd.DataFrame(np.random.randint(10,60,(20,1)), columns=["CPU"]))
            c2.area_chart(pd.DataFrame(np.random.randint(200,900,(20,1)), columns=["NET"]), color="#00FF00")
        else: st.info("系統待命中...")

    with t2:
        st.subheader("🛡️ PVP 防禦設定")
        st.caption("設定防禦密碼，防止他人猜中偷錢。")
        st.info("當前密碼: **** (隱藏)")
        with st.form("set_def"):
            nc = st.text_input("新防禦密碼 (4位數字)", max_chars=4, type="password")
            if st.form_submit_button("更新"):
                if len(nc)==4 and nc.isdigit():
                    user["defense_code"] = nc
                    save_db({"users": load_db()["users"]|{uid:user}, "bbs":[]})
                    st.success("密碼已更新！")
                else: st.error("格式錯誤")
        
        st.write("#### 🎒 防禦道具庫存")
        inv = user.get("inventory", {})
        c1, c2 = st.columns(2)
        c1.metric("🔥 防火牆", inv.get("Firewall", 0), help="抵銷傷害")
        c2.metric("💓 混亂之心", inv.get("Chaos Heart", 0), help="選項加倍")

    with t3:
        st.markdown("* **股市**: 低買高賣賺價差。\n* **PVP**: 買腳本攻人，猜密碼。\n* **任務**: 達成後需手動領獎。")

def page_stock_market(uid, user):
    

[Image of stock market chart]

    st.title("💹 夜之城證券交易所 (NCSE)")
    generate_market_data()
    prices = st.session_state.stock_prices
    history = st.session_state.stock_history
    u_stocks = user.get("stocks", {})

    st.subheader("📊 市場行情")
    if st.button("🔄 刷新報價 (模擬隔日)"):
        del st.session_state.stock_prices
        generate_market_data()
        st.rerun()

    cols = st.columns(4)
    for i, (code, info) in enumerate(STOCKS_DATA.items()):
        curr = prices[code]
        delta = curr - info['base']
        with cols[i].container(border=True):
            st.metric(f"{info['name']}", f"${curr}", f"{delta}")
            st.line_chart(history[code], height=100)
            st.caption(info['desc'])

    st.markdown("---")
    st.subheader("💻 交易終端")
    sel_code = st.selectbox("選擇股票", list(STOCKS_DATA.keys()))
    sel_price = prices[sel_code]
    owned = u_stocks.get(sel_code, 0)

    c1, c2 = st.columns(2)
    with c1.container(border=True):
        st.write("#### 🔵 買入")
        st.write(f"單價: **${sel_price}** | 現金: ${user['money']:,}")
        qty_b = st.number_input("數量", 1, 1000, 10, key="buy_q")
        cost = qty_b * sel_price
        st.write(f"總成本: ${cost:,}")
        if st.button("買入", type="primary"):
            if user['money'] >= cost:
                user['money'] -= cost
                user.setdefault("stocks", {})[sel_code] = owned + qty_b
                check_mission(uid, user, "stock_buy")
                st.toast(f"已買入 {qty_b} 股 {sel_code}")
                save_db({"users": load_db()["users"]|{uid:user}, "bbs":[]})
                time.sleep(1); st.rerun()
            else: st.error("現金不足")

    with c2.container(border=True):
        st.write("#### 🔴 賣出")
        st.write(f"持有: **{owned}** 股 | 市值: ${owned*sel_price:,}")
        qty_s = st.number_input("數量", 1, max(1, owned), 1, key="sell_q")
        earn = qty_s * sel_price
        st.write(f"預計獲利: ${earn:,}")
        if st.button("賣出"):
            if owned >= qty_s:
                user['stocks'][sel_code] -= qty_s
                user['money'] += earn
                if user['stocks'][sel_code] == 0: del user['stocks'][sel_code]
                check_mission(uid, user, "stock_sell")
                st.toast(f"已賣出獲得 ${earn}")
                save_db({"users": load_db()["users"]|{uid:user}, "bbs":[]})
                time.sleep(1); st.rerun()
            else: st.error("持倉不足")

    st.markdown("---")
    st.subheader("💼 資產組合")
    if not u_stocks: st.info("無持倉。")
    else:
        p_data = [{"代碼":c, "股數":q, "現價":prices.get(c,0), "市值":q*prices.get(c,0)} for c,q in u_stocks.items()]
        st.dataframe(pd.DataFrame(p_data), use_container_width=True)
        total_val = sum([d["市值"] for d in p_data])
        st.metric("股票總市值", f"${total_val:,}")

def page_pvp(uid, user):
    st.title("⚔️ 網路戰 (PVP)")
    db = load_db()
    targets = [u for u in db["users"] if u != uid and u != "frank"]
    if not targets: st.warning("無目標。"); return

    tid = st.selectbox("目標 IP", targets)
    t_user = db["users"][tid]
    st.info(f"目標: {t_user['name']} | Lv.{t_user['level']}")
    
    if user.get("inventory", {}).get("Brute Force Script", 0) <= 0:
        st.error("❌ 缺少攻擊腳本 (Brute Force Script)，請至黑市購買。"); return

    with st.expander("🛠️ 攻擊配置", expanded=True):
        use_neck = False
        if user.get("inventory", {}).get("Clarity Necklace", 0) > 0:
            use_neck = st.checkbox("💎 使用 Clarity Necklace (選項減半)")

    if "pvp_st" not in st.session_state: st.session_state.pvp_st = "ready"
    
    if st.button("🚀 啟動入侵") or st.session_state.pvp_st == "go":
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

        st.markdown("### 🔑 破解防禦層")
        if has_chaos: st.error("⚠️ 對方有混亂之心，難度加倍！")
        if use_neck: st.success("💎 清醒項鍊生效中。")

        cols = st.columns(4)
        for i, code in enumerate(st.session_state.pvp_opts):
            if cols[i%4].button(code, key=f"pvp_{code}"):
                # 消耗
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
                        st.toast(f"攻擊成功 (被防火牆減傷)！搶得 ${loot}", icon="🔥")
                    else:
                        st.balloons(); st.toast(f"💥 爆擊成功！搶得 ${loot}", icon="💰")
                    
                    t_user["money"] -= loot; user["money"] += loot
                    check_mission(uid, user, "pvp_win")
                else:
                    st.error("🚫 密碼錯誤！入侵失敗。")
                
                db["users"][uid] = user; db["users"][tid] = t_user
                save_db(db)
                del st.session_state.pvp_opts; del st.session_state.pvp_st
                time.sleep(2); st.rerun()

def page_missions(uid, user):
    st.title("🎯 任務中心")
    ms = load_missions_from_file()
    done = user.get("completed_missions", [])
    pending = user.get("pending_claims", [])
    
    # 領獎區
    if pending:
        st.markdown("### 🎁 待領取獎勵")
        for mid in pending:
            m = ms.get(mid, HIDDEN_MISSIONS.get(mid))
            if not m: continue
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.write(f"**{m['title']}**"); c1.caption
