import requests, os, datetime, time

BOT = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('TELEGRAM_TOKEN') or os.getenv('BOT_TOKEN')
CHAT = os.getenv('TELEGRAM_CHAT_ID') or os.getenv('CHAT_ID') or os.getenv('TELEGRAM_CHAT')

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT}/sendMessage", data={"chat_id": CHAT, "text": msg})
    except: pass

def get_ema(prices, period):
    k = 2 / (period + 1)
    ema = prices[0]
    for p in prices[1:]:
        ema = p * k + ema * (1-k)
    return ema

EXCLUDE = {"BTC","HYPE","PEPE","PENGU","SOL","ETH","BNB","XRP","DOGE","SHIB","ADA","AVAX","DOT","LINK","TRX","MATIC","LTC","BCH","ETC"}

try:
    r = requests.get("https://indodax.com/api/tickers", timeout=15).json()
    tickers = r.get('tickers', {})

    candidates = []
    for pair, d in tickers.items():
        if not pair.endswith('_idr'): continue
        try:
            vol_mn = float(d.get('vol_idr',0))/1_000_000
            if vol_mn < 20: continue
            last = float(d['last'])
            if last < 50: continue
            coin = pair.replace('_idr','').upper()
            if coin in EXCLUDE: continue
            candidates.append((vol_mn, pair, coin, float(d['low']), float(d['high']), last, vol_mn))
        except: continue

    candidates = sorted(candidates, key=lambda x: x[0], reverse=True)[:40]

    serok = []
    now = int(time.time())
    from_ts = now - (30 * 3600)

    for vol_mn, pair, coin, low, high, last, v in candidates:
        try:
            url = f"https://indodax.com/tradingview/history?symbol={coin}IDR&resolution=60&from={from_ts}&to={now}"
            ch = requests.get(url, timeout=8).json()
            closes = ch.get('c', [])
            if len(closes) < 22: continue

            ema9 = get_ema(closes[-9:], 9)
            ema21 = get_ema(closes[-21:], 21)

            if ema9 < ema21: continue # trend turun skip

            jarak_low = (last-low)/low*100 if low else 0
            turun_high = (high-last)/high*100 if high else 0

            if turun_high < 0.5: continue
            if turun_high > 6: continue

            hrp = f"Rp{last:,.0f}".replace(',', '.')
            sl = last * 0.98
            tp = last * 1.04
            sl_hrp = f"Rp{sl:,.0f}".replace(',', '.')
            tp_hrp = f"Rp{tp:,.0f}".replace(',', '.')

            # V7.1 INSTANT ENTRY - EMA9 di atas EMA21 + koreksi
            if 0.5 <= jarak_low <= 8.0 and 0.8 <= turun_high <= 5.5 and vol_mn > 25:
                serok.append(f"🎯 {coin} {hrp} EMA9 {ema9:.0f}>21 {ema21:.0f} -{turun_high:.1f}% V:{vol_mn:.0f}jt SL:{sl_hrp} TP:{tp_hrp}")

        except:
            continue

    jam = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%H:%M WIB")
    msg = f"🤖 V7.1 INSTANT {jam}\nEMA9>EMA21 + Vol 25jt+\n\n"
    if serok:
        msg += f"🎯 ENTRY HARI INI:\n" + "\n".join(serok[:8])
        print(msg)
        send(msg)
    else:
        print("DIAM - Ga ada EMA9>21")
        send(f"🤖 V7.1 {jam}\nDIAM - Vol 25jt ga ada yang EMA9>21")

except Exception as e:
    send(f"Error V7.1: {e}")
