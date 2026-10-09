Ini min kode lengkapnya, tinggal *TEKAN LAMA > COPY > PASTE* di kotak hitam gede itu:
import os
import asyncio
from telegram import Bot

TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = "213453765"

async def main():
    bot = Bot(token=TOKEN)
    text = "🔥 APALUU BOT AKTIF MIN!\n\nID 213453765 konek!\nRepo Apaluu-bot siap!"
    await bot.send_message(chat_id=CHAT_ID, text=text)

asyncio.run(main())
