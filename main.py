import requests
import os
import time
from datetime import datetime

# CONFIG V12.1 HYBRID
VERSION = "V12.1 HYBRID"
MIN_PUMP = 1.5
MAX_PUMP = 18.0
MIN_VOL = 5000000  # 5jt volume minimal

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_tele(msg):
    if not TOKEN or not CHAT_ID:
        print("Token/ChatID kosong!")
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"Gagal kirim tele: {e}")

def scan():
    print(f"[{VERSION}] Scanning...")
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=15).json()
        
        loose = []
        koreksi = []
        serok = []
        
        for c in r:
            symbol = c['symbol']
            if not symbol.endswith('USDT'): continue
            if 'BULL' in symbol or 'BEAR' in symbol: continue
            
            try:
                change = float(c['priceChangePercent'])
                vol = float(c['quoteVolume'])
                price = float(c['lastPrice'])
            except:
                continue

            if vol < MIN_VOL: continue

            # V12.1 HYBRID LOGIC
            if MIN_PUMP <= change <= MAX_PUMP:
                if change < 5:
                    serok.append(f"{symbol} ({change:.1f}%)")
                elif change < 12:
                    koreksi.append(f"{symbol} ({change:.1f}%)")
                else:
                    loose.append(f"{symbol} ({change:.1f}%)")

        total_scan = len([x for x in r if 'USDT' in x['symbol']])
        
        jam = datetime.now().strftime("%H:%M WIB")
        
        msg = f"""*{VERSION} - {jam}*
Scan {total_scan} koin

🚀 *ENTRY DULUAN: {len(loose)} koin*
{chr(10).join(loose[:10]) if loose else "Belum ada"}

📉 *SELESAI KOREKSI: {len(koreksi)} koin*
{chr(10).join(koreksi[:10]) if koreksi else "Belum ada"}

💰 *SEROK BOTTOM: {len(serok)} koin*
{chr(10).join(serok[:10]) if serok else "Belum ada"}

_Min: +{MIN_PUMP}% Max: +{MAX_PUMP}%_
"""
        send_tele(msg)
        print("Sukses kirim tele")
        
    except Exception as e:
        send_tele(f"*{VERSION} ERROR:* {e}")
        print(e)

if __name__ == "__main__":
    scan()
