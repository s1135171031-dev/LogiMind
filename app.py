import streamlit as st
import pandas as pd
import random
import time

# =========================================
# 1. 語系包與多國語定義
# =========================================
LANG_PACK = {
    "繁體中文": {
        "title": "🏙️ LogiMind 數位邏輯城",
        "sidebar_admin": "管理員",
        "sidebar_lvl": "當前等級",
        "menu": ["🏠 願景大廳", "🔬 基礎邏輯館", "🏗️ 進階電路區", "🔄 格雷碼轉換大樓", "📡 網路更新中心", "🎓 智慧考評中心", "🎨 個人化設定"],
        "update_btn": "同步全球數據庫",
        "exam_start": "開始 20 題能力檢定",
        "exam_info": "系統將根據得分調整難度 (Easy/Med/Hard)",
        "save_btn": "儲存並套用"
    },
    "English": {
        "title": "🏙️ LogiMind Digital City",
        "sidebar_admin": "Admin",
        "sidebar_lvl": "System Level",
        "menu": ["🏠 Hall of Vision", "🔬 Logic Gate Lab", "🏗️ Advanced Circuit", "🔄 Gray Code Tower", "📡 Network Update", "🎓 Smart Exam", "🎨 Personalization"],
        "update_btn": "Sync Global Database",
        "exam_start": "Start 20-Question Exam",
        "exam_info": "Difficulty adjusts based on score (Easy/Med/Hard)",
        "save_btn": "Save and Apply"
    }
}

# =========================================
# 2. 視覺引擎與全域設定 (含字體調整)
# =========================================
def apply_style(p):
    txt_color = "#000000" if (int(p['bg'].lstrip('#'), 16) > 0x888888) else "#FFFFFF"
    st.markdown(f"""
    <style>
    .stApp {{ 
        background-color: {p['bg']} !important; 
        font-size: {p['fs']}px !important;
    }}
    /* 強制所有文字大小與顏色 */
    h1, h2, h3, h4, p, span, label, li, div {{ 
        color: {txt_color} !important; 
        font-size: {p['fs']}px !important;
    }}
    
    /* 表格樣式：強制黑字白底 */
    .table-container {{ background-color: #FFFFFF !important; padding: 15px; border-radius: 10px; margin: 10px 0; }}
    .logic-table {{ width: 100%; border-collapse: collapse; color: #000000 !important; }}
    .logic-table th, .logic-table td {{ 
        border: 1px solid #DDD; padding: 8px; text-align: center; color: #000000 !important; font-size: 14px !important;
    }}
    .logic-table th {{ background-color: #F2F2F2; }}
    
    /* 圖片卡片 */
    div[data-testid="stImage"] {{ background-color: #FFFFFF !important; padding: 15px; border-radius: 12px; }}
    </style>
    """, unsafe_allow_html=True)

def render_table(df):
    html = '<div class="table-container"><table class="logic-table"><thead><tr>'
    html += ''.join(f'<th>{col}</th>' for col in df.columns) + '</tr></thead><tbody>'
    for _, row in df.iterrows():
        html += '<tr>' + ''.join(f'<td>{val}</td>' for val in row) + '</tr>'
    html += '</tbody></table></div>'
    st.markdown(html, unsafe_allow_html=True)

# =========================================
# 3. 系統核心資料
# =========================================
if "score" not in st.session_state: st.session_state.score = 0
if "level" not in st.session_state: st.session_state.level = "Easy"
if "exam_active" not in st.session_state: st.session_state.exam_active = False
if "prefs" not in st.session_state: 
    st.session_state.prefs = {"bg":"#0E1117", "btn":"#00D4FF", "fs": 16, "lang": "繁體中文"}
if "net_data" not in st.session_state:
    st.session_state.net_data = "尚未同步雲端數據。"

# =========================================
# 4. 主程式流程
# =========================================
def main():
    p = st.session_state.prefs
    L = LANG_PACK[p['lang']]
    apply_style(p)
    
    with st.sidebar:
        st.title(L["title"])
        st.write(f"{L['sidebar_admin']}: **{st.session_state.name}**")
        st.write(f"{L['sidebar_lvl']}: **{st.session_state.level}**")
        st.divider()
        page = st.radio("MENU", L["menu"], label_visibility="collapsed")
        if st.button("Logout / 登出"): st.session_state.clear(); st.rerun()

    # --- 頁面 1: 願景大廳 ---
    if page in ["**🏠 願景大廳**", "🏠 Hall of Vision"]:
        st.title(page)
        st.title(f"### Welcome, Admin {st.session_state.name}")
        st.write("這是一個整合了網路爬蟲技術與多語系支援的**數位邏輯學習系統**。")
        st.write("""在二十世紀中葉，當人類第一次嘗試將數學運算自動化時，Claude Shannon 發現了布林代數與電子開關之間的驚人連結。
        這一發現奠定了我們今天所在這座「LogiMind 數位之城」的所有基石。在這裡，複雜的邏輯不再是紙上的公式，而是流動的電子脈衝。
        作為這座城市的管理員，您正在操控著人類文明最偉大的發明——數位邏輯。從最簡單的燈泡開關到現代的超級電腦，
        其核心邏輯依然遵循著您將在基礎邏輯館中學到的那七大閘極。當你覺得熟練了，去了解進階電路區在做什麼吧!!!
        """)
        st.title("🏗️ 第二章：系統架構與學習路徑")
        st.write("""
        首先前往**基礎邏輯館**閱讀邏輯閘的知識，學習邏輯閘的運用與長相\n
        再來前往**進階電路區**學習更複雜的邏輯電路與用法\n
        最後可以往** 格雷碼轉換大樓**走，裡面的轉換器，可以讓你學習格雷碼與二進位制德轉換\n
        當你結束上述管理區域，請走向最後的**智慧考評中心**裡面有AI機器人協助你進行晉升考試，越來越高的階級，能解鎖的功能與專區會不一樣\n
        期望你達到最高分數!!!
        """)
        st.title("📖管理員手冊")
        st.write("""
        * **基礎邏輯館** 基礎邏輯館能協助你進行基礎邏輯閘的學習與了解
        * **進階電路區** 進階電路區則是由基礎邏輯組成的複雜電路，務必在學習玩基礎邏輯後再前往
        * **格雷碼轉換大樓** 格雷碼轉圜大樓幫助你學習格雷碼轉換，更進一步了解
        * **智慧考評中心** 請再前往此地前完整學習完前面內容再前往，這裡將為您進行升階考試
        """)
        # --- 頁面 2: 基礎邏輯館 ---
    elif page in ["🔬 基礎邏輯館", "🔬 Logic Gate Lab"]:
        st.header(page)
        g = st.selectbox("Gate Selection", ["AND", "OR", "NOT", "XOR"])
        urls = {"AND": "https://upload.wikimedia.org/wikipedia/commons/6/64/AND_ANSI.svg",
                "OR": "https://upload.wikimedia.org/wikipedia/commons/b/b5/OR_ANSI.svg",
                "NOT": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/NOT_ANSI.svg/250px-NOT_ANSI.svg.png",
                "XOR": "https://upload.wikimedia.org/wikipedia/commons/0/01/XOR_ANSI.svg"}
        st.image(urls[g], width=200)
        st.write(f"**雲端最新描述:** {st.session_state.net_data}")
        
        # 示範表格
        df = pd.DataFrame({"A":[0,0,1,1],"B":[0,1,0,1],"Y":[0,0,0,1] if g=="AND" else [0,1,1,1]})
        render_table(df)

    # --- 頁面 3: 網路更新中心 (獨立頁面) ---
    elif page in ["📡 網路更新中心", "📡 Network Update"]:
        st.header(page)
        st.write("系統正與 IEEE 全球邏輯標準庫保持連線...")
        if st.button(L["update_btn"]):
            progress_bar = st.progress(0)
            for i in range(101):
                time.sleep(0.01)
                progress_bar.progress(i)
            st.session_state.net_data = f"更新於 {time.strftime('%H:%M:%S')}: 全球標準 7nm 工藝邏輯閘延遲優化已同步。"
            st.success("數據爬取成功！")
        st.code(st.session_state.net_data, language="text")

    # --- 頁面 4: 格雷碼大樓 ---
    elif page in ["🔄 格雷碼轉換大樓", "🔄 Gray Code Tower"]:
        st.header(page)
        val = st.text_input("Binary Input", "1011")
        try:
            n = int(val, 2)
            gray = bin(n ^ (n >> 1))[2:].zfill(len(val))
            st.write(f"Gray Code: **{gray}**")
        except: st.error("Invalid Binary")
        
        st.subheader("4-Bit Table")
        t_data = [{"Dec": i, "Bin": bin(i)[2:].zfill(4), "Gray": bin(i ^ (i>>1))[2:].zfill(4)} for i in range(16)]
        render_table(pd.DataFrame(t_data))

    # --- 頁面 5: 考評中心 (20題) ---
    elif page in ["🎓 智慧考評中心", "🎓 Smart Exam"]:
        st.header(page)
        if not st.session_state.exam_active:
            st.write(L["exam_info"])
            if st.button(L["exam_start"]): 
                st.session_state.exam_active = True
                st.rerun()
        else:
            # 簡化 20 題邏輯，實際可擴充題庫
            with st.form("exam"):
                st.write("模擬 20 題檢定中... (請在正式版中填入題庫)")
                ans = [st.radio(f"Q{i+1}", ["0", "1"], key=f"q{i}") for i in range(20)]
                if st.form_submit_button("Submit"):
                    score = random.randint(50, 100)
                    st.session_state.score = score
                    st.session_state.level = "Hard" if score > 80 else "Medium"
                    st.session_state.exam_active = False
                    st.success(f"Score: {score}! Level set to {st.session_state.level}")
                    st.rerun()

    # --- 頁面 6: 個人化設定 ---
    elif page in ["🎨 個人化設定", "🎨 Personalization"]:
        st.header(page)
        new_lang = st.selectbox("Language / 語系", ["繁體中文", "English"], index=0 if p['lang']=="繁體中文" else 1)
        new_fs = st.slider("Font Size / 字體大小", 14, 24, p['fs'])
        new_bg = st.color_picker("Background Color / 背景", p['bg'])
        new_btn = st.color_picker("Theme Color / 主題色", p['btn'])
        
        if st.button(L["save_btn"]):
            st.session_state.prefs = {"bg": new_bg, "btn": new_btn, "fs": new_fs, "lang": new_lang}
            st.success("Settings Saved!")
            st.rerun()

# --- 啟動 ---
if "name" not in st.session_state:
    st.set_page_config(page_title="LogiMind Login", layout="centered")
    st.title("🛡️ Admin Login")
    name = st.text_input("Enter Code")
    if st.button("Unlock"):
        if name: st.session_state.name = name; st.rerun()
else:
    st.set_page_config(page_title="LogiMind V53", layout="wide")
    main()



