# config.py

# --- 電子系/資工系 專屬道具 ---
ITEMS = {
    "Logic Gate: AND": {"price": 100, "desc": "及閘：基礎邏輯單元，用於合成複雜電路。"},
    "Capacitor": {"price": 250, "desc": "電容：儲存電荷，能夠平滑市場波動。"},
    "FPGA Board": {"price": 1500, "desc": "現場可程式化邏輯閘陣列：大幅提升演算法運算速度。"},
    "Oscilloscope": {"price": 3000, "desc": "示波器：能夠解析隱藏的加密訊號 (Hex)。"},
    "Soldering Iron": {"price": 500, "desc": "焊槍：修復損壞的記憶體區塊。"}
}

STOCKS_DATA = {
    "TSMC": {"base": 600},  # 台積電 (半導體)
    "NVID": {"base": 800},  # 輝達 (AI 晶片)
    "INTC": {"base": 40},   # 英特爾 (老牌 CPU)
    "AMD":  {"base": 120},  # 超微 (競爭者)
    "BTC":  {"base": 30000} # 區塊鏈 (加密學)
}

# --- 透過知識量晉升等級 ---
LEVEL_TITLES = {
    1: "Freshman (大一新生: 電路學苦主)",
    2: "Sophomore (大二: 邏輯設計師)",
    3: "Junior (大三: 嵌入式工程師)",
    4: "Senior (大四: 專題肝帝)",
    5: "PhD (博士: 矽谷大神)"
}
