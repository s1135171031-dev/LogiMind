# config.py

# --- 物品清單 ---
ITEMS = {
    "Nutri-Paste": {"price": 10, "desc": "像是嘔吐物的營養膏。"},
    "Stim-Pack": {"price": 50, "desc": "非法興奮劑，手會抖。"},
    "Data Chip": {"price": 100, "desc": "從垃圾堆撿來的晶片。"},
    "VR Headset": {"price": 300, "desc": "逃避現實的最佳工具。"},
    "Cyber-Arm": {"price": 1200, "desc": "比肉體強，但會漏油。"},
    "GPU (Mining)": {"price": 2500, "desc": "現在比人命還值錢。"},
    "Trojan Virus": {"price": 800, "desc": "PVP 專用：駭入別人的帳戶。"},
    "Firewall": {"price": 1000, "desc": "防止被別人駭入。"},
    # ☣️ 毒氣系統道具
    "Anti-Rad Pill": {"price": 200, "desc": "醫療用：消除 30 點中毒指數。", "type": "cure", "value": 30},
    "Gas Mask": {"price": 1500, "desc": "裝備：持有時，大幅降低中毒機率。"}
}

STOCKS_DATA = {
    "CYBR": {"name": "CyberCorp", "base": 80, "volatility": 2.0},
    "NEO":  {"name": "Neo-Tokyo", "base": 120, "volatility": 2.0},
    "SLUM": {"name": "Slum Ind.", "base": 15, "volatility": 3.0},
    "AI":   {"name": "Skynet", "base": 60, "volatility": 2.0},
    "BOND": {"name": "City Bond", "base": 30, "volatility": 1.5},
    "DOGE": {"name": "MemeCoin", "base": 5, "volatility": 5.0}
}

# 🆙 等級稱號系統
LEVEL_TITLES = {
    1: "Street Rat (街頭混混)",
    2: "Script Kiddie (腳本小子)",
    3: "Code Monkey (碼農)",
    4: "Glitch Hunter (故障獵人)",
    5: "Netrunner (網路行者)",
    6: "System Architect (架構師)",
    7: "Cyber Lord (賽博領主)",
    8: "City Legend (城市傳說)",
    9: "The Ghost (幽靈)",
    10: "AI Singularity (奇異點)"
}

# --- 邏輯閘 SVG 圖示庫 ---
SVG_LIB = {
    "AND": '<svg width="100" height="50"><path d="M10,10 L40,10 A25,25 0 0,1 40,60 L10,60 Z" fill="none" stroke="#00ff41" stroke-width="2"/><line x1="0" y1="20" x2="10" y2="20" stroke="#00ff41"/><line x1="0" y1="50" x2="10" y2="50" stroke="#00ff41"/><line x1="65" y1="35" x2="100" y2="35" stroke="#00ff41"/></svg>',
    "OR": '<svg width="100" height="50"><path d="M10,10 Q40,10 55,35 Q40,60 10,60 Q25,35 10,10" fill="none" stroke="#00ff41" stroke-width="2"/><line x1="0" y1="20" x2="15" y2="20" stroke="#00ff41"/><line x1="0" y1="50" x2="15" y2="50" stroke="#00ff41"/><line x1="55" y1="35" x2="100" y2="35" stroke="#00ff41"/></svg>',
    "NOT": '<svg width="100" height="50"><path d="M10,10 L40,35 L10,60 Z" fill="none" stroke="#00ff41" stroke-width="2"/><circle cx="45" cy="35" r="5" stroke="#00ff41" fill="none"/><line x1="0" y1="35" x2="10" y2="35" stroke="#00ff41"/><line x1="50" y1="35" x2="100" y2="35" stroke="#00ff41"/></svg>',
    "XOR": '<svg width="100" height="50"><path d="M20,10 Q50,10 65,35 Q50,60 20,60 Q35,35 20,10" fill="none" stroke="#00ff41" stroke-width="2"/><path d="M10,10 Q25,35 10,60" fill="none" stroke="#00ff41" stroke-width="2"/><line x1="0" y1="20" x2="15" y2="20" stroke="#00ff41"/><line x1="0" y1="50" x2="15" y2="50" stroke="#00ff41"/><line x1="65" y1="35" x2="100" y2="35" stroke="#00ff41"/></svg>',
    "NAND": '<svg width="100" height="50"><path d="M10,10 L40,10 A25,25 0 0,1 40,60 L10,60 Z" fill="none" stroke="#00ff41" stroke-width="2"/><circle cx="70" cy="35" r="5" stroke="#00ff41" fill="none"/><line x1="0" y1="20" x2="10" y2="20" stroke="#00ff41"/><line x1="0" y1="50" x2="10" y2="50" stroke="#00ff41"/><line x1="75" y1="35" x2="100" y2="35" stroke="#00ff41"/></svg>',
    "NOR": '<svg width="100" height="50"><path d="M10,10 Q40,10 55,35 Q40,60 10,60 Q25,35 10,10" fill="none" stroke="#00ff41" stroke-width="2"/><circle cx="60" cy="35" r="5" stroke="#00ff41" fill="none"/><line x1="0" y1="20" x2="15" y2="20" stroke="#00ff41"/><line x1="0" y1="50" x2="15" y2="50" stroke="#00ff41"/><line x1="65" y1="35" x2="100" y2="35" stroke="#00ff41"/></svg>',
    "XNOR": '<svg width="100" height="50"><path d="M20,10 Q50,10 65,35 Q50,60 20,60 Q35,35 20,10" fill="none" stroke="#00ff41" stroke-width="2"/><path d="M10,10 Q25,35 10,60" fill="none" stroke="#00ff41" stroke-width="2"/><circle cx="70" cy="35" r="5" stroke="#00ff41" fill="none"/><line x1="0" y1="20" x2="15" y2="20" stroke="#00ff41"/><line x1="0" y1="50" x2="15" y2="50" stroke="#00ff41"/><line x1="75" y1="35" x2="100" y2="35" stroke="#00ff41"/></svg>'
}
