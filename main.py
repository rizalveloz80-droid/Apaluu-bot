import requests, os, time
BOT = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT = os.getenv('TELEGRAM_CHAT_ID')

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT}/sendMessage"
        requests.post(url, json={"chat_id": CHAT, "text": msg, "parse_mode": "Markdown"}, timeout=20)
    except Exception as e:
        print(f"Tele Error: {e}")

try:
    # Pakai header biar ga ke-block
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get("https://api.binance.com/api/v3/ticker/24hr", headers=headers, timeout=20)
    data = r.json()
    
    # CEK KALO DI-BLOCK
    if isinstance(data, dict):
        print(f"Binance block response: {data}")
        send(f"⚠️ Binance API block: {data}\nCoba lagi 15 menit")
        exit(0)
    
    bull=[]; ont=""
    for d in data:
        s=d.get('symbol','')
        if not s.endswith('USDT'): continue
        ch=float(d.get('priceChangePercent',0))
        if s=='ONTUSDT':
            ont=f"ONTUSDT IJO {ch:.2f}% 🚀" if ch>0 else f"ONTUSDT MERAH {ch:.2f}%"
            if ch>0: bull.append(f"{s} ({ch:.2f}%) - WAJIB IJO")
        elif ch>=3.0:
            bull.append(f"{s} ({ch:.2f}%)")
    
    if not bull:
        send(f"🔍 V5.1 SCAN {time.strftime('%H:%M')} WIB - DIAM, ga ada bullish")
    else:
        txt="\n".join(bull[:20])
        send(f"🔥 *V5.1 BULLISH TRENDING*\n{ont}\n\n🚀 *IJO ONLY:*\n{txt}\n\n⏰ {time.strftime('%H:%M WIB')}")
    print("Done sent OK")
except Exception as e:
    print(f"Error: {e}")
    send(f"Bot Error: {e}")
