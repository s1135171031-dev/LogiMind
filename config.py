# ==========================================
# 檔案: config.py
# 用途: 靜態資料設定
# ==========================================

# 股票資料 (設定基本波動率)
STOCKS_DATA = {
    "CYBR": {"name": "Cyberdyne", "base": 120, "volatility": 0.05},
    "ROBO": {"name": "US Robots", "base": 85,  "volatility": 0.04},
    "AI":   {"name": "Skynet AI", "base": 300, "volatility": 0.08},
    "NUKA": {"name": "Nuka Cola", "base": 15,  "volatility": 0.02},
    "WEY":  {"name": "Weyland",   "base": 210, "volatility": 0.03}
}

# 商店道具
ITEMS = {
    "Brute Force Script": {"price": 200, "desc": "Allows 1 hack attempt (PVP)."},
    "Firewall V1":        {"price": 500, "desc": "Reduces hack success rate against you."},
    "RAM Upgrade":        {"price": 1000, "desc": "Speed up operations (Cosmetic)."},
    "Encrypted Key":      {"price": 3000, "desc": "Mystery item."}
}

# 隨機事件 (影響股市)
CITY_EVENTS = [
    {"name": "Stable", "desc": "Market is normal.", "effect": "none"},
    {"name": "Zero Day", "desc": "Massive cyber attack reported!", "effect": "crash"},
    {"name": "AI Breakthrough", "desc": "New sentient AI discovered.", "effect": "tech_boom"},
    {"name": "Whale Movement", "desc": "Anonymous trillionaire entering market.", "effect": "whale"},
]

# 邏輯閘 SVG 圖示
SVG_LIB = {
    "AND": """<svg height="100" width="100"><path d="M10,10 L50,10 A40,40 0 0,1 50,90 L10,90 Z" fill="none" stroke="#00ff41" stroke-width="3"/><line x1="0" y1="30" x2="10" y2="30" stroke="#00ff41" /><line x1="0" y1="70" x2="10" y2="70" stroke="#00ff41" /><line x1="90" y1="50" x2="100" y2="50" stroke="#00ff41" /></svg>""",
    "OR":  """<svg height="100" width="100"><path d="M10,10 Q60,10 90,50 Q60,90 10,90 Q30,50 10,10 Z" fill="none" stroke="#00ff41" stroke-width="3"/><line x1="0" y1="30" x2="10" y2="30" stroke="#00ff41" /><line x1="0" y1="70" x2="10" y2="70" stroke="#00ff41" /><line x1="90" y1="50" x2="100" y2="50" stroke="#00ff41" /></svg>""",
    "NOT": """<svg height="100" width="100"><path d="M10,10 L90,50 L10,90 Z" fill="none" stroke="#00ff41" stroke-width="3"/><circle cx="95" cy="50" r="5" stroke="#00ff41" fill="none"/><line x1="0" y1="50" x2="10" y2="50" stroke="#00ff41" /></svg>"""
}
