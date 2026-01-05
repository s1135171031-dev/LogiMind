# ==========================================
# 檔案: config.py
# ==========================================
import random

# --- 城市每日事件 ---
CITY_EVENTS = [
    {"name": "牛市來臨", "desc": "加密貨幣與股市齊漲，經濟活動熱絡。", "effect": "mining_boost"},
    {"name": "太陽風暴", "desc": "強烈電磁干擾，駭客入侵成功率下降 (PVP減益)，科技股下跌。", "effect": "hack_nerf"},
    {"name": "黑色星期五", "desc": "黑市商人心情好，全場道具打 7 折。", "effect": "shop_discount"},
    {"name": "系統維護", "desc": "中央處理器降頻，無特殊加成。", "effect": None},
    {"name": "零日漏洞", "desc": "發現新的系統漏洞，PVP 攻擊獎勵提升。", "effect": "attack_boost"},
]

# --- 道具清單 ---
ITEMS = {
    "Mining GPU": {"price": 2000, "desc": "被動收入：每日登入挖掘 $100 (可疊加)。"},
    "Firewall": {"price": 500, "desc": "防禦(消耗)：抵銷 PVP 失敗時的傷害。"},
    "Chaos Heart": {"price": 1500, "desc": "防禦(消耗)：讓攻擊者選項加倍 (4變8)。"},
    "Clarity Necklace": {"price": 1200, "desc": "攻擊(消耗)：讓你的選項減半 (4變2)。"},
    "Brute Force Script": {"price": 300, "desc": "攻擊(消耗)：發動駭客攻擊的必備軟體。"}
}

# --- 股市設定 (V23 New) ---
STOCKS_DATA = {
    "CYBR": {"name": "賽博科技", "base": 150, "volatility": 0.05, "desc": "高科技晶片龍頭，價格穩定。"},
    "ARMS": {"name": "荒坂軍工", "base": 300, "volatility": 0.15, "desc": "私人武裝部隊，波動極大。"},
    "BIO":  {"name": "生化科技", "base": 80,  "volatility": 0.08, "desc": "研發長生藥，投機性強。"},
    "ENGY": {"name": "核能矩陣", "base": 50,  "volatility": 0.02, "desc": "基礎電力，便宜且穩定。"}
}

# --- 邏輯閘 SVG ---
SVG_LIB = {
    "AND": '<svg width="100" height="60"><path d="M10,10 L50,10 A30,20 0 0,1 50,50 L10,50 Z" fill="none" stroke="white" stroke-width="2"/><line x1="0" y1="20" x2="10" y2="20" stroke="white"/><line x1="0" y1="40" x2="10" y2="40" stroke="white"/><line x1="80" y1="30" x2="100" y2="30" stroke="white"/></svg>',
    "OR": '<svg width="100" height="60"><path d="M10,10 Q30,30 10,50 L40,50 Q80,30 40,10 Z" fill="none" stroke="white" stroke-width="2"/><line x1="0" y1="20" x2="20" y2="20" stroke="white"/><line x1="0" y1="40" x2="20" y2="40" stroke="white"/><line x1="75" y1="30" x2="100" y2="30" stroke="white"/></svg>',
    "NOT": '<svg width="100" height="60"><path d="M20,10 L60,30 L20,50 Z" fill="none" stroke="white" stroke-width="2"/><circle cx="65" cy="30" r="5" stroke="white" fill="none"/><line x1="0" y1="30" x2="20" y2="30" stroke="white"/><line x1="70" y1="30" x2="100" y2="30" stroke="white"/></svg>'
}

# --- 摩斯密碼表 ---
MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---', 
    '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...', 
    '8': '---..', '9': '----.'
}
