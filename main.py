
import os, asyncio
from telegram import Bot

TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = "213453765"

async def main():
    bot = Bot(token=TOKEN)
    print("BOT APALUU NYALA MIN!")
    while True:
        try:
            await bot.send_message(chat_id=CHAT_ID, text="Apaluu bot aktif min ✅")
            print("Pesan terkirim!")
        except Exception as e:
            print(f"Error: {e}")
        await asyncio.sleep(300)

asyncio.run(main())
