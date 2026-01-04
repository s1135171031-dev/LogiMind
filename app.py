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
    page_title="CityOS V9.5 Engineer RPG",
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
        "desc": "擅長硬體。解鎖：[訊號產生器]、[電阻色碼]。", "unlocks": ["Resistor", "AdvancedCircuit", "SignalGen"]
    },
    "Programmer": {
        "name": "軟體工程師", "icon": "💻", 
        "desc": "擅長編碼。解鎖：[進位轉換]、[ASCII]。", "unlocks": ["ASCII", "BaseConverter"]
    },
    "Architect": {
        "name": "系統架構師", "icon": "⚡", 
        "desc": "全能型專家。解鎖：[所有工具]。", "unlocks": ["All"]
    },
    "Hacker": {
        "name": "資安專家", "icon": "🛡️", 
        "desc": "擅長網絡。解鎖：[網路計算器]、[密碼學]。", "unlocks": ["Crypto", "NetworkCalc"]
    }
}

SVG_LIB = {
    "AND": '''<svg width="100" height="60"><path d="M10,5 L40,5 C55,5 65,15 65,25 C65,35 55,45 40,45 L10,45 Z" fill="none" stroke="#CCC" stroke-width="3"/><path d="M0,15 L10,15 M0,35 L10,35 M65,25 L80,25" stroke="#CCC" stroke-width="3"/></svg>''',
    "OR": '''<svg width="100" height="60"><path d="M10,5 L35,5 Q50,25 35,45 L10,45 Q25,25 10,5 Z" fill="none" stroke="#CCC" stroke-width="3"/><path d="M0,15 L15,15 M0,35 L15,35 M45,25 L60,25" stroke="#CCC" stroke-width="3"/></svg>''',
    "NOT": '''<svg width="100" height="60"><path d="M20,5 L20,45 L55,25 Z" fill="none" stroke="#CCC" stroke-width="3"/><circle cx="59" cy="25" r="3" fill="none" stroke="#CCC" stroke-width="2"/><path d="M0,25 L20,25 M63,25 L80,25" stroke="#CCC" stroke-width="3"/></svg>''',
    "XOR": '''<svg width="100" height="60"><path d="M20,5 L45,5 Q60,25 45,45 L20,45 Q35,25 20,5 Z" fill="none" stroke="#CCC" stroke-width="3"/><path d="M10,5 Q25,25 10,45" fill="none" stroke="#CCC" stroke-width="3"/><path d="M0,15 L15,15 M0,35 L15,35 M55,25 L70,25" stroke="#CCC" stroke-width="3"/></svg>''',
    "NAND": '''<svg width="100" height="60"><path d="M10,5 L40,5 C55,5 65,15 65,25 C65,35 55,45 40,45 L10,45 Z" fill="none" stroke="#CCC" stroke-width="3"/><circle cx="69" cy="25" r="3" fill="none" stroke="#CCC" stroke-width="2"/><path d="M0,15 L10,15 M0,35 L10,35 M73,25 L85,25" stroke="#CCC" stroke-width="3"/></svg>''',
    "NOR": '''<svg width="100" height="60"><path d="M10,5 L35,5 Q50,25 35,45 L10,45 Q25,25 10,5 Z" fill="none" stroke="#CCC" stroke-width="3"/><circle cx="64" cy="25" r="3" fill="none" stroke="#CCC" stroke-width="2"/><path d="M0,15 L15,15 M0,35 L15,35 M68,25 L80,25" stroke="#CCC" stroke-width="3"/></svg>'''
}

# ==============================================================================
# 2. Backend Logic
# ==============================================================================

def get_admin_data():
    return {
        "password": "x12345678x", "name": "Frank (Admin)", 
        "level": 100, "exp": 99999, "money": 99999, "job": "Architect", 
        "badges": ["GM"], "inventory": ["無限經驗卡"],
        "last_quiz_date": str(date.today()), "quiz_attempts": 0, "history_score": 5,
        "bio": "System Creator."
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
    if os.path.exists(QUESTION_DB_FILE):
        try:
            with open(QUESTION_DB_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    p = line.strip().split('|')
                    if len(p)>=5: questions.append({"id":p[0],"type":p[1],"q":p[2],"opts":p[3].split(','),"ans":p[4]})
            return questions
        except: pass
    for i in range(5):
        questions.append({"id":f"M{i}","type":"1","q":f"Logic Test {i}","opts":["0","1"],"ans":"1"})
    return questions

def check_level_up(user):
    cur, exp = user.get("level", 1), user.get("exp", 0)
    new_lvl = 1 + (exp // 100)
    if new_lvl > cur:
        user["level"] = new_lvl; return True, new_lvl
    return False, cur

# ==============================================================================
# 3. 頁面功能模組
# ==============================================================================

def render_sidebar_hud(user):
    st.sidebar.markdown(f"### 🆔 {user['name']}")
    job = CLASSES.get(user.get("job", "Novice"), CLASSES["Novice"])
    st.sidebar.markdown(f"**職業**: {job['icon']} {job['name']}")
    c1, c2 = st.sidebar.columns([1,2])
    c1.metric("Lv", user.get("level", 1))
    c2.metric("💰", user.get("money", 0))
    st.sidebar.progress((user.get("exp",0)%100)/100.0, text=f"XP: {user.get('exp',0)}")
    st.sidebar.markdown("---")

def page_shop(uid, user):
    st.title("🛒 道具商店")
    c1, c2 = st.columns([2, 1])
    with c1:
        items = [{"name":"經驗卡","p":100},{"name":"重置券","p":200},{"name":"咖啡","p":50}]
        cols = st.columns(3)
        for i, item in enumerate(items):
            with cols[i]:
                st.info(f"{item['name']}\n${item['p']}")
                if st.button("購買", key=f"b{i}"):
                    if user["money"]>=item['p']:
                        user["money"]-=item['p']; 
                        if "inventory" not in user: user["inventory"]=[]
                        user["inventory"].append(item['name'])
                        db=load_db(); db["users"][uid]=user; save_db(db)
                        st.toast("購買成功!"); st.rerun()
                    else: st.error("沒錢")
    with c2:
        st.write("🎒 背包:", ", ".join(user.get("inventory", [])))

def page_network():
    st.title("🌐 網路子網掩碼計算器")
    ip = st.text_input("IP", "192.168.1.10")
    cidr = st.slider("CIDR", 0, 32, 24)
    try:
        net = ipaddress.IPv4Network(f"{ip}/{cidr}", strict=False)
        st.code(f"Net: {net.network_address}\nMask: {net.netmask}\nHosts: {net.num_addresses}")
    except: st.error("Error")

def page_signal_gen():
    st.title("🌊 波形訊號產生器")
    c1, c2 = st.columns([1,3])
    with c1:
        wt = st.selectbox("Wave", ["Sine","Square"])
        freq = st.slider("Hz", 1, 100, 5)
    with c2:
        t = np.linspace(0, 1, 500)
        y = np.sin(2*np.pi*freq*t) if wt=="Sine" else np.sign(np.sin(2*np.pi*freq*t))
        fig, ax = plt.subplots(figsize=(8,3))
        ax.plot(t, y, 'g'); ax.set_facecolor('#111'); fig.patch.set_facecolor('#111')
        ax.tick_params(colors='white')
        st.pyplot(fig)

def page_daily_quiz(uid, user):
    st.header("📝 每日測驗")
    today = str(date.today())
    if user.get("last_quiz_date")!=today:
        user["last_quiz_date"]=today; user["quiz_attempts"]=0
        db=load_db(); db["users"][uid]=user; save_db(db)
    
    if user["quiz_attempts"]>=3: st.error("今日次數已盡"); return
    
    if "qs" not in st.session_state:
        st.session_state.qs = random.sample(load_questions(), 3)
        st.session_state.q_idx = 0
        st.session_state.score = 0
    
    q_curr = st.session_state.qs[st.session_state.q_idx]
    st.write(f"Q{st.session_state.q_idx+1}: {q_curr['q']}")
    with st.form("quiz"):
        ans = st.radio("Ans", q_curr['opts'])
        if st.form_submit_button("Submit"):
            if ans==q_curr['ans']: st.session_state.score+=1
            if st.session_state.q_idx+1 >= 3:
                # Finish
                r = st.session_state.score
                gain = r * 20
                st.success(f"得分: {r}/3 | +${gain}")
                user["money"]+=gain; user["exp"]+=gain*2; user["quiz_attempts"]+=1
                check_level_up(user)
                db=load_db(); db["users"][uid]=user; save_db(db)
                del st.session_state["qs"]
                st.rerun()
            else:
                st.session_state.q_idx+=1
                st.rerun()

def page_toolbox(user):
    st.title("🧰 基礎工具箱")
    t1, t2 = st.tabs(["邏輯閘", "進位"])
    with t1:
        g = st.selectbox("Gate", list(SVG_LIB.keys()))
        a, b = st.toggle("A"), st.toggle("B")
        st.write("Res:", int(eval(f"{a} and {b}") if g=="AND" else 0)) # 簡化顯示
        st.markdown(SVG_LIB[g].replace('width="100"','width="200"'), unsafe_allow_html=True)
    with t2:
        v = st.number_input("Dec", 255)
        st.code(f"HEX: {hex(v)}")

def page_career(uid, user):
    st.title("🏹 轉職中心")
    curr = user.get("job", "Novice")
    for k,v in CLASSES.items():
        if k=="Novice": continue
        with st.container(border=True):
            c1, c2 = st.columns([3,1])
            c1.markdown(f"### {v['icon']} {v['name']}")
            c1.caption(v['desc'])
            if curr==k: c2.button("Current", disabled=True, key=k)
            elif user["level"]>=5: 
                if c2.button("轉職", key=k):
                    user["job"]=k; db=load_db(); db["users"][uid]=user; save_db(db); st.rerun()
            else: c2.button("Lv.5解鎖", disabled=True, key=k)

def page_board(uid, user):
    st.title("💬 留言")
    db=load_db(); msgs=db.get("messages", [])
    t = st.text_input("Msg")
    if st.button("Send") and t:
        msgs.insert(0, {"u":user["name"],"j":user.get("job","Novice"),"t":t})
        db["messages"]=msgs[:20]; save_db(db); st.rerun()
    for m in msgs: st.caption(f"{CLASSES.get(m['j'],CLASSES['Novice'])['icon']} {m['u']}: {m['t']}")

def page_profile(uid, user):
    st.title("📇 名片")
    st.write(user)

# ==============================================================================
# 4. 主流程 (含動態側邊欄)
# ==============================================================================
def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in=False

    # --- Login ---
    if not st.session_state.logged_in:
        st.markdown("<h1 style='text-align:center'>🏙️ CityOS V9.5</h1>", unsafe_allow_html=True)
        c2 = st.columns([1,2,1])[1]
        with c2:
            tab1, tab2 = st.tabs(["登入", "註冊"])
            with tab1:
                u = st.text_input("帳號", value="") # 空白
                p = st.text_input("密碼", type="password", value="")
                if st.button("登入"):
                    db=load_db()
                    if u in db["users"] and db["users"][u]["password"]==p:
                        st.session_state.logged_in=True
                        st.session_state.user_id=u
                        st.session_state.user_data=db["users"][u]
                        st.rerun()
                    else: st.error("Fail")
            with tab2:
                nu = st.text_input("新帳號"); np_ = st.text_input("新密碼", type="password")
                if st.button("註冊"):
                    db=load_db()
                    if nu not in db["users"]:
                        db["users"][nu] = {"password":np_,"name":nu,"level":1,"exp":0,"money":0,"job":"Novice"}
                        save_db(db); st.success("OK")
        return

    # --- Main App ---
    user = st.session_state.user_data
    uid = st.session_state.user_id
    render_sidebar_hud(user)
    
    # === 動態選單邏輯 (Dynamic Sidebar) ===
    job = user.get("job", "Novice")
    
    # 1. 核心選單 (Everyone)
    pages = {"📊 主控台": "home", "📝 每日測驗": "quiz", "🏹 轉職中心": "career", "🛒 道具商店": "shop"}
    
    # 2. 職業解鎖功能 (Job Unlocks)
    # 只有工程師(Engineer)或架構師(Architect)看得到
    if job in ["Engineer", "Architect"]:
        pages["🌊 訊號產生器"] = "signal"
        
    # 只有駭客(Hacker)或架構師(Architect)看得到
    if job in ["Hacker", "Architect"]:
        pages["🌐 網路工具"] = "network"
        
    # 3. 社群與系統 (System)
    pages["💬 社群留言"] = "board"
    pages["📇 個人名片"] = "profile"
    
    # 側邊欄渲染
    st.sidebar.markdown("### 🗺️ 導航")
    
    # 使用單一 Radio，但選項是動態過濾過的
    selection_name = st.sidebar.radio("前往", list(pages.keys()), label_visibility="collapsed")
    selection = pages[selection_name]

    # 4. 登出按鈕 (獨立放在最下方)
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 登出系統"):
        st.session_state.logged_in = False
        del st.session_state['user_data']
        st.rerun()

    # === 頁面路由 ===
    if selection == "home":
        st.title("📊 主控台")
        st.info(f"歡迎回來，{user['name']}。")
        st.write("目前系統運作正常。")
        st.line_chart(np.random.randn(10,2))
        
    elif selection == "quiz": page_daily_quiz(uid, user)
    elif selection == "shop": page_shop(uid, user)
    elif selection == "signal": page_signal_gen()
    elif selection == "network": page_network()
    elif selection == "career": page_career(uid, user)
    elif selection == "board": page_board(uid, user)
    elif selection == "profile": page_profile(uid, user)

if __name__ == "__main__":
    main()
