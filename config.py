# ==========================================
# 檔案: config.py (V29.0 Hardcore Economy)
# ==========================================

# --- 城市隨機事件 ---
CITY_EVENTS = [
    {"name": "平靜的一天", "desc": "除了你的存款在縮水，一切都很平靜。", "effect": None},
    {"name": "韭菜收割日", "desc": "股市大戶進場，散戶請抓緊扶手。", "effect": "tech_boom"},
    {"name": "伺服器過熱", "desc": "全城降速，就像你阿嬤家的撥接網路。", "effect": "network_slow"},
    {"name": "跳樓大拍賣", "desc": "黑市打七折！雖然你還是買不起。", "effect": "shop_discount"},
    {"name": "礦工的眼淚", "desc": "顯卡價格崩盤...等等，是暴漲才對。", "effect": "mining_boost"},
    {"name": "查水表", "desc": "金管會介入，駭客收益大幅降低。", "effect": "hack_nerf"},
]

# --- 物品清單 (價格不變，但因獎勵變少，相對變超貴) ---
ITEMS = {
    "Firewall": {"price": 500, "desc": "防止被搶的最後一道防線，比你的薪水還貴。"},
    "Brute Force Script": {"price": 300, "desc": "攻擊別人的腳本。投資有賺有賠，入侵失敗請自行負責。"},
    "Mining GPU": {"price": 1200, "desc": "放在背包就能挖礦？你信這種鬼話？(增加被動收入)"},
    "Chaos Heart": {"price": 2500, "desc": "讓入侵者看到 8 個密碼選項。看他們崩潰就是爽。"},
    "Clarity Necklace": {"price": 2000, "desc": "作弊神器，刪除一半錯誤答案。有錢就是任性。"},
    "Engineer Heart": {"price": 50, "desc": "俗稱「咖啡」。沒有它，你的程式碼就是一坨義大利麵。"}
}

# --- 股票數據 (波動率大幅提升) ---
STOCKS_DATA = {
    "CYBR": {"name": "賽博科技", "base": 100, "volatility": 0.30}, # 原 0.15 -> 0.3 (大起大落)
    "NETW": {"name": "全球網通", "base": 50, "volatility": 0.15},  # 原 0.05 -> 0.15
    "DARK": {"name": "暗網控股", "base": 200, "volatility": 0.40}, # 妖股等級
    "CHIP": {"name": "台積電路", "base": 80, "volatility": 0.20},
}

# --- 摩斯密碼表 (維持不變) ---
MORSE_CODE_DICT = { 'A':'.-', 'B':'-...', 'C':'-.-.', 'D':'-..', 'E':'.', 
    'F':'..-.', 'G':'--.', 'H':'....', 'I':'..', 'J':'.---', 'K':'-.-', 
    'L':'.-..', 'M':'--', 'N':'-.', 'O':'---', 'P':'.--.', 'Q':'--.-', 
    'R':'.-.', 'S':'...', 'T':'-', 'U':'..-', 'V':'...-', 'W':'.--', 
    'X':'-..-', 'Y':'-.--', 'Z':'--..', '1':'.----', '2':'..---', 
    '3':'...--', '4':'....-', '5':'.....', '6':'-....', '7':'--...', 
    '8':'---..', '9':'----.', '0':'-----', ', ':'--..--', '.':'.-.-.-', 
    '?':'..--..', '/':'-..-.', '-':'-....-', '(':'-.--.', ')':'-.--.-'}

# --- SVG 邏輯閘圖示 (維持修復版) ---
SVG_LIB = {
    "AND": '''<svg viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg"><path d="M10,10 L40,10 A25,25 0 0,1 40,60 L10,60 Z" fill="none" stroke="#00FF00" stroke-width="3"/><text x="25" y="40" fill="white" font-family="monospace" font-size="14">AND</text></svg>''',
    "OR": '''<svg viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg"><path d="M10,10 Q60,10 80,35 Q60,60 10,60 Q30,35 10,10 Z" fill="none" stroke="#00FF00" stroke-width="3"/><text x="25" y="40" fill="white" font-family="monospace" font-size="14">OR</text></svg>''',
    "NOT": '''<svg viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg"><path d="M10,10 L60,35 L10,60 Z" fill="none" stroke="#00FF00" stroke-width="3"/><circle cx="65" cy="35" r="5" stroke="#00FF00" fill="none" stroke-width="3"/><text x="15" y="40" fill="white" font-family="monospace" font-size="14">NOT</text></svg>''',
    "NAND": '''<svg viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg"><path d="M10,10 L40,10 A25,25 0 0,1 40,60 L10,60 Z" fill="none" stroke="#FF5555" stroke-width="3"/><circle cx="70" cy="35" r="5" stroke="#FF5555" fill="none" stroke-width="3"/><text x="20" y="40" fill="white" font-family="monospace" font-size="14">NAND</text></svg>''',
    "NOR": '''<svg viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg"><path d="M10,10 Q60,10 80,35 Q60,60 10,60 Q30,35 10,10 Z" fill="none" stroke="#FF5555" stroke-width="3"/><circle cx="85" cy="35" r="5" stroke="#FF5555" fill="none" stroke-width="3"/><text x="25" y="40" fill="white" font-family="monospace" font-size="14">NOR</text></svg>''',
    "XOR": '''<svg viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg"><path d="M5,10 Q25,35 5,60" fill="none" stroke="#5555FF" stroke-width="3"/><path d="M15,10 Q65,10 85,35 Q65,60 15,60 Q35,35 15,10 Z" fill="none" stroke="#5555FF" stroke-width="3"/><text x="35" y="40" fill="white" font-family="monospace" font-size="14">XOR</text></svg>''',
    "XNOR": '''<svg viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg"><path d="M5,10 Q25,35 5,60" fill="none" stroke="#5555FF" stroke-width="3"/><path d="M15,10 Q65,10 85,35 Q65,60 15,60 Q35,35 15,10 Z" fill="none" stroke="#5555FF" stroke-width="3"/><circle cx="90" cy="35" r="5" stroke="#5555FF" fill="none" stroke-width="3"/><text x="35" y="40" fill="white" font-family="monospace" font-size="14">XNOR</text></svg>''',
    "BUFFER": '''<svg viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg"><path d="M10,10 L60,35 L10,60 Z" fill="none" stroke="#FFFF55" stroke-width="3"/><text x="20" y="40" fill="white" font-family="monospace" font-size="14">BUF</text></svg>''',
}
