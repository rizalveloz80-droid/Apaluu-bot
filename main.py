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
            if vol_mn < 10: continue
            last = float(d['last'])
            if last < 50: continue
            coin = pair.replace('_idr','').upper()
            if coin in EXCLUDE: continue
            candidates.append((vol_mn, pair, coin, float(d['low']), float(d['high']), last, vol_mn))
        except: continue

    candidates = sorted(candidates, key=lambda x: x[0], reverse=True)[:60]

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

            jarak_ema = ((ema9-ema21)/ema21*100) # minus = masih di bawah
            turun_high = (high-last)/high*100 if high else 0

            hrp = f"Rp{last:,.0f}".replace(',', '.')
            sl = last * 0.97
            tp = last * 1.06
            sl_hrp = f"Rp{sl:,.0f}".replace(',', '.')
            tp_hrp = f"Rp{tp:,.0f}".replace(',', '.')

            # MODE BEAR MARKET: cari yang paling deket mau GC
            # EMA9 masih di bawah tapi selisih < 1% = mau nyilang!
            if -2.0 <= jarak_ema <= 2.0 and turun_high < 8:
                status = "GOLDEN" if jarak_ema >=0 else f"DEKET GC {jarak_ema:.2f}%"
                serok.append((jarak_ema, vol_mn, f"🎯 {coin} {hrp} {status} -{turun_high:.1f}% V:{vol_mn:.0f}jt SL:{sl_hrp} TP:{tp_hrp}"))

        except:
            continue

    jam = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%H:%M WIB")

    if serok:
        serok = sorted(serok, key=lambda x: x[0], reverse=True)
        pesan = [x[2] for x in serok[:8]]
        msg = f"🤖 V7.3 REVERSAL {jam}\nBEAR MARKET - Cari Deket GC\n\n🎯 SIAP BALIK ARAH:\n" + "\n".join(pesan)
        print(msg)
        send(msg)
    else:
        print("DIAM TOTAL - Bear ekstrim")
        send(f"🤖 V7.3 {jam}\nDIAM TOTAL - Bear ekstrim, semua EMA jauh di bawah, tunggu jam 10:00 WIB")

except Exception as e:
    send(f"Error V7.3: {e}")
