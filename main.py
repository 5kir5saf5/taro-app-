import asyncio, os, json
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
import g4f

TOKEN = 'ТВОЙ_ТОКЕН' # Получи у @BotFather
WEB_APP_URL = 'ТВОЯ_ССЫЛКА_ОТ_VERCEL'

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(m: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🔮 Открыть Таро", web_app=WebAppInfo(url=WEB_APP_URL))
    ]])
    await m.answer("Добро пожаловать! Жми кнопку ниже, чтобы начать расклад.", reply_markup=kb)

@dp.message(lambda m: m.web_app_data)
async def get_data(m: types.Message):
    data = json.loads(m.web_app_data.data)
    question = data['question']
    cards = ", ".join(data['cards'])
    
    msg = await m.answer("⌛ Нейросеть расшифровывает знаки...")
    
    prompt = f"Ты эксперт Таро. Вопрос: {question}. Карты: {cards}. Дай краткую трактовку."
    try:
        res = await g4f.ChatCompletion.create_async(model="gpt-3.5-turbo", messages=[{"role":"user","content":prompt}])
        await msg.edit_text(f"📝 Трактовка:\n\n{res}")
    except:
        await msg.edit_text("Ошибка нейросети. Попробуй позже.")

async def main():
    # Заглушка для порта Render
    from aiohttp import web
    app = web.Application(); runner = web.AppRunner(app); await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.getenv("PORT", 8080))).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
