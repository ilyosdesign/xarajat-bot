import os
import asyncio
import re
import json
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import FSInputFile
from dotenv import load_dotenv

from google import genai
from google.genai import types as genai_types

from database import init_db, add_expense
from exporters import export_to_excel, export_to_pdf

# .env fayldan o'zgaruvchilarni yuklash
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not BOT_TOKEN or not GEMINI_API_KEY:
    print("Iltimos, .env faylida BOT_TOKEN va GEMINI_API_KEY ni kiriting.")
    exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = genai.Client(api_key=GEMINI_API_KEY)
init_db()

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("Assalomu alaykum! Men xarajatlarni hisoblovchi botman.\n"
                         "Menga '#xarajat' yoki '#harajat' so'zi qatnashgan matn, ovozli xabar yoki chek rasmini yuboring.\n"
                         "Hisobotni yuklab olish uchun /excel yoki /pdf buyrug'idan foydalaning.")

def get_chat_info(message: types.Message):
    if message.chat.type in ["group", "supergroup"]:
        return 'group', message.chat.title
    return 'private', message.from_user.id

@dp.message(Command("excel"))
async def excel_cmd(message: types.Message):
    chat_type, identifier = get_chat_info(message)
    fname = f"Xarajatlar_{identifier}.xlsx".replace(" ", "_")
    filename = export_to_excel(chat_type, identifier, filename=fname)
    if filename:
        file = FSInputFile(filename)
        await message.answer_document(file, caption="Sizning xarajatlaringiz ro'yxati (Excel).")
        os.remove(filename)
    else:
        await message.answer("Hozircha xarajatlar yo'q.")

@dp.message(Command("pdf"))
async def pdf_cmd(message: types.Message):
    chat_type, identifier = get_chat_info(message)
    fname = f"Hisobot_{identifier}.pdf".replace(" ", "_")
    filename = export_to_pdf(chat_type, identifier, filename=fname)
    if filename:
        file = FSInputFile(filename)
        await message.answer_document(file, caption="Sizning xarajatlaringiz ro'yxati (PDF).")
        os.remove(filename)
    else:
        await message.answer("Hozircha xarajatlar yo'q.")

@dp.message(Command("clear"))
async def clear_cmd(message: types.Message):
    from database import clear_expenses
    chat_type, identifier = get_chat_info(message)
    clear_expenses(chat_type, identifier)
    if chat_type == 'private':
        await message.answer("Shaxsiy xarajatlaringiz tarixi to'liq tozalandi! 🧹")
    else:
        await message.answer(f"Xarajatlar tarixi to'liq tozalandi! 🧹")

def extract_json_from_text(res_text: str):
    json_str = re.search(r'\{.*\}', res_text, re.DOTALL)
    if json_str:
        try:
            return json.loads(json_str.group())
        except:
            pass
    return None

prompt_template = """
Siz xarajatlarni hisoblovchi uzbek tilidagi aqlli yordamchisiz.
Ushbu matn, ovoz yoki chek rasmidan quyidagi ma'lumotlarni juda aniqlik bilan toping:
1. "amount": Yakuniy to'langan xarajat summasi (faqat raqam). Agar chekda "Савдо" (Jami summa) va "Скидка" (Chegirma) alohida ko'rsatilgan bo'lsa, ularni hisoblang: Jami summadan chegirmasini ayirib tashlang va yakuniy narxni yozing (masalan, 177233.9 dan 233.9 ni ayirib, 177000 deb yozing). Agar "Итого" yoki "To'lanuvchi summa" tayyor bo'lsa, o'shani oling. "Скидка" ning o'zini xarajat deb olmang!
2. "shop_name": Xarid qilingan do'kon nomi. DIQQAT: Chekdagi "Клиент", "Xaridor", "Mijoz" qatoriga yozilgan yoki umuman xaridorga tegishli ismlarni (masalan, "AS MEBEL ASADILLO") ASLO do'kon nomi qilib olmang! Agar do'kon nomi aniq tepada alohida ko'rsatilmagan bo'lsa (masalan tepada faqat "Асосий" degan so'z bo'lsa), unda qat'iyan "Noma'lum" deb yozing.
3. "products": Olingan barcha mahsulotlar nomi va miqdorini ro'yxat qilib yozing.
Faqat JSON formatda qaytaring, qo'shimcha gaplarsiz.
"""

async def parse_expense_from_text(text: str):
    prompt = f"{prompt_template}\nMatn: {text}"
    try:
        response = await client.aio.models.generate_content(
            model='gemini-3.5-flash-lite',
            contents=prompt
        )
        data = extract_json_from_text(response.text)
        if data:
            return data.get("amount", 0), data.get("shop_name", "Noma'lum"), data.get("products", "Noma'lum")
        return None, None, None
    except Exception as e:
        print("Gemini API Error:", e)
        return None, None, None

@dp.message(F.text)
async def handle_text(message: types.Message):
    text = message.text or ""
    text_lower = text.lower()
    group_name = message.chat.title if message.chat.title else "Shaxsiy"
    
    if text.startswith('/'):
        return
        
    is_private = message.chat.type == "private"
    if "#xarajat" in text_lower or "#harajat" in text_lower or is_private:
        msg = await message.answer("Tahlil qilinmoqda...")
        amount, shop, products = await parse_expense_from_text(text)
        if amount:
            add_expense(message.from_user.id, amount, products, shop, group_name=group_name)
            await msg.edit_text(f"✅ Xarajat saqlandi!\nSumma: {amount}\nDo'kon: {shop}\nMahsulotlar: {products}")
        else:
            await msg.edit_text("Kechirasiz, xarajat ma'lumotlarini aniqlay olmadim.")
    else:
        # Group chat but without hashtag
        pass

@dp.message(F.voice)
async def handle_voice(message: types.Message):
    caption = (message.caption or "").lower()
    is_private = message.chat.type == "private"
    if "#xarajat" not in caption and "#harajat" not in caption and not is_private:
        return

    msg = await message.answer("Ovozli xabar yuklab olinib, tahlil qilinmoqda...")
    group_name = message.chat.title if message.chat.title else "Shaxsiy"
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    
    downloaded_file_name = f"voice_{message.from_user.id}.ogg"
    await bot.download_file(file_path, downloaded_file_name)
    
    try:
        sample_file = client.files.upload(file=downloaded_file_name)
        response = await client.aio.models.generate_content(
            model='gemini-3.5-flash-lite',
            contents=[sample_file, prompt_template]
        )
        
        data = extract_json_from_text(response.text)
        if data:
            amount = data.get("amount", 0)
            shop = data.get("shop_name", "Noma'lum")
            products = data.get("products", "Noma'lum")
            if amount:
                add_expense(message.from_user.id, amount, products, shop, group_name=group_name)
                await msg.edit_text(f"🎙 Ovozdan aniqlandi va saqlandi!\nSumma: {amount}\nDo'kon: {shop}\nMahsulotlar: {products}")
            else:
                await msg.edit_text(f"Ovozdan o'qilgan matn:\n{response.text}")
        else:
            await msg.edit_text(f"Ovozdan xarajat aniqlanmadi. Matn:\n{response.text}")
    except Exception as e:
        print("Error processing voice:", e)
        await msg.edit_text("Ovozni tahlil qilishda xatolik yuz berdi.")
    finally:
        if os.path.exists(downloaded_file_name):
            os.remove(downloaded_file_name)

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    caption = (message.caption or "").lower()
    is_private = message.chat.type == "private"
    if "#xarajat" not in caption and "#harajat" not in caption and not is_private:
        return

    msg = await message.answer("Rasm tahlil qilinmoqda...")
    group_name = message.chat.title if message.chat.title else "Shaxsiy"
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_path = file.file_path
    
    downloaded_file_name = f"photo_{message.from_user.id}.jpg"
    await bot.download_file(file_path, downloaded_file_name)
    
    try:
        sample_file = client.files.upload(file=downloaded_file_name)
        response = await client.aio.models.generate_content(
            model='gemini-3.5-flash-lite',
            contents=[sample_file, prompt_template]
        )
        
        data = extract_json_from_text(response.text)
        if data:
            amount = data.get("amount", 0)
            shop = data.get("shop_name", "Noma'lum")
            products = data.get("products", "Rasmdan xarajat")
            if amount:
                add_expense(message.from_user.id, amount, products, shop, group_name=group_name)
                await msg.edit_text(f"🖼 Rasmdan aniqlandi va saqlandi!\nSumma: {amount}\nDo'kon: {shop}\nMahsulotlar: {products}")
            else:
                await msg.edit_text("Rasmdan xarajat summasi aniqlanmadi.")
        else:
            await msg.edit_text("Rasmdan to'g'ri xarajat ma'lumoti o'qilmadi.")
    except Exception as e:
        print("Error processing photo:", e)
        await msg.edit_text("Rasmni tahlil qilishda xatolik yuz berdi.")
    finally:
        if os.path.exists(downloaded_file_name):
            os.remove(downloaded_file_name)

from aiohttp import web

async def handle(request):
    return web.Response(text="Bot is running!")

async def web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Web server started on port {port}")

async def main():
    print("Bot ishga tushdi...")
    await web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
