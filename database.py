import json
import os
from datetime import datetime

DB_FILE = "expenses.json"

def init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

def save_expenses(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def add_expense(user_id, amount, description, shop_name="Noma'lum", category="Umumiy", group_name="Shaxsiy"):
    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    expense = {
        "user_id": user_id,
        "amount": amount,
        "description": description,
        "shop_name": shop_name,
        "category": category,
        "group_name": group_name,
        "date": datetime.now().isoformat()
    }
    data.append(expense)
    
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def clear_expenses(chat_type, identifier):
    expenses = get_expenses()
    if chat_type == 'private':
        # Faqat shu foydalanuvchining shaxsiy xarajatlarini o'chirish
        filtered = [d for d in expenses if not (d.get('user_id') == identifier and d.get('group_name') == 'Shaxsiy')]
    else:
        # Shu guruhning xarajatlarini o'chirish
        filtered = [d for d in expenses if d.get('group_name') != identifier]
    
    save_expenses(filtered)
        
def get_expenses():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data
