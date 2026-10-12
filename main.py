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
            if vol_mn < 40: continue
            last = float(d['last'])
            low = float(d['low'])
            if last < 5: continue
            coin = pair.replace('_idr','').upper()
            if coin in {"BTC","ETH","USDT","USDC"}: continue
            chg = ((last-low)/low*100) if low else 0
            all_coins.append((chg, vol_mn, coin, last, low))
        except: continue

    # JANGAN SORT DULU, BIAR YANG +3% KEDETEK!
    early = []
    trending = []
    now = int(time.time())
    from_ts = now - (40*3600)

    # Scan 80 koin random vol gede, bukan cuma top gainer
    for chg, vol_mn, coin, last, low in sorted(all_coins, key=lambda x: x[1], reverse=True)[:80]:

        if chg < 2: continue
        try:
            url = f"https://indodax.com/tradingview/history?symbol={coin}IDR&resolution=15&from={from_ts}&to={now}"
            hist = requests.get(url, timeout=8).json()
            closes = hist.get('c', [])
            if len(closes) < 22: continue
            ema9 = get_ema(closes[-9:], 9)
            ema21 = get_ema(closes[-21:], 21)
            jarak = ((ema9-ema21)/ema21*100) if ema21 else 0
            hrp = f"Rp{last:,.0f}".replace(',', '.')

            # LOGIKA FIX
            if 2 <= chg <= 14 and ema9 > ema21 and jarak <= 3 and vol_mn > 40:
                early.append((vol_mn, f"⚡ EARLY {coin} {hrp} +{chg:.1f}% EMA9>21 Vol:{vol_mn:.0f}jt - ENTRY SEBELUM TRENDING"))
            elif chg >= 15:
                trending.append((chg, f"🚀 {coin} +{chg:.0f}% {hrp} V:{vol_mn:.0f}jt"))

        except: continue

    jam = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%H:%M WIB")
    msg = f"🤖 V9.2 UNIVERSAL FIX {jam}\nScan 80 koin Vol>40jt (by Volume)\n"

    if early:
        msg += "\n🎯 ENTRY DULUAN (koin apapun +2-14%):\n" + "\n".join([x[1] for x in sorted(early, reverse=True)[:6]])
    else:
        msg += "\n🎯 ENTRY DULUAN: Belum ada yang +2-14% & EMA baru naik - tunggu 15 menit"

    if trending:
        trending = sorted(trending, reverse=True)[:5]
        msg += "\n\n🚀 UDAH TRENDING (jangan kejar, kayak WORMHOLE +103% tadi):\n" + "\n".join([x[1] for x in trending])

    if not early and not trending:
        msg += "\nMarket sepi total"

    print(msg)
    send(msg)

except Exception as e:
    send(f"Error V9.2: {e}")
