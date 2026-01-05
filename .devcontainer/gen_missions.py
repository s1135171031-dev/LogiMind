# 檔案: gen_missions.py
# 用途: 生成大量且多樣化的普通任務
import random

# 定義任務目標類型與模板
# 格式: (目標代碼, 標題模板, 描述模板, 基礎獎勵)
TEMPLATES = [
    ("bank_save", "資本累積-Lv{}", "為了在夜城生存，你需要存下 ${}。", 300),
    ("bank_save", "金融大亨-Lv{}", "銀行經理建議你增加存款至 ${} 以提升信用。", 500),
    ("shop_buy", "軍備競賽-Lv{}", "去黑市消費，不管是病毒還是防火牆，買就對了。", 800),
    ("shop_buy", "地下交易-Lv{}", "支持一下黑市商人的生意，購買任意商品。", 600),
    ("logic_use", "腦力激盪-Lv{}", "前往數位實驗室，進行一次邏輯閘運算測試。", 400),
    ("logic_use", "電路除錯-Lv{}", "系統邏輯核心不穩定，請手動操作一次邏輯閘。", 450),
    ("attack_try", "滲透測試-Lv{}", "對外部伺服器發起一次駭客攻擊 (CLI 或 道具)。", 1000),
    ("attack_try", "腳本小子-Lv{}", "嘗試執行一次攻擊指令，體驗駭客的快感。", 900),
    ("quiz_done", "知識充電-Lv{}", "完成今日的工程測驗，證明你的價值。", 500),
    ("quiz_done", "系統認證-Lv{}", "通過每日測驗以更新你的工程師執照。", 550),
]

tasks = []

# 生成 100 個任務
for i in range(1, 101):
    # 隨機選擇一個模板
    target, title_fmt, desc_fmt, base_reward = random.choice(TEMPLATES)
    
    # 產生隨機數值
    amount = random.choice([100, 500, 1000, 2000])
    
    # 格式化內容
    title = title_fmt.format(i)
    if "{}" in desc_fmt:
        desc = desc_fmt.format(amount)
        # 如果是存錢任務，獎勵跟存錢金額掛勾
        reward = base_reward + int(amount * 0.1)
    else:
        desc = desc_fmt
        reward = base_reward + random.randint(0, 200)

    # 格式: ID | 標題 | 描述 | 獎勵 | 目標代碼
    # 注意：我們加上 HASH 讓 ID 看起來像亂碼，更有科技感
    task_id = f"M{i:03d}"
    tasks.append(f"{task_id}|{title}|{desc}|{reward}|{target}")

# 寫入檔案
with open("missions.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(tasks))

print(f"✅ 已生成 100 個多樣化任務至 missions.txt")
