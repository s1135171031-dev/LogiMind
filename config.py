# config.py

# --- 物品清單 (賽博毒舌版) ---
ITEMS = {
    # 🔴 視覺副作用：畫面高頻震動 (Shake)
    "Stim-Pack": {
        "price": 50, 
        "desc": "⚠️ [警告] 中樞神經破壞者。\n便宜的興奮劑。打下去瞬間覺得自己是神，但副作用會讓你連滑鼠都握不穩 (畫面劇烈震動)。"
    },

    # 🟢 視覺副作用：畫面流體扭曲 + 變色 (Dizzy)
    "Nutri-Paste": {
        "price": 10, 
        "desc": "🤮 [警告] 為了活下去。\n口感像過期的機油。勉強能止餓，但你的視網膜會開始融化，世界變得五顏六色 (畫面暈眩扭曲)。"
    },

    # 🔵 視覺副作用：雜訊掃描線 (Glitch)
    "Cyber-Arm": {
        "price": 1200, 
        "desc": "🦾 [裝備] 死人的遺產。\n從屍體拆下來的二手義肢。力量很大，但神經接觸不良，會干擾你的視覺訊號 (視訊雜訊)。"
    },

    # --- 功能性道具 ---
    "Data Chip": {
        "price": 100, 
        "desc": "💾 數位垃圾。\n某個倒楣鬼腦袋裡的備份。運氣好是比特幣金鑰，運氣差就是他死前的跑馬燈。"
    },
    
    "VR Headset": {
        "price": 300, 
        "desc": "🕶️ 現實逃避器。\n這座城市太爛了，戴上它去虛擬世界當個現充吧。至少那裡的天空是藍的。"
    },
    
    "GPU (Mining)": {
        "price": 2500, 
        "desc": "⛏️ 現代煉金石。\n比你那無用的肉體值錢多了。放在背包裡感覺就在發燙。"
    },
    
    "Trojan Virus": {
        "price": 800, 
        "desc": "⚔️ 數位兇器。\nPVP 專用。注入後，對方的銀行帳戶就是你的提款機。"
    },
    
    "Firewall": {
        "price": 1000, 
        "desc": "🛡️ 數位保險套。\n雖然擋不住真正的高手，但至少能讓你在睡覺時不被路邊的腳本小子扒光。"
    },
    
    "Anti-Rad Pill": {
        "price": 200, 
        "desc": "💊 系統格式化。\n醫療級解毒劑。能消除體內毒素，並強制排出所有興奮劑與劣質食物 (消除副作用)。",
        "type": "cure", 
        "value": 30
    },
    
    "Gas Mask": {
        "price": 1500, 
        "desc": "😷 貧民窟奢侈品。\n在這個充滿毒氣的鬼地方，呼吸乾淨空氣是「付費會員」的特權。"
    },
    
    "Python Manual": {
        "price": 500, 
        "desc": "📚 舊世界的禁書。\n讀懂它，你就能從「使用者」進化成「造物主」。"
    }
}

STOCKS_DATA = {
    "CYBR": {"name": "CyberCorp", "base": 80, "volatility": 2.0},
    "NEO":  {"name": "Neo-Tokyo", "base": 120, "volatility": 2.0},
    "SLUM": {"name": "Slum Ind.", "base": 15, "volatility": 3.0},
    "AI":   {"name": "Skynet", "base": 60, "volatility": 2.0},
    "BOND": {"name": "City Bond", "base": 30, "volatility": 1.5},
    "DOGE": {"name": "MemeCoin", "base": 5, "volatility": 5.0}
}

LEVEL_TITLES = {
    1: "Street Rat (街頭混混)", 2: "Script Kiddie (腳本小子)", 3: "Code Monkey (碼農)",
    4: "Glitch Hunter (故障獵人)", 5: "Netrunner (網路行者)", 6: "System Architect (架構師)",
    7: "Cyber Lord (賽博領主)", 8: "City Legend (城市傳說)", 9: "The Ghost (幽靈)", 10: "AI Singularity (奇異點)"
}

# 修正高度為 70，防止圖形被切掉
SVG_LIB = {
    "AND": '<svg width="100" height="70"><path d="M10,10 L40,10 A25,25 0 0,1 40,60 L10,60 Z" fill="none" stroke="#00ff41" stroke-width="2"/><line x1="0" y1="20" x2="10" y2="20" stroke="#00ff41"/><line x1="0" y1="50" x2="10" y2="50" stroke="#00ff41"/><line x1="65" y1="35" x2="100" y2="35" stroke="#00ff41"/></svg>',
    "OR": '<svg width="100" height="70"><path d="M10,10 Q40,10 55,35 Q40,60 10,60 Q25,35 10,10" fill="none" stroke="#00ff41" stroke-width="2"/><line x1="0" y1="20" x2="15" y2="20" stroke="#00ff41"/><line x1="0" y1="50" x2="15" y2="50" stroke="#00ff41"/><line x1="55" y1="35" x2="100" y2="35" stroke="#00ff41"/></svg>',
    "NOT": '<svg width="100" height="70"><path d="M10,10 L40,35 L10,60 Z" fill="none" stroke="#00ff41" stroke-width="2"/><circle cx="45" cy="35" r="5" stroke="#00ff41" fill="none"/><line x1="0" y1="35" x2="10" y2="35" stroke="#00ff41"/><line x1="50" y1="35" x2="100" y2="35" stroke="#00ff41"/></svg>',
    "XOR": '<svg width="100" height="70"><path d="M20,10 Q50,10 65,35 Q50,60 20,60 Q35,35 20,10" fill="none" stroke="#00ff41" stroke-width="2"/><path d="M10,10 Q25,35 10,60" fill="none" stroke="#00ff41" stroke-width="2"/><line x1="0" y1="20" x2="15" y2="20" stroke="#00ff41"/><line x1="0" y1="50" x2="15" y2="50" stroke="#00ff41"/><line x1="65" y1="35" x2="100" y2="35" stroke="#00ff41"/></svg>',
    "NAND": '<svg width="100" height="70"><path d="M10,10 L40,10 A25,25 0 0,1 40,60 L10,60 Z" fill="none" stroke="#00ff41" stroke-width="2"/><circle cx="70" cy="35" r="5" stroke="#00ff41" fill="none"/><line x1="0" y1="20" x2="10" y2="20" stroke="#00ff41"/><line x1="0" y1="50" x2="10" y2="50" stroke="#00ff41"/><line x1="75" y1="35" x2="100" y2="35" stroke="#00ff41"/></svg>',
    "NOR": '<svg width="100" height="70"><path d="M10,10 Q40,10 55,35 Q40,60 10,60 Q25,35 10,10" fill="none" stroke="#00ff41" stroke-width="2"/><circle cx="60" cy="35" r="5" stroke="#00ff41" fill="none"/><line x1="0" y1="20" x2="15" y2="20" stroke="#00ff41"/><line x1="0" y1="50" x2="15" y2="50" stroke="#00ff41"/><line x1="65" y1="35" x2="100" y2="35" stroke="#00ff41"/></svg>',
    "XNOR": '<svg width="100" height="70"><path d="M20,10 Q50,10 65,35 Q50,60 20,60 Q35,35 20,10" fill="none" stroke="#00ff41" stroke-width="2"/><path d="M10,10 Q25,35 10,60" fill="none" stroke="#00ff41" stroke-width="2"/><circle cx="70" cy="35" r="5" stroke="#00ff41" fill="none"/><line x1="0" y1="20" x2="15" y2="20" stroke="#00ff41"/><line x1="0" y1="50" x2="15" y2="50" stroke="#00ff41"/><line x1="75" y1="35" x2="100" y2="35" stroke="#00ff41"/></svg>'
}
