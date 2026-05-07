import json
import hashlib
import os

USERS_FILE = "users.json"

def _load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def _save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def _hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password, security_answer):
    users = _load_users()
    if username in users:
        return False, "Username already exists."
    
    users[username] = {
        "password": _hash_password(password),
        "security_answer": security_answer.strip().lower(),
        "unlocked_index": 0,
        "quiz_scores": {}
    }
    _save_users(users)
    return True, "Account created successfully."

def verify_login(username, password):
    users = _load_users()
    if username not in users:
        return False, "Invalid username or password.", None
    
    if users[username]["password"] == _hash_password(password):
        if "unlocked_index" not in users[username]:
            users[username]["unlocked_index"] = 0
        if "quiz_scores" not in users[username]:
            users[username]["quiz_scores"] = {}
            
        # Convert string keys back to int for quiz_scores to match our app logic
        int_scores = {int(k): v for k, v in users[username]["quiz_scores"].items()}
        users[username]["quiz_scores"] = int_scores
        
        return True, "Login successful.", users[username]
    return False, "Invalid username or password.", None

def reset_password(username, security_answer, new_password):
    users = _load_users()
    if username not in users:
        return False, "Username not found."
    
    if users[username].get("security_answer") == security_answer.strip().lower():
        users[username]["password"] = _hash_password(new_password)
        _save_users(users)
        return True, "Password reset successfully."
    return False, "Incorrect security answer."

def save_user_progress(username, unlocked_index, quiz_scores):
    users = _load_users()
    if username in users:
        users[username]["unlocked_index"] = unlocked_index
        # Convert int keys to string for JSON serialization
        users[username]["quiz_scores"] = {str(k): v for k, v in quiz_scores.items()}
        _save_users(users)
