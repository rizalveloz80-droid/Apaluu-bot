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

    # FILTER AWAL VOL 30jt dulu biar ga berat
    candidates = []
    for pair, d in tickers.items():
        if not pair.endswith('_idr'): continue
        try:
            vol_mn = float(d.get('vol_idr',0))/1_000_000
            if vol_mn < 30: continue
            last = float(d['last'])
            if last < 50: continue
            coin = pair.replace('_idr','').upper()
            if coin in EXCLUDE: continue
            candidates.append((vol_mn, pair, coin, float(d['low']), float(d['high']), last, vol_mn))
        except: continue

    # Ambil 40 coin paling rame vol nya aja biar ga timeout
    candidates = sorted(candidates, key=lambda x: x[0], reverse=True)[:40]

    serok = []
    koreksi = []

    now = int(time.time())
    from_ts = now - (30 * 3600) # 30 jam terakhir buat EMA21

    for vol_mn, pair, coin, low, high, last, v in candidates:
        try:
            # API TradingView Indodax buat candle 1 jam
            url = f"https://indodax.com/tradingview/history?symbol={coin}IDR&resolution=60&from={from_ts}&to={now}"
            ch = requests.get(url, timeout=8).json()
            closes = ch.get('c', [])
            if len(closes) < 22: continue

            ema9 = get_ema(closes[-9:], 9)
            ema21 = get_ema(closes[-21:], 21)
            ema9_prev = get_ema(closes[-10:-1], 9)
            ema21_prev = get_ema(closes[-22:-1], 21)

            # CROSSOVER ASLI: EMA9 motong EMA21 ke atas
            golden_cross = ema9_prev <= ema21_prev and ema9 > ema21
            death_cross = ema9_prev >= ema21_prev and ema9 < ema21
            if death_cross: continue # kalo mau mati skip

            jarak_low = (last-low)/low*100 if low else 0
            turun_high = (high-last)/high*100 if high else 0

            # Anti Pucuk
            if turun_high < 0.5: continue
            if turun_high > 6: continue

            hrp = f"Rp{last:,.0f}".replace(',', '.')
            sl = last * 0.98
            tp = last * 1.04
            sl_hrp = f"Rp{sl:,.0f}".replace(',', '.')
            tp_hrp = f"Rp{tp:,.0f}".replace(',', '.')

            # MODE 1: GOLDEN CROSS + VOL 40jt = SEROK BAWAH
            if golden_cross and 0.5 <= jarak_low <= 5.0 and 1.0 <= turun_high <= 4.0 and vol_mn > 40:
                serok.append(f"🎯 {coin} GC! {hrp} EMA9>{ema21:.0f} -{turun_high:.1f}% V:{vol_mn:.0f}jt SL:{sl_hrp} TP:{tp_hrp}")

            # MODE 2: EMA9 masih di atas EMA21 + koreksi = SELESAI KOREKSI
            elif ema9 > ema21 and 1.0 <= jarak_low <= 7.0 and 0.5 <= turun_high <= 5.5 and vol_mn > 30:
                koreksi.append(f"✅ {coin} {hrp} EMA9>21 -{turun_high:.1f}% V:{vol_mn:.0f}jt")

        except:
            continue

    jam = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%H:%M WIB")
    msg = f"🤖 V7 EMA CROSS {jam}\nEMA9 x EMA21 Asli + Vol 40/30\n\n"
    if serok:
        msg += f"🎯 GOLDEN CROSS (40jt+):\n" + "\n".join(serok[:6]) + "\n\n"
    if koreksi:
        msg += f"📈 TREND NAIK KOREKSI (30jt+):\n" + "\n".join(koreksi[:6]) + "\n\n"

    if serok or koreksi:
        print(msg)
        send(msg)
    else:
        print("DIAM - Ga ada Golden Cross hari ini")
        send(f"🤖 V7 EMA {jam}\nDIAM - Ga ada GC EMA9>21\nVol 40 coin teratas dicek, trend lagi turun semua")

except Exception as e:
    send(f"Error V7: {e}")
