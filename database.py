import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def init_db():
    pass

def add_expense(user_id, amount, description, shop_name="Noma'lum", category="Umumiy", group_name="Shaxsiy"):
    expense = {
        "user_id": user_id,
        "amount": amount,
        "description": str(description) if not isinstance(description, list) else "\\n".join(str(d) for d in description),
        "shop_name": shop_name,
        "category": category,
        "group_name": str(group_name),
        "date": datetime.now().isoformat()
    }
    
    try:
        res = requests.post(f"{SUPABASE_URL}/rest/v1/expenses", headers=get_headers(), json=expense)
        if res.status_code not in (200, 201):
            return f"Baza xatosi ({res.status_code}): {res.text}"
        return None
    except Exception as e:
        return f"Xato: {e}"

def clear_expenses(chat_type, identifier):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    try:
        if chat_type == 'private':
            requests.delete(f"{SUPABASE_URL}/rest/v1/expenses?user_id=eq.{identifier}&group_name=eq.Shaxsiy", headers=headers)
        else:
            requests.delete(f"{SUPABASE_URL}/rest/v1/expenses?group_name=eq.{identifier}", headers=headers)
    except Exception as e:
        print("Baza xatosi (DELETE):", e)
        
def get_expenses():
    try:
        res = requests.get(f"{SUPABASE_URL}/rest/v1/expenses", headers=get_headers())
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        print("Baza xatosi (GET):", e)
    return []
