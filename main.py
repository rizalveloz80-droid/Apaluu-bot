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
            if vol_mn < 30: continue
            last = float(d['last'])
            low = float(d['low'])
            high = float(d['high'])
            if last < 20: continue
            coin = pair.replace('_idr','').upper()
            if coin in {"BTC","ETH","USDT","BNB","SOL"}: continue
            chg = ((last-low)/low*100) if low else 0
            all_coins.append((chg, vol_mn, coin, last, low, high))
        except: continue

    # --- MODE EARLY ---
    early = []
    now = int(time.time())
    from_ts = now - (30*3600)

    for chg, vol_mn, coin, last, low, high in all_coins:
        # INI KUNCINYA MIN: sebelum trending itu chg masih 3-12%
        if not (3 <= chg <= 12): continue
        try:
            url = f"https://indodax.com/tradingview/history?symbol={coin}IDR&resolution=60&from={from_ts}&to={now}"
            ch = requests.get(url, timeout=8).json()
            closes = ch.get('c', [])
            if len(closes) < 22: continue
            ema9 = get_ema(closes[-9:], 9)
            ema21 = get_ema(closes[-21:], 21)
            if ema9 < ema21: continue
            jarak_ema = (ema9-ema21)/ema21*100
            turun_high = (high-last)/high*100 if high else 0
            # EMA baru nyilang + masih deket high
            if 0 <= jarak_ema <= 2.5 and turun_high < 7:
                hrp = f"Rp{last:,.0f}".replace(',', '.')
                early.append((chg, vol_mn, f"⚡ EARLY {coin} {hrp} +{chg:.1f}% EMA baru nyilang V:{vol_mn:.0f}jt - Beli sekarang sblm trending! SL 3%"))
        except: continue

    # Buat perbandingan, tetep kasih tau yang udah trending biar lu ga FOMO
    gainers = sorted([c for c in all_coins if c[0] >= 15], key=lambda x: x[0], reverse=True)[:3]

    jam = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%H:%M WIB")
    msg = f"🤖 V8 EARLY {jam}\nCari +3-12% sblm Trending\n"

    if early:
        early = sorted(early, key=lambda x: x[1], reverse=True)[:5]
        msg += "\n⚡ ENTRY SEBELUM TRENDING (beli sekarang!):\n" + "\n".join([x[2] for x in early])
    else:
        msg += "\n⚡ EARLY: Belum ada yang siap terbang, tunggu 15 menit lagi"

    if gainers:
        msg += "\n\n🚀 UDAH TRENDING (jangan kejar):\n"
        for chg, vol_mn, coin, last, low, high in gainers:
            hrp = f"Rp{last:,.0f}".replace(',', '.')
            msg += f"{coin} +{chg:.0f}% {hrp}\n"

    print(msg)
    send(msg)

except Exception as e:
    send(f"Error V8: {e}")
