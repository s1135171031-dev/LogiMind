# config.py

# 1. 物品清單 (名稱: {價格, 描述})
ITEMS = {
    "Stim-Pack": {"price": 150, "desc": "興奮劑：使用後畫面會劇烈震動。"},
    "Nutri-Paste": {"price": 100, "desc": "營養膏：食用後視線會迷幻扭曲。"},
    "Cyber-Arm": {"price": 800, "desc": "義肢：裝備後介面會出現電路故障閃爍。"},
    "Trojan Virus": {"price": 300, "desc": "木馬病毒：PVP 入侵必備工具。"},
    "Anti-Rad Pill": {"price": 500, "desc": "抗輻射藥丸：清除所有負面特效與輻射值。"}
}

# 2. 股票代碼與基準價
STOCKS_DATA = {
    "NVID": {"base": 800},  # Nvidia 梗
    "TSMC": {"base": 600},  # 台積電梗
    "CYBR": {"base": 150},  # Cyberpunk
    "ARAS": {"base": 2000}, # Arasaka
    "DOGE": {"base": 5}     # 狗狗幣
}

# 3. 等級稱號
LEVEL_TITLES = {
    1: "Script Kiddie (腳本小子)",
    2: "Code Monkey (代碼猴)",
    3: "Net Runner (網路行者)",
    4: "Sys Admin (系統管理員)",
    5: "Techno Wizard (科技巫師)"
}

# 4. 邏輯閘 SVG 圖形 (簡單的視覺化)
# 這裡用簡單的 SVG 字符串代表電路符號
SVG_LIB = {
    "AND": """<svg width="100" height="50"><path d="M10 10 H30 A20 20 0 0 1 30 40 H10 V10 Z" fill="none" stroke="#00ff41" stroke-width="2"/><line x1="0" y1="15" x2="10" y2="15" stroke="#00ff41"/><line x1="0" y1="35" x2="10" y2="35" stroke="#00ff41"/><line x1="50" y1="25" x2="60" y2="25" stroke="#00ff41"/></svg>""",
    "OR": """<svg width="100" height="50"><path d="M10 10 Q30 10 40 25 Q30 40 10 40 Q20 25 10 10" fill="none" stroke="#00ff41" stroke-width="2"/><line x1="0" y1="15" x2="10" y2="15" stroke="#00ff41"/><line x1="0" y1="35" x2="10" y2="35" stroke="#00ff41"/><line x1="40" y1="25" x2="50" y2="25" stroke="#00ff41"/></svg>""",
    "NOT": """<svg width="100" height="50"><path d="M10 10 L40 25 L10 40 V10 Z" fill="none" stroke="#00ff41" stroke-width="2"/><circle cx="45" cy="25" r="3" stroke="#00ff41" fill="none"/><line x1="0" y1="25" x2="10" y2="25" stroke="#00ff41"/><line x1="48" y1="25" x2="60" y2="25" stroke="#00ff41"/></svg>""",
    "XOR": """<svg width="100" height="50"><path d="M15 10 Q35 10 45 25 Q35 40 15 40 Q25 25 15 10" fill="none" stroke="#00ff41" stroke-width="2"/><path d="M5 10 Q15 25 5 40" fill="none" stroke="#00ff41" stroke-width="2"/><line x1="0" y1="15" x2="10" y2="15" stroke="#00ff41"/><line x1="0" y1="35" x2="10" y2="35" stroke="#00ff41"/><line x1="45" y1="25" x2="55" y2="25" stroke="#00ff41"/></svg>"""
}
