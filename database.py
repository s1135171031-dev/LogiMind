# ==========================================
# 檔案: database.py
# ==========================================
import streamlit as st
import random
import time

def init_db():
    if "db" not in st.session_state:
        st.session_state.db = {
            "users": {
                "frank": {
                    "name": "Frank", "password": "x", "money": 99999, "level": 99, 
                    "stocks": {}, "inventory": {}, 
                    "mailbox": [{"from": "Admin", "title": "Welcome", "msg": "Welcome to CityOS", "read": False}], 
                    "active_missions": [],
                    "completed_missions": []
                }
            },
            "bbs": []
        }

def get_user(uid):
    return st.session_state.db["users"].get(uid)

def save_user(uid, data):
    st.session_state.db["users"][uid] = data

def create_user(uid, password, name):
    if uid in st.session_state.db["users"]:
        return False
    st.session_state.db["users"][uid] = {
        "name": name, "password": password, "money": 1000, "level": 1, 
        "stocks": {}, "inventory": {}, 
        "mailbox": [{"from": "System", "title": "Welcome", "msg": "Welcome to CityOS.", "read": False}], 
        "active_missions": [],
        "completed_missions": []
    }
    return True

def send_mail(to_uid, from_uid, subject, msg):
    if to_uid in st.session_state.db["users"]:
        mail = {
            "from": from_uid, "title": subject, "msg": msg,
            "read": False, "time": time.strftime("%H:%M")
        }
        st.session_state.db["users"][to_uid]["mailbox"].insert(0, mail)
        return True
    return False

def check_mission(uid, user, action_type, extra_val=0):
    if not user.get("active_missions"):
        missions_pool = [
            {"id": "m1", "title": "First Investment", "desc": "Buy any stock.", "type": "stock_buy", "reward": 200},
            {"id": "m2", "title": "Hacker Training", "desc": "Run a command in Terminal.", "type": "cli_input", "reward": 150},
            {"id": "m3", "title": "Knowledge Base", "desc": "Complete a Quiz.", "type": "quiz_done", "reward": 100},
            {"id": "m4", "title": "Gear Up", "desc": "Buy an item from Shop.", "type": "shop_buy", "reward": 300},
            {"id": "m5", "title": "Communication", "desc": "Send an email.", "type": "send_mail", "reward": 150}
        ]
        completed = user.get("completed_missions", [])
        available = [m for m in missions_pool if m['id'] not in completed]
        if not available: available = missions_pool
        user["active_missions"] = random.sample(available, min(2, len(available)))
    
    completed_indices = []
    for i, m in enumerate(user["active_missions"]):
        done = False
        if m['type'] == action_type: done = True
        
        if done:
            user.setdefault("pending_claims", []).append(m)
            completed_indices.append(i)
            st.toast(f"✅ Mission Complete: {m['title']}")
    
    for i in sorted(completed_indices, reverse=True):
        done_mission = user["active_missions"].pop(i)
        user.setdefault("completed_missions", []).append(done_mission['id'])
    
    save_user(uid, user)
