# 檔案: database.py 的部分更新

# --- 定義怪異的隱藏成就 ---
HIDDEN_MISSIONS = {
    # 既有成就
    "H_ZERO": {"title": "💸 破產俱樂部", "desc": "現金歸零。身無分文也是一種修行。", "reward": 1000},
    "H_777":  {"title": "🎰 幸運七七七", "desc": "現金剛好等於 $777。", "reward": 7777},
    "H_SHOP": {"title": "🛍️ 囤積症患者", "desc": "背包內擁有超過 15 個物品。", "reward": 2000},
    "H_HACK": {"title": "💀 ROOT ACCESS", "desc": "在 CLI 發現了管理者指令。", "reward": 5000},
    
    # --- 🔥 新增的奇怪成就 ---
    "H_MATH": {"title": "🤓 數字敏感度", "desc": "在進位轉換器輸入了 '1024' (工程師的整數)。", "reward": 1024},
    "H_SPAM": {"title": "🤬 憤怒的駭客", "desc": "在 CLI 連續輸入錯誤指令超過 5 次。", "reward": 500},
    "H_BANK": {"title": "🏦 避險大師", "desc": "銀行存款超過 $100,000 但身上現金低於 $100。", "reward": 3000},
    "H_LOGIC":{"title": "⚡ 電路過載", "desc": "在數位實驗室把所有開關都打開 (Input A=1, B=1)。", "reward": 600}
}

# ... (中間省略 load 函數 ...)

# --- 修改 check_mission 邏輯以支援怪任務 ---
def check_mission(uid, user, action_type, extra_data=None):
    missions = load_missions_from_file()
    completed_any = False
    
    # 1. 檢查普通任務
    for mid, m_data in missions.items():
        if m_data["target"] == action_type and mid not in user.get("completed_missions", []):
            user["completed_missions"].append(mid)
            user["money"] += m_data["reward"]
            user["exp"] = user.get("exp", 0) + 100
            st.toast(f"🎉 任務完成：{m_data['title']} (+${m_data['reward']})")
            completed_any = True

    # 2. 檢查隱藏成就 (Easter Eggs)
    
    # [H_ZERO] 現金歸零
    if "H_ZERO" not in user["completed_missions"] and user["money"] == 0:
        _unlock(user, "H_ZERO"); completed_any = True

    # [H_777] 現金 777
    if "H_777" not in user["completed_missions"] and user["money"] == 777:
        _unlock(user, "H_777"); completed_any = True

    # [H_SHOP] 背包囤積 > 15
    inv_count = sum(user.get("inventory", {}).values())
    if "H_SHOP" not in user["completed_missions"] and inv_count >= 15:
        _unlock(user, "H_SHOP"); completed_any = True
        
    # [H_BANK] 錢都在銀行 (避險大師)
    if "H_BANK" not in user["completed_missions"] and user.get("bank_deposit",0) > 100000 and user["money"] < 100:
        _unlock(user, "H_BANK"); completed_any = True

    # [H_HACK] CLI 輸入 sudo su
    if action_type == "cli_input" and extra_data == "sudo su":
        if "H_HACK" not in user["completed_missions"]:
            _unlock(user, "H_HACK"); completed_any = True

    # [H_SPAM] CLI 錯誤指令 (需要在 extra_data 傳入 'error_cmd')
    if action_type == "cli_error":
        # 我們用一個暫存變數記錄錯誤次數，這裡簡化處理，只要觸發一次 error 就給過 (或者是 session state 判斷)
        # 為了更嚴謹，這裡假設 app.py 會判斷 session_state.error_count
        if "H_SPAM" not in user["completed_missions"] and extra_data >= 5:
             _unlock(user, "H_SPAM"); completed_any = True

    # [H_MATH] 輸入 1024
    if action_type == "crypto_input" and str(extra_data) == "1024":
        if "H_MATH" not in user["completed_missions"]:
            _unlock(user, "H_MATH"); completed_any = True

    # [H_LOGIC] 全開開關
    if action_type == "logic_state" and extra_data == "11": # A=1, B=1
        if "H_LOGIC" not in user["completed_missions"]:
            _unlock(user, "H_LOGIC"); completed_any = True

    # 存檔
    if completed_any and uid != "frank":
        save_db({"users": load_db()["users"] | {uid: user}, "bbs": load_db().get("bbs", [])})
    
    return user

def _unlock(user, mid):
    hm = HIDDEN_MISSIONS[mid]
    user["completed_missions"].append(mid)
    user["money"] += hm["reward"]
    st.toast(f"🏆 隱藏成就解鎖！【{hm['title']}】\n{hm['desc']}", icon="🔥")
