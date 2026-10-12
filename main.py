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

EXCLUDE = {"BTC","SOL","ETH","BNB","XRP","DOGE","SHIB","PEPE"}

try:
    r = requests.get("https://indodax.com/api/tickers", timeout=15).json()
    tickers = r.get('tickers', {})

    list_all = []
    for pair, d in tickers.items():
        if not pair.endswith('_idr'): continue
        try:
            vol_mn = float(d.get('vol_idr',0))/1_000_000
            if vol_mn < 25: continue
            last = float(d['last'])
            coin = pair.replace('_idr','').upper()
            if coin in EXCLUDE: continue
            change = float(d.get('percent',0)) if 'percent' in d else 0
            list_all.append((vol_mn, pair, coin, float(d['low']), float(d['high']), last, vol_mn, change))
        except: continue

    list_all = sorted(list_all, key=lambda x: x[0], reverse=True)[:60]

    serok = []
    ijo = []
    now = int(time.time())
    from_ts = now - (30 * 3600)

    for vol_mn, pair, coin, low, high, last, v, change in list_all:
        try:
            # IJO OVERBOUGHT DETECTOR - MASIH ADA MIN!
            if change >= 15:
                hrp = f"Rp{last:,.0f}".replace(',', '.')
                ijo.append(f"🚀 {coin} {hrp} +{change:.1f}% JANGAN KEJAR (tunggu koreksi)")
                continue

            url = f"https://indodax.com/tradingview/history?symbol={coin}IDR&resolution=60&from={from_ts}&to={now}"
            ch = requests.get(url, timeout=8).json()
            closes = ch.get('c', [])
            if len(closes) < 22: continue
            ema9 = get_ema(closes[-9:], 9)
            ema21 = get_ema(closes[-21:], 21)
            if ema9 < ema21: continue

            jarak_low = (last-low)/low*100 if low else 0
            turun_high = (high-last)/high*100 if high else 0
            hrp = f"Rp{last:,.0f}".replace(',', '.')
            sl = f"Rp{last*0.97:,.0f}".replace(',', '.')
            tp = f"Rp{last*1.05:,.0f}".replace(',', '.')

            if 0.5 <= jarak_low <= 10 and 0.5 <= turun_high <= 5:
                serok.append((vol_mn, f"🎯 {coin} {hrp} -{turun_high:.1f}% V:{vol_mn:.0f}jt SL:{sl} TP:{tp}"))

        except: continue

    jam = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%H:%M WIB")
    msg = f"🤖 V7.4 COMBO {jam}\n"

    if serok:
        serok = sorted(serok, key=lambda x: x[0], reverse=True)[:5]
        msg += "\n🎯 SEROK KOREKSI:\n" + "\n".join([x[1] for x in serok])

    if ijo:
        msg += "\n\n🚀 IJO OVERBOUGHT (Masih ada min!):\n" + "\n".join(ijo[:5])

    if not serok and not ijo:
        msg += "\nDIAM TOTAL - Bear ekstrim, tunggu jam 10:00 WIB"

    print(msg)
    send(msg)

except Exception as e:
    send(f"Error V7.4: {e}")
