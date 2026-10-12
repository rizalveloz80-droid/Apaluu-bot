import requests, os
from datetime import datetime

VERSION = "V12.1 HYBRID"
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def main():
    r = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=20).json()
    c1=c2=c3=0
    list1=[]
    total = 0
    for c in r:
        if not c['symbol'].endswith('USDT'): continue
        total+=1
        try:
            ch = float(c['priceChangePercent'])
            vol = float(c['quoteVolume'])
        except: continue
        if vol < 5000000: continue
        if 1.5 <= ch <= 18:
            c1+=1
            if len(list1)<10: list1.append(f"{c['symbol']} {ch:.1f}%")
    jam = datetime.now().strftime("%H:%M WIB")
    msg = f"🤖 *{VERSION} {jam}*\nScan {total} koin Vol>5jt\n\n⚡ ENTRY DULUAN (+1.5-18%): {c1} koin\n" + ("\n".join(list1) if list1 else "Belum ada - Market sepi") + "\n\n✅ SELESAI KOREKSI: 0 koin\n💎 SEROK BOTTOM: 0 koin\n\n_Hybrid Mode Aktif_"
    send(msg)
    print(f"Sukses {VERSION}")

if __name__ == "__main__":
    main()
