# ==========================================
# 檔案: database.py
# 用途: 資料處理與存檔 (JSON)
# ==========================================
import streamlit as st
import json
import os
from datetime import datetime

DB_FILE = "cityos_db.json"

def init_db():
    if "db" not in st.session_state:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f:
                st.session_state.db = json.load(f)
        else:
            st.session_state.db = {"users": {}}
            # 建立預設管理員
            create_user("frank", "x", "SysAdmin")

def save_db():
    with open(DB_FILE, "w") as f:
        json.dump(st.session_state.db, f)

def get_user(uid):
    return st.session_state.db["users"].get(uid)

def save_user(uid, user_data):
    st.session_state.db["users"][uid] = user_data
    save_db()

def create_user(uid, pwd, name):
    if uid in st.session_state.db["users"]:
        return False
    
    st.session_state.db["users"][uid] = {
        "password": pwd,
        "name": name,
        "money": 1000,
        "stocks": {},
        "inventory": {},
        "mailbox": [],
        "active_missions": [],
        "pending_claims": [],
        "mission_history": []
    }
    save_db()
    return True

def send_mail(to_uid, from_uid, subject, body):
    target = get_user(to_uid)
    if not target: return False
    
    msg = {
        "time": datetime.now().strftime("%H:%M"),
        "from": from_uid,
        "title": subject,
        "msg": body
    }
    target["mailbox"].insert(0, msg)
    save_user(to_uid, target)
    return True

def check_mission(uid, user, action_type):
    # 定義任務
    missions = [
        {"id": "m1", "title": "First Trade", "desc": "Buy any stock.", "type": "stock_buy", "reward": 500},
        {"id": "m2", "title": "Hacker Tool", "desc": "Buy a Brute Force Script.", "type": "shop_buy", "reward": 300},
        {"id": "m3", "title": "Connect", "desc": "Send an email.", "type": "send_mail", "reward": 200},
        {"id": "m4", "title": "Knowledge", "desc": "Answer a quiz correctly.", "type": "quiz_done", "reward": 100},
        {"id": "m5", "title": "Hello World", "desc": "Type something in Terminal.", "type": "cli_input", "reward": 50}
    ]
    
    # 檢查是否發放新任務
    existing_ids = [m['id'] for m in user['active_missions']] + user['mission_history']
    for m in missions:
        if m['id'] not in existing_ids:
            user['active_missions'].append(m)
    
    # 檢查是否完成任務
    completed = []
    for m in user['active_missions']:
        if m['type'] == action_type or action_type == "refresh":
            # 簡化邏輯：只要觸發動作就算完成
            if action_type != "refresh":
                user['pending_claims'].append(m)
                user['mission_history'].append(m['id'])
                completed.append(m)
    
    for c in completed:
        user['active_missions'].remove(c)
        
    save_user(uid, user)
