import requests, os

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('TELEGRAM_TOKEN') or os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID') or os.getenv('CHAT_ID') or os.getenv('TELEGRAM_CHAT')

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except: pass

def main():
    data = requests.get("https://indodax.com/api/summaries", timeout=20).json()
    tickers = data['tickers']
    prices_24h = data.get('prices_24h', {})

    all_candidates = []

    BIG_CAP = {"BTC","ETH","SOL","XRP","HYPE","BNB","DOGE","SHIB","PEPE","PENGU","USDT","USDC"}

    for pair, t in tickers.items():
        if not pair.endswith('_idr'): continue
        try:
            vol = float(t['vol_idr'])
            last = float(t['last'])
            low = float(t['low'])
            high = float(t['high'])
            key = pair.replace('_','')
            p24 = float(prices_24h.get(key, 0))
            if p24 == 0 or low == 0 or last == 0: continue
            chg = (last-p24)/p24*100
            dist_low = (last-low)/low*100
            dist_high = (high-last)/last*100
            coin = pair.replace('_idr','').upper()
            if coin in BIG_CAP: continue # NO BIG CAP di semua kategori!
            if dist_high < 0.3: continue

            all_candidates.append((pair, coin, chg, vol, dist_low, dist_high, last))
        except: continue

    # Sort by vol biar adil
    all_candidates.sort(key=lambda x: x[3], reverse=True)

    fresh, early, ijo, trending, serok = [], [], [], [], []
    used = set()

    for pair, coin, chg, vol, dl, dh, last in all_candidates:
        pid = f"{coin}_IDR"
        if pid in used: continue

        # FRESH 0.5-3.5%
        if len(fresh) < 4 and 0.5 <= chg <= 3.5 and vol >= 50_000_000 and 1 <= dl <= 30:
            fresh.append((pid, chg, vol, dl)); used.add(pid); continue
        # EARLY 1.5-8%
        if len(early) < 4 and 1.5 <= chg <= 8 and vol >= 80_000_000 and 3 <= dl <= 60:
            early.append((pid, chg, vol, dl)); used.add(pid); continue
        # IJO ONLY 3-15%
        if len(ijo) < 4 and 3 <= chg <= 15 and vol >= 100_000_000:
            ijo.append((pid, chg, vol, dl)); used.add(pid); continue
        # TRENDING 12-30%
        if len(trending) < 4 and 12 <= chg <= 30 and vol >= 100_000_000:
            trending.append((pid, chg, vol, dl)); used.add(pid); continue
        # SEROK MICIN -7 to -0.5%
        if len(serok) < 4 and -7 <= chg <= -0.5 and 50_000_000 <= vol <= 900_000_000:
            serok.append((pid, chg, vol, dl, dh)); used.add(pid); continue

    msg = f"🎯 V20 FINAL NO DUPLIKAT 20 KOIN - {len(tickers)} Scan\n\n"
    if fresh:
        msg += f"🌱 FRESH 0.5-3.5% ({len(fresh)}):\n"
        for i,(p,c,v,dl) in enumerate(fresh,1): msg += f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {v/1e6:.0f}jt\n"
        msg+="\n"
    if early:
        msg += f"⚡ EARLY 1.5-8% ({len(early)}):\n"
        for i,(p,c,v,dl) in enumerate(early,1): msg += f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {v/1e6:.0f}jt\n"
        msg+="\n"
    if ijo:
        msg += f"📈 IJO ONLY 3-15% ({len(ijo)}):\n"
        for i,(p,c,v,dl) in enumerate(ijo,1): msg += f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {v/1e6:.0f}jt\n"
        msg+="\n"
    if trending:
        msg += f"🚀 TRENDING 12-30% [CNG] ({len(trending)}):\n"
        for i,(p,c,v,dl) in enumerate(trending,1): msg += f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {v/1e6:.0f}jt | GAS!\n"
        msg+="\n"
    if serok:
        msg += f"💎 SEROK MICIN -7 to -0.5% ({len(serok)}):\n"
        for i,(p,c,v,dl,dh) in enumerate(serok,1): msg += f"{i}. {p} {c:.1f}% | {dl:.1f}% low | {v/1e6:.0f}jt\n"

    print(msg)
    send(msg)

if __name__ == "__main__":
    main()
