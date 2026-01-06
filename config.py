# config.py
# 用途: 存放遊戲常數、道具設定、圖片資源

ITEMS = {
    "Mining GPU": {"price": 2000, "desc": "基礎礦機，每日登入 +$100", "type": "passive"},
    "Trojan Virus": {"price": 500, "desc": "PVP 消耗品: 攻擊必備", "type": "attack"},
    "Firewall": {"price": 800, "desc": "PVP 消耗品: 抵擋一次攻擊", "type": "defense"},
    "Brute Force Script": {"price": 1200, "desc": "PVP 道具: 提升攻擊成功率", "type": "tool"},
    "Coffee": {"price": 50, "desc": "回復精力 (裝飾用)", "type": "consumable"}
}

# 股市設定 (基價與波動率)
STOCKS_DATA = {
    "CYBR": {"name": "CyberCorp", "base": 500, "volatility": 0.05},
    "ROBO": {"name": "RoboDynamics", "base": 300, "volatility": 0.08},
    "AI":   {"name": "Sentient AI", "base": 800, "volatility": 0.12},
    "FOOD": {"name": "SynthFood", "base": 50, "volatility": 0.02},
    "HACK": {"name": "ZeroDay Grp", "base": 150, "volatility": 0.20}
}

# 每日事件
CITY_EVENTS = [
    {"id": "E01", "name": "平靜的一天", "desc": "各項指數正常。", "effect": "normal"},
    {"id": "E02", "name": "牛市來臨", "desc": "科技股看漲，挖礦收益 +50%。", "effect": "tech_boom"},
    {"id": "E03", "name": "黑色星期五", "desc": "黑市大特價，所有道具 7 折。", "effect": "shop_discount"},
    {"id": "E04", "name": "太陽風暴", "desc": "通訊干擾，駭客攻擊成功率下降。", "effect": "hack_nerf"},
    {"id": "E05", "name": "金融海嘯", "desc": "股市全面崩跌預警！", "effect": "crash"},
]

# SVG 邏輯閘資源
SVG_LIB = {
    "AND": '''<svg width="150" height="80"><path d="M20,10 L70,10 C95,10 110,30 110,40 C110,50 95,70 70,70 L20,70 Z" fill="none" stroke="#00FF00" stroke-width="3"/><path d="M0,25 L20,25 M0,55 L20,55 M110,40 L140,40" stroke="#00FF00" stroke-width="3"/><text x="40" y="45" fill="white" font-family="monospace">AND</text></svg>''',
    "OR": '''<svg width="150" height="80"><path d="M20,10 L60,10 Q90,40 60,70 L20,70 Q45,40 20,10 Z" fill="none" stroke="#00FF00" stroke-width="3"/><path d="M0,25 L25,25 M0,55 L25,55 M90,40 L120,40" stroke="#00FF00" stroke-width="3"/><text x="35" y="45" fill="white" font-family="monospace">OR</text></svg>''',
    "XOR": '''<svg width="150" height="80"><path d="M35,10 L75,10 Q105,40 75,70 L35,70 Q60,40 35,10 Z" fill="none" stroke="#00FF00" stroke-width="3"/><path d="M15,10 Q40,40 15,70" fill="none" stroke="#00FF00" stroke-width="3"/><path d="M0,25 L25,25 M0,55 L25,55 M105,40 L135,40" stroke="#00FF00" stroke-width="3"/><text x="50" y="45" fill="white" font-family="monospace">XOR</text></svg>''',
    "NOT": '''<svg width="150" height="80"><path d="M30,10 L30,70 L90,40 Z" fill="none" stroke="#00FF00" stroke-width="3"/><circle cx="96" cy="40" r="5" fill="none" stroke="#00FF00" stroke-width="2"/><path d="M0,40 L30,40 M102,40 L130,40" stroke="#00FF00" stroke-width="3"/><text x="40" y="45" fill="white" font-family="monospace">NOT</text></svg>'''
}
