import os
import asyncio
from dotenv import load_dotenv
from google import genai
import re
import json

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

prompt_template = """
Ushbu matn, ovoz yoki rasmdan quyidagi ma'lumotlarni aniqlang:
1. Jami xarajat summasini (faqat raqam).
2. Xarid qilingan do'kon nomini (agar aniq bo'lsa, yo'qsa "Noma'lum").
3. Barcha mahsulotlar nomi va nimalar olinganini to'liq ro'yxat qilib yozing.
Faqat JSON qaytaring, masalan: 
{"amount": 50000, "shop_name": "Korzinka", "products": "1. Non 2ta\n2. Choy 1ta"}
"""

def extract_json_from_text(res_text: str):
    json_str = re.search(r'\{.*\}', res_text, re.DOTALL)
    if json_str:
        try:
            return json.loads(json_str.group())
        except:
            pass
    return None

async def test_api():
    text = "#xarajat Kechki ovqat uchun 400 000 va 150 000 so'm berdim Abdumominga"
    prompt = f"{prompt_template}\nMatn: {text}"
    print("Sending to Gemini async...")
    try:
        response = await client.aio.models.generate_content(
            model='gemini-3.1-pro-preview',
            contents=prompt
        )
        print("Response received:", response.text)
    except Exception as e:
        print("Gemini API Error:", e)

asyncio.run(test_api())
