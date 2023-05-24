from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message
from aiogram.types import BotCommand
import asyncio
from parser import PayeerParser, KucoinParser, BinanceParser, Analytics

import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

API_TOKEN: str = os.getenv("API_TOKEN")

# Создаем объекты бота и диспетчера
bot: Bot = Bot(token=API_TOKEN)
dp: Dispatcher = Dispatcher(bot)
p = PayeerParser()
a = Analytics()
k = KucoinParser()
b = BinanceParser()


@dp.message_handler(commands=["start"])
async def process_start_command(message: Message):
    await message.answer('Поиск арбитражных сделок запущен. Когда сделка будет найдена, мы пришлём вам сообщение')
    global chat_id
    chat_id = message.chat.id
    asyncio.create_task(search_arb(bot))


@dp.message_handler(commands=['help'])
async def process_help_command(message: Message):
    await message.answer('Напиши мне что-нибудь и в ответ '
                         'я пришлю тебе твое сообщение')


@dp.message_handler(commands=['kucoin_prices'])
async def get_kucoin_prices(message: Message):
    await message.answer(text=k.print_prices_from_kucoin())


@dp.message_handler(commands=['payeer_prices'])
async def get_payeer_prices(message: Message):
    await message.answer(text=p.print_prices_from_payeer())


@dp.message_handler(commands=['binance_prices'])
async def get_binance_prices(message: Message):
    await message.answer(text=b.print_prices_from_binance())


@dp.message_handler(commands=['analytics'])
async def analytics(message: Message):
    await message.answer(text=a.print_message())


@dp.message_handler()
async def send_echo(message: Message):
    await message.reply(text=message.text)


async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/help',
                   description='Справка по работе бота'),
        BotCommand(command='/payeer_prices',
                   description='Котировки с биржи Payeer'),
        BotCommand(command='/kucoin_prices',
                   description='Котировки с биржи Kucoin'),
        BotCommand(command='/binance_prices',
                   description='Котировки с биржи Binance'),
        BotCommand(command='/analytics',
                   description='Анализ котировок')
    ]

    await bot.set_my_commands(main_menu_commands)


async def search_arb(bot: Bot):
    coins = ["BTC", "ETH", "LTC", "DASH", "XRP", "BCH"]
    while True:
        maxDiff = 0
        for coin in coins:
            diff = a.checkDiff(b=b.get_all_prices_from_binance(), p=p.get_all_prices_from_payeer(), k=k.get_all_prices_from_kucoin(), coin=coin)
            if diff > 1.02 and diff > maxDiff:
                maxDiff = diff
        if maxDiff > 1.025:
            await bot.send_message(text=a.print_message(), chat_id=chat_id)
            await asyncio.sleep(3600)
        await asyncio.sleep(60)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
