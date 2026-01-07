# app.py
import streamlit as st
import random
import time
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from config import ITEMS, STOCKS_DATA, SVG_LIB

# 🔥 確保這裡引入了 apply_environmental_hazard
from database import (init_db, get_user, save_user, create_user, 
                      get_global_stock_state, save_global_stock_state, 
                      rebuild_market, check_mission, send_mail, get_all_users,
                      apply_environmental_hazard)

st.set_page_config(page_title="CityOS Hazard", layout="wide", page_icon="☣️")
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00ff41; font-family: monospace; }
    div.stButton > button { background-color: #000; border: 1px solid #00ff41; color: #00ff41; }
    div.stButton > button:hover { background-color: #00ff41; color: #000; }
    .js-plotly-plot .plotly .main-svg { background: rgba(0,0,0,0) !important; }
    .stProgress > div > div > div > div { background-color: #ff3333; }
</style>
""", unsafe_allow_html=True)

init_db()

# --- 輔助函數 ---
def update_stock_market():
    global_state = get_global_stock_state()
    if not global_state: return
    now = time.time()
    if now - global_state.get("last_update", 0) > 0.5:
        new_prices = {}
        for code, data in STOCKS_DATA.items():
            prev = global_state["prices"].get(code, data["base"])
            direction = random.choice([-1, 1])
            change_pct = random.uniform(0.05, 0.2)
            jitter = random.randint(2, 10) * direction
            new_p = int(prev * (1 + (direction * change_pct))) + jitter
            new_p = max(1, new_p)
            new_prices[code] = new_p
        global_state["prices"] = new_prices
        global_state["last_update"] = now
        hist = new_prices.copy()
        hist["_time"] = datetime.now().strftime("%H:%M:%S")
        global_state["history"].append(hist)
        if len(global_state["history"]) > 60: global_state["history"].pop(0)
        save_global_stock_state(global_state)
    st.session_state.stock_prices = global_state["prices"]
    st.session_state.stock_history = pd.DataFrame(global_state["history"])

def render_k_line(symbol):
    if "stock_history" not in st.session_state or st.session_state.stock_history.empty:
        st.write("等待市場數據..."); return
    df = st.session_state.stock_history.copy()
    if symbol not in df.columns: return
    df['Close'] = df[symbol]
    df['Open'] = df[symbol].shift(1).fillna(df[symbol])
    import numpy as np
    df['High'] = df[['Open', 'Close']].max(axis=1) + np.random.randint(0, 3, len(df))
    df['Low'] = df[['Open', 'Close']].min(axis=1) - np.random.randint(0, 3, len(df))
    fig = go.Figure(data=[go.Candlestick(x=df['_time'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], increasing_line_color='#00ff41', decreasing_line_color='#ff3333')])
    fig.update_layout(title=f"{symbol} K-Line", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#00ff41'), xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=30, b=0), height=350)
    st.plotly_chart(fig, use_container_width=True)

# --- 頁面功能區 ---

def page_dashboard(uid, user):
    st.title(f"🏙️ 儀表板: {user['name']}")
    update_stock_market()
    stock_val = sum([amt * st.session_state.stock_prices.get(c, 0) for c, amt in user.get('stocks',{}).items()])
    total = user['money'] + stock_val
    c1, c2, c3 = st.columns(3)
    c1.metric("總身價", f"${total:,}")
    c2.metric("現金", f"${user['money']:,}")
    c3.metric("持股", f"${stock_val:,}")
    if "stock_history" in st.session_state and not st.session_state.stock_history.empty:
        st.subheader("市場總覽")
        df = st.session_state.stock_history.drop(columns=["_time"], errors="ignore")
        st.line_chart(df, height=200)

def page_stock(uid, user):
    st.title("📉 專業交易所"); auto = st.toggle("⚡ 自動刷新", value=True); update_stock_market(); prices = st.session_state.stock_prices
    cols = st.columns(len(STOCKS_DATA)); 
    for i, (k, v) in enumerate(prices.items()): cols[i].metric(k, f"${v}")
    c1, c2 = st.columns([2, 1])
    with c2:
        st.subheader("交易面板"); selected_stock = st.selectbox("標的", list(STOCKS_DATA.keys()))
        current_price = prices.get(selected_stock, 0); st.metric(f"現價: {selected_stock}", f"${current_price}")
        t1, t2 = st.tabs(["買", "賣"])
        with t1:
            qty = st.number_input("股數", 1, 1000, 10, key="bq"); cost = current_price * qty
            if st.button(f"買進 (-${cost})"): 
                if user['money']>=cost: user['money']-=cost; user.setdefault('stocks',{})[selected_stock]=user['stocks'].get(selected_stock,0)+qty; check_mission(uid,user,"stock_buy"); save_user(uid,user); st.success("OK"); st.rerun()
                else: st.error("沒錢")
        with t2:
            own = user.get('stocks',{}).get(selected_stock,0); st.write(f"持有: {own}"); sqty = st.number_input("股數", 1, max(1,own), 1, key="sq")
            income = current_price * sqty
            if st.button(f"賣出 (+${income})"):
                if own>=sqty: user['money']+=income; user['stocks'][selected_stock]-=sqty; save_user(uid,user); st.success("OK"); st.rerun()
    with c1: render_k_line(selected_stock)
    if auto: time.sleep(1); st.rerun()

# 🔥 新版：邏輯電路設計 (取代舊的 page_lab)
def page_lab(uid, user):
    st.title("🔌 邏輯電路設計 (Circuit Designer)")
    st.caption("CityOS 硬體實驗室：請使用邏輯閘設計電路。")

    st.subheader("1. 輸入訊號 (Inputs)")
    col_i1, col_i2, col_i3, col_i4 = st.columns(4)
    with col_i1: in_A = st.toggle("A", value=True)
    with col_i2: in_B = st.toggle("B", value=False)
    with col_i3: in_C = st.toggle("C", value=True)
    with col_i4: in_D = st.toggle("D", value=False)
    
    st.markdown("---")
    st.subheader("2. 第一級處理 (Layer 1)")
    c1, c2 = st.columns(2)
    
    # 邏輯閘清單 (從 config.py 的 SVG_LIB 讀取)
    gate_options = list(SVG_LIB.keys())

    with c1:
        st.write("處理訊號 A & B")
        gate_L = st.selectbox("左側邏輯閘", gate_options, key="gl")
        res_L = False
        if gate_L == "AND": res_L = in_A and in_B
        elif gate_L == "OR": res_L = in_A or in_B
        elif gate_L == "XOR": res_L = in_A != in_B
        elif gate_L == "NAND": res_L = not (in_A and in_B)
        elif gate_L == "NOR": res_L = not (in_A or in_B)
        elif gate_L == "XNOR": res_L = in_A == in_B
        elif gate_L == "NOT": res_L = not in_A # NOT只取第一個輸入
        st.info(f"L 輸出: {int(res_L)}")

    with c2:
        st.write("處理訊號 C & D")
        gate_R = st.selectbox("右側邏輯閘", gate_options, key="gr")
        res_R = False
        if gate_R == "AND": res_R = in_C and in_D
        elif gate_R == "OR": res_R = in_C or in_D
        elif gate_R == "XOR": res_R = in_C != in_D
        elif gate_R == "NAND": res_R = not (in_C and in_D)
        elif gate_R == "NOR": res_R = not (in_C or in_D)
        elif gate_R == "XNOR": res_R = in_C == in_D
        elif gate_R == "NOT": res_R = not in_C
        st.info(f"R 輸出: {int(res_R)}")

    st.markdown("⬇️")
    st.subheader("3. 最終輸出 (Master Output)")
    col_main, col_res = st.columns([2, 1])
    
    with col_main:
        st.write("L 與 R 的最終運算")
        gate_M = st.selectbox("核心邏輯閘", gate_options, key="gm")
        final_res = False
        if gate_M == "AND": final_res = res_L and res_R
        elif gate_M == "OR": final_res = res_L or res_R
        elif gate_M == "XOR": final_res = res_L != res_R
        elif gate_M == "NAND": final_res = not (res_L and res_R)
        elif gate_M == "NOR": final_res = not (res_L or res_R)
        elif gate_M == "XNOR": final_res = res_L == res_R
        elif gate_M == "NOT": final_res = not res_L

    with col_res:
        st.write("## 結果")
        if final_res:
            st.success("HIGH (1)")
            st.markdown("💡", unsafe_allow_html=True)
        else:
            st.error("LOW (0)")
            st.markdown("⚫", unsafe_allow_html=True)

    st.divider()
    if st.button("💾 上傳設計圖"):
        st.toast("設計圖已上傳至雲端伺服器！")
        check_mission(uid, user, "cli_input") # 當作完成一次技術操作
        save_user(uid, user)

def page_shop(uid, user):
    st.title("🛒 黑市 & 背包")
    t1, t2 = st.tabs(["購買", "使用/查看"])
    with t1:
        for k, v in ITEMS.items():
            with st.expander(f"{k} (${v['price']})"):
                st.write(v['desc'])
                if st.button(f"購買 {k}"):
                    if user['money'] >= v['price']:
                        user['money'] -= v['price']
                        user.setdefault('inventory', {})[k] = user['inventory'].get(k, 0) + 1
                        check_mission(uid, user, "shop_buy")
                        save_user(uid, user)
                        st.success("購買成功")
                        st.rerun()
                    else: st.error("資金不足")
    with t2:
        st.write(f"🎒 背包: {user.get('inventory', {})}")
        if user.get("inventory", {}).get("Anti-Rad Pill", 0) > 0:
            st.divider()
            st.write("💉 醫療用品")
            if st.button("吞下 Anti-Rad Pill (解毒)"):
                user["inventory"]["Anti-Rad Pill"] -= 1
                if user["inventory"]["Anti-Rad Pill"] <= 0: del user["inventory"]["Anti-Rad Pill"]
                old_tox = user.get("toxicity", 0)
                user["toxicity"] = max(0, old_tox - 30)
                check_mission(uid, user, "use_item")
                save_user(uid, user)
                st.success(f"毒素清除！ ({old_tox}% -> {user['toxicity']}%)")
                st.rerun()

def page_missions(uid, user):
    st.title("🎯 任務板")
    if user.get("pending_claims"):
        for i, m in enumerate(user["pending_claims"]):
            if st.button(f"領取 ${m['reward']} ({m['title']})", key=f"c_{i}"): user['money']+=m['reward']; user["pending_claims"].pop(i); save_user(uid,user); st.rerun()
    st.subheader("進行中")
    for m in user.get("active_missions", []): st.warning(f"🔸 {m['title']}: {m['desc']} (${m['reward']})")

def page_pvp(uid, user):
    st.title("⚔️ PVP")
    if time.time()-user.get("last_hack",0)<30: st.info(f"冷卻中... {int(30-(time.time()-user['last_hack']))}s"); return
    targets = [u for u in get_all_users() if u!=uid and u!="admin"]; 
    if not targets: st.write("無目標"); return
    target = st.selectbox("目標", targets); has_virus = user.get("inventory",{}).get("Trojan Virus",0)>0; st.write(f"病毒: {'✅' if has_virus else '❌'}")
    if st.button("攻擊", disabled=not has_virus):
        user["inventory"]["Trojan Virus"]-=1; victim=get_user(target)
        if victim.get("inventory",{}).get("Firewall",0)>0: victim["inventory"]["Firewall"]-=1; send_mail(target,"Sys","防禦","擋下攻擊"); st.error("被擋下")
        else: loot=min(random.randint(50,150), victim['money']); victim['money']-=loot; user['money']+=loot; send_mail(target,"Sys","警報",f"被搶 ${loot}"); st.success(f"搶奪 ${loot}")
        user["last_hack"]=time.time(); save_user(target,victim); save_user(uid,user); st.rerun()

def page_cli(uid, user):
    st.title("💻 CLI"); cmd=st.text_input(f"{uid}@cityos:~$")
    if cmd: check_mission(uid,user,"cli_input"); st.code("OK" if cmd in ["ls","bal","date"] else "Error")

# --- 主程式 ---
def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    if not st.session_state.logged_in:
        st.title("CITY_OS // HAZARD"); c1,c2=st.tabs(["Log","Reg"]); 
        with c1: 
            u=st.text_input("ID"); p=st.text_input("PW",type="password")
            if st.button("LOGIN"): 
                if get_user(u) and get_user(u)['password']==p: st.session_state.logged_in=True; st.session_state.uid=u; st.rerun()
        with c2:
            nu=st.text_input("NID"); np=st.text_input("NPW",type="password"); nn=st.text_input("Name")
            if st.button("REG"): 
                if create_user(nu,np,nn): st.success("OK"); st.rerun()
        return

    uid = st.session_state.uid; user = get_user(uid)
    
    # ☣️ 毒氣模擬 (這裡呼叫 database 裡的函數)
    if apply_environmental_hazard(uid, user):
        st.toast("⚠️ 警報：檢測到有害氣體吸入！", icon="☣️")
        
    # ☠️ 毒發懲罰
    if user["toxicity"] >= 100:
        st.error("☠️ 身體崩潰！緊急送醫急救... (-$200)")
        user["money"] = max(0, user["money"] - 200)
        user["toxicity"] = 50 
        save_user(uid, user)
        time.sleep(2)
        st.rerun()

    with st.sidebar:
        st.title(f"{user['name']}")
        st.write(f"💵 ${user['money']}")
        
        # 顯示中毒狀況
        tox = user.get("toxicity", 0)
        st.write(f"☣️ 中毒指數: {tox}%")
        st.progress(tox / 100)
        if tox > 80: st.caption("⚠️ 命在旦夕！")
        
        if user.get("inventory", {}).get("Gas Mask", 0) > 0:
            st.success("😷 面具: 裝備中")
        else:
            st.warning("😶 無防護")

        nav = st.radio("MENU", ["儀表板", "交易所", "任務", "黑市", "PVP", "CLI", "邏輯設計"])
        st.divider()
        if st.button("LOGOUT"): st.session_state.logged_in = False; st.rerun()

    if nav == "儀表板": page_dashboard(uid, user)
    elif nav == "交易所": page_stock(uid, user)
    elif nav == "任務": page_missions(uid, user)
    elif nav == "黑市": page_shop(uid, user)
    elif nav == "PVP": page_pvp(uid, user)
    elif nav == "CLI": page_cli(uid, user)
    elif nav == "邏輯設計": page_lab(uid, user)

if __name__ == "__main__":
    main()
