# ==========================================
# 檔案: config.py
# 用途: 遊戲靜態資料 (已移除題目，改由外部讀取)
# ==========================================

# 1. 道具清單
ITEMS = {
    "Brute Force Script": {"price": 150, "desc": "PVP 攻擊必備工具 (消耗品)"},
    "Firewall Patch":     {"price": 200, "desc": "降低被駭客攻擊的機率 (被動)"},
    "Quantum CPU":        {"price": 1000, "desc": "算力增強，每秒被動收入 +$5"},
    "Coffee":             {"price": 50,   "desc": "工程師的燃料 (純裝飾)"},
    "VPN Subscription":   {"price": 300,  "desc": "隱藏 IP，PVP 失敗時減少懲罰"},
    "GPU Cluster":        {"price": 5000, "desc": "礦場大亨，每秒被動收入 +$20"},
    "Golden Key":         {"price": 9999, "desc": "傳說中的管理員權限 (解鎖成就)"},
    "Energy Drink":       {"price": 20,   "desc": "便宜的提神飲料"},
    "coffee":             {"price": 50,   "desc": "俗稱工程師心臟，但你不會更強，好好練習吧"}
}

# 2. 股市設定 (高波動 High Volatility 版)
STOCKS_DATA = {
    "CYBR": {"name": "Cyberdyne", "base": 150, "volatility": 0.25}, 
    "NETW": {"name": "NetworkSol", "base": 120, "volatility": 0.15},
    "BIO":  {"name": "BioGen",    "base": 130, "volatility": 0.18},
    "EENG": {"name": "E-Energy",  "base": 100, "volatility": 0.12},
    "ROBO": {"name": "RoboCorp",  "base": 180, "volatility": 0.22},
    "AI":   {"name": "SkyNet AI", "base": 200, "volatility": 0.30}
}

# 3. 隨機事件
CITY_EVENTS = [
    {"name": "Market Crash",    "desc": "全球伺服器過熱，股市崩盤 (-30%)。", "effect": "crash"},
    {"name": "Tech Boom",       "desc": "AI 技術突破，科技股狂飆 (+30%)。", "effect": "tech_boom"},
    {"name": "Quiet Day",       "desc": "平靜的一天，市場微幅震盪。", "effect": "none"},
    {"name": "Gov Subsidy",     "desc": "政府發放數位補助金。", "effect": "rich"},
    {"name": "Blackout",        "desc": "大規模停電，無法挖礦。", "effect": "mining_nerf"},
    {"name": "Ransomware",      "desc": "勒索病毒肆虐，銀行暫停服務。", "effect": "bank_lock"},
    {"name": "Solar Flare",     "desc": "太陽閃焰干擾，通訊中斷。", "effect": "comm_down"},
    {"name": "IPO Launch",      "desc": "新創公司上市，市場熱絡。", "effect": "market_up"},
    {"name": "Zero Day",        "desc": "發現零日漏洞，PVP 成功率提升。", "effect": "hack_boost"},
    {"name": "Whale Movement",  "desc": "巨鯨進場，特定股票劇烈波動。", "effect": "whale"}
]

# 4. 邏輯實驗室圖示 (SVG)
SVG_LIB = {
    "AND": '<svg height="40" width="80"><path d="M10,5 L30,5 A15,15 0 0 1 30,35 L10,35 Z" fill="none" stroke="#0f0" stroke-width="2"/><line x1="0" y1="12" x2="10" y2="12" stroke="#0f0"/><line x1="0" y1="28" x2="10" y2="28" stroke="#0f0"/><line x1="45" y1="20" x2="80" y2="20" stroke="#0f0"/><text x="20" y="25" fill="#0f0" font-family="Courier" font-size="10">AND</text></svg>',
    "OR": '<svg height="40" width="80"><path d="M10,5 Q25,5 35,20 Q25,35 10,35 Q20,20 10,5" fill="none" stroke="#0f0" stroke-width="2"/><line x1="0" y1="12" x2="15" y2="12" stroke="#0f0"/><line x1="0" y1="28" x2="15" y2="28" stroke="#0f0"/><line x1="35" y1="20" x2="80" y2="20" stroke="#0f0"/><text x="20" y="25" fill="#0f0" font-family="Courier" font-size="10">OR</text></svg>',
    "NOT": '<svg height="40" width="80"><path d="M10,5 L35,20 L10,35 Z" fill="none" stroke="#0f0" stroke-width="2"/><circle cx="38" cy="20" r="3" stroke="#0f0" fill="none"/><line x1="0" y1="20" x2="10" y2="20" stroke="#0f0"/><line x1="41" y1="20" x2="80" y2="20" stroke="#0f0"/><text x="15" y="25" fill="#0f0" font-family="Courier" font-size="10">NOT</text></svg>'
}
