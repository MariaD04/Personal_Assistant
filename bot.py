import os

import asyncio
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv

from agent import run_agent

load_dotenv()

bot = Bot(token=os.environ["BOT_TOKEN"])
dp = Dispatcher()


@dp.message()
async def start_handler(message: types.Message):
    """
    Обрабатывает любое сообщение от пользователя телеграмм-боту

    Args:
        message (Message): объект сообщения от пользователя

    Returns:
        None
    """
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    print("start agent")
    response = await run_agent(message)
    print("agent is done")
    await message.answer(response)


async def main():
    """
    Запуск бота

    Returns:
        None
    """
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
