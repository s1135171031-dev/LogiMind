# 檔案名稱: config.py
# 用途: 存放所有遊戲常數、SVG 資源、物品設定

# --- SVG 資源 ---
SVG_LIB = {
    "AND": '''<svg width="150" height="80"><path d="M20,10 L70,10 C95,10 110,30 110,40 C110,50 95,70 70,70 L20,70 Z" fill="none" stroke="#00FF00" stroke-width="3"/><path d="M0,25 L20,25 M0,55 L20,55 M110,40 L140,40" stroke="#00FF00" stroke-width="3"/><text x="40" y="45" fill="white" font-family="monospace">AND</text></svg>''',
    "OR": '''<svg width="150" height="80"><path d="M20,10 L60,10 Q90,40 60,70 L20,70 Q45,40 20,10 Z" fill="none" stroke="#00FF00" stroke-width="3"/><path d="M0,25 L25,25 M0,55 L25,55 M90,40 L120,40" stroke="#00FF00" stroke-width="3"/><text x="35" y="45" fill="white" font-family="monospace">OR</text></svg>''',
    "XOR": '''<svg width="150" height="80"><path d="M35,10 L75,10 Q105,40 75,70 L35,70 Q60,40 35,10 Z" fill="none" stroke="#00FF00" stroke-width="3"/><path d="M15,10 Q40,40 15,70" fill="none" stroke="#00FF00" stroke-width="3"/><path d="M0,25 L25,25 M0,55 L25,55 M105,40 L135,40" stroke="#00FF00" stroke-width="3"/><text x="50" y="45" fill="white" font-family="monospace">XOR</text></svg>''',
    "NOT": '''<svg width="150" height="80"><path d="M30,10 L30,70 L90,40 Z" fill="none" stroke="#00FF00" stroke-width="3"/><circle cx="96" cy="40" r="5" fill="none" stroke="#00FF00" stroke-width="2"/><path d="M0,40 L30,40 M102,40 L130,40" stroke="#00FF00" stroke-width="3"/><text x="40" y="45" fill="white" font-family="monospace">NOT</text></svg>'''
}

# --- 每日事件庫 ---
CITY_EVENTS = [
    {"id": "E01", "name": "平靜的一天", "desc": "各項指數正常。", "effect": None},
    {"id": "E02", "name": "牛市來臨", "desc": "加密貨幣飆升，挖礦收益 +50%。", "effect": "mining_boost"},
    {"id": "E03", "name": "黑色星期五", "desc": "黑市大特價，所有道具 7 折。", "effect": "shop_discount"},
    {"id": "E04", "name": "太陽風暴", "desc": "通訊干擾，駭客攻擊成功率與收益下降。", "effect": "hack_nerf"},
    {"id": "E05", "name": "系統漏洞", "desc": "防火牆失效，攻擊收益加倍！", "effect": "hack_boost"},
]

# --- 任務資料庫 ---
MISSIONS = {
    "M01": {"title": "初入社會", "desc": "前往銀行存入至少 $100。", "reward": 500, "target": "bank_save"},
    "M02": {"title": "裝備升級", "desc": "在黑市購買任意一件物品。", "reward": 800, "target": "shop_buy"},
    "M03": {"title": "邏輯入門", "desc": "在數位實驗室操作一次邏輯閘。", "reward": 600, "target": "logic_use"},
    "M04": {"title": "第一滴血", "desc": "成功執行一次駭客攻擊 (不論成敗)。", "reward": 1000, "target": "attack_try"},
    "M05": {"title": "資安大師", "desc": "將個人防禦代碼修改一次 (重置)。", "reward": 1500, "target": "change_code"}
}

# --- 職業與物品 ---
CLASSES = {
    "Novice": {"name": "一般市民", "icon": "👤", "desc": "權限受限。請盡快轉職。"},
    "Engineer": {"name": "硬體工程師", "icon": "🔧", "desc": "解鎖：[數位實驗室]、[挖礦加成]。"},
    "Programmer": {"name": "軟體工程師", "icon": "💻", "desc": "解鎖：[密碼學中心]、[CLI模式]。"},
    "Hacker": {"name": "資安專家", "icon": "🛡️", "desc": "解鎖：[駭客終端]、[黑市借貸]。"},
    "Architect": {"name": "系統創造者", "icon": "👑", "desc": "全知全能。"}
}

ITEMS = {
    "Mining GPU": {"price": 2000, "desc": "基礎礦機，每日登入 +$100", "type": "passive"},
    "Trojan Virus": {"price": 500, "desc": "攻擊必備：木馬程式 (消耗品)", "type": "attack"},
    "Firewall": {"price": 800, "desc": "防禦必備：抵擋一次攻擊 (消耗品)", "type": "defense"},
    "Chaos Heart": {"price": 1200, "desc": "混亂之心：被攻擊時，使對方選項 x2 (消耗品)", "type": "trap"},
    "Clarity Necklace": {"price": 1500, "desc": "清醒項鍊：攻擊時，排除一半錯誤選項 (消耗品)", "type": "buff"}
}
