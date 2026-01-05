# ==========================================
# 檔案: config.py (V28.1 Fix Visuals)
# ==========================================

# --- 城市隨機事件 ---
CITY_EVENTS = [
    {"name": "平靜的一天", "desc": "風和日麗，網路連線穩定。", "effect": None},
    {"name": "黑客松大賽", "desc": "科技股大漲，但網路擁堵。", "effect": "tech_boom"},
    {"name": "DDOS 攻擊", "desc": "全城網路變慢，防禦系統升級。", "effect": "network_slow"},
    {"name": "黑色星期五", "desc": "黑市全面七折！", "effect": "shop_discount"},
    {"name": "挖礦熱潮", "desc": "顯示卡價格飆升，CybrCoin 波動劇烈。", "effect": "mining_boost"},
    {"name": "金融監管", "desc": "所有駭客行動收益降低。", "effect": "hack_nerf"},
]

# --- 物品清單 ---
ITEMS = {
    "Firewall": {"price": 500, "desc": "PVP 防禦道具，減少被搶金額 (消耗品)"},
    "Brute Force Script": {"price": 300, "desc": "PVP 攻擊道具，入侵必備 (消耗品)"},
    "Mining GPU": {"price": 1200, "desc": "放在背包裡似乎能增加一點駭客運氣..."},
    "Chaos Heart": {"price": 2500, "desc": "讓入侵你的駭客面臨 8 個選項而非 4 個 (消耗品)"},
    "Clarity Necklace": {"price": 2000, "desc": "攻擊時移除一半錯誤選項 (消耗品)"},
    "Coffee": {"price": 50, "desc": "工程師的燃料，目前僅供收藏。"}
}

# --- 股票數據 ---
STOCKS_DATA = {
    "CYBR": {"name": "CyberCorp", "base": 100, "volatility": 0.15},
    "NETW": {"name": "NetWorld", "base": 50, "volatility": 0.05},
    "DARK": {"name": "DarkWeb Inc", "base": 200, "volatility": 0.25},
    "CHIP": {"name": "MicroChip", "base": 80, "volatility": 0.1},
}

# --- 摩斯密碼表 ---
MORSE_CODE_DICT = { 'A':'.-', 'B':'-...', 'C':'-.-.', 'D':'-..', 'E':'.', 
    'F':'..-.', 'G':'--.', 'H':'....', 'I':'..', 'J':'.---', 'K':'-.-', 
    'L':'.-..', 'M':'--', 'N':'-.', 'O':'---', 'P':'.--.', 'Q':'--.-', 
    'R':'.-.', 'S':'...', 'T':'-', 'U':'..-', 'V':'...-', 'W':'.--', 
    'X':'-..-', 'Y':'-.--', 'Z':'--..', '1':'.----', '2':'..---', 
    '3':'...--', '4':'....-', '5':'.....', '6':'-....', '7':'--...', 
    '8':'---..', '9':'----.', '0':'-----', ', ':'--..--', '.':'.-.-.-', 
    '?':'..--..', '/':'-..-.', '-':'-....-', '(':'-.--.', ')':'-.--.-'}

# --- SVG 邏輯閘圖示 (高對比修復版) ---
# 使用 stroke="white" 確保在深色模式下可見，加粗線條 stroke-width="3"
SVG_LIB = {
    "AND": '''<svg viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg">
        <path d="M10,10 L40,10 A25,25 0 0,1 40,60 L10,60 Z" fill="none" stroke="#00FF00" stroke-width="3"/>
        <text x="25" y="40" fill="white" font-family="monospace" font-size="14">AND</text>
    </svg>''',
    
    "OR": '''<svg viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg">
        <path d="M10,10 Q60,10 80,35 Q60,60 10,60 Q30,35 10,10 Z" fill="none" stroke="#00FF00" stroke-width="3"/>
        <text x="25" y="40" fill="white" font-family="monospace" font-size="14">OR</text>
    </svg>''',
    
    "NOT": '''<svg viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg">
        <path d="M10,10 L60,35 L10,60 Z" fill="none" stroke="#00FF00" stroke-width="3"/>
        <circle cx="65" cy="35" r="5" stroke="#00FF00" fill="none" stroke-width="3"/>
        <text x="15" y="40" fill="white" font-family="monospace" font-size="14">NOT</text>
    </svg>''',
    
    "NAND": '''<svg viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg">
        <path d="M10,10 L40,10 A25,25 0 0,1 40,60 L10,60 Z" fill="none" stroke="#FF5555" stroke-width="3"/>
        <circle cx="70" cy="35" r="5" stroke="#FF5555" fill="none" stroke-width="3"/>
        <text x="20" y="40" fill="white" font-family="monospace" font-size="14">NAND</text>
    </svg>''',
    
    "NOR": '''<svg viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg">
        <path d="M10,10 Q60,10 80,35 Q60,60 10,60 Q30,35 10,10 Z" fill="none" stroke="#FF5555" stroke-width="3"/>
        <circle cx="85" cy="35" r="5" stroke="#FF5555" fill="none" stroke-width="3"/>
        <text x="25" y="40" fill="white" font-family="monospace" font-size="14">NOR</text>
    </svg>''',
    
    "XOR": '''<svg viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg">
        <path d="M5,10 Q25,35 5,60" fill="none" stroke="#5555FF" stroke-width="3"/>
        <path d="M15,10 Q65,10 85,35 Q65,60 15,60 Q35,35 15,10 Z" fill="none" stroke="#5555FF" stroke-width="3"/>
        <text x="35" y="40" fill="white" font-family="monospace" font-size="14">XOR</text>
    </svg>''',
    
    "XNOR": '''<svg viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg">
        <path d="M5,10 Q25,35 5,60" fill="none" stroke="#5555FF" stroke-width="3"/>
        <path d="M15,10 Q65,10 85,35 Q65,60 15,60 Q35,35 15,10 Z" fill="none" stroke="#5555FF" stroke-width="3"/>
        <circle cx="90" cy="35" r="5" stroke="#5555FF" fill="none" stroke-width="3"/>
        <text x="35" y="40" fill="white" font-family="monospace" font-size="14">XNOR</text>
    </svg>''',
    
    "BUFFER": '''<svg viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg">
        <path d="M10,10 L60,35 L10,60 Z" fill="none" stroke="#FFFF55" stroke-width="3"/>
        <text x="20" y="40" fill="white" font-family="monospace" font-size="14">BUF</text>
    </svg>''',
}
