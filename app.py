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
# 0. 核心設定與常數 (RPG + System)
# ==================================================
USER_DB_FILE = "users.json"
EXP_PER_LEVEL = 100

# 職業定義 (RPG)
CLASSES = {
    "None": {"name": "市民 (Citizen)", "desc": "尚無專精", "icon": "👤", "color": "#888888"},
    "Guardian": {"name": "守護者 (Guardian)", "desc": "專精資訊安全與加密技術", "icon": "🛡️", "color": "#00FF99"},
    "Architect": {"name": "架構師 (Architect)", "desc": "專精邏輯運算與硬體架構", "icon": "⚡", "color": "#00CCFF"},
    "Oracle": {"name": "預言家 (Oracle)", "desc": "專精數據分析與預測", "icon": "🔮", "color": "#D500F9"}
}

# 商店物品 (RPG)
SHOP_ITEMS = {
    "theme_cyber_punk": {"name": "主題: 賽博龐克 (Cyber Yellow)", "cost": 100, "type": "theme", "key": "Cyber Punk"},
    "theme_matrix": {"name": "主題: 駭客任務 (Matrix Green)", "cost": 150, "type": "theme", "key": "Matrix"},
    "theme_royal": {"name": "主題: 皇家特務 (Royal Gold)", "cost": 300, "type": "theme", "key": "Royal"}
}

# 介面主題 (擴充版)
THEMES = {
    "Night City": {"bg": "#212529", "txt": "#E9ECEF", "btn": "#495057", "btn_txt": "#FFFFFF", "card": "#343A40", "chart": ["#00ADB5", "#EEEEEE", "#FF2E63"]},
    "Day City": {"bg": "#F8F9FA", "txt": "#343A40", "btn": "#6C757D", "btn_txt": "#FFFFFF", "card": "#FFFFFF", "chart": ["#343A40", "#6C757D", "#ADB5BD"]},
    "Cyber Punk": {"bg": "#0b0c10", "txt": "#c5c6c7", "btn": "#fca311", "btn_txt": "#000000", "card": "#1f2833", "chart": ["#fca311", "#45a29e", "#66fcf1"]},
    "Matrix": {"bg": "#0D0208", "txt": "#00FF41", "btn": "#003B00", "btn_txt": "#00FF41", "card": "#001A00", "chart": ["#008F11", "#00FF41", "#003B00"]},
    "Royal": {"bg": "#2C001E", "txt": "#FFD700", "btn": "#590035", "btn_txt": "#FFD700", "card": "#420025", "chart": ["#FFD700", "#FF007F", "#C0C0C0"]}
}

# 權限等級
LEVEL_MAP = {
    "實習生": 0,
    "初級管理員": 1,
    "中級管理員": 2,
    "高級管理員": 3,
    "最高指揮官": 99
}

# ==================================================
# 1. 資料庫與 RPG 邏輯
# ==================================================
def init_user_db():
    if not os.path.exists(USER_DB_FILE) or os.path.getsize(USER_DB_FILE) == 0:
        default_data = {
            "users": {
                "frank": {
                    "password": "x12345678x",
                    "name": "Frank (Supreme Commander)",
                    "email": "frank@cityos.gov",
                    "level": "最高指揮官",
                    "avatar_color": "#000000",
                    "history": [],
                    # RPG Data
                    "exp": 9900, "rpg_level": 99, "coins": 9999, "class_type": "None",
                    "inventory": list(THEMES.keys()), "last_login": ""
                },
                "user": {
                    "password": "123",
                    "name": "Site Operator",
                    "email": "op@cityos.gov",
                    "level": "初級管理員", 
                    "avatar_color": "#4285F4",
                    "history": [],
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
            data = json.load(f)
            # 自動修復：如果舊帳號沒有 RPG 欄位，補上預設值
            changed = False
            for u in data["users"].values():
                if "coins" not in u: 
                    u.update({"coins": 0, "exp": 0, "rpg_level": 1, "class_type": "None", "inventory": ["Night City", "Day City"], "last_login": ""})
                    changed = True
            if changed: save_db(data)
            return data
    except:
        return {"users": {}}

def save_db(data):
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- RPG Helper Functions ---
def add_exp(user_key, amount):
    db = load_db()
    if user_key in db["users"]:
        u = db["users"][user_key]
        u["exp"] += amount
        new_level = 1 + (u["exp"] // EXP_PER_LEVEL)
        if new_level > u.get("rpg_level", 1):
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
            u["rpg_level"] = 1 + (u["exp"] // EXP_PER_LEVEL)
            save_db(db)
            return True, bonus_coins, bonus_exp
    return False, 0, 0

def purchase_item(user_key, item_id):
    db = load_db()
    user = db["users"][user_key]
    item = SHOP_ITEMS[item_id]
    if item["cost"] > user["coins"]: return False, "餘額不足"
    if item["key"] in user.get("inventory", []): return False, "已擁有此物品"
    user["coins"] -= item["cost"]
    user["inventory"].append(item["key"])
    save_db(db)
    return True, f"購買成功：{item['name']}"

def change_class(user_key, new_class):
    db = load_db()
    user = db["users"][user_key]
    if user.get("rpg_level", 1) < 5 and user["level"] != "最高指揮官":
        return False, "等級不足 (需 Lv.5)"
    user["class_type"] = new_class
    save_db(db)
    return True, f"轉職成功！你現在是 {CLASSES[new_class]['name']}"

def check_access(user_level_str, required_level_str):
    u_score = LEVEL_MAP.get(user_level_str, 0)
    r_score = LEVEL_MAP.get(required_level_str, 0)
    return u_score >= r_score

# ==================================================
# 2. 系統視覺與工具
# ==================================================
st.set_page_config(page_title="CityOS V5.0", layout="wide", page_icon="🏙️")

SVG_ICONS = {
    "MUX": '''<svg width="120" height="100" viewBox="0 0 120 100" xmlns="http://www.w3.org/2000/svg"><path d="M30,10 L90,25 L90,75 L30,90 Z" fill="none" stroke="currentColor" stroke-width="3"/><text x="45" y="55" fill="currentColor" font-size="14">MUX</text><path d="M10,25 L30,25 M10,40 L30,40 M10,55 L30,55 M10,70 L30,70 M90,50 L110,50 M60,85 L60,95" stroke="currentColor" stroke-width="2"/></svg>''',
    "AND": '''<svg width="100" height="60" viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg"><path d="M10,10 L40,10 C55,10 65,20 65,30 C65,40 55,50 40,50 L10,50 Z" fill="none" stroke="currentColor" stroke-width="3"/><path d="M0,20 L10,20 M0,40 L10,40 M65,30 L80,30" stroke="currentColor" stroke-width="3"/></svg>''',
    "OR": '''<svg width="100" height="60" viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg"><path d="M10,10 L35,10 Q50,30 35,50 L10,50 Q25,30 10,10 Z" fill="none" stroke="currentColor" stroke-width="3"/><path d="M0,20 L15,20 M0,40 L15,40 M45,30 L60,30" stroke="currentColor" stroke-width="3"/></svg>''',
    "XOR": '''<svg width="100" height="60" viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg"><path d="M20,10 L45,10 Q60,30 45,50 L20,50 Q35,30 20,10 Z" fill="none" stroke="currentColor" stroke-width="3"/><path d="M10,10 Q25,30 10,50" fill="none" stroke="currentColor" stroke-width="3"/><path d="M0,20 L15,20 M0,40 L15,40 M55,30 L70,30" stroke="currentColor" stroke-width="3"/></svg>'''
}

if "user_data" not in st.session_state:
    init_df = pd.DataFrame(np.random.randint(40, 60, size=(30, 3)), columns=['CPU', 'NET', 'SEC'])
    st.session_state.update({
        "logged_in": False, "user_key": "", "user_data": {}, 
        "theme_name": "Night City",
        "monitor_data": init_df, "exam_active": False, "quiz_batch": []
    })

def apply_theme():
    current_theme = st.session_state.theme_name
    t = THEMES.get(current_theme, THEMES["Night City"])
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {t['bg']} !important; }}
    h1, h2, h3, h4, p, span, div, label, li, .stMarkdown, .stExpander, .stTabs, .stMetricValue {{ color: {t['txt']} !important; font-family: 'Segoe UI', sans-serif; }}
    .stButton>button {{ background-color: {t['btn']} !important; color: {t['btn_txt']} !important; border: none !important; border-radius: 6px !important; }}
    div[data-testid="stDataFrame"], div[data-testid="stExpander"] {{ background-color: {t['card']} !important; border: 1px solid rgba(128,128,128,0.2); }}
    [data-testid="stSidebar"] {{ background-color: {t['card']}; border-right: 1px solid rgba(128,128,128,0.1); }}
    
    .commander-card {{ border: 2px solid gold !important; box-shadow: 0 0 15px rgba(255, 215, 0, 0.2); background: linear-gradient(135deg, rgba(0,0,0,0.8), rgba(50,50,50,0.9)); }}
    .commander-badge {{ color: gold; font-weight: bold; font-size: 0.8em; border: 1px solid gold; padding: 2px 6px; border-radius: 4px; display: inline-block; margin-top:5px;}}
    .intro-box {{ background-color: rgba(0, 173, 181, 0.1); border-left: 5px solid #00ADB5; padding: 15px; border-radius: 5px; margin-bottom: 20px; line-height: 1.6;}}
    </style>
    """, unsafe_allow_html=True)

def render_svg(svg_code):
    svg_black = svg_code.replace('stroke="currentColor"', 'stroke="#888888"').replace('fill="currentColor"', 'fill="#888888"')
    b64 = base64.b64encode(svg_black.encode('utf-8')).decode("utf-8")
    st.markdown(f'''<div style="background-color: rgba(255,255,255,0.05); border-radius: 8px; padding: 20px; margin-bottom: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"><img src="data:image/svg+xml;base64,{b64}" width="200"/></div>''', unsafe_allow_html=True)

def load_qs_from_txt():
    q = []
    errors = []
    if os.path.exists("questions.txt"):
        try:
            with open("questions.txt", "r", encoding="utf-8") as f:
                for idx, l in enumerate(f):
                    line_content = l.strip()
                    if not line_content: continue
                    p = line_content.split("|")
                    if len(p) == 5: 
                        q.append({"id":p[0],"diff":p[1],"q":p[2],"o":p[3].split(","),"a":p[4]})
                    else:
                        errors.append(f"Line {idx+1}: 格式錯誤")
        except Exception as e:
            errors.append(str(e))
    return q, errors

def update_data_random_walk():
    last_row = st.session_state.monitor_data.iloc[-1]
    new_vals = [max(0, min(100, last_row[col] + random.randint(-5, 5))) for col in ['CPU', 'NET', 'SEC']]
    new_row = pd.DataFrame([new_vals], columns=['CPU', 'NET', 'SEC'])
    updated_df = pd.concat([st.session_state.monitor_data, new_row], ignore_index=True)
    if len(updated_df) > 30: updated_df = updated_df.iloc[1:]
    st.session_state.monitor_data = updated_df
    return updated_df

# ==================================================
# 3. 主應用程式邏輯
# ==================================================
def main_app():
    # 確保 session 資料是最新的
    db = load_db()
    if st.session_state.user_key in db["users"]:
        st.session_state.user_data = db["users"][st.session_state.user_key]
    
    user = st.session_state.user_data
    user_key = st.session_state.user_key
    user_lvl = user.get("level", "實習生")
    
    # RPG Data
    rpg_lvl = user.get("rpg_level", 1)
    coins = user.get("coins", 0)
    exp = user.get("exp", 0)
    u_class = user.get("class_type", "None")
    
    apply_theme()
    t_colors = THEMES[st.session_state.theme_name]["chart"]
    
    is_commander = (user_lvl == "最高指揮官")
    class_info = CLASSES.get(u_class, CLASSES["None"])

    with st.sidebar:
        st.title("🏙️ CityOS V5.0")
        st.caption("Hybrid System (Logic + RPG)")
        
        # --- RPG 個人卡片 ---
        card_bg = "rgba(255,255,255,0.05)"
        border_color = class_info.get('color', '#888')
        card_class = "commander-card" if is_commander else ""
        badge_html = "<div class='commander-badge'>SUPREME ACCESS</div>" if is_commander else ""
        
        st.markdown(f"""
        <div class="{card_class}" style="padding:15px; background:{card_bg}; border-radius:8px; margin-bottom:15px; border-left:4px solid {border_color};">
            <div style="font-size:1.1em; font-weight:bold;">{class_info['icon']} {user['name']}</div>
            <div style="font-size:0.8em; opacity:0.7;">{user['email']}</div>
            <div style="font-size:0.8em; margin-top:5px; color:{border_color};">{user_lvl}</div>
            <hr style="margin: 5px 0; opacity: 0.3;">
            <div style="display:flex; justify-content:space-between; font-size:0.9em;">
                <span>Lv. {rpg_lvl}</span>
                <span>💰 {coins}</span>
            </div>
            {badge_html}
        </div>
        """, unsafe_allow_html=True)
        
        # EXP Progress
        exp_in_curr_lvl = exp % EXP_PER_LEVEL
        st.progress(exp_in_curr_lvl / EXP_PER_LEVEL)
        st.caption(f"EXP: {exp_in_curr_lvl} / {EXP_PER_LEVEL}")
        # -------------------
        
        # 動態選單生成
        st.markdown("### 導航選單")
        menu_options = {
            "Dashboard": "🏙️ 城市儀表板",
            "Electricity": "⚡ 電力設施 (Logic)",
            "Boolean": "🧩 布林轉換器 (Lv1+)",
            "GrayCode": "🏦 格雷碼核心 (Lv2+)",
            "BaseConv": "🔢 進制轉換 (Lv2+)",
            "InfoSec": "🛡️ 資訊安全局 (Lv2+)", 
            "KMap": "🗺️ 卡諾圖 (Lv3+)",
            "Academy": "🎓 市政學院",
            "Shop": "🛒 補給站 (New)",
            "Profile": "📂 市民檔案",
        }
        
        if is_commander:
            menu_options["Commander"] = "☢️ 核心控制"

        selection = st.radio("前往", list(menu_options.values()), label_visibility="collapsed")

    # -------------------------------------------
    # 頁面: 城市儀表板
    # -------------------------------------------
    if selection == "🏙️ 城市儀表板":
        col_h1, col_h2 = st.columns([3, 1])
        with col_h1: st.title(f"👋 早安，{class_info['name']}")
        with col_h2: st.caption(datetime.now().strftime("%Y-%m-%d %H:%M"))
        
        # RPG 每日獎勵
        if st.button("🎁 領取每日補給"):
            ok, c, e = check_daily_login(user_key)
            if ok: 
                st.balloons()
                st.success(f"領取成功！ 獲得 {c} Coins, {e} EXP")
                time.sleep(1); st.rerun()
            else:
                st.info("今天已經領過囉！明天再來。")

        # 職業特效
        if u_class == "Oracle": st.success("🔮 預言家專屬：系統預測模組已啟動")
        elif u_class == "Guardian": st.success("🛡️ 守護者專屬：防火牆強化中")

        st.markdown("""
        <div class="intro-box">
            <b>CityOS V5.0 Hybrid</b> 整合了傳統邏輯運算與現代 RPG 激勵系統。
            <br>完成運算任務可獲得 <b>EXP</b>，通過市政學院考核可獲得 <b>Coins</b>。
            前往 <b>補給站</b> 購買主題，或在 <b>市民檔案</b> 進行轉職。
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("📡 即時監控")
            chart_ph = st.empty()
            for _ in range(5): 
                df = update_data_random_walk()
                chart_ph.area_chart(df, color=t_colors, height=250)
                time.sleep(0.3)

        with col2:
            st.subheader("📁 狀態")
            qs, errs = load_qs_from_txt()
            st.metric("題庫總數", len(qs))
            st.metric("目前等級", rpg_lvl)

    # -------------------------------------------
    # 頁面: 電力設施 (Logic)
    # -------------------------------------------
    elif selection == "⚡ 電力設施 (Logic)":
        st.header("⚡ 邏輯閘視覺化")
        col1, col2 = st.columns([1, 2])
        with col1:
            gate = st.selectbox("選擇邏輯閘", ["AND", "OR", "XOR", "MUX"])
            if st.button("執行模擬"):
                render_svg(SVG_ICONS.get(gate, SVG_ICONS["AND"]))
                add_exp(user_key, 2) # Reward
                st.success("模擬完成 (+2 EXP)")
        with col2:
             render_svg(SVG_ICONS.get(gate, SVG_ICONS["AND"]))

    # -------------------------------------------
    # 頁面: 布林轉換器 (Lv1+)
    # -------------------------------------------
    elif selection == "🧩 布林轉換器 (Lv1+)":
        if check_access(user_lvl, "初級管理員"):
            st.header("🧩 布林代數實驗室")
            c1, c2 = st.columns(2)
            with c1:
                op = st.selectbox("運算邏輯", ["A AND B", "A OR B", "A XOR B", "NOT A", "NAND"])
            with c2:
                res = []
                for a in [0, 1]:
                    for b in [0, 1]:
                        if op == "A AND B": val = a & b
                        elif op == "A OR B": val = a | b
                        elif op == "A XOR B": val = a ^ b
                        elif op == "NOT A": val = 1 - a
                        elif op == "NAND": val = 1 - (a & b)
                        res.append({"A": a, "B": b, "Out": val})
                st.dataframe(pd.DataFrame(res), use_container_width=True)
                
            if st.button("生成真值表報告"):
                add_exp(user_key, 5)
                st.toast("報告已生成 (+5 EXP)")
        else:
            st.error("🔒 權限不足：需要 [初級管理員] 權限。")

    # -------------------------------------------
    # 頁面: 格雷碼 (Lv2+)
    # -------------------------------------------
    elif selection == "🏦 格雷碼核心 (Lv2+)":
        if check_access(user_lvl, "中級管理員"):
            st.header("🏦 格雷碼運算單元")
            val_str = st.text_input("輸入十進位數值", "127")
            if val_str.isdigit():
                val = int(val_str)
                gray_val = val ^ (val >> 1)
                c1, c2 = st.columns(2)
                with c1: st.metric("Binary", bin(val)[2:])
                with c2: st.metric("Gray Code", bin(gray_val)[2:])
                
                if st.button("確認轉換"):
                    add_exp(user_key, 5)
                    st.success(f"轉換成功 (+5 EXP)")
            else:
                st.error("請輸入整數")
        else:
            st.error("🔒 權限不足：需要 [中級管理員] 權限。")

    # -------------------------------------------
    # 頁面: 進制轉換 (Lv2+)
    # -------------------------------------------
    elif selection == "🔢 進制轉換 (Lv2+)":
        if check_access(user_lvl, "中級管理員"):
            st.header("🔢 多功能進制轉換器")
            c1, c2 = st.columns(2)
            with c1:
                base_from = st.selectbox("來源進制", [2, 8, 10, 16], index=2)
                num_input = st.text_input("輸入數值", "255")
            with c2:
                try:
                    dec_val = int(num_input, base_from)
                    st.write(f"**BIN (2):** `{bin(dec_val)[2:]}`")
                    st.write(f"**OCT (8):** `{oct(dec_val)[2:]}`")
                    st.write(f"**DEC (10):** `{dec_val}`")
                    st.write(f"**HEX (16):** `{hex(dec_val)[2:].upper()}`")
                    if st.button("記錄數據"):
                        add_exp(user_key, 5)
                        st.toast("數據已歸檔 (+5 EXP)")
                except ValueError:
                    st.error("輸入格式與選擇的進制不符")
        else:
            st.error("🔒 權限不足：需要 [中級管理員] 權限。")

    # -------------------------------------------
    # 頁面: 資訊安全局 (Lv2+)
    # -------------------------------------------
    elif selection == "🛡️ 資訊安全局 (Lv2+)":
        if check_access(user_lvl, "中級管理員"):
            st.header("🛡️ 資訊安全局")
            tab_crypt, tab_hash = st.tabs(["🔐 凱薩加密", "#️⃣ 數位雜湊"])
            
            with tab_crypt:
                plain_text = st.text_input("輸入明文", "HELLO CITY")
                shift = st.slider("偏移量", 1, 25, 3)
                mode = st.radio("模式", ["加密", "解密"], horizontal=True)
                res = ""
                if plain_text:
                    for char in plain_text:
                        if char.isalpha():
                            start = 65 if char.isupper() else 97
                            offset = shift if mode == "加密" else -shift
                            res += chr((ord(char) - start + offset) % 26 + start)
                        else: res += char
                st.success(f"結果: {res}")
                if st.button("執行加密運算"): add_exp(user_key, 5); st.toast("+5 EXP")

            with tab_hash:
                h_txt = st.text_input("雜湊輸入", "Password")
                st.code(f"SHA-256: {hashlib.sha256(h_txt.encode()).hexdigest()}")
                if st.button("驗證雜湊"):
                    bonus = 20 if u_class == "Guardian" else 10
                    add_exp(user_key, bonus)
                    st.success(f"驗證完成 (+{bonus} EXP)")

        else: st.error("🔒 權限不足：需要 [中級管理員] 權限。")

    # -------------------------------------------
    # 頁面: 卡諾圖 (Lv3+)
    # -------------------------------------------
    elif selection == "🗺️ 卡諾圖 (Lv3+)":
        if check_access(user_lvl, "高級管理員"):
            st.header("🗺️ 卡諾圖求簡")
            st.info("Karnaugh Map (3 Variables)")
            # 這裡簡化顯示，只保留邏輯
            if st.button("執行化簡運算"):
                add_exp(user_key, 10)
                st.success("運算完成 (+10 EXP)")
        else: st.error("🔒 權限不足：需要 [高級管理員] 權限。")

    # -------------------------------------------
    # 頁面: 市政學院 (All)
    # -------------------------------------------
    elif selection == "🎓 市政學院":
        st.header("🎓 市政考評")
        qs, errs = load_qs_from_txt()
        if errs: st.warning(f"題庫錯誤: {len(errs)} 行")
        
        if not st.session_state.exam_active:
            if st.button("🚀 啟動考核"):
                if len(qs) >= 5:
                    st.session_state.quiz_batch = random.sample(qs, 5)
                    st.session_state.exam_active = True
                    st.rerun()
                else: st.error("題庫不足 5 題")
        else:
            with st.form("exam_form"):
                ans = {}
                for i, q in enumerate(st.session_state.quiz_batch):
                    st.write(f"**{i+1}. {q['q']}**")
                    ans[i] = st.radio("Select", q['o'], key=f"q{i}", index=None, label_visibility="collapsed")
                    st.divider()
                
                if st.form_submit_button("提交考卷"):
                    if any(a is None for a in ans.values()):
                        st.warning("請作答所有題目")
                    else:
                        score = sum([1 for i in range(5) if ans[i]==st.session_state.quiz_batch[i]['a']])
                        
                        # RPG Rewards
                        reward_coins = score * 10
                        reward_exp = score * 15
                        add_coins(user_key, reward_coins)
                        add_exp(user_key, reward_exp)
                        
                        # Save History
                        db = load_db()
                        db["users"][user_key]["history"].append({
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "score": f"{score}/5"
                        })
                        save_db(db)
                        
                        if score==5: st.balloons()
                        st.success(f"得分: {score}/5 | 獲得 {reward_coins} Coins, {reward_exp} EXP")
                        st.session_state.exam_active = False
                        time.sleep(2); st.rerun()

    # -------------------------------------------
    # 頁面: 補給站 (NEW)
    # -------------------------------------------
    elif selection == "🛒 補給站 (New)":
        st.header("🛒 CityOS 補給站")
        st.markdown(f"**持有貨幣:** `{coins} CityCoins`")
        
        cols = st.columns(3)
        for idx, (item_id, item) in enumerate(SHOP_ITEMS.items()):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.subheader("🎨" if item["type"] == "theme" else "🎁")
                    st.write(f"**{item['name']}**")
                    st.write(f"💰 {item['cost']}")
                    if item["key"] in user.get("inventory", []):
                        st.button("已擁有", disabled=True, key=item_id)
                    else:
                        if st.button(f"購買", key=item_id):
                            ok, msg = purchase_item(user_key, item_id)
                            if ok: st.success(msg); time.sleep(1); st.rerun()
                            else: st.error(msg)

    # -------------------------------------------
    # 頁面: 市民檔案 (RPG Update)
    # -------------------------------------------
    elif selection == "📂 市民檔案":
        st.header("📂 檔案與轉職中心")
        
        # 轉職區
        st.subheader("⚔️ 職業管理")
        st.info(f"當前職業: **{class_info['name']}**")
        
        if u_class == "None":
            st.write("可選職業 (需 Lv.5 或 指揮官):")
            c1, c2, c3 = st.columns(3)
            if st.button("轉職 守護者"): 
                ok, msg = change_class(user_key, "Guardian")
                if ok: st.balloons(); st.rerun()
                else: st.error(msg)
            if st.button("轉職 架構師"):
                ok, msg = change_class(user_key, "Architect")
                if ok: st.balloons(); st.rerun()
                else: st.error(msg)
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
                else: st.error("金幣不足")

        st.divider()
        st.subheader("🎨 介面風格 (Inventory)")
        my_themes = user.get("inventory", ["Night City"])
        selected_theme = st.selectbox("選擇主題", my_themes, index=0 if st.session_state.theme_name not in my_themes else my_themes.index(st.session_state.theme_name))
        
        if selected_theme != st.session_state.theme_name:
            st.session_state.theme_name = selected_theme
            st.rerun()

        st.divider()
        if st.button("登出系統"):
            st.session_state.logged_in = False
            st.rerun()

    # -------------------------------------------
    # 頁面: 核心控制 (Commander Only)
    # -------------------------------------------
    elif selection == "☢️ 核心控制" and is_commander:
        st.title("☢️ 核心控制台")
        db = load_db()
        st.subheader("用戶權限管理")
        c1, c2, c3 = st.columns(3)
        with c1: target = st.selectbox("選擇目標", list(db["users"].keys()))
        with c2: new_lvl = st.selectbox("調整等級", list(LEVEL_MAP.keys()))
        with c3:
            st.write("")
            st.write("")
            if st.button("更新"):
                if target == "frank" and new_lvl != "最高指揮官": st.error("不可降級指揮官")
                else:
                    db["users"][target]["level"] = new_lvl
                    save_db(db)
                    st.success("Updated")
        
        st.dataframe(pd.DataFrame(db["users"]).T)

# ==================================================
# 4. 登入頁面
# ==================================================
def login_page():
    apply_theme()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("CityOS V5.0")
        st.caption("Secure Information Systems")
        
        if not os.path.exists("questions.txt"):
            st.error("⚠️ 題庫 questions.txt 遺失，請建立檔案以使用考評功能。")

        tab1, tab2 = st.tabs(["🔒 登入", "📝 註冊"])
        with tab1:
            u = st.text_input("帳號")
            p = st.text_input("密碼", type="password")
            if st.button("登入系統"):
                db = load_db()
                if u in db["users"] and db["users"][u]["password"] == p:
                    st.session_state.logged_in = True
                    st.session_state.user_key = u
                    st.rerun()
                else: st.error("帳號或密碼錯誤")
        with tab2:
            nu = st.text_input("新帳號")
            np_ = st.text_input("新密碼", type="password")
            ne = st.text_input("Email")
            if st.button("建立檔案"):
                db = load_db()
                if nu in db["users"]: st.error("帳號已存在")
                else:
                    db["users"][nu] = {
                        "password": np_, "name": nu, "email": ne,
                        "level": "初級管理員", "avatar_color": "#4285F4", "history": [],
                        "exp": 0, "rpg_level": 1, "coins": 0, "class_type": "None",
                        "inventory": ["Night City", "Day City"], "last_login": ""
                    }
                    save_db(db)
                    st.success("註冊成功，請登入")

if st.session_state.logged_in: main_app()
else: login_page()
