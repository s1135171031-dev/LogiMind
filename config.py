# config.py
# 城市設定檔：定義這座反烏托邦城市的基礎數據

# 物品清單 (名稱, 價格, 描述)
ITEMS = {
    "Nutri-Paste": {"price": 20, "desc": "像是嘔吐物的營養膏，維持生命最低需求。"},
    "Synthetic Beer": {"price": 50, "desc": "含微量輻射的合成啤酒，能暫時忘記這該死的生活。"},
    "Stim-Pack": {"price": 150, "desc": "非法興奮劑。工作效率提升，副作用是手抖。"},
    "Data Chip (Corrupted)": {"price": 300, "desc": "從垃圾堆撿來的晶片，可能藏著舊時代的A片或病毒。"},
    "VR Headset": {"price": 800, "desc": "逃避現實的最佳工具。現實很爛，虛擬世界比較香。"},
    "Cyber-Arm (Rusty)": {"price": 2500, "desc": "二手機械手臂，伺服馬達聲音很大，但比肉體強。"},
    "GPU (Mining)": {"price": 5000, "desc": "挖礦專用顯卡。現在比人命還值錢。"},
    "Firewall Key": {"price": 10000, "desc": "企業級防火牆金鑰。駭客夢寐以求的玩具。"}
}

# 股市清單 (代碼: {名稱, 基準價, 波動率})
# 注意：即使這裡波動率寫得很低，database.py 也會強制讓它們發瘋
STOCKS_DATA = {
    "CYBR": {"name": "CyberCorp", "base": 1200, "volatility": 0.15},
    "NEO":  {"name": "Neo-Tokyo Real Estate", "base": 5000, "volatility": 0.05},
    "SLUM": {"name": "Slum Recyclers", "base": 50, "volatility": 0.30},
    "AI":   {"name": "Skynet AI", "base": 3000, "volatility": 0.20},
    "MED":  {"name": "BioLife (Organ Harvesting)", "base": 800, "volatility": 0.08},
    "GOV":  {"name": "City Bond (Fake)", "base": 100, "volatility": 0.01}, # 就算是債券也會崩盤
    "COIN": {"name": "DogeDark", "base": 10, "volatility": 0.50}
}

# 隨機城市事件
CITY_EVENTS = [
    {"name": "Acid Rain", "effect": "depression", "desc": "酸雨警報。全城心情低落，消費意願下降。"},
    {"name": "Cyber Attack", "effect": "crash", "desc": "駭客攻擊交易所。股價即將大怒神。"},
    {"name": "Corporate War", "effect": "volatility", "desc": "兩大企業開戰。有人發財，有人喪命。"},
    {"name": "AI Glitch", "effect": "pump", "desc": "交易演算法出錯，全線隨機暴漲。"},
    {"name": "Normal Day", "effect": "none", "desc": "又是一個平淡無奇、充滿壓迫感的一天。"}
]
