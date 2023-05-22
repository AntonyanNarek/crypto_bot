from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from parser import PayeerParser, KucoinParser, BinanceParser, Analytics

API_TOKEN: str = '5910465654:AAH0FWSi70xqgRvDUNqzALhv-pSR4s_Vol8'

# Создаем объекты бота и диспетчера
bot: Bot = Bot(token=API_TOKEN)
dp: Dispatcher = Dispatcher()
p = PayeerParser()
a = Analytics()
k = KucoinParser()
b = BinanceParser()

# Этот хэндлер будет срабатывать на команду "/start"
@dp.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    await message.answer('Привет!\nМеня зовут Эхо-бот!\nНапиши мне что-нибудь')


@dp.message(Command(commands=['help']))
async def process_help_command(message: Message):
    await message.answer('Напиши мне что-нибудь и в ответ '
                         'я пришлю тебе твое сообщение')


@dp.message(Command(commands=['kucoinPrices']))
async def get_kucoin_prices(message: Message):
    await message.answer(text=k.print_prices())


@dp.message(Command(commands=['payeerPrices']))
async def get_payeer_prices(message: Message):
    await message.answer(text=p.print_prices())


@dp.message(Command(commands=['priceBTC']))
async def get_ticker(message: Message):
    await message.answer(text=p.get_price("BTC_USD"))


@dp.message(Command(commands=['binancePrices']))
async def get_binance_prices(message: Message):
    await message.answer(text=b.print_prices())


@dp.message(Command(commands=['analytics']))
async def analytics(message: Message):
    await message.answer(text=a.print_message())


@dp.message()
async def send_echo(message: Message):
    await message.reply(text=message.text)


if __name__ == '__main__':
    dp.run_polling(bot)