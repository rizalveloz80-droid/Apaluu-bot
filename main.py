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

try:
    r = requests.get("https://indodax.com/api/tickers", timeout=20).json()
    tickers = r.get('tickers', {})

    all_coins = []
    for pair, d in tickers.items():
        if not pair.endswith('_idr'): continue
        try:
            vol_mn = float(str(d.get('vol_idr','0')))/1_000_000
            if vol_mn < 50: continue # Vol 50jt+ biar semua koin berpotensi masuk
            last = float(d['last'])
            low = float(d['low'])
            high = float(d['high'])
            if last < 5: continue
            coin = pair.replace('_idr','').upper()
            if coin in {"BTC","ETH","USDT","USDC"}: continue
            chg = ((last-low)/low*100) if low else 0
            all_coins.append((chg, vol_mn, coin, last, low, high))
        except: continue

    all_coins = sorted(all_coins, key=lambda x: x[0], reverse=True)[:40]

    early = []
    breakout = []
    overbought = []

    now = int(time.time())
    from_ts = now - (40*3600)

    for chg, vol_mn, coin, last, low, high in all_coins:
        try:
            url = f"https://indodax.com/tradingview/history?symbol={coin}IDR&resolution=15&from={from_ts}&to={now}"
            hist = requests.get(url, timeout=8).json()
            closes = hist.get('c', [])
            if len(closes) < 22: continue
            ema9 = get_ema(closes[-9:], 9)
            ema21 = get_ema(closes[-21:], 21)
            ema9_prev = get_ema(closes[-10:-1], 9)
            ema21_prev = get_ema(closes[-22:-1], 21)
            jarak_ema9 = ((last-ema9)/ema9*100) if ema9 else 0
            hrp = f"Rp{last:,.0f}".replace(',', '.')

            # UNIVERSAL LOGIC - BERLAKU UNTUK KOIN APAPUN
            if 3 <= chg <= 14 and ema9_prev < ema21_prev and ema9 > ema21:
                early.append(f"⚡ {coin} {hrp} +{chg:.1f}% GOLDEN CROSS baru! V:{vol_mn:.0f}jt | ENTRY SEBELUM TRENDING")
            elif 15 <= chg <= 29 and ema9 > ema21:
                breakout.append(f"🔥 {coin} {hrp} +{chg:.1f}% Breakout Vol:{vol_mn:.0f}jt | IKUTI TREN, SL 4%")
            elif chg >= 30:
                overbought.append(f"⚠️ {coin} {hrp} +{chg:.1f}% OVERBOUGHT Jarak EMA9 +{jarak_ema9:.1f}% | JANGAN FOMO")

        except: continue

    jam = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%H:%M WIB")
    msg = f"🤖 V9.1 UNIVERSAL HUNTER {jam}\nScan {len(all_coins)} koin Vol>50jt\n"

    if early:
        msg += "\n🎯 ENTRY DULUAN (sblm trending, koin apapun):\n" + "\n".join(early[:5])
    else:
        msg += "\n🎯 ENTRY DULUAN: Belum ada golden cross baru"

    if breakout:
        msg += "\n\n🔥 LAGI BREAKOUT (koin apapun yang lagi naik):\n" + "\n".join(breakout[:5])

    if overbought:
        msg += "\n\n⚠️ UDAH TERBANG TINGGI (jangan kejar):\n" + "\n".join(overbought[:5])

    if not early and not breakout and not overbought:
        msg += "\nDIAM - Market lagi sepi, ga ada koin +3%"

    print(msg)
    send(msg)

except Exception as e:
    send(f"Error V9.1: {e}")
