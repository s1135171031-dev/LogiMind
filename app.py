import streamlit as st
import pandas as pd
import random
import os
import time
import json
import numpy as np
import ipaddress
from datetime import datetime, date
import matplotlib.pyplot as plt

# ==============================================================================
# 1. 系統核心設定 & 常數
# ==============================================================================
st.set_page_config(
    page_title="CityOS V11.0 Engineer RPG",
    layout="wide",
    page_icon="🏙️",
    initial_sidebar_state="expanded"
)

USER_DB_FILE = "cityos_users.json"
QUESTION_DB_FILE = "questions.txt"

# 職業系統
CLASSES = {
    "Novice": {
        "name": "一般市民", "icon": "👤", 
        "desc": "基礎權限。適合新手。", "unlocks": []
    },
    "Engineer": {
        "name": "硬體工程師", "icon": "🔧", 
        "desc": "硬體專家。解鎖：[訊號產生器]、[挖礦效率+20%]", "unlocks": ["SignalGen", "MiningBonus"]
    },
    "Programmer": {
        "name": "軟體工程師", "icon": "💻", 
        "desc": "軟體專家。解鎖：[頭像生成器]、[進位轉換]", "unlocks": ["AvatarGen", "BaseConverter"]
    },
    "Architect": {
        "name": "系統架構師", "icon": "⚡", 
        "desc": "全能神。解鎖：[所有功能]。", "unlocks": ["All"]
    },
    "Hacker": {
        "name": "資安專家", "icon": "🛡️", 
        "desc": "網絡攻防。解鎖：[駭客終端機]、[網路工具]", "unlocks": ["Terminal", "NetworkCalc"]
    }
}

SVG_LIB = {
    "AND": '''<svg width="100" height="60"><path d="M10,5 L40,5 C55,5 65,15 65,25 C65,35 55,45 40,45 L10,45 Z" fill="none" stroke="#CCC" stroke-width="3"/><path d="M0,15 L10,15 M0,35 L10,35 M65,25 L80,25" stroke="#CCC" stroke-width="3"/></svg>''',
    "OR": '''<svg width="100" height="60"><path d="M10,5 L35,5 Q50,25 35,45 L10,45 Q25,25 10,5 Z" fill="none" stroke="#CCC" stroke-width="3"/><path d="M0,15 L15,15 M0,35 L15,35 M45,25 L60,25" stroke="#CCC" stroke-width="3"/></svg>'''
}

# ==============================================================================
# 2. 資料庫邏輯 (Backend)
# ==============================================================================

def get_admin_data():
    return {
        "password": "x12345678x", "name": "Frank (Admin)", 
        "level": 100, "exp": 99999, "money": 99999, "job": "Architect", 
        "inventory": ["RTX 4090"], "mining_balance": 0.0,
        "last_quiz_date": str(date.today()), "quiz_attempts": 0, "bio": "System Creator."
    }

def init_db():
    if not os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "w", encoding="utf-8") as f:
            json.dump({"users": {"frank": get_admin_data()}, "messages": []}, f, ensure_ascii=False, indent=4)

def load_db():
    init_db()
    try:
        with open(USER_DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "frank" not in data["users"]:
            data["users"]["frank"] = get_admin_data(); save_db(data)
        return data
    except:
        if os.path.exists(USER_DB_FILE): os.remove(USER_DB_FILE)
        return load_db()

def save_db(data):
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_questions():
    questions = []
    # 這裡模擬題庫，實際可讀檔
    demos = [
        {"q":"在 Python 中，哪個關鍵字用於定義函數?", "opts":["func", "def", "function", "lambda"], "ans":"def"},
        {"q":"二進位數字 1010 等於十進位的多少?", "opts":["8", "10", "12", "5"], "ans":"10"},
        {"q":"HTTP 協定中，哪個狀態碼代表「找不到網頁」?", "opts":["200", "500", "404", "403"], "ans":"404"},
        {"q":"邏輯閘 AND 的輸入為 1 和 0 時，輸出為何?", "opts":["1", "0", "High", "Z"], "ans":"0"},
        {"q":"下列哪個不是 Linux 的發行版?", "opts":["Ubuntu", "CentOS", "Windows", "Kali"], "ans":"Windows"}
    ]
    return demos

def check_level_up(user):
    cur, exp = user.get("level", 1), user.get("exp", 0)
    new_lvl = 1 + (exp // 100)
    if new_lvl > cur:
        user["level"] = new_lvl; return True, new_lvl
    return False, cur

# ==============================================================================
# 3. 主要功能模組
# ==============================================================================

# --- [V11.0 更新] 每日測驗系統 (含確認頁面) ---
def page_daily_quiz(uid, user):
    st.header("📝 每日工程師能力測驗")
    
    # 1. 檢查日期與次數
    today = str(date.today())
    if user.get("last_quiz_date") != today:
        user["last_quiz_date"] = today
        user["quiz_attempts"] = 0
        db = load_db(); db["users"][uid] = user; save_db(db)
    
    attempts_left = 3 - user.get("quiz_attempts", 0)
    
    # 初始化 Session State
    if "quiz_phase" not in st.session_state:
        st.session_state.quiz_phase = "LOBBY" # LOBBY, PLAYING, RESULT
        st.session_state.quiz_score = 0
        st.session_state.quiz_idx = 0
    
    # === 階段 1: 準備大廳 (Lobby) ===
    if st.session_state.quiz_phase == "LOBBY":
        
        # 顯示狀態卡片
        c1, c2, c3 = st.columns(3)
        c1.metric("今日剩餘次數", f"{attempts_left} / 3")
        c2.metric("單題獎勵", "$20 / 40xp")
        c3.metric("全對額外獎勵", "$50")
        
        st.divider()
        
        if attempts_left <= 0:
            st.warning("🔒 今日測驗次數已用盡，請明天再來！")
            st.info("💡 提示：你可以去「雲端挖礦」或「駭客終端」賺取更多金幣。")
        else:
            st.info("準備好了嗎？測驗內容包含基礎邏輯、程式語言與電腦科學知識。")
            
            # 開始按鈕
            if st.button("🚀 確認開始測驗", use_container_width=True, type="primary"):
                # 載入題目
                all_q = load_questions()
                st.session_state.quiz_qs = random.sample(all_q, 3) # 隨機抽3題
                st.session_state.quiz_phase = "PLAYING"
                st.session_state.quiz_idx = 0
                st.session_state.quiz_score = 0
                st.rerun()

    # === 階段 2: 測驗進行中 (Playing) ===
    elif st.session_state.quiz_phase == "PLAYING":
        q_list = st.session_state.quiz_qs
        idx = st.session_state.quiz_idx
        q_curr = q_list[idx]
        
        # 進度條
        st.progress((idx + 1) / len(q_list), text=f"Question {idx+1} / {len(q_list)}")
        
        st.subheader(f"Q{idx+1}: {q_curr['q']}")
        
        with st.form(key=f"quiz_form_{idx}"):
            user_ans = st.radio("請選擇答案:", q_curr['opts'], key=f"ans_{idx}")
            submitted = st.form_submit_button("送出答案")
            
            if submitted:
                if user_ans == q_curr['ans']:
                    st.toast("✅ 正確！", icon="🎉")
                    st.session_state.quiz_score += 1
                else:
                    st.toast(f"❌ 錯誤... 正解是 {q_curr['ans']}", icon="⚠️")
                
                time.sleep(0.5) # 稍微停頓讓使用者看提示
                
                # 判斷是否下一題
                if idx + 1 < len(q_list):
                    st.session_state.quiz_idx += 1
                    st.rerun()
                else:
                    st.session_state.quiz_phase = "RESULT"
                    st.rerun()

    # === 階段 3: 結算畫面 (Result) ===
    elif st.session_state.quiz_phase == "RESULT":
        score = st.session_state.quiz_score
        total_q = 3
        
        # 計算獎勵
        money_gain = score * 20
        exp_gain = score * 40
        if score == total_q:
            money_gain += 50 # 全對獎金
            st.balloons()
        
        st.markdown(f"<h2 style='text-align:center'>測驗結束</h2>", unsafe_allow_html=True)
        
        rc1, rc2 = st.columns(2)
        with rc1:
            st.markdown(f"### 答對題數: {score} / {total_q}")
            if score == total_q: st.success("🌟 完美表現！ (S級)")
            elif score >= 1: st.info("👍 還不錯！ (A級)")
            else: st.error("💀 再接再厲...")
            
        with rc2:
            st.markdown("### 獲得獎勵")
            st.write(f"💰 金幣: +${money_gain}")
            st.write(f"📈 經驗: +{exp_gain} XP")
        
        if st.button("領取獎勵並返回大廳", use_container_width=True):
            # 寫入資料庫
            user["money"] += money_gain
            user["exp"] += exp_gain
            user["quiz_attempts"] += 1
            is_up, new_lv = check_level_up(user)
            if is_up: st.toast(f"升級了！目前等級 Lv.{new_lv}", icon="🆙")
            
            db = load_db()
            db["users"][uid] = user
            save_db(db)
            
            # 重置狀態
            st.session_state.quiz_phase = "LOBBY"
            st.rerun()

# --- 其他功能 (保留 V10.0) ---

def page_mining(uid, user):
    st.title("⛏️ 雲端挖礦場")
    
    # 計算算力
    hashrate = 0
    for item in user.get("inventory", []):
        if "GTX 1060" in item: hashrate += 10
        elif "RTX 3060" in item: hashrate += 30
        elif "RTX 4090" in item: hashrate += 100
    if user.get("job") == "Engineer": hashrate *= 1.2
    
    # 被動挖礦模擬
    balance = user.get("mining_balance", 0.0)
    mined_now = hashrate * 0.001 * random.uniform(0.8, 1.2)
    user["mining_balance"] = balance + mined_now
    
    c1, c2, c3 = st.columns(3)
    c1.metric("算力 (Hash/s)", int(hashrate))
    c2.metric("持有 BTC", f"{user['mining_balance']:.6f}")
    c3.metric("預估價值", f"${int(user['mining_balance'] * 5000)}")
    
    if st.button("💰 提領收益"):
        if user["mining_balance"] > 0.0001:
            gain = int(user['mining_balance'] * 5000)
            user["money"] += gain
            user["mining_balance"] = 0
            db = load_db(); db["users"][uid] = user; save_db(db)
            st.success(f"已提領 ${gain}")
            st.rerun()
        else: st.warning("餘額不足")

    st.markdown("---")
    st.caption("🛒 購買顯卡增加算力")
    gpus = [{"n":"GTX 1060", "p":500}, {"n":"RTX 4090", "p":3500}]
    cc = st.columns(2)
    for i, g in enumerate(gpus):
        with cc[i]:
            if st.button(f"買 {g['n']} (${g['p']})"):
                if user["money"] >= g['p']:
                    user["money"] -= g['p']
                    if "inventory" not in user: user["inventory"] = []
                    user["inventory"].append(g['n'])
                    db = load_db(); db["users"][uid] = user; save_db(db)
                    st.rerun()
                else: st.error("沒錢")

def page_hacker_terminal(uid, user):
    st.title("📟 駭客終端機")
    if "term_log" not in st.session_state: st.session_state.term_log = ["System ready."]
    
    st.code("\n".join(st.session_state.term_log), language="bash")
    cmd = st.chat_input("Command (scan, crack, loot)")
    
    if cmd:
        st.session_state.term_log.append(f"> {cmd}")
        if cmd == "scan": res = "Found target: 192.168.1.X"
        elif cmd == "crack": 
            if random.random() > 0.5: 
                res = "Access Granted."; st.session_state.hacked = True
            else: res = "Access Denied."
        elif cmd == "loot":
            if st.session_state.get("hacked"):
                amt = random.randint(50, 200)
                res = f"Stolen ${amt}."; user["money"] += amt; st.session_state.hacked=False
                db = load_db(); db["users"][uid] = user; save_db(db)
            else: res = "No access."
        else: res = "Unknown command."
        st.session_state.term_log.append(res)
        st.rerun()

def page_avatar_gen(uid, user):
    st.title("🧬 頭像生成")
    f = st.selectbox("Face", ["( )", "[ ]"])
    e = st.selectbox("Eyes", ["o o", "- -", "X X"])
    av = f"  {f[0]} {e} {f[1]}  "
    st.code(av)
    if st.button("Save to Bio"):
        user["bio"] = av; db=load_db(); db["users"][uid]=user; save_db(db)
        st.success("Saved!")

def page_signal_gen():
    st.title("🌊 訊號產生器")
    freq = st.slider("Hz", 1, 100, 10)
    t = np.linspace(0, 1, 200)
    y = np.sin(2*np.pi*freq*t)
    st.line_chart(y)

def page_network():
    st.title("🌐 網路工具")
    ip = st.text_input("IP", "192.168.1.1")
    st.write(f"Analyzing {ip}...")

def page_career(uid, user):
    st.title("🏹 轉職")
    curr = user.get("job", "Novice")
    for k, v in CLASSES.items():
        if k == "Novice": continue
        c1, c2 = st.columns([3,1])
        c1.write(f"**{v['name']}**: {v['desc']}")
        if curr == k: c2.button("當前", disabled=True, key=k)
        elif user["level"] >= 5:
            if c2.button("轉職", key=k):
                user["job"] = k; db=load_db(); db["users"][uid]=user; save_db(db); st.rerun()
        else: c2.button("Lv.5", disabled=True, key=k)

def page_profile(uid, user):
    st.title(f"📇 {user['name']}")
    st.write(f"Job: {user.get('job')} | Money: ${user.get('money')}")
    st.text(user.get("bio", ""))

# ==============================================================================
# 4. 主程式與導航
# ==============================================================================
def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("🏙️ CityOS V11.0")
        u = st.text_input("User"); p = st.text_input("Pass", type="password")
        if st.button("Login"):
            db = load_db()
            if u in db["users"] and db["users"][u]["password"] == p:
                st.session_state.logged_in = True; st.session_state.user_id = u
                st.session_state.user_data = db["users"][u]
                st.rerun()
            else: st.error("Error or Register first")
        return

    # Logged In
    user = st.session_state.user_data
    uid = st.session_state.user_id
    
    # Sidebar HUD
    st.sidebar.markdown(f"### 🆔 {user['name']}")
    st.sidebar.markdown(f"**{CLASSES.get(user.get('job','Novice'))['name']}**")
    c1, c2 = st.sidebar.columns(2)
    c1.metric("Lv", user.get("level", 1))
    c2.metric("💰", user.get("money", 0))
    st.sidebar.progress((user.get("exp",0)%100)/100.0)
    st.sidebar.divider()

    # Dynamic Navigation
    job = user.get("job", "Novice")
    pages = {"📊 主控台":"home", "📝 每日測驗":"quiz", "🏹 轉職中心":"career", "⛏️ 雲端挖礦":"mining"}
    
    if job in ["Engineer", "Architect"]: pages["🌊 訊號產生器"] = "signal"
    if job in ["Programmer", "Architect"]: pages["🧬 頭像生成器"] = "avatar"
    if job in ["Hacker", "Architect"]: pages["📟 駭客終端機"] = "terminal"; pages["🌐 網路工具"] = "network"
    
    pages["📇 個人名片"] = "profile"

    sel_name = st.sidebar.radio("導航", list(pages.keys()))
    sel = pages[sel_name]
    
    if st.sidebar.button("登出"):
        st.session_state.logged_in = False; st.rerun()

    # Routing
    if sel == "home":
        st.title("📊 主控台")
        st.info("歡迎回來。請從側邊欄選擇功能。")
        st.bar_chart(np.random.randint(10, 100, 7))
    elif sel == "quiz": page_daily_quiz(uid, user)
    elif sel == "mining": page_mining(uid, user)
    elif sel == "terminal": page_hacker_terminal(uid, user)
    elif sel == "avatar": page_avatar_gen(uid, user)
    elif sel == "signal": page_signal_gen()
    elif sel == "network": page_network()
    elif sel == "career": page_career(uid, user)
    elif sel == "profile": page_profile(uid, user)

if __name__ == "__main__":
    main()
