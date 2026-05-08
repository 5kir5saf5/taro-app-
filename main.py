import asyncio, os, json, datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
import g4f

TOKEN = '8409716817:AAHmmfy7anmiTdbPLzv8JI3m83bru0x6UJE'
WEB_APP_URL = 'ТВОЯ_ССЫЛКА_ОТ_VERCEL'
PAYMENT_LINK = 'https://yoomoney.ru/to/твой_номер_счета' # Ссылка на оплату

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Словарь для хранения даты последнего бесплатного расклада {user_id: date}
user_limits = {}

@dp.message(CommandStart())
async def start(m: types.Message):
    # Кнопка для открытия Таро
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🔮 Открыть Таро", web_app=WebAppInfo(url=WEB_APP_URL))
    ]])
    await m.answer("Добро пожаловать! Жми кнопку ниже, чтобы начать.", reply_markup=kb)

@dp.message(lambda m: m.web_app_data)
async def get_data(m: types.Message):
    user_id = m.from_user.id
    today = datetime.date.today()

    # ПРОВЕРКА ЛИМИТА
    # Если юзер уже гадал сегодня
    if user_id in user_limits and user_limits[user_id] == today:
        # Создаем кнопку оплаты
        pay_kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="💳 Оплатить расклад (100₽)", url=PAYMENT_LINK)
        ]])
        
        await m.answer(
            "🛑 Лимит исчерпан!\n\n"
            "Бесплатный расклад доступен 1 раз в сутки. "
            "Чтобы получить еще один сейчас, пожалуйста, оплатите услугу по ссылке ниже.",
            reply_markup=pay_kb
        )
        return # Останавливаем код, трактовку не даем

    # Если лимит не превышен — работаем дальше
    data = json.loads(m.web_app_data.data)
    question = data['question']
    cards = ", ".join(data['cards'])
    
    msg = await m.answer("⌛ Нейросеть расшифровывает знаки...")
    
    prompt = f"Ты эксперт Таро. Вопрос: {question}. Карты: {cards}. Дай краткую трактовку."
    try:
        res = await g4f.ChatCompletion.create_async(model="gpt-3.5-turbo", messages=[{"role":"user","content":prompt}])
        await msg.edit_text(f"📝 Твоя бесплатная трактовка на сегодня:\n\n{res}")
        
        # ЗАПИСЫВАЕМ, ЧТО ЮЗЕР ИСПОЛЬЗОВАЛ ЛИМИТ
        user_limits[user_id] = today
        
    except:
        await msg.edit_text("Ошибка нейросети. Попробуй позже.")

async def main():
    from aiohttp import web
    app = web.Application(); runner = web.AppRunner(app); await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.getenv("PORT", 8080))).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
