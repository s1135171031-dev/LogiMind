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
from itertools import combinations

# ==================================================
# 0. 核心設定與常數 (RPG + System)
# ==================================================
USER_DB_FILE = "users.json"
EXP_PER_LEVEL = 100

# 職業定義
CLASSES = {
    "None": {"name": "市民 (Citizen)", "desc": "尚無專精", "icon": "👤", "color": "#888888"},
    "Guardian": {"name": "守護者 (Guardian)", "desc": "專精資訊安全與加密技術", "icon": "🛡️", "color": "#00FF99"},
    "Architect": {"name": "架構師 (Architect)", "desc": "專精邏輯運算與硬體架構", "icon": "⚡", "color": "#00CCFF"},
    "Oracle": {"name": "預言家 (Oracle)", "desc": "專精數據分析與預測", "icon": "🔮", "color": "#D500F9"},
    "Engineer": {"name": "工程師 (Engineer)", "desc": "專精電路設計與歐姆定律", "icon": "🔧", "color": "#FF9900"}
}

# 商店物品
SHOP_ITEMS = {
    "theme_cyber_punk": {"name": "主題: 賽博龐克 (Cyber Yellow)", "cost": 100, "type": "theme", "key": "Cyber Punk"},
    "theme_matrix": {"name": "主題: 駭客任務 (Matrix Green)", "cost": 150, "type": "theme", "key": "Matrix"},
    "theme_royal": {"name": "主題: 皇家特務 (Royal Gold)", "cost": 300, "type": "theme", "key": "Royal"},
    "theme_amber": {"name": "主題: 復古終端 (Retro Amber)", "cost": 200, "type": "theme", "key": "Retro Amber"},
    "theme_ocean": {"name": "主題: 深海潛航 (Deep Ocean)", "cost": 250, "type": "theme", "key": "Deep Ocean"}
}

# 介面主題
THEMES = {
    "Night City": {"bg": "#212529", "txt": "#E9ECEF", "btn": "#495057", "btn_txt": "#FFFFFF", "card": "#343A40", "chart": ["#00ADB5", "#EEEEEE", "#FF2E63"]},
    "Day City": {"bg": "#F8F9FA", "txt": "#343A40", "btn": "#6C757D", "btn_txt": "#FFFFFF", "card": "#FFFFFF", "chart": ["#343A40", "#6C757D", "#ADB5BD"]},
    "Cyber Punk": {"bg": "#0b0c10", "txt": "#c5c6c7", "btn": "#fca311", "btn_txt": "#000000", "card": "#1f2833", "chart": ["#fca311", "#45a29e", "#66fcf1"]},
    "Matrix": {"bg": "#0D0208", "txt": "#00FF41", "btn": "#003B00", "btn_txt": "#00FF41", "card": "#001A00", "chart": ["#008F11", "#00FF41", "#003B00"]},
    "Royal": {"bg": "#2C001E", "txt": "#FFD700", "btn": "#590035", "btn_txt": "#FFD700", "card": "#420025", "chart": ["#FFD700", "#FF007F", "#C0C0C0"]},
    "Retro Amber": {"bg": "#1A1A1A", "txt": "#FFB000", "btn": "#332200", "btn_txt": "#FFB000", "card": "#261C00", "chart": ["#FFB000", "#FFD000", "#885500"]},
    "Deep Ocean": {"bg": "#001f3f", "txt": "#7FDBFF", "btn": "#0074D9", "btn_txt": "#FFFFFF", "card": "#003366", "chart": ["#7FDBFF", "#0074D9", "#39CCCC"]}
}

LEVEL_MAP = {"實習生": 0, "初級管理員": 1, "中級管理員": 2, "高級管理員": 3, "最高指揮官": 99}

# ==================================================
# 1. 邏輯核心工具 (K-Map Solver)
# ==================================================
def diff_by_one(s1, s2):
    diff = 0
    res = list(s1)
    for i in range(len(s1)):
        if s1[i] != s2[i]:
            diff += 1
            res[i] = '-'
    return diff == 1, "".join(res)

def solve_kmap_logic(minterms):
    if not minterms: return "0"
    if len(minterms) == 16: return "1"
    
    # 1. 轉成二進制字串
    terms = [format(m, '04b') for m in minterms]
    
    # 2. 簡化過程 (Quine-McCluskey 簡易版)
    prime_implicants = set(terms)
    while True:
        new_implicants = set()
        checked = set()
        sorted_terms = sorted(list(prime_implicants))
        
        merged = False
        for i in range(len(sorted_terms)):
            for j in range(i + 1, len(sorted_terms)):
                t1, t2 = sorted_terms[i], sorted_terms[j]
                is_diff_one, merged_term = diff_by_one(t1, t2)
                if is_diff_one:
                    new_implicants.add(merged_term)
                    checked.add(t1)
                    checked.add(t2)
                    merged = True
        
        # 保留沒被合併的項
        for t in prime_implicants:
            if t not in checked:
                new_implicants.add(t)
        
        if not merged:
            break
        prime_implicants = new_implicants

    # 3. 轉換成布林表達式
    # A=0, B=1, C=2, D=3
    vars = ['A', 'B', 'C', 'D']
    expressions = []
    
    for term in prime_implicants:
        parts = []
        for i, char in enumerate(term):
            if char == '0': parts.append(f"{vars[i]}'")
            elif char == '1': parts.append(f"{vars[i]}")
        if not parts: expressions.append("1")
        else: expressions.append("".join(parts))
    
    final_expr = " + ".join(expressions)
    return final_expr, list(prime_implicants)

# ==================================================
# 2. 資料庫與 RPG 邏輯
# ==================================================
def init_user_db():
    if not os.path.exists(USER_DB_FILE) or os.path.getsize(USER_DB_FILE) == 0:
        default_data = {
            "users": {
                "frank": {
                    "password": "x12345678x", "name": "Frank (Supreme Commander)", "email": "frank@cityos.gov",
                    "level": "最高指揮官", "avatar_color": "#000000", "history": [],
                    "exp": 9900, "rpg_level": 99, "coins": 9999, "class_type": "None",
                    "inventory": list(THEMES.keys()), "last_login": ""
                },
                "user": {
                    "password": "123", "name": "Site Operator", "email": "op@cityos.gov",
                    "level": "初級管理員", "avatar_color": "#4285F4", "history": [],
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
            changed = False
            for u in data["users"].values():
                if "coins" not in u: 
                    u.update({"coins": 0, "exp": 0, "rpg_level": 1, "class_type": "None", "inventory": ["Night City", "Day City"], "last_login": ""})
                    changed = True
            if changed: save_db(data)
            return data
    except: return {"users": {}}

def save_db(data):
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

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
            bonus_coins = 50; bonus_exp = 50
            u["coins"] += bonus_coins; u["exp"] += bonus_exp
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
# 3. 系統視覺與工具
# ==================================================
st.set_page_config(page_title="CityOS V6.0", layout="wide", page_icon="🏙️")

SVG_ICONS = {
    "AND": '''<svg width="100" height="60" viewBox="0 0 100 60"><path d="M10,10 L40,10 C55,10 65,20 65,30 C65,40 55,50 40,50 L10,50 Z" fill="none" stroke="currentColor" stroke-width="3"/><path d="M0,20 L10,20 M0,40 L10,40 M65,30 L80,30" stroke="currentColor" stroke-width="3"/></svg>''',
    "OR": '''<svg width="100" height="60" viewBox="0 0 100 60"><path d="M10,10 L35,10 Q50,30 35,50 L10,50 Q25,30 10,10 Z" fill="none" stroke="currentColor" stroke-width="3"/><path d="M0,20 L15,20 M0,40 L15,40 M45,30 L60,30" stroke="currentColor" stroke-width="3"/></svg>''',
    "XOR": '''<svg width="100" height="60" viewBox="0 0 100 60"><path d="M20,10 L45,10 Q60,30 45,50 L20,50 Q35,30 20,10 Z" fill="none" stroke="currentColor" stroke-width="3"/><path d="M10,10 Q25,30 10,50" fill="none" stroke="currentColor" stroke-width="3"/><path d="M0,20 L15,20 M0,40 L15,40 M55,30 L70,30" stroke="currentColor" stroke-width="3"/></svg>''',
    "NOT": '''<svg width="100" height="60" viewBox="0 0 100 60"><path d="M20,10 L20,50 L60,30 Z" fill="none" stroke="currentColor" stroke-width="3"/><circle cx="65" cy="30" r="4" fill="none" stroke="currentColor" stroke-width="2"/><path d="M0,30 L20,30 M69,30 L80,30" stroke="currentColor" stroke-width="3"/></svg>''',
    "NAND": '''<svg width="100" height="60" viewBox="0 0 100 60"><path d="M10,10 L40,10 C55,10 65,20 65,30 C65,40 55,50 40,50 L10,50 Z" fill="none" stroke="currentColor" stroke-width="3"/><circle cx="70" cy="30" r="4" fill="none" stroke="currentColor" stroke-width="2"/><path d="M0,20 L10,20 M0,40 L10,40 M74,30 L85,30" stroke="currentColor" stroke-width="3"/></svg>''',
    "NOR": '''<svg width="100" height="60" viewBox="0 0 100 60"><path d="M10,10 L35,10 Q50,30 35,50 L10,50 Q25,30 10,10 Z" fill="none" stroke="currentColor" stroke-width="3"/><circle cx="50" cy="30" r="4" fill="none" stroke="currentColor" stroke-width="2"/><path d="M0,20 L15,20 M0,40 L15,40 M54,30 L70,30" stroke="currentColor" stroke-width="3"/></svg>''',
    "XNOR": '''<svg width="100" height="60" viewBox="0 0 100 60"><path d="M20,10 L45,10 Q60,30 45,50 L20,50 Q35,30 20,10 Z" fill="none" stroke="currentColor" stroke-width="3"/><path d="M10,10 Q25,30 10,50" fill="none" stroke="currentColor" stroke-width="3"/><circle cx="50" cy="30" r="4" fill="none" stroke="currentColor" stroke-width="2"/><path d="M0,20 L15,20 M0,40 L15,40 M54,30 L70,30" stroke="currentColor" stroke-width="3"/></svg>''',
    "MUX": '''<svg width="120" height="100" viewBox="0 0 120 100"><path d="M30,10 L90,25 L90,75 L30,90 Z" fill="none" stroke="currentColor" stroke-width="3"/><text x="45" y="55" fill="currentColor" font-size="14">MUX</text><path d="M10,25 L30,25 M10,40 L30,40 M10,55 L30,55 M10,70 L30,70 M90,50 L110,50 M60,85 L60,95" stroke="currentColor" stroke-width="2"/></svg>'''
}

if "user_data" not in st.session_state:
    init_df = pd.DataFrame(np.random.randint(40, 60, size=(30, 3)), columns=['CPU', 'NET', 'SEC'])
    st.session_state.update({
        "logged_in": False, "user_key": "", "user_data": {}, 
        "theme_name": "Night City", "monitor_data": init_df, 
        "exam_active": False, "quiz_batch": [],
        "kmap_values": [0]*16 # K-Map State
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
    .kmap-cell-0 {{ background-color: {t['card']}; color: {t['txt']}; border: 1px solid #555; height: 50px; display:flex; align-items:center; justify-content:center; cursor:pointer; }}
    .kmap-cell-1 {{ background-color: #00ADB5; color: black; border: 1px solid #00ADB5; height: 50px; display:flex; align-items:center; justify-content:center; cursor:pointer; font-weight:bold;}}
    </style>
    """, unsafe_allow_html=True)

def render_svg(svg_code):
    svg_black = svg_code.replace('stroke="currentColor"', 'stroke="#888888"').replace('fill="currentColor"', 'fill="#888888"')
    b64 = base64.b64encode(svg_black.encode('utf-8')).decode("utf-8")
    st.markdown(f'''<div style="background-color: rgba(255,255,255,0.05); border-radius: 8px; padding: 20px; margin-bottom: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"><img src="data:image/svg+xml;base64,{b64}" width="200"/></div>''', unsafe_allow_html=True)

def get_truth_table(gate):
    data = []
    if gate == "NOT": data = [{"A": 0, "Out": 1}, {"A": 1, "Out": 0}]
    elif gate == "MUX":
        data = [{"Sel": 0, "A": 0, "B": "X", "Out": 0}, {"Sel": 0, "A": 1, "B": "X", "Out": 1},
                {"Sel": 1, "A": "X", "B": 0, "Out": 0}, {"Sel": 1, "A": "X", "B": 1, "Out": 1}]
    else:
        for a in [0, 1]:
            for b in [0, 1]:
                out = 0
                if gate == "AND": out = a & b
                elif gate == "OR": out = a | b
                elif gate == "XOR": out = a ^ b
                elif gate == "NAND": out = 1 - (a & b)
                elif gate == "NOR": out = 1 - (a | b)
                elif gate == "XNOR": out = 1 - (a ^ b)
                data.append({"A": a, "B": b, "Out": out})
    return pd.DataFrame(data)

def load_qs_from_txt():
    q = []
    errors = []
    if os.path.exists("questions.txt"):
        try:
            with open("questions.txt", "r", encoding="utf-8") as f:
                for idx, l in enumerate(f):
                    l = l.strip()
                    if not l: continue
                    p = l.split("|")
                    if len(p) == 5: q.append({"id":p[0],"diff":p[1],"q":p[2],"o":p[3].split(","),"a":p[4]})
                    else: errors.append(f"Line {idx+1}: 格式錯誤")
        except Exception as e: errors.append(str(e))
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
# 4. 主應用程式邏輯
# ==================================================
def main_app():
    db = load_db()
    if st.session_state.user_key in db["users"]:
        st.session_state.user_data = db["users"][st.session_state.user_key]
    
    user = st.session_state.user_data
    user_key = st.session_state.user_key
    user_lvl = user.get("level", "實習生")
    rpg_lvl = user.get("rpg_level", 1)
    coins = user.get("coins", 0)
    exp = user.get("exp", 0)
    u_class = user.get("class_type", "None")
    
    apply_theme()
    t_colors = THEMES[st.session_state.theme_name]["chart"]
    
    is_commander = (user_lvl == "最高指揮官")
    class_info = CLASSES.get(u_class, CLASSES["None"])

    with st.sidebar:
        st.title("🏙️ CityOS V6.0")
        st.caption("Logic Master Edition")
        
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
        
        st.progress((exp % EXP_PER_LEVEL) / EXP_PER_LEVEL)
        st.caption(f"EXP: {exp % EXP_PER_LEVEL} / {EXP_PER_LEVEL}")
        
        st.markdown("### 導航選單")
        menu_options = {
            "Dashboard": "🏙️ 城市儀表板",
            "Electricity": "⚡ 電力設施 (Logic)",
            "Circuit": "🔌 基礎電路 (Circuit)",
            "Boolean": "🧩 布林轉換器 (Lv1+)",
            "GrayCode": "🏦 格雷碼核心 (Lv2+)",
            "BaseConv": "🔢 進制轉換 (Lv2+)",
            "InfoSec": "🛡️ 資訊安全局 (Lv2+)", 
            "KMap": "🗺️ 卡諾圖 (Lv3+)", # UPGRADED
            "Academy": "🎓 市政學院",
            "Shop": "🛒 補給站 (New)",
            "Profile": "📂 市民檔案",
        }
        if is_commander: menu_options["Commander"] = "☢️ 核心控制"

        selection = st.radio("前往", list(menu_options.values()), label_visibility="collapsed")

    # -------------------------------------------
    # Page Content
    # -------------------------------------------
    if selection == "🏙️ 城市儀表板":
        col_h1, col_h2 = st.columns([3, 1])
        with col_h1: st.title(f"👋 早安，{class_info['name']}")
        with col_h2: st.caption(datetime.now().strftime("%Y-%m-%d %H:%M"))
        
        if st.button("🎁 領取每日補給"):
            ok, c, e = check_daily_login(user_key)
            if ok: 
                st.balloons(); st.success(f"領取成功！ 獲得 {c} Coins, {e} EXP")
                time.sleep(1); st.rerun()
            else: st.info("今天已經領過囉！明天再來。")

        if u_class == "Architect": st.success("⚡ 架構師專屬：邏輯運算效率提升")
        elif u_class == "Engineer": st.success("🔧 工程師專屬：硬體運算效率提升")

        st.markdown("""
        <div class="intro-box">
            <b>CityOS V6.0</b> 卡諾圖 (K-Map) 全面升級！
            <br>現在支援 <b>4 變數互動式求解</b>，點擊網格即可生成最簡布林函數。
            內建 Quine-McCluskey 演算法核心。
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns([3, 1])
        with c1:
            st.subheader("📡 即時監控")
            chart_ph = st.empty()
            for _ in range(5): 
                df = update_data_random_walk()
                chart_ph.area_chart(df, color=t_colors, height=250)
                time.sleep(0.3)
        with c2:
            st.subheader("📁 狀態")
            qs, errs = load_qs_from_txt()
            st.metric("題庫總數", len(qs))
            st.metric("目前等級", rpg_lvl)

    # -------------------------------------------
    # ⚡ 電力設施
    # -------------------------------------------
    elif selection == "⚡ 電力設施 (Logic)":
        st.header("⚡ 邏輯閘視覺化 (Advanced)")
        col_ctrl, col_viz = st.columns([1, 2])
        with col_ctrl:
            gate = st.selectbox("選擇邏輯閘", ["AND", "OR", "XOR", "NAND", "NOR", "XNOR", "NOT", "MUX"])
            st.divider()
            st.markdown("##### 📖 真值表")
            st.dataframe(get_truth_table(gate), use_container_width=True, hide_index=True)
            if st.button("執行模擬"): add_exp(user_key, 3); st.toast("模擬完成 (+3 EXP)")
        with col_viz:
            st.subheader("電路圖示")
            render_svg(SVG_ICONS.get(gate, SVG_ICONS["AND"]))

    # -------------------------------------------
    # 🔌 基礎電路
    # -------------------------------------------
    elif selection == "🔌 基礎電路 (Circuit)":
        st.header("🔌 基礎電路實驗室")
        tab_ohm, tab_res = st.tabs(["Ω 歐姆定律", "🔗 串並聯"])
        with tab_ohm:
            c1, c2 = st.columns(2)
            with c1: v = st.number_input("電壓 (V)", 5.0, step=0.5); r = st.number_input("電阻 (Ω)", 100.0, step=10.0)
            with c2: 
                if r>0: st.metric("電流 (A)", f"{v/r:.4f} A", f"{(v/r)*1000:.2f} mA")
                if st.button("記錄數據"): add_exp(user_key, 5); st.success("記錄完成 (+5 EXP)")
        with tab_res:
            mode = st.radio("模式", ["串聯", "並聯"])
            r1 = st.slider("R1", 1, 1000, 100); r2 = st.slider("R2", 1, 1000, 100)
            rt = r1+r2 if mode=="串聯" else (r1*r2)/(r1+r2)
            st.metric("總電阻", f"{rt:.2f} Ω")

    # -------------------------------------------
    # 🧩 布林轉換器
    # -------------------------------------------
    elif selection == "🧩 布林轉換器 (Lv1+)":
        if check_access(user_lvl, "初級管理員"):
            st.header("🧩 布林代數")
            op = st.selectbox("運算", ["A AND B", "A OR B", "A XOR B", "NOT A", "NAND"])
            res = []
            for a in [0,1]:
                for b in [0,1]:
                    v = 0
                    if op=="A AND B": v=a&b
                    elif op=="A OR B": v=a|b
                    elif op=="A XOR B": v=a^b
                    elif op=="NOT A": v=1-a
                    elif op=="NAND": v=1-(a&b)
                    res.append({"A":a,"B":b,"Out":v})
            st.dataframe(pd.DataFrame(res), use_container_width=True)
        else: st.error("權限不足")

    # -------------------------------------------
    # 🏦 格雷碼
    # -------------------------------------------
    elif selection == "🏦 格雷碼核心 (Lv2+)":
        if check_access(user_lvl, "中級管理員"):
            st.header("🏦 格雷碼")
            v_str = st.text_input("輸入整數", "127")
            if v_str.isdigit():
                v = int(v_str)
                st.code(f"Binary: {bin(v)[2:]}\nGray:   {bin(v^(v>>1))[2:]}")
                if st.button("轉換"): add_exp(user_key, 5); st.success("完成 (+5 EXP)")
        else: st.error("權限不足")

    # -------------------------------------------
    # 🔢 進制轉換
    # -------------------------------------------
    elif selection == "🔢 進制轉換 (Lv2+)":
        if check_access(user_lvl, "中級管理員"):
            st.header("🔢 進制轉換")
            base = st.selectbox("Base", [2,8,10,16], index=2)
            val = st.text_input("Value", "255")
            try:
                d = int(val, base)
                st.write(f"BIN: `{bin(d)[2:]}` | OCT: `{oct(d)[2:]}` | HEX: `{hex(d)[2:].upper()}`")
            except: st.error("格式錯誤")
        else: st.error("權限不足")

    # -------------------------------------------
    # 🛡️ 資安
    # -------------------------------------------
    elif selection == "🛡️ 資訊安全局 (Lv2+)":
        if check_access(user_lvl, "中級管理員"):
            st.header("🛡️ 資安局")
            txt = st.text_input("Text", "HELLO")
            st.write(f"SHA256: `{hashlib.sha256(txt.encode()).hexdigest()}`")
        else: st.error("權限不足")

    # -------------------------------------------
    # 🗺️ 卡諾圖 (MAJOR UPGRADE)
    # -------------------------------------------
    elif selection == "🗺️ 卡諾圖 (Lv3+)":
        if check_access(user_lvl, "高級管理員"):
            st.header("🗺️ 4-Variable K-Map Solver")
            st.caption("Quine-McCluskey Algorithm Engine")
            
            # Gray Code Order for 4x4
            # AB \ CD | 00(0) | 01(1) | 11(3) | 10(2)
            # 00 (0)  | 0     | 1     | 3     | 2
            # 01 (1)  | 4     | 5     | 7     | 6
            # 11 (3)  | 12    | 13    | 15    | 14
            # 10 (2)  | 8     | 9     | 11    | 10
            
            grid_indices = [
                [0, 1, 3, 2],
                [4, 5, 7, 6],
                [12, 13, 15, 14],
                [8, 9, 11, 10]
            ]
            row_labels = ["00", "01", "11", "10"]
            col_labels = ["00", "01", "11", "10"]

            c_control, c_grid = st.columns([1, 2])
            
            with c_control:
                st.info("💡 點擊右側網格設定真值 (0/1)")
                if st.button("🔄 重置網格"):
                    st.session_state.kmap_values = [0]*16
                    st.rerun()
                
                # Calculate
                minterms = [i for i, v in enumerate(st.session_state.kmap_values) if v == 1]
                expr, implicants = solve_kmap_logic(minterms)
                
                st.divider()
                st.markdown("### 🧮 結果")
                st.latex(f"F = {expr}")
                
                if st.button("記錄運算結果"):
                    bonus = 15 if u_class == "Architect" else 10
                    add_exp(user_key, bonus)
                    st.success(f"已存檔 (+{bonus} EXP)")

            with c_grid:
                # Header Row
                cols = st.columns([1, 1, 1, 1, 1])
                cols[0].write("**AB \ CD**")
                for i, l in enumerate(col_labels):
                    cols[i+1].write(f"**{l}**")
                
                # Grid Rows
                for r_idx, row_idxs in enumerate(grid_indices):
                    cols = st.columns([1, 1, 1, 1, 1])
                    cols[0].write(f"**{row_labels[r_idx]}**") # Row Label
                    
                    for c_idx, cell_idx in enumerate(row_idxs):
                        val = st.session_state.kmap_values[cell_idx]
                        btn_text = "1" if val else "0"
                        btn_type = "primary" if val else "secondary"
                        
                        # Use button as toggle
                        if cols[c_idx+1].button(btn_text, key=f"kmap_{cell_idx}", use_container_width=True):
                            st.session_state.kmap_values[cell_idx] = 1 - val
                            st.rerun()

            st.write(f"**Minterms (m):** {minterms}")
            st.write(f"**Prime Implicants:** {implicants}")

        else: st.error("🔒 權限不足：需要 [高級管理員] 權限。")

    # -------------------------------------------
    # 🎓 考評 & 🛒 商店 & 📂 檔案
    # -------------------------------------------
    elif selection == "🎓 市政學院":
        st.header("🎓 市政考評")
        qs, _ = load_qs_from_txt()
        if not st.session_state.exam_active:
            if st.button("🚀 啟動考核"):
                if len(qs)>=5: 
                    st.session_state.quiz_batch = random.sample(qs, 5)
                    st.session_state.exam_active = True
                    st.rerun()
        else:
            with st.form("exam"):
                ans = {}
                for i,q in enumerate(st.session_state.quiz_batch):
                    st.write(f"{i+1}. {q['q']}")
                    ans[i] = st.radio("A", q['o'], key=f"q{i}", label_visibility="collapsed")
                    st.divider()
                if st.form_submit_button("交卷"):
                    score = sum([1 for i in range(5) if ans[i]==st.session_state.quiz_batch[i]['a']])
                    add_coins(user_key, score*10); add_exp(user_key, score*15)
                    st.success(f"得分 {score}/5"); st.session_state.exam_active = False
                    time.sleep(2); st.rerun()

    elif selection == "🛒 補給站 (New)":
        st.header("🛒 補給站"); st.write(f"💰 {coins}")
        cols = st.columns(3)
        for i, (k, v) in enumerate(SHOP_ITEMS.items()):
            with cols[i%3]:
                st.write(f"**{v['name']}**\n💰 {v['cost']}")
                if v['key'] in user.get("inventory",[]): st.button("已擁有", disabled=True, key=k)
                else: 
                    if st.button("購買", key=k): 
                        ok, msg = purchase_item(user_key, k)
                        if ok: st.rerun()

    elif selection == "📂 市民檔案":
        st.header(f"📂 {class_info['name']}")
        if u_class=="None":
            c1, c2, c3, c4 = st.columns(4)
            if c1.button("守護者"): change_class(user_key, "Guardian"); st.rerun()
            if c2.button("架構師"): change_class(user_key, "Architect"); st.rerun()
            if c3.button("預言家"): change_class(user_key, "Oracle"); st.rerun()
            if c4.button("工程師"): change_class(user_key, "Engineer"); st.rerun()
        else:
            if st.button("重置職業 (500$)"): 
                if coins>=500: add_coins(user_key, -500); change_class(user_key, "None"); st.rerun()
        
        st.divider()
        sel = st.selectbox("主題", user.get("inventory",[]))
        if sel != st.session_state.theme_name: 
            st.session_state.theme_name = sel; st.rerun()
        if st.button("登出"): st.session_state.logged_in = False; st.rerun()

    elif selection == "☢️ 核心控制" and is_commander:
        st.title("Admin"); db=load_db(); st.dataframe(pd.DataFrame(db["users"]).T)

# ==================================================
# Login
# ==================================================
def login_page():
    apply_theme()
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        st.title("CityOS V6.0"); st.caption("Logic Master")
        if not os.path.exists("questions.txt"): st.error("⚠️ 建立 questions.txt 以使用考題")
        t1, t2 = st.tabs(["登入", "註冊"])
        with t1:
            u = st.text_input("User"); p = st.text_input("Pass", type="password")
            if st.button("Login"):
                db = load_db()
                if u in db["users"] and db["users"][u]["password"] == p:
                    st.session_state.logged_in = True; st.session_state.user_key = u; st.rerun()
        with t2:
            nu = st.text_input("New User"); np_ = st.text_input("New Pass", type="password")
            if st.button("Sign Up"):
                db = load_db()
                if nu not in db["users"]:
                    db["users"][nu] = {"password": np_, "name": nu, "email": "", "level": "初級管理員", "exp":0, "coins":0, "class_type":"None", "inventory":["Night City"], "last_login":""}
                    save_db(db); st.success("OK")

if st.session_state.logged_in: main_app()
else: login_page()
