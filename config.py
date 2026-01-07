# config.py
# 城市設定檔

ITEMS = {
    "Nutri-Paste": {"price": 10, "desc": "像是嘔吐物的營養膏。"},
    "Stim-Pack": {"price": 50, "desc": "非法興奮劑，手會抖。"},
    "Data Chip": {"price": 100, "desc": "從垃圾堆撿來的晶片。"},
    "VR Headset": {"price": 300, "desc": "逃避現實的最佳工具。"},
    "Cyber-Arm": {"price": 1200, "desc": "比肉體強，但會漏油。"},
    "GPU (Mining)": {"price": 2500, "desc": "現在比人命還值錢。"},
    "Trojan Virus": {"price": 800, "desc": "PVP 專用：駭入別人的帳戶。"},
    "Firewall": {"price": 1000, "desc": "防止被別人駭入。"}
}

# 🔥 修改：價格改小 (10~150)，波動率全部調到最高
STOCKS_DATA = {
    "CYBR": {"name": "CyberCorp", "base": 80, "volatility": 2.0},
    "NEO":  {"name": "Neo-Tokyo", "base": 120, "volatility": 2.0},
    "SLUM": {"name": "Slum Ind.", "base": 15, "volatility": 3.0}, # 垃圾股
    "AI":   {"name": "Skynet", "base": 60, "volatility": 2.0},
    "BOND": {"name": "City Bond", "base": 30, "volatility": 1.5},
    "DOGE": {"name": "MemeCoin", "base": 5, "volatility": 5.0}   # 價格極低但跳動極大
}

CITY_EVENTS = [
    {"name": "Acid Rain", "effect": "depression", "desc": "酸雨警報。全城心情低落。"},
    {"name": "Cyber Attack", "effect": "crash", "desc": "交易所遭駭，股價大亂。"},
    {"name": "Corporate War", "effect": "volatility", "desc": "企業開戰，血流成河。"},
    {"name": "AI Glitch", "effect": "pump", "desc": "演算法故障，隨機暴漲。"},
    {"name": "Normal Day", "effect": "none", "desc": "平淡無奇的絕望一天。"}
]

SVG_LIB = {
    "AND": '<svg width="100" height="50"><path d="M10,10 L40,10 A25,25 0 0,1 40,60 L10,60 Z" fill="none" stroke="#00ff41" stroke-width="2"/><line x1="0" y1="20" x2="10" y2="20" stroke="#00ff41"/><line x1="0" y1="50" x2="10" y2="50" stroke="#00ff41"/><line x1="65" y1="35" x2="100" y2="35" stroke="#00ff41"/></svg>',
    "OR": '<svg width="100" height="50"><path d="M10,10 Q40,10 55,35 Q40,60 10,60 Q25,35 10,10" fill="none" stroke="#00ff41" stroke-width="2"/><line x1="0" y1="20" x2="15" y2="20" stroke="#00ff41"/><line x1="0" y1="50" x2="15" y2="50" stroke="#00ff41"/><line x1="55" y1="35" x2="100" y2="35" stroke="#00ff41"/></svg>',
    "NOT": '<svg width="100" height="50"><path d="M10,10 L40,35 L10,60 Z" fill="none" stroke="#00ff41" stroke-width="2"/><circle cx="45" cy="35" r="5" stroke="#00ff41" fill="none"/><line x1="0" y1="35" x2="10" y2="35" stroke="#00ff41"/><line x1="50" y1="35" x2="100" y2="35" stroke="#00ff41"/></svg>',
    "XOR": '<svg width="100" height="50"><path d="M20,10 Q50,10 65,35 Q50,60 20,60 Q35,35 20,10" fill="none" stroke="#00ff41" stroke-width="2"/><path d="M10,10 Q25,35 10,60" fill="none" stroke="#00ff41" stroke-width="2"/><line x1="0" y1="20" x2="15" y2="20" stroke="#00ff41"/><line x1="0" y1="50" x2="15" y2="50" stroke="#00ff41"/><line x1="65" y1="35" x2="100" y2="35" stroke="#00ff41"/></svg>'
}
