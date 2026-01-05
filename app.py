# ==========================================
# 檔案名稱: app.py
# 用途: Streamlit 介面入口
# 執行指令: streamlit run app.py
# ==========================================
import streamlit as st
import random
import time
import pandas as pd
from config import CITY_EVENTS, MISSIONS, ITEMS, SVG_LIB, MORSE_CODE_DICT
from database import load_db, save_db, init_db, check_mission, get_today_event, get_admin_data, log_intruder, load_quiz_from_file

st.set_page_config(page_title="CityOS Ultimate", layout="wide", page_icon="🏙️", initial_sidebar_state="expanded")

# --- 各功能頁面函數 ---

def page_crypto(uid, user):
    st.title("🔐 密碼學中心")
    tab1, tab2, tab3 = st.tabs(["進位轉換", "凱薩密碼", "摩斯電碼"])

    with tab1:
        st.subheader("Base Converter")
        val = st.text_input("輸入十進位數字", "255")
        if val.isdigit():
            n = int(val)
            c1, c2, c3 = st.columns(3)
            c1.metric("Binary (2)", f"{n:b}")
            c2.metric("Octal (8)", f"{n:o}")
            c3.metric("Hex (16)", f"{n:X}")
        else:
            st.error("請輸入有效數字")

    with tab2:
        st.subheader("Caesar Cipher")
        text = st.text_input("輸入文字 (English only)", "HELLO CITY").upper()
        shift = st.slider("位移量 (Shift)", 1, 25, 3)
        res = ""
        for char in text:
            if char.isalpha():
                code = ord(char) + shift
                if code > ord('Z'): code -= 26
                res += chr(code)
            else:
                res += char
        st.success(f"加密結果: {res}")

    with tab3:
        st.subheader("Morse Code")
        m_text = st.text_input("輸入文字轉摩斯", "SOS").upper()
        if st.button("轉換 & 發送"):
            morse_res = " ".join([MORSE_CODE_DICT.get(c, c) for c in m_text])
            st.code(morse_res)
            # 視覺化訊號
            visual_signal = ""
            for m in morse_res:
                if m == ".": visual_signal += "🟢 "
                elif m == "-": visual_signal += "🔴 "
                else: visual_signal += "  "
            st.write(f"訊號模擬: {visual_signal}")

def page_quiz(uid, user):
    st.title("📝 每日工程測驗 (1000題庫版)")
    st.caption("題目來自外部資料庫。答對獲得金錢與經驗值。每日限一次。")
    
    if "quiz_today_done" not in st.session_state: st.session_state.quiz_today_done = False

    if st.session_state.quiz_today_done:
        st.info("您今天已經完成測驗了，明天再來吧！")
        return

    # 初始化：從檔案抽取題目
    if "current_question" not in st.session_state:
        all_questions = load_quiz_from_file()
        if not all_questions:
            st.error("❌ 找不到題庫檔案 (questions.txt)，請確認檔案位置。")
            return
        st.session_state.current_question = random.choice(all_questions)

    q_data = st.session_state.current_question

    st.write(f"### Q: {q_data['q']}")
    st.caption(f"ID: {q_data['id']} | 難度: {q_data['level']}")
    
    choice = st.radio("請選擇答案:", q_data['options'], key="quiz_choice")
    
    if st.button("提交答案"):
        if choice == q_data['ans']:
            st.balloons()
            st.success(f"回答正確！ 答案是 {q_data['ans']}")
            st.write("獲得獎勵： $300 + 50 EXP")
            user["money"] += 300
            user["exp"] += 50
            check_mission(uid, user, "quiz_done")
            if uid != "frank": 
                save_db({"users": load_db()["users"] | {uid: user}, "bbs": []})
            st.session_state.quiz_today_done = True
            del st.session_state.current_question 
            st.rerun()
        else:
            st.error("回答錯誤... 系統鎖定中。")
            st.session_state.quiz_today_done = True
            del st.session_state.current_question
            st.rerun()

def page_leaderboard(uid, user):
    st.title("🏆 名人堂 (Hall of Fame)")
    db = load_db()
    users = db["users"]
    
    data = []
    for u_id, u_data in users.items():
        total_assets = u_data.get("money", 0) + u_data.get("bank_deposit", 0)
        data.append({
            "User": u_data["name"],
            "Job": u_data["job"],
            "Level": u_data.get("level", 1),
            "Total Assets": total_assets
        })
    
    if data:
        df = pd.DataFrame(data).sort_values(by="Total Assets", ascending=False).reset_index(drop=True)
        df.index += 1
        st.dataframe(df, use_container_width=True)
    else:
        st.write("目前無數據")

def page_digital_lab(uid, user):
    st.title("🔬 數位邏輯實驗室")
    tab1, tab2, tab3 = st.tabs(["邏輯閘", "卡諾圖 (K-Map)", "格雷碼"])
    
    with tab1: # 邏輯閘
        gate = st.selectbox("選擇元件", list(SVG_LIB.keys()))
        c1, c2 = st.columns(2)
        a = c1.toggle("Input A (1)", False); b = c2.toggle("Input B (1)", False)
        
        # 簡易邏輯計算 (包含 NAND/NOR)
        res = 0
        if gate=="AND": res = 1 if (a and b) else 0
        elif gate=="OR": res = 1 if (a or b) else 0
        elif gate=="XOR": res = 1 if (a != b) else 0
        elif gate=="NOT": res = 0 if a else 1
        elif gate=="NAND": res = 0 if (a and b) else 1
        elif gate=="NOR": res = 0 if (a or b) else 1
        
        st.markdown(SVG_LIB[gate], unsafe_allow_html=True); st.metric("Output", res)
        if gate and (a or b): check_mission(uid, user, "logic_use")

    with tab2: # K-Map
        st.subheader("2-Var K-Map")
        if "kmap" not in st.session_state: st.session_state.kmap = [0,0,0,0]
        c1, c2 = st.columns(2)
        with c1: 
            st.write("A=0"); 
            if st.button(f"00: {st.session_state.kmap[0]}", key="k0"): st.session_state.kmap[0]^=1; st.rerun()
            if st.button(f"01: {st.session_state.kmap[1]}", key="k1"): st.session_state.kmap[1]^=1; st.rerun()
        with c2: 
            st.write("A=1"); 
            if st.button(f"10: {st.session_state.kmap[2]}", key="k2"): st.session_state.kmap[2]^=1; st.rerun()
            if st.button(f"11: {st.session_state.kmap[3]}", key="k3"): st.session_state.kmap[3]^=1; st.rerun()
        ones = [i for i, x in enumerate(st.session_state.kmap) if x == 1]
        st.code(f"Minterms (位置): {ones}", language="text")

    with tab3: # 格雷碼
        num = st.slider("Decimal (0-15)", 0, 15, 3)
        st.metric("Gray Code", f"{(num^(num>>1)):04b}", delta="相鄰只變一位")

def page_bank(uid, user):
    st.title("🏦 賽博銀行")
    c1, c2 = st.columns(2)
    c1.metric("存款", f"${user.get('bank_deposit',0):,}"); c2.metric("現金", f"${user['money']:,}")
    amt = st.number_input("金額", 0, 1000000, 100)
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("📥 存入") and user['money'] >= amt:
            user['money'] -= amt; user['bank_deposit'] += amt
            check_mission(uid, user, "bank_save")
            if uid!="frank": save_db({"users":load_db()["users"]|{uid:user}, "bbs": []})
            st.rerun()
    with col_btn2:
        if st.button("📤 提款") and user['bank_deposit'] >= amt:
            user['bank_deposit'] -= amt; user['money'] += amt
            if uid!="frank": save_db({"users":load_db()["users"]|{uid:user}, "bbs": []})
            st.rerun()

def page_shop(uid, user):
    st.title("🛒 地下黑市")
    evt = st.session_state.today_event
    discount = 0.7 if evt["effect"] == "shop_discount" else 1.0
    if discount < 1: st.success("🔥 黑色星期五特價中！")
    
    cols = st.columns(3)
    idx = 0
    for item, info in ITEMS.items():
        price = int(info['price'] * discount)
        with cols[idx%3].container(border=True):
            st.write(f"**{item}** (${price})"); st.caption(info['desc'])
            if st.button(f"購買", key=f"buy_{item}"):
                if user['money'] >= price:
                    user['money'] -= price; user.setdefault("inventory", {})[item] = user.get("inventory", {}).get(item, 0) + 1
                    check_mission(uid, user, "shop_buy")
                    if uid!="frank": save_db({"users":load_db()["users"]|{uid:user}, "bbs": []})
                    st.toast(f"已購買 {item}")
                    time.sleep(0.5); st.rerun()
                else:
                    st.error("現金不足")
        idx+=1

def page_cli_os(uid, user):
    st.markdown("""<style>.stTextInput > div > div > input {background-color: #000; color: #00ff00; font-family: 'Courier New';}</style>""", unsafe_allow_html=True)
    st.title("💻 Terminal Mode")
    if "cli_hist" not in st.session_state: st.session_state.cli_hist = ["System Ready..."]
    for l in st.session_state.cli_hist[-10:]: st.text(l)
    cmd = st.chat_input("Command >>")
    if cmd:
        st.session_state.cli_hist.append(f"user@cityos:~$ {cmd}")
        t = cmd.split()
        if t[0]=="help": res = "whoami, bal, clear"
        elif t[0]=="clear": st.session_state.cli_hist=[]; st.rerun()
        elif t[0]=="bal": res = f"Cash: {user['money']}"
        elif t[0]=="whoami": res = f"User: {user['name']}"
        else: res = "Unknown command"
        st.session_state.cli_hist.append(res); st.rerun()

def page_missions(uid, user):
    st.title("🎯 任務中心")
    done = user.get("completed_missions", [])
    st.progress(len(done)/len(MISSIONS), text=f"進度 {len(done)}/{len(MISSIONS)}")
    for mid, m in MISSIONS.items():
        icon = "✅" if mid in done else "🚧"
        with st.expander(f"{icon} {m['title']} (${m['reward']})"):
            st.write(m['desc']); st.caption(f"目標代碼: {m['target']}")

# --- 主程式進入點 ---
def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    if "today_event" not in st.session_state: st.session_state.today_event = get_today_event()

    # 登入畫面
    if not st.session_state.logged_in:
        st.markdown("<h1 style='text-align: center;'>🏙️ CityOS Final</h1>", unsafe_allow_html=True)
        st.info(f"📅 今日事件: {st.session_state.today_event['name']}")
        
        tab_l, tab_r = st.tabs(["登入", "註冊"])
        with tab_l:
            u = st.text_input("帳號"); p = st.text_input("密碼", type="password")
            if st.button("Login"):
                db = load_db()
                if u in db["users"] and db["users"][u]["password"]==p:
                    st.session_state.logged_in=True; st.session_state.user_id=u; st.session_state.user_data=db["users"][u]; st.rerun()
                else: 
                    st.error("登入失敗"); log_intruder(u)
        with tab_r:
            nu = st.text_input("新帳號"); np = st.text_input("新密碼", type="password")
            if st.button("註冊"):
                db = load_db()
                if nu not in db["users"]:
                    # 預設註冊為 Novice
                    db["users"][nu] = {"password": np, "name": nu, "job": "Novice", "money": 1000, "level": 1, "exp": 0, "bank_deposit": 0, "inventory": {}, "completed_missions": []}
                    save_db(db); st.success("註冊成功，請登入")
        return

    # 登入後邏輯
    uid = st.session_state.user_id
    if uid == "frank": user = st.session_state.user_data 
    else: user = load_db()["users"].get(uid, st.session_state.user_data)

    st.sidebar.title(f"🆔 {user['name']}")
    st.sidebar.write(f"Lv.{user.get('level',1)} | {user['job']}")
    
    nav = st.sidebar.radio("導航", ["大廳", "任務", "銀行", "黑市", "實驗室", "密碼學", "每日測驗", "名人堂", "CLI"])
    
    if st.sidebar.button("登出"): st.session_state.logged_in=False; st.rerun()

    if nav == "大廳": 
        st.title("📊 城市控制台")
        st.write(f"今日運勢：**{st.session_state.today_event['name']}**")
        st.write(st.session_state.today_event['desc'])
        st.info("💡 提示：前往「每日測驗」賺取獎勵！")
    elif nav == "任務": page_missions(uid, user)
    elif nav == "銀行": page_bank(uid, user)
    elif nav == "黑市": page_shop(uid, user)
    elif nav == "實驗室": page_digital_lab(uid, user)
    elif nav == "密碼學": page_crypto(uid, user)
    elif nav == "每日測驗": page_quiz(uid, user)
    elif nav == "名人堂": page_leaderboard(uid, user)
    elif nav == "CLI": page_cli_os(uid, user)

if __name__ == "__main__":
    main()
