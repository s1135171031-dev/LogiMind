import streamlit as st
import pandas as pd
import random
import os
import base64
import time
import json
import hashlib
import numpy as np 
from datetime import datetime, date

# ==================================================
# 0. 核心設定與常數
# ==================================================
USER_DB_FILE = "users_v4.json" # 更新檔名以區隔舊版
LEVEL_CAP = 100
EXP_PER_LEVEL = 100

# 職業定義
CLASSES = {
    "None": {"name": "市民 (Citizen)", "desc": "尚無專精", "icon": "👤"},
    "Guardian": {"name": "守護者 (Guardian)", "desc": "專精資訊安全與加密技術", "icon": "🛡️", "color": "#00FF99"},
    "Architect": {"name": "架構師 (Architect)", "desc": "專精邏輯運算與硬體架構", "icon": "⚡", "color": "#00CCFF"},
    "Oracle": {"name": "預言家 (Oracle)", "desc": "專精數據分析與預測", "icon": "🔮", "color": "#D500F9"}
}

# 商店物品 (主題)
SHOP_ITEMS = {
    "theme_cyber_punk": {"name": "主題: 賽博龐克 (Cyber Yellow)", "cost": 100, "type": "theme", "key": "Cyber Punk"},
    "theme_matrix": {"name": "主題: 駭客任務 (Matrix Green)", "cost": 150, "type": "theme", "key": "Matrix"},
    "theme_royal": {"name": "主題: 皇家特務 (Royal Gold)", "cost": 300, "type": "theme", "key": "Royal"}
}

# 基礎主題
THEMES = {
    "Night City": {"bg": "#212529", "txt": "#E9ECEF", "btn": "#495057", "btn_txt": "#FFFFFF", "card": "#343A40", "chart": ["#00ADB5", "#EEEEEE", "#FF2E63"]},
    "Day City": {"bg": "#F8F9FA", "txt": "#343A40", "btn": "#6C757D", "btn_txt": "#FFFFFF", "card": "#FFFFFF", "chart": ["#343A40", "#6C757D", "#ADB5BD"]},
    # 解鎖主題
    "Cyber Punk": {"bg": "#0b0c10", "txt": "#c5c6c7", "btn": "#fca311", "btn_txt": "#000000", "card": "#1f2833", "chart": ["#fca311", "#45a29e", "#66fcf1"]},
    "Matrix": {"bg": "#0D0208", "txt": "#00FF41", "btn": "#003B00", "btn_txt": "#00FF41", "card": "#001A00", "chart": ["#008F11", "#00FF41", "#003B00"]},
    "Royal": {"bg": "#2C001E", "txt": "#FFD700", "btn": "#590035", "btn_txt": "#FFD700", "card": "#420025", "chart": ["#FFD700", "#FF007F", "#C0C0C0"]}
}

# ==================================================
# 1. 資料庫管理 (RPG 擴充版)
# ==================================================
def init_user_db():
    if not os.path.exists(USER_DB_FILE):
        default_data = {
            "users": {
                "frank": {
                    "password": "x", "name": "Frank (Commander)", "email": "frank@cityos.gov",
                    "level": "最高指揮官", "avatar_color": "#000000", "history": [],
                    # RPG Data
                    "exp": 9900, "rpg_level": 99, "coins": 9999, "class_type": "None",
                    "inventory": ["Night City", "Day City", "Cyber Punk", "Matrix", "Royal"], "last_login": ""
                },
                "user": {
                    "password": "123", "name": "Site Operator", "email": "op@cityos.gov",
                    "level": "初級管理員", "avatar_color": "#4285F4", "history": [],
                    # RPG Data
                    "exp": 0, "rpg_level": 1, "coins": 0, "class_type": "None",
                    "inventory": ["Night City", "Day City"], "last_login": ""
                }
            }
        }
        with open(USER_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=4, ensure_ascii=False)

def load_db():
    init_user_db()
    try:
        with open(USER_DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return {"users": {}}

def save_db(data):
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- RPG 邏輯 ---
def add_exp(user_key, amount):
    db = load_db()
    if user_key in db["users"]:
        u = db["users"][user_key]
        u["exp"] += amount
        # 簡單升級公式
        new_level = 1 + (u["exp"] // EXP_PER_LEVEL)
        if new_level > u["rpg_level"]:
            u["rpg_level"] = new_level
            st.toast(f"🎉 升級了！現在是 Level {new_level}", icon="🆙")
        save_db(db)
        return u
    return None

def add_coins(user_key, amount):
    db = load_db()
    if user_key in db["users"]:
        db["users"][user_key]["coins"] += amount
        save_db(db)
        st.toast(f"💰 獲得 {amount} CityCoins", icon="🪙")
        return db["users"][user_key]
    return None

def check_daily_login(user_key):
    db = load_db()
    if user_key in db["users"]:
        u = db["users"][user_key]
        today = str(date.today())
        if u.get("last_login") != today:
            u["last_login"] = today
            bonus_coins = 50
            bonus_exp = 50
            u["coins"] += bonus_coins
            u["exp"] += bonus_exp
            # Recalculate level just in case
            u["rpg_level"] = 1 + (u["exp"] // EXP_PER_LEVEL)
            save_db(db)
            return True, bonus_coins, bonus_exp
    return False, 0, 0

def purchase_item(user_key, item_id):
    db = load_db()
    user = db["users"][user_key]
    item = SHOP_ITEMS[item_id]
    
    if item["cost"] > user["coins"]:
        return False, "餘額不足"
    
    if item["key"] in user.get("inventory", []):
        return False, "已擁有此物品"
        
    user["coins"] -= item["cost"]
    user["inventory"].append(item["key"])
    save_db(db)
    return True, f"購買成功：{item['name']}"

def change_class(user_key, new_class):
    db = load_db()
    user = db["users"][user_key]
    if user["rpg_level"] < 5:
        return False, "等級不足 (需 Lv.5)"
    user["class_type"] = new_class
    save_db(db)
    return True, f"轉職成功！你現在是 {CLASSES[new_class]['name']}"

# ==================================================
# 2. 介面與工具函數
# ==================================================
st.set_page_config(page_title="CityOS V4.0", layout="wide", page_icon="🏙️")

if "user_data" not in st.session_state:
    st.session_state.update({
        "logged_in": False, "user_key": "", "user_data": {}, 
        "theme_name": "Night City", 
        "monitor_data": pd.DataFrame(np.random.randint(40, 60, size=(30, 3)), columns=['CPU', 'NET', 'SEC']), 
        "exam_active": False, "quiz_batch": []
    })

def apply_theme():
    # 確保當前主題在用戶庫存中，否則重置
    current_theme = st.session_state.theme_name
    # 簡化處理：如果主題名稱不在定義中(可能Key不同)，fallback
    t_key = current_theme.split(":")[-1].strip().replace("(", "").replace(")", "") 
    # 上面這行有點複雜，直接用 mapping
    t = THEMES.get(current_theme, THEMES["Night City"])
    # 如果選到解鎖主題，需檢查是否擁有 (略過此檢查以保持流暢，但在切換時控制)
    
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {t['bg']} !important; }}
    h1, h2, h3, h4, p, span, div, label, li, .stMarkdown, .stExpander, .stTabs, .stMetricValue {{ color: {t['txt']} !important; font-family: 'Segoe UI', sans-serif; }}
    .stButton>button {{ background-color: {t['btn']} !important; color: {t['btn_txt']} !important; border: none !important; border-radius: 6px !important; }}
    div[data-testid="stDataFrame"], div[data-testid="stExpander"] {{ background-color: {t['card']} !important; border: 1px solid rgba(128,128,128,0.2); }}
    [data-testid="stSidebar"] {{ background-color: {t['card']}; border-right: 1px solid rgba(128,128,128,0.1); }}
    .rpg-stat-box {{ background: rgba(255,255,255,0.05); padding: 10px; border-radius: 5px; margin-bottom: 5px; font-size: 0.9em; }}
    </style>
    """, unsafe_allow_html=True)

def render_svg(svg_code):
    b64 = base64.b64encode(svg_code.encode('utf-8')).decode("utf-8")
    st.markdown(f'<img src="data:image/svg+xml;base64,{b64}" width="200"/>', unsafe_allow_html=True)

# 簡易 SVG 定義
SVG_GATES = {
    "AND": '''<svg width="100" height="60" xmlns="http://www.w3.org/2000/svg"><path d="M10,10 L40,10 C55,10 65,20 65,30 C65,40 55,50 40,50 L10,50 Z" fill="none" stroke="#888" stroke-width="3"/><path d="M0,20 L10,20 M0,40 L10,40 M65,30 L80,30" stroke="#888" stroke-width="3"/></svg>''',
    "OR": '''<svg width="100" height="60" xmlns="http://www.w3.org/2000/svg"><path d="M10,10 L35,10 Q50,30 35,50 L10,50 Q25,30 10,10 Z" fill="none" stroke="#888" stroke-width="3"/><path d="M0,20 L15,20 M0,40 L15,40 M45,30 L60,30" stroke="#888" stroke-width="3"/></svg>'''
}

def load_qs():
    # 內建簡易題庫，避免檔案遺失問題
    return [
        {"q": "AND 閘輸入 1, 1 輸出為何?", "o": ["0", "1"], "a": "1"},
        {"q": "二進位 1010 等於十進位多少?", "o": ["8", "10", "12"], "a": "10"},
        {"q": "格雷碼的主要特性?", "o": ["相鄰兩數僅1bit不同", "運算速度快"], "a": "相鄰兩數僅1bit不同"},
        {"q": "哪種加密是不可逆的?", "o": ["AES", "RSA", "Hash (SHA-256)"], "a": "Hash (SHA-256)"},
        {"q": "CPU 中的 ALU 負責什麼?", "o": ["儲存資料", "算術邏輯運算"], "a": "算術邏輯運算"}
    ]

# ==================================================
# 3. 主程式邏輯
# ==================================================
def main_app():
    # 重新讀取最新的 User Data (確保金幣/EXP同步)
    db = load_db()
    user_key = st.session_state.user_key
    if user_key not in db["users"]: # 避免用戶被刪除後報錯
        st.session_state.logged_in = False
        st.rerun()
    
    user = db["users"][user_key]
    st.session_state.user_data = user # Update session
    
    apply_theme()
    
    # 變數提取
    lvl = user.get("level", "實習生") # 權限等級
    rpg_lvl = user.get("rpg_level", 1) # RPG 等級
    exp = user.get("exp", 0)
    coins = user.get("coins", 0)
    u_class = user.get("class_type", "None")
    
    # 計算進度條
    exp_in_curr_lvl = exp % EXP_PER_LEVEL
    progress_val = exp_in_curr_lvl / EXP_PER_LEVEL

    # --- Sidebar: 個人資訊卡 (RPG Style) ---
    with st.sidebar:
        st.title("🏙️ CityOS V4.0")
        st.caption("Cyber-Evolution System")
        
        # 顯示職業圖示
        class_info = CLASSES.get(u_class, CLASSES["None"])
        class_icon = class_info["icon"]
        
        st.markdown(f"""
        <div style="border-left: 4px solid {class_info.get('color', '#888')}; padding-left: 10px; margin-bottom: 20px;">
            <h3 style="margin:0">{class_icon} {user['name']}</h3>
            <small style="color:#aaa">{lvl}</small>
        </div>
        """, unsafe_allow_html=True)
        
        # RPG Stats
        c1, c2 = st.columns(2)
        with c1: st.metric("Level", rpg_lvl)
        with c2: st.metric("Coins", coins)
        
        st.write(f"EXP: {exp_in_curr_lvl} / {EXP_PER_LEVEL}")
        st.progress(progress_val)
        
        st.info(f"職業: {class_info['name']}")

        # 選單
        st.markdown("---")
        menu = {
            "Dash": "🏙️ 儀表板",
            "Logic": "⚡ 邏輯設施",
            "Base": "🔢 進制轉換",
            "Sec": "🛡️ 資訊安全局", # V3.2 Feature
            "Academy": "🎓 市政學院",
            "Shop": "🛒 補給站",   # V4.0 Feature
            "Profile": "📂 市民檔案" # Class Change here
        }
        sel = st.radio("導航", list(menu.values()), label_visibility="collapsed")

    # -----------------------------------
    # 頁面 1: 儀表板 (Dashboard)
    # -----------------------------------
    if sel == "🏙️ 儀表板":
        st.title(f"👋 早安，{class_info['name']}")
        
        # 每日登入檢查 (在頁面加載時已在後台執行，這裡只顯示狀態)
        # 如果是今天第一次登入，在 login 函數那邊會給予獎勵，這裡我們可以顯示一個歡迎橫幅
        
        # 職業專屬 Buff 顯示
        if u_class == "Oracle":
            st.success("🔮 預言家專屬技能發動：系統負載預測已優化")
        elif u_class == "Guardian":
            st.success("🛡️ 守護者專屬技能發動：防火牆效能提升 20%")
            
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("📡 即時監控")
            # 模擬數據
            chart_data = pd.DataFrame(
                np.random.randint(20, 90, size=(20, 3)),
                columns=['CPU', 'NET', 'SEC']
            )
            # 預言家可以看到更多數據
            if u_class == "Oracle":
                chart_data['PREDICT'] = np.random.randint(40, 60, size=20)
            
            st.line_chart(chart_data, height=250)
        
        with col2:
            st.subheader("📢 任務板")
            st.markdown("""
            * ✅ **每日登入**: +50 Coins (已完成)
            * ⬜ **完成一次考核**: +20 Coins
            * ⬜ **購買一個主題**: +100 EXP
            """)
            st.caption("完成任務以提升等級並解鎖更多功能！")

    # -----------------------------------
    # 頁面 2: 邏輯設施 (Logic)
    # -----------------------------------
    elif sel == "⚡ 邏輯設施":
        st.header("⚡ 邏輯閘實驗室")
        gate = st.selectbox("Component", ["AND", "OR"])
        render_svg(SVG_GATES.get(gate, SVG_GATES["AND"]))
        
        st.write("---")
        st.caption("操作提示：點擊下方按鈕進行模擬")
        if st.button("執行模擬運算"):
            with st.spinner("Calculating..."):
                time.sleep(0.5)
                add_exp(user_key, 5) # 微量 XP 獎勵
            st.success("運算完成！(EXP +5)")

    # -----------------------------------
    # 頁面 3: 進制轉換 (Base)
    # -----------------------------------
    elif sel == "🔢 進制轉換":
        st.header("🔢 數據轉換中心")
        val = st.number_input("Decimal Input", value=255)
        st.code(f"Binary: {bin(val)[2:]}\nHex: {hex(val)[2:].upper()}")
        
        if st.button("記錄數據"):
            add_exp(user_key, 5)
            st.toast("數據已歸檔 (EXP +5)")

    # -----------------------------------
    # 頁面 4: 資訊安全局 (InfoSec) - V3.2 + Class Buff
    # -----------------------------------
    elif sel == "🛡️ 資訊安全局":
        st.header("🛡️ 資訊安全局")
        
        tabs = st.tabs(["🔐 基礎加密", "#️⃣ 雜湊驗證", "☢️ RSA (守護者專用)"])
        
        with tabs[0]: # 凱薩
            txt = st.text_input("明文", "SECRET")
            shift = st.slider("偏移", 1, 10, 3)
            res = "".join([chr(ord(c)+shift) for c in txt])
            st.code(f"Cipher: {res}")
            
        with tabs[1]: # Hash
            h_txt = st.text_input("雜湊輸入", "Password")
            st.code(f"SHA256: {hashlib.sha256(h_txt.encode()).hexdigest()}")
            if st.button("驗證雜湊"):
                add_exp(user_key, 10)
                
        with tabs[2]: # RSA Class Exclusive
            if u_class == "Guardian" or lvl == "最高指揮官":
                st.success("權限驗證通過：守護者協定")
                st.info("此區域模擬非對稱金鑰生成...")
                c1, c2 = st.columns(2)
                c1.metric("Public Key", "E=65537, N=...")
                c2.metric("Private Key", "Hidden")
                if st.button("生成新金鑰對"):
                    st.spinner("Generating primes...")
                    time.sleep(1)
                    st.success("New Keys Generated! (EXP +20)")
                    add_exp(user_key, 20)
            else:
                st.error("⛔ 存取被拒：此功能僅限「守護者」職業或指揮官使用。請前往市民檔案進行轉職。")

    # -----------------------------------
    # 頁面 5: 市政學院 (Academy)
    # -----------------------------------
    elif sel == "🎓 市政學院":
        st.header("🎓 技能考核中心")
        qs = load_qs()
        
        if not st.session_state.exam_active:
            st.write(f"當前等級: {rpg_lvl}")
            if st.button("🚀 開始測驗 (消耗 0 體力)"):
                st.session_state.quiz_batch = random.sample(qs, 3)
                st.session_state.exam_active = True
                st.rerun()
        else:
            score = 0
            with st.form("quiz"):
                for i, q in enumerate(st.session_state.quiz_batch):
                    st.write(f"**Q{i+1}: {q['q']}**")
                    ans = st.radio("Ans", q['o'], key=f"q{i}")
                    if ans == q['a']: score += 1
                
                if st.form_submit_button("提交"):
                    st.session_state.exam_active = False
                    reward_coins = score * 10
                    reward_exp = score * 20
                    
                    st.balloons()
                    st.success(f"測驗結束！答對 {score}/3 題")
                    st.info(f"獲得獎勵： {reward_coins} Coins, {reward_exp} EXP")
                    
                    add_coins(user_key, reward_coins)
                    add_exp(user_key, reward_exp)
                    time.sleep(2)
                    st.rerun()

    # -----------------------------------
    # 頁面 6: 補給站 (Shop) - NEW
    # -----------------------------------
    elif sel == "🛒 補給站":
        st.header("🛒 CityOS 補給站")
        st.markdown(f"**持有貨幣:** `{coins} CityCoins`")
        
        cols = st.columns(3)
        for idx, (item_id, item) in enumerate(SHOP_ITEMS.items()):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.subheader(item["type"] == "theme" and "🎨" or "🎁")
                    st.write(f"**{item['name']}**")
                    st.write(f"💰 {item['cost']}")
                    
                    is_owned = item["key"] in user.get("inventory", [])
                    
                    if is_owned:
                        st.button("已擁有", disabled=True, key=item_id)
                    else:
                        if st.button(f"購買", key=item_id):
                            ok, msg = purchase_item(user_key, item_id)
                            if ok:
                                st.success(msg)
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(msg)

    # -----------------------------------
    # 頁面 7: 市民檔案 (Profile) & 轉職
    # -----------------------------------
    elif sel == "📂 市民檔案":
        st.header("📂 檔案管理")
        
        # 1. 轉職系統
        st.subheader("⚔️ 職業專精 (Class Spec)")
        current = CLASSES.get(u_class)
        st.info(f"當前職業: **{current['name']}** - {current['desc']}")
        
        if u_class == "None":
            st.write("可選職業 (需 Lv.5):")
            c1, c2, c3 = st.columns(3)
            
            # Guardian
            with c1:
                st.write("#### 🛡️ 守護者")
                st.caption("解鎖 RSA 加密工具")
                if st.button("轉職 守護者"):
                    ok, msg = change_class(user_key, "Guardian")
                    if ok: st.balloons(); st.rerun()
                    else: st.error(msg)
            
            # Architect
            with c2:
                st.write("#### ⚡ 架構師")
                st.caption("解鎖高階邏輯模擬")
                if st.button("轉職 架構師"):
                    ok, msg = change_class(user_key, "Architect")
                    if ok: st.balloons(); st.rerun()
                    else: st.error(msg)

            # Oracle
            with c3:
                st.write("#### 🔮 預言家")
                st.caption("解鎖數據預測儀表板")
                if st.button("轉職 預言家"):
                    ok, msg = change_class(user_key, "Oracle")
                    if ok: st.balloons(); st.rerun()
                    else: st.error(msg)
        else:
            if st.button("🔄 重置職業 (花費 500 Coins)"):
                if coins >= 500:
                    add_coins(user_key, -500)
                    change_class(user_key, "None")
                    st.rerun()
                else:
                    st.error("金幣不足")

        st.divider()
        
        # 2. 主題切換 (Inventory)
        st.subheader("🎨 介面風格")
        my_themes = user.get("inventory", ["Night City"])
        selected_theme = st.selectbox("選擇主題", my_themes, index=0 if st.session_state.theme_name not in my_themes else my_themes.index(st.session_state.theme_name))
        
        if selected_theme != st.session_state.theme_name:
            st.session_state.theme_name = selected_theme
            st.rerun()
            
        st.divider()
        if st.button("登出系統"):
            st.session_state.logged_in = False
            st.rerun()

# ==================================================
# 4. 登入頁面
# ==================================================
def login_page():
    # 簡易登入樣式
    st.title("CityOS V4.0")
    st.subheader("Cyber-Evolution")
    
    init_user_db() # 確保 DB 存在
    
    tab1, tab2 = st.tabs(["登入", "註冊"])
    
    with tab1:
        u = st.text_input("User", "frank")
        p = st.text_input("Pass", "x", type="password")
        if st.button("Login"):
            db = load_db()
            users = db["users"]
            if u in users and users[u]["password"] == p:
                # 每日登入邏輯
                ok, c, e = check_daily_login(u)
                
                st.session_state.logged_in = True
                st.session_state.user_key = u
                
                if ok:
                    st.toast(f"每日登入獎勵！ Coins +{c}, EXP +{e}", icon="🎁")
                st.rerun()
            else:
                st.error("Fail")
                
    with tab2:
        nu = st.text_input("New User")
        np_ = st.text_input("New Pass", type="password")
        if st.button("Register"):
            db = load_db()
            if nu not in db["users"]:
                db["users"][nu] = {
                    "password": np_, "name": nu, "email": f"{nu}@city.gov",
                    "level": "實習生", "coins": 100, "exp": 0, "rpg_level": 1,
                    "class_type": "None", "inventory": ["Night City", "Day City"],
                    "history": [], "last_login": ""
                }
                save_db(db)
                st.success("註冊成功，請登入")
            else:
                st.error("帳號已存在")

if st.session_state.logged_in:
    main_app()
else:
    login_page()
