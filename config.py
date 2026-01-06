# config.py
# 用途: 遊戲常數配置 (毒舌版)

# 道具描述：極度諷刺
ITEMS = {
    "Mining GPU": {
        "price": 2500, 
        "desc": "過時的電子垃圾。雖然慢得要死，但你這種窮人也只買得起這個。每日 +$100 (少得可憐)。", 
        "type": "passive"
    },
    "Trojan Virus": {
        "price": 600, 
        "desc": "給那些不懂程式碼的廢物用的攻擊腳本。點一下就能搞破壞，滿意了嗎？", 
        "type": "attack"
    },
    "Firewall": {
        "price": 900, 
        "desc": "虛假的安全感。雖然能擋一次攻擊，但擋不住你人生的失敗。", 
        "type": "defense"
    },
    "Brute Force Script": {
        "price": 1500, 
        "desc": "暴力破解。毫無美感，純粹靠運氣，跟你的人生一樣。", 
        "type": "tool"
    },
    "Coffee": {
        "price": 80, 
        "desc": "深褐色的化學汙泥。喝了能讓你清醒地意識到自己的處境有多悲慘。", 
        "type": "consumable"
    }
}

# 股市設定
STOCKS_DATA = {
    "CYBR": {"name": "CyberCorp", "base": 500, "volatility": 0.05},
    "ROBO": {"name": "RoboDynamics", "base": 300, "volatility": 0.08},
    "AI":   {"name": "Sentient AI", "base": 800, "volatility": 0.12},
    "FOOD": {"name": "SynthFood", "base": 50, "volatility": 0.02},
    "HACK": {"name": "ZeroDay Grp", "base": 150, "volatility": 0.20}
}

# 每日事件 (充滿絕望感)
CITY_EVENTS = [
    {"id": "E01", "name": "無聊的一天", "desc": "空氣汙染指數 99%。沒什麼特別的，除了你還活著。", "effect": "normal"},
    {"id": "E02", "name": "資本狂歡", "desc": "科技巨頭股價飆升。當然，這跟身為韭菜的你沒什麼關係，除非你買了股票。", "effect": "tech_boom"},
    {"id": "E03", "name": "清倉大拍賣", "desc": "黑市商人急著跑路，東西隨便賣。快買，別問來源。", "effect": "shop_discount"},
    {"id": "E04", "name": "太陽閃焰", "desc": "通訊中斷。連網路都拋棄你了，攻擊成功率下降。", "effect": "hack_nerf"},
    {"id": "E05", "name": "市場崩盤", "desc": "看著那些富人的資產蒸發，是你今天唯一的樂趣。", "effect": "crash"},
]

# SVG 邏輯閘資源
SVG_LIB = {
    "AND": '''<svg width="150" height="80"><path d="M20,10 L70,10 C95,10 110,30 110,40 C110,50 95,70 70,70 L20,70 Z" fill="none" stroke="#00FF00" stroke-width="3"/><path d="M0,25 L20,25 M0,55 L20,55 M110,40 L140,40" stroke="#00FF00" stroke-width="3"/><text x="40" y="45" fill="white" font-family="monospace">AND</text></svg>''',
    "OR": '''<svg width="150" height="80"><path d="M20,10 L60,10 Q90,40 60,70 L20,70 Q45,40 20,10 Z" fill="none" stroke="#00FF00" stroke-width="3"/><path d="M0,25 L25,25 M0,55 L25,55 M90,40 L120,40" stroke="#00FF00" stroke-width="3"/><text x="35" y="45" fill="white" font-family="monospace">OR</text></svg>''',
    "XOR": '''<svg width="150" height="80"><path d="M35,10 L75,10 Q105,40 75,70 L35,70 Q60,40 35,10 Z" fill="none" stroke="#00FF00" stroke-width="3"/><path d="M15,10 Q40,40 15,70" fill="none" stroke="#00FF00" stroke-width="3"/><path d="M0,25 L25,25 M0,55 L25,55 M105,40 L135,40" stroke="#00FF00" stroke-width="3"/><text x="50" y="45" fill="white" font-family="monospace">XOR</text></svg>''',
    "NOT": '''<svg width="150" height="80"><path d="M30,10 L30,70 L90,40 Z" fill="none" stroke="#00FF00" stroke-width="3"/><circle cx="96" cy="40" r="5" fill="none" stroke="#00FF00" stroke-width="2"/><path d="M0,40 L30,40 M102,40 L130,40" stroke="#00FF00" stroke-width="3"/><text x="40" y="45" fill="white" font-family="monospace">NOT</text></svg>'''
}
