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
            if vol_mn < 35: continue
            last = float(d['last'])
            low = float(d['low'])
            high = float(d['high'])
            if last < 5: continue
            coin = pair.replace('_idr','').upper()
            if coin in {"BTC","ETH","USDT","USDC"}: continue
            chg = ((last-low)/low*100) if low else 0
            drop_high = ((high-last)/high*100) if high else 0
            near_low = ((last-low)/low*100) if low else 0
            all_coins.append((vol_mn, chg, coin, last, low, high, drop_high, near_low))
        except: continue

    early = []
    trending = []
    selesai_koreksi = []
    serok_bottom = []

    now = int(time.time())
    from_ts = now - (40*3600)

    # Scan 100 koin by volume biar semua ketangkep
    for vol_mn, chg, coin, last, low, high, drop_high, near_low in sorted(all_coins, key=lambda x: x[0], reverse=True)[:100]:
        try:
            url = f"https://indodax.com/tradingview/history?symbol={coin}IDR&resolution=15&from={from_ts}&to={now}"
            hist = requests.get(url, timeout=8).json()
            closes = hist.get('c', [])
            if len(closes) < 22: continue
            ema9 = get_ema(closes[-9:], 9)
            ema21 = get_ema(closes[-21:], 21)
            ema9_prev = get_ema(closes[-10:-1], 9)
            ema21_prev = get_ema(closes[-22:-1], 21)
            hrp = f"Rp{last:,.0f}".replace(',', '.')

            # 1. ENTRY DULUAN
            if 2 <= chg <= 14 and ema9 > ema21:
                early.append((vol_mn, f"⚡ {coin} {hrp} +{chg:.1f}% Vol:{vol_mn:.0f}jt EMA naik"))

            # 2. UDAH TRENDING
            if chg >= 15:
                trending.append((chg, f"🚀 {coin} +{chg:.0f}% {hrp} V:{vol_mn:.0f}jt"))

            # 3. SELESAI KOREKSI - INI YANG HILANG TADI MIN!
            if 2 <= drop_high <= 8 and ema9 > ema21 and 1 <= near_low <= 10 and chg >= 3:
                selesai_koreksi.append((vol_mn, f"✅ {coin} {hrp} turun -{drop_high:.1f}% dari high, dekat low +{near_low:.1f}% Vol:{vol_mn:.0f}jt - SEROK KOREKSI SELESAI"))

            # 4. SEROK BOTTOM - DARI BAWAH BANGET
            if near_low <= 4 and drop_high >= 5 and ema9_prev < ema21_prev and ema9 >= ema21*0.998:
                serok_bottom.append((vol_mn, f"💎 {coin} {hrp} BOTTOM! Di low +{near_low:.1f}% drop -{drop_high:.1f}% Vol:{vol_mn:.0f}jt - SEROK DARI BAWAH"))

        except: continue

    jam = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%H:%M WIB")
    msg = f"🤖 V10 COMPLETE {jam}\nScan 100 koin Vol>35jt\n"

    if early:
        msg += "\n⚡ ENTRY SEBELUM TRENDING:\n" + "\n".join([x[1] for x in sorted(early, reverse=True)[:4]])
    else:
        msg += "\n⚡ ENTRY DULUAN: Belum ada"

    if selesai_koreksi:
        msg += "\n\n✅ SELESAI KOREKSI (siap naik lagi):\n" + "\n".join([x[1] for x in sorted(selesai_koreksi, reverse=True)[:4]])

    if serok_bottom:
        msg += "\n\n💎 SEROK BOTTOM (dari bawah):\n" + "\n".join([x[1] for x in sorted(serok_bottom, reverse=True)[:4]])

    if trending:
        msg += "\n\n🚀 UDAH TRENDING (jangan kejar):\n" + "\n".join([x[1] for x in sorted(trending, reverse=True)[:4]])

    if not early and not selesai_koreksi and not serok_bottom and not trending:
        msg += "\nMarket sepi total - tunggu 15 menit"

    print(msg)
    send(msg)

except Exception as e:
    send(f"Error V10: {e}")
