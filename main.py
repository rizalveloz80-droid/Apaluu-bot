import requests, os

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('TELEGRAM_TOKEN') or os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID') or os.getenv('CHAT_ID') or os.getenv('TELEGRAM_CHAT')

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except Exception as e:
        print(f"Send error {e}")

def main():
    # FIX BUG 1 & 2 - ANTI SEPI TOTAL
    data = requests.get("https://indodax.com/api/summaries", timeout=20).json()
    tickers = data['tickers']
    prices_24h = data.get('prices_24h', {})

    print(f"DEBUG Scan {len(tickers)} koin | prices_24h {len(prices_24h)}")

    fresh = []
    early = []
    ijo_trending = []
    trending_lanjutan = []
    serok_micin = []

    # EXCLUDE BIG CAP BIAR SEROK GAK ITU2 AJA
    BIG_CAP = {"BTC","ETH","SOL","XRP","HYPE","BNB","DOGE","SHIB","PEPE","PENGU"}

    for pair, t in tickers.items():
        if not pair.endswith('_idr'):
            continue
        try:
            vol = float(t['vol_idr'])
            last = float(t['last'])
            low = float(t['low'])
            high = float(t['high'])
            # FIX BUG KEY - tia_idr -> tiaidr
            key = pair.replace('_','')
            p24 = float(prices_24h.get(key, 0))

            if p24 == 0 or low == 0 or last == 0 or high == 0:
                continue

            chg = (last - p24) / p24 * 100
            dist_low = (last - low) / low * 100 if low > 0 else 0
            dist_high = (high - last) / last * 100 if last > 0 else 0
            coin = pair.replace('_idr','').upper()

            # ANTI PUCUK PAS
            if dist_high < 0.3:
                continue

            # 1. FRESH PUMP 0.5-3.5% (V5.5) - 4 koin
            if 0.5 <= chg <= 3.5 and vol >= 50_000_000 and 1 <= dist_low <= 30:
                fresh.append((f"{coin}_IDR", chg, vol, dist_low))

            # 2. EARLY 1.5-8% (V17) - 4 koin
            if 1.5 <= chg <= 8 and vol >= 80_000_000 and 3 <= dist_low <= 60:
                early.append((f"{coin}_IDR", chg, vol, dist_low))

            # 3. IJO ONLY TRENDING 3-15% (V6 FINAL) - 4 koin
            if 3 <= chg <= 15 and vol >= 120_000_000 and dist_high >= 1:
                ijo_trending.append((f"{coin}_IDR", chg, vol, dist_low))

            # 4. TRENDING LANJUTAN 12-30% [CNG KEMARIN] - 4 koin
            if 12 <= chg <= 30 and vol >= 100_000_000 and 8 <= dist_low <= 80 and dist_high >= 2:
                trending_lanjutan.append((f"{coin}_IDR", chg, vol, dist_low))

            # 5. SEROK MICIN -7 to -0.5% (FIX BIAR GAK SOL XRP TERUS) - 4 koin
            if coin not in BIG_CAP:
                if -7 <= chg <= -0.5 and 50_000_000 <= vol <= 900_000_000 and 0 <= dist_low <= 10:
                    serok_micin.append((f"{coin}_IDR", chg, vol, dist_low, dist_high))

        except:
            continue

    # SORT BY VOL & AMBIL 20 KOIN
    fresh = sorted(fresh, key=lambda x: x[2], reverse=True)[:4]
    early = sorted(early, key=lambda x: x[2], reverse=True)[:4]
    ijo_trending = sorted(ijo_trending, key=lambda x: x[2], reverse=True)[:4]
    trending_lanjutan = sorted(trending_lanjutan, key=lambda x: x[2], reverse=True)[:4]
    serok_micin = sorted(serok_micin, key=lambda x: x[2], reverse=True)[:4]

    msg = f"🎯 V19 FIX SEROK MICIN 20 KOIN - {len(tickers)} Scan\n\n"

    if fresh:
        msg += f"🌱 FRESH PUMP 0.5-3.5% (V5.5) ({len(fresh)}):\n"
        for i,(p,c,v,dl) in enumerate(fresh,1):
            msg += f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {v/1e6:.0f}jt\n"
        msg += "\n"

    if early:
        msg += f"⚡ EARLY 1.5-8% (V17) ({len(early)}):\n"
        for i,(p,c,v,dl) in enumerate(early,1):
            msg += f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {v/1e6:.0f}jt\n"
        msg += "\n"

    if ijo_trending:
        msg += f"📈 IJO ONLY TRENDING 3-15% (V6) ({len(ijo_trending)}):\n"
        for i,(p,c,v,dl) in enumerate(ijo_trending,1):
            msg += f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {v/1e6:.0f}jt\n"
        msg += "\n"

    if trending_lanjutan:
        msg += f"🚀 TRENDING LANJUTAN 12-30% [CNG] ({len(trending_lanjutan)}):\n"
        for i,(p,c,v,dl) in enumerate(trending_lanjutan,1):
            msg += f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {v/1e6:.0f}jt | GAS!\n"
        msg += "\n"

    if serok_micin:
        msg += f"💎 SEROK MICIN -7 to -0.5% ({len(serok_micin)}):\n"
        for i,(p,c,v,dl,dh) in enumerate(serok_micin,1):
            msg += f"{i}. {p} {c:.1f}% | {dl:.1f}% low | {v/1e6:.0f}jt\n"
        msg += "\n"
    else:
        msg += f"💎 SEROK MICIN -7 to -0.5%: Kosong, semua micin lagi ijo!\n\n"

    total = len(fresh)+len(early)+len(ijo_trending)+len(trending_lanjutan)+len(serok_micin)
    if total == 0:
        msg += "😴 Sepi min, jangan maksa entry!\n"

    print(msg)
    send(msg)

if __name__ == "__main__":
    main()
