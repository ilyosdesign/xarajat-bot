# Xarajatlarni Boshqaruvchi Telegram Bot

Ushbu loyiha Google Gemini AI (Sun'iy Intelekt) va Telegram Bot API yordamida yaratilgan. Bot shaxsiy chatlarda yoki guruhlarda yozilgan ovozli xabarlar, rasmlar (cheklar) va matnlardan xarajatlarni o'qib oladi va hisoblab boradi. Shuningdek, ularni to'liq Excel faylida yuklab olish imkoniyatini beradi.

## Imkoniyatlari
- 🎤 **Ovozdan o'qish**: Ovozli xabarlarni eshitib, ichidan qancha xarajat va nimaga sarflanganini aniqlaydi.
- 🖼 **Cheklarni o'qish**: Rasm ko'rinishidagi kvitansiya yoki cheklarni o'qib, undagi barcha mahsulotlar va jami summani ro'yxatga oladi.
- 📝 **Matndan o'qish**: `#xarajat` yoki `#harajat` heshtegi orqali yozilgan matnlarni analiz qiladi.
- 📊 **Excel hisobot**: Barcha qilingan xarajatlarni to'g'ridan-to'g'ri Telegramning o'zida `.xlsx` formatida yuklab olish.
- 👥 **Guruhlar bilan ishlash**: Bot guruhga qo'shilganda, qaysi guruhdan xarajat yozilganligini alohida ustun qilib Excelga yozib boradi.

## O'rnatish va Ishga tushirish

1. Loyihani yuklab oling va papkaga kiring:
   ```bash
   git clone <repo-url>
   cd expense_bot
   ```
2. Kerakli kutubxonalarni o'rnating:
   ```bash
   pip install -r requirements.txt
   ```
3. `.env` faylini yarating va quyidagi kalitlarni kiriting:
   ```env
   BOT_TOKEN=telegram_botfather_token_shu_yerga
   GEMINI_API_KEY=google_ai_studio_api_kaliti_shu_yerga
   ```
4. Botni ishga tushiring:
   ```bash
   python bot.py
   ```

## Texnologiyalar
- **Python 3.10+**
- **Aiogram 3.x** - Telegram Bot uchun
- **Google GenAI** - Gemini 3.6 Flash modeli (Sun'iy intellekt tahlili uchun)
- **Pandas / Openpyxl** - Excel bilan ishlash uchun
