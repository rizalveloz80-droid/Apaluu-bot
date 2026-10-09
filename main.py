import os, asyncio
from telegram import Bot
TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = "213453765"
async def main():
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text="🔥 APALUU BOT AKTIF MIN! Repo siap!")
asyncio.run(main())
