import streamlit as st
import pandas as pd
import random
import time
import json
from datetime import datetime

# 匯入你的後端模組 (確保 config.py 與 database.py 在同目錄)
from config import ITEMS, STOCKS_DATA, SVG_LIB, MORSE_CODE_DICT
from database import (
    load_db, save_db, check_mission, get_today_event, 
    load_quiz_from_file, log_intruder, send_mail
)

# --- 1. 頁面基礎設定 ---
st.set_page_config(page_title="CityOS_V30", page_icon="🌃", layout="wide")

# 載入 CSS (賽博龐克風格)
st.markdown("""
<style>
    .main { background-color: #0e1117; color: #00ff41; font-family: 'Courier New', monospace; }
    .stButton>button { color: #0e1117; background-color: #00ff41; border: 1px solid #00ff41; }
    .stButton>button:hover { color: #00ff41; background-color: #0e1117; }
    .stToast { background-color: #333333; color: #00ff41; border-left: 5px solid #00ff41; }
    h1, h2, h3 { color: #00ff41 !important; text-shadow: 0 0 5px #00ff41; }
    .metric-card { border: 1px solid #333; padding: 10px; border-radius: 5px; background: #111; }
</style>
""", unsafe_allow_html=True)

# --- 2. Session 初始化 (包含股市數據) ---
if "user" not in st.session_state:
    st.session_state.user = None

if "stock_prices" not in st.session_state:
    # 初始化股價與歷史紀錄 (讓首頁有東西可以畫)
    st.session_state.stock_prices = {k: v["base"] for k, v in STOCKS_DATA.items()}
    st.session_state.stock_history = pd.DataFrame(columns=STOCKS_DATA.keys())
    # 預先生成幾筆數據以免圖表空白
    new_row = st.session_state.stock_prices.copy()
    st.session_state.stock_history = pd.concat([st.session_state.stock_history, pd.DataFrame([new_row])], ignore_index=True)

if "cli_h" not in st.session_state:
    st.session_state.cli_h = ["CityOS Kernel v30.0 initialized...", "System: Monitoring user activity...", "Type 'help' to start."]

# --- 3. 核心功能函式 ---

def simulate_market():
    """模擬市場波動 (Hardcore Mode: 波動劇烈)"""
    new_prices = {}
    for code, data in STOCKS_DATA.items():
        current = st.session_state.stock_prices[code]
        # 波動率來自 config.py
        volatility = data.get("volatility", 0.1)  
        change = random.uniform(-volatility, volatility)
        
        # 加入隨機事件影響
        evt = get_today_event()
        if evt["effect"] == "tech_boom" and code in ["CYBR", "CHIP"]: change += 0.1
        if evt["effect"] == "mining_boost" and code == "DARK": change += 0.2
        if evt["effect"] == "network_slow" and code == "NETW": change -= 0.15

        new_price = max(1, int(current * (1 + change)))
        new_prices[code] = new_price
    
    st.session_state.stock_prices = new_prices
    # 更新歷史紀錄 (用於繪圖)
    new_row = pd.DataFrame([new_prices])
    st.session_state.stock_history = pd.concat([st.session_state.stock_history, new_row], ignore_index=True)
    # 只保留最近 50 筆以節省資源
    if len(st.session_state.stock_history) > 50:
        st.session_state.stock_history = st.session_state.stock_history.iloc[-50:]

def render_sidebar(user, uid):
    """側邊欄資訊"""
    with st.sidebar:
        st.header(f"👤 {user['name']}")
        st.caption(f"ID: {uid} | Job: {user['job']}")
        
        # 狀態欄
        col1, col2 = st.columns(2)
        col1.metric("Cash", f"${user['money']}")
        col2.metric("Level", f"Lv.{user['level']}")
        
        # 顯示背包簡化版
        st.divider()
        st.text("🎒 背包物品:")
        if not user.get("inventory"):
            st.caption("空空如也 (窮)")
        else:
            for item, qty in user["inventory"].items():
                st.text(f"- {item}: {qty}")
        
        st.divider()
        if st.button("🚪 安全登出"):
            st.session_state.user = None
            st.rerun()

# --- 4. 各頁面邏輯 ---

def page_home(uid, user):
    st.title(f"🌃 Night City Dashboard")
    st.markdown(f"早安，**{user['name']}**。今天是 {datetime.now().strftime('%Y-%m-%d')}。")
    
    # 隨機事件播報
    evt = get_today_event()
    st.info(f"📢 今日頭條：{evt['name']} - {evt['desc']}")

    # --- 新增：首頁股市看板 ---
    st.subheader("📈 市場即時監控")
    
    # 計算資產
    stock_val = sum([amt * st.session_state.stock_prices.get(code,0) for code, amt in user.get("stocks",{}).items()])
    total_assets = user['money'] + user.get('bank_deposit', 0) + stock_val
    
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("💰 總資產估值", f"${total_assets:,}", delta=None)
    col_b.metric("🏦 銀行存款", f"${user.get('bank_deposit', 0):,}")
    col_c.metric("📉 股票市值", f"${stock_val:,}")

    # 顯示折線圖
    if not st.session_state.stock_history.empty:
        st.line_chart(st.session_state.stock_history, height=250)
    else:
        st.caption("市場數據載入中...")

    # 任務概況
    st.divider()
    st.subheader("🎯 待辦事項 (Active Missions)")
    if not user["active_missions"]:
        st.caption("目前無任務。去喝杯咖啡吧。")
    else:
        for m in user["active_missions"]:
            with st.expander(f"📌 {m['title']} (報酬: ${m['reward']})"):
                st.write(m['desc'])
                st.progress(min(100, int((user.get("exp", 0) % 1000) / 10)))

def page_stock(uid, user):
    st.title("💹 黑市交易所")
    st.caption("警告：投資有賺有賠，更多時候是賠光。")

    if st.button("🔄 刷新市場 (模擬波動)"):
        simulate_market()
        st.toast("市場數據已更新", icon="📉")
        st.rerun()

    # 顯示主要的大圖表
    st.line_chart(st.session_state.stock_history)

    # 交易介面
    col1, col2 = st.columns([2, 1])
    with col1:
        target = st.selectbox("選擇股票", list(STOCKS_DATA.keys()))
        info = STOCKS_DATA[target]
        curr_price = st.session_state.stock_prices[target]
        st.metric(info["name"], f"${curr_price}", delta_color="off")
        
    with col2:
        action = st.radio("操作", ["買入", "賣出"], horizontal=True)
        qty = st.number_input("數量", min_value=1, value=10)

    if st.button("下單確認"):
        cost = curr_price * qty
        user.setdefault("stocks", {})
        
        if action == "買入":
            if user["money"] >= cost:
                user["money"] -= cost
                user["stocks"][target] = user["stocks"].get(target, 0) + qty
                st.success(f"買入 {qty} 股 {target}。")
                check_mission(uid, user, "stock_buy", extra_data=target, extra_val=qty)
                save_db({"users": load_db()["users"] | {uid: user}, "bbs": []})
                st.rerun()
            else:
                st.error("資金不足！去解任務賺錢吧。")
        elif action == "賣出":
            if user["stocks"].get(target, 0) >= qty:
                user["money"] += cost
                user["stocks"][target] -= qty
                if user["stocks"][target] == 0: del user["stocks"][target]
                st.success(f"賣出 {qty} 股 {target}，獲利 ${cost}。")
                save_db({"users": load_db()["users"] | {uid: user}, "bbs": []})
                st.rerun()
            else:
                st.error("股票庫存不足！不要做空，你會破產。")

def page_mission(uid, user):
    st.title("⚔️ 任務中心")
    st.caption("這裡只有髒活，但至少給錢 (雖然不多)。")

    # 刷新任務按鈕
    if st.button("🔄 尋找新合約"):
        check_mission(uid, user, "refresh") # 觸發刷新邏輯
        st.rerun()

    # 顯示任務列表
    for i, m in enumerate(user["active_missions"]):
        st.markdown(f"### 🔸 {m['title']}")
        st.write(f"📜 {m['desc']}")
        st.caption(f"💰 報酬: ${m['reward']}")
        st.divider()

    # 領取獎勵區
    if user["pending_claims"]:
        st.success(f"你有 {len(user['pending_claims'])} 個任務已完成！")
        if st.button("🎁 全部領取"):
            total = 0
            for pm in user["pending_claims"]:
                total += pm["reward"]
                # 記錄到已完成
                user.setdefault("completed_missions", []).append(pm["id"])
            
            user["money"] += total
            user["exp"] += total * 2
            user["pending_claims"] = [] # 清空待領取
            
            # 升級檢查
            if user["exp"] >= user["level"] * 1000:
                user["level"] += 1
                st.toast(f"🎉 升級了！目前等級 {user['level']}", icon="🆙")
            
            save_db({"users": load_db()["users"] | {uid: user}, "bbs": []})
            st.balloons()
            st.rerun()

def page_shop(uid, user):
    st.title("🛒 地下商城")
    st.caption("物價通膨嚴重，愛買不買隨你。")
    
    for item_name, info in ITEMS.items():
        with st.container():
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.markdown(f"**{item_name}**")
            c1.caption(info["desc"])
            c2.text(f"${info['price']}")
            if c3.button("購買", key=f"buy_{item_name}"):
                if user["money"] >= info["price"]:
                    user["money"] -= info["price"]
                    user.setdefault("inventory", {})
                    user["inventory"][item_name] = user["inventory"].get(item_name, 0) + 1
                    
                    st.toast(f"已購買 {item_name}", icon="🛍️")
                    check_mission(uid, user, "shop_buy", extra_data=item_name)
                    save_db({"users": load_db()["users"] | {uid: user}, "bbs": []})
                    st.rerun()
                else:
                    st.error("錢不夠。你的肝還夠用嗎？")
            st.divider()

def page_cli(uid, user):
    # --- 毒舌版 CLI ---
    st.title("💻 終端機 (CLI)")
    st.markdown("模擬 Linux 終端機環境。輸入 `help` 查看指令。")
    
    sarcastic_responses = [
        "找不到指令。你的鍵盤是壞了還是手指太粗？",
        "Permission Denied. 你以為你是誰？Frank 嗎？",
        "錯誤：智商不足，無法執行此操作。",
        "這不是 Linux，不要亂試 `rm -rf /`，我會報警。",
        "系統偵測到無效輸入，建議去『邏輯實驗室』重修。",
        "你要不要先去喝杯咖啡醒醒腦再來打字？",
        "404 Brain Not Found.",
        "你在測試我的耐心嗎？",
        "指令錯誤。再錯一次我就要把你的錢歸零囉（開玩笑的...或許吧）。"
    ]

    # 顯示歷史紀錄 (最後 8 行)
    for l in st.session_state.cli_h[-8:]:
        st.code(l, language="bash")
        
    cmd = st.chat_input("user@cityos:~$")
    
    if cmd:
        st.session_state.cli_h.append(f"user@cityos:~$ {cmd}")
        # 觸發任務檢查
        check_mission(uid, user, "cli_input", extra_data=cmd)
        
        res = ""
        # 正常指令
        if cmd == "help": 
            res = "可用指令: bal (餘額), whoami (我是誰), scan (掃描), sudo (作死), clear (清空)"
        elif cmd == "bal": 
            if user['money'] < 100:
                res = f"Cash: ${user['money']} (天啊，真窮...)"
            else:
                res = f"Cash: ${user['money']}"
        elif cmd == "whoami": 
            res = f"User: {user['name']} | Job: {user['job']} | Status: Still Single?"
        elif cmd == "scan": 
            res = "Scanning network... [ERROR] Too many bugs found in your code."
        elif cmd == "clear": 
            st.session_state.cli_h = []
            st.rerun()
            
        # 特殊與毒舌指令
        elif cmd.startswith("sudo"): 
            if cmd == "sudo su":
                # 成就觸發點
                check_mission(uid, user, "cli_input", extra_data="sudo su")
                res = "System: 哇，你真的試了？給你個成就，快滾。"
            else:
                res = "System: 權限拒絕。你沒有管理員權限，你甚至沒有女朋友。"
        elif cmd == "exit":
            res = "System: 想跑？門都沒有。 (請使用側邊欄登出)"
        elif cmd == "rm -rf /":
            res = "System: 正在刪除 System32... 騙你的，別做傻事。"
        else: 
            # 隨機嘲諷
            res = f"bash: {cmd}: " + random.choice(sarcastic_responses)
            # 錯誤次數任務觸發
            check_mission(uid, user, "cli_error", extra_val=st.session_state.get("cli_err",0)+1)
            
        st.session_state.cli_h.append(res)
        st.rerun()

# --- 5. 主程式入口 ---
def main():
    db_data = load_db()
    
    # 登入頁面
    if not st.session_state.user:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.title("🏙️ CityOS Login")
            st.markdown("### Welcome to Night City")
            st.markdown("請輸入你的神經網絡憑證 (ID/Pass)")
            
            uid_input = st.text_input("User ID")
            pwd_input = st.text_input("Password", type="password")
            
            if st.button("Login"):
                if uid_input in db_data["users"] and db_data["users"][uid_input]["password"] == pwd_input:
                    st.session_state.user = uid_input
                    st.success("Access Granted.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Access Denied. 試著入侵嗎？")
    else:
        # 已登入狀態
        uid = st.session_state.user
        user = db_data["users"][uid]
        
        # 顯示側邊欄
        render_sidebar(user, uid)
        
        # 導航選單
        menu = st.sidebar.radio("Navigation", ["📊 儀表板", "⚔️ 任務中心", "💹 股市", "🛒 商城", "💻 終端機"])
        
        if menu == "📊 儀表板":
            page_home(uid, user)
        elif menu == "⚔️ 任務中心":
            page_mission(uid, user)
        elif menu == "💹 股市":
            page_stock(uid, user)
        elif menu == "🛒 商城":
            page_shop(uid, user)
        elif menu == "💻 終端機":
            page_cli(uid, user)

if __name__ == "__main__":
    main()
