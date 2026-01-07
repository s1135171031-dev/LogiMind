# config.py
# 城市設定檔：包含物品、股票、事件、以及邏輯實驗室圖形

ITEMS = {
    "Nutri-Paste": {"price": 20, "desc": "像是嘔吐物的營養膏。"},
    "Stim-Pack": {"price": 150, "desc": "非法興奮劑，手會抖。"},
    "Data Chip": {"price": 300, "desc": "從垃圾堆撿來的晶片。"},
    "VR Headset": {"price": 800, "desc": "逃避現實的最佳工具。"},
    "Cyber-Arm": {"price": 2500, "desc": "比肉體強，但會漏油。"},
    "GPU (Mining)": {"price": 5000, "desc": "現在比人命還值錢。"},
    "Trojan Virus": {"price": 1500, "desc": "PVP 專用：駭入別人的帳戶。"},
    "Firewall": {"price": 2000, "desc": "防止被別人駭入。"}
}

# 綠線風格：高波動率設定
STOCKS_DATA = {
    "CYBR": {"name": "CyberCorp", "base": 1200, "volatility": 0.5},
    "NEO":  {"name": "Neo-Tokyo", "base": 5000, "volatility": 0.4},
    "SLUM": {"name": "Slum Ind.", "base": 50, "volatility": 1.2},
    "AI":   {"name": "Skynet", "base": 3000, "volatility": 0.6},
    "BOND": {"name": "City Bond", "base": 100, "volatility": 0.3},
    "DOGE": {"name": "MemeCoin", "base": 10, "volatility": 1.5}
}

CITY_EVENTS = [
    {"name": "Acid Rain", "effect": "depression", "desc": "酸雨警報。全城心情低落。"},
    {"name": "Cyber Attack", "effect": "crash", "desc": "交易所遭駭，股價大亂。"},
    {"name": "Corporate War", "effect": "volatility", "desc": "企業開戰，血流成河。"},
    {"name": "AI Glitch", "effect": "pump", "desc": "演算法故障，隨機暴漲。"},
    {"name": "Normal Day", "effect": "none", "desc": "平淡無奇的絕望一天。"}
]

# 邏輯實驗室的 SVG 圖示
SVG_LIB = {
    "AND": '<svg width="100" height="50"><path d="M10,10 L40,10 A25,25 0 0,1 40,60 L10,60 Z" fill="none" stroke="#00ff41" stroke-width="2"/><line x1="0" y1="20" x2="10" y2="20" stroke="#00ff41"/><line x1="0" y1="50" x2="10" y2="50" stroke="#00ff41"/><line x1="65" y1="35" x2="100" y2="35" stroke="#00ff41"/></svg>',
    "OR": '<svg width="100" height="50"><path d="M10,10 Q40,10 55,35 Q40,60 10,60 Q25,35 10,10" fill="none" stroke="#00ff41" stroke-width="2"/><line x1="0" y1="20" x2="15" y2="20" stroke="#00ff41"/><line x1="0" y1="50" x2="15" y2="50" stroke="#00ff41"/><line x1="55" y1="35" x2="100" y2="35" stroke="#00ff41"/></svg>',
    "NOT": '<svg width="100" height="50"><path d="M10,10 L40,35 L10,60 Z" fill="none" stroke="#00ff41" stroke-width="2"/><circle cx="45" cy="35" r="5" stroke="#00ff41" fill="none"/><line x1="0" y1="35" x2="10" y2="35" stroke="#00ff41"/><line x1="50" y1="35" x2="100" y2="35" stroke="#00ff41"/></svg>',
    "XOR": '<svg width="100" height="50"><path d="M20,10 Q50,10 65,35 Q50,60 20,60 Q35,35 20,10" fill="none" stroke="#00ff41" stroke-width="2"/><path d="M10,10 Q25,35 10,60" fill="none" stroke="#00ff41" stroke-width="2"/><line x1="0" y1="20" x2="15" y2="20" stroke="#00ff41"/><line x1="0" y1="50" x2="15" y2="50" stroke="#00ff41"/><line x1="65" y1="35" x2="100" y2="35" stroke="#00ff41"/></svg>'
}
