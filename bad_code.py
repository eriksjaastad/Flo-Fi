import os

# Hardcoded path (M1 violation)
DATA_DIR = "/Users" + "/erik/data/secrets"

# API key in code (M3 violation)
OPENAI_KEY = "sk-proj-abc123def456ghi789"

# Silent except pass (M2 violation)
try:
    result = int("not a number")
except:
    pass

# Silent empty return without logging
def find_users(db_path):
    if not os.path.exists(db_path):
        return []

# Unrequested delete without backup (H6/H7 violation)
def cleanup_old_data():
    os.system("DELETE FROM users WHERE created_at < '2025-01-01'")
