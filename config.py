# config.py - System Configuration

# 1. 電子系道具清單
ITEMS = {
    "Logic Gate: AND": {"price": 100, "desc": "及閘 (AND Gate)：基礎邏輯單元，用於合成電路"},
    "Capacitor": {"price": 250, "desc": "電容 (Capacitor)：儲存電荷，濾除雜訊"},
    "FPGA Board": {"price": 1500, "desc": "FPGA 開發板：硬體描述語言 (Verilog) 專用"},
    "Oscilloscope": {"price": 3000, "desc": "示波器 (Oscilloscope)：解析電壓波形與 Hex 訊號"},
    "Soldering Iron": {"price": 500, "desc": "電烙鐵 (Soldering Iron)：修復損壞的記憶體區塊"},
    "Graphing Calc": {"price": 1200, "desc": "工程計算機 (Graphing Calc)：支援微積分符號運算"}
}

# 2. 股市資料 (科技股)
STOCKS_DATA = {
    "TSMC": {"base": 600},  # 台積電
    "NVID": {"base": 800},  # 輝達
    "INTC": {"base": 40},   # 英特爾
    "AMD":  {"base": 120},  # 超微
    "BTC":  {"base": 30000} # 比特幣
}

# 3. 等級稱號
LEVEL_TITLES = {
    1: "大一菜鳥 (Freshman)",
    2: "大二邏輯設計師 (Sophomore)",
    3: "大三嵌入式工程師 (Junior)",
    4: "大四專題肝帝 (Senior)",
    5: "博士矽谷大神 (PhD Architect)"
}
