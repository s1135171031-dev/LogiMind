# config.py

# 1. 物品清單
ITEMS = {
    "Stim-Pack": {"price": 150, "desc": "興奮劑：使用後畫面會劇烈震動。"},
    "Nutri-Paste": {"price": 100, "desc": "營養膏：食用後視線會迷幻扭曲。"},
    "Cyber-Arm": {"price": 800, "desc": "義肢：裝備後介面會出現電路故障閃爍。"},
    "Trojan Virus": {"price": 300, "desc": "木馬病毒：PVP 入侵必備工具。"},
    "Anti-Rad Pill": {"price": 500, "desc": "抗輻射藥丸：清除所有負面特效與輻射值。"}
}

# 2. 股票代碼與基準價
STOCKS_DATA = {
    "NVID": {"base": 800},
    "TSMC": {"base": 600},
    "CYBR": {"base": 150},
    "ARAS": {"base": 2000},
    "DOGE": {"base": 5},
    "BTC":  {"base": 30000}
}

# 3. 等級稱號
LEVEL_TITLES = {
    1: "Script Kiddie (腳本小子)",
    2: "Code Monkey (代碼猴)",
    3: "Net Runner (網路行者)",
    4: "Sys Admin (系統管理員)",
    5: "Techno Wizard (科技巫師)"
}
