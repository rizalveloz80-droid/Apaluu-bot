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

    BIG_CAP = {"BTC","ETH","SOL","XRP","HYPE","BNB","DOGE","SHIB","PEPE","PENGU","USDT","USDC","AVAX","TRX","DOT"}

    candidates = []
    for pair, t in tickers.items():
        if not pair.endswith('_idr'): continue
        try:
            vol = float(t['vol_idr'])
            last = float(t['last'])
            low = float(t['low'])
            high = float(t['high'])
            key = pair.replace('_','')
            p24 = float(prices_24h.get(key, 0))
            if p24 == 0 or low == 0: continue
            chg = (last-p24)/p24*100
            dl = (last-low)/low*100
            dh = (high-last)/last*100 if last>0 else 0
            coin = pair.replace('_idr','').upper()
            if coin in BIG_CAP: continue
            if dh < 0.3: continue
            candidates.append((pair, coin, chg, vol, dl, dh))
        except: continue

    candidates.sort(key=lambda x: x[3], reverse=True)

    fresh, early, ijo, trending, serok = [], [], [], [], []
    used = set()

    for pair, coin, chg, vol, dl, dh in candidates:
        pid = f"{coin}_IDR"
        if pid in used: continue

        # 1. FRESH = RUMUS SIDEWAYS + VOLUME (Whale Nyicil)
        # chg 0.5-3.5% + dl 1-10% + vol 80jt+ = datar tapi vol naik
        if len(fresh) < 4 and 0.5 <= chg <= 3.5 and 1 <= dl <= 10 and vol >= 80_000_000:
            fresh.append((pid, chg, vol, dl)); used.add(pid); continue

        # 2. EARLY = RUMUS BREAKOUT AWAL
        # chg 3.5-8% + dl 8-22% + vol 150jt+ = mulai nembus resistance
        if len(early) < 4 and 3.5 < chg <= 8 and 8 <= dl <= 22 and vol >= 120_000_000:
            early.append((pid, chg, vol, dl)); used.add(pid); continue

        # 3. IJO ONLY = RUMUS BREAKOUT KONFIRMASI (vol meledak)
        # chg 8-15% + dl >=12% + dh >=1.5% + vol 200jt+ = breakout valid
        if len(ijo) < 4 and 8 < chg <= 15 and dl >= 12 and dh >= 1.5 and vol >= 150_000_000:
            ijo.append((pid, chg, vol, dl)); used.add(pid); continue

        # 4. TRENDING = RUMUS MOMENTUM LISTING (50-200% potensi)
        # chg 15-35% + dl 15-35% + vol 200jt+ = viral / baru listing
        if len(trending) < 4 and 15 < chg <= 35 and 15 <= dl <= 40 and vol >= 150_000_000:
            trending.append((pid, chg, vol, dl)); used.add(pid); continue

        # 5. SEROK MICIN = RUMUS RSI OVERSOLD (<30)
        # chg -7 to -0.5 + dl 0-5% + vol 100jt+ = di dasar banget mau mantul
        if len(serok) < 4 and -7 <= chg <= -0.5 and 0 <= dl <= 6 and vol >= 80_000_000:
            serok.append((pid, chg, vol, dl)); used.add(pid); continue

    msg = f"🎯 V22 RUMUS PRO 20 KOIN - {len(tickers)} Scan\n\n"

    if fresh:
        msg += f"🌱 FRESH Sideways+Vol ({len(fresh)}):\n"
        for i,(p,c,v,dl) in enumerate(fresh,1):
            msg += f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {v/1e6:.0f}jt\n"
        msg += "\n"
    if early:
        msg += f"⚡ EARLY Breakout Awal ({len(early)}):\n"
        for i,(p,c,v,dl) in enumerate(early,1):
            msg += f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {v/1e6:.0f}jt\n"
        msg += "\n"
    if ijo:
        msg += f"📈 IJO Breakout Valid ({len(ijo)}):\n"
        for i,(p,c,v,dl) in enumerate(ijo,1):
            msg += f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {v/1e6:.0f}jt\n"
        msg += "\n"
    if trending:
        msg += f"🚀 TRENDING Listing Viral ({len(trending)}):\n"
        for i,(p,c,v,dl) in enumerate(trending,1):
            msg += f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {v/1e6:.0f}jt | GAS!\n"
        msg += "\n"
    if serok:
        msg += f"💎 SEROK RSI Oversold ({len(serok)}):\n"
        for i,(p,c,v,dl) in enumerate(serok,1):
            msg += f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {v/1e6:.0f}jt\n"

    total = len(fresh)+len(early)+len(ijo)+len(trending)+len(serok)
    msg += f"\n✅ Total {total} koin unik! | API Aman"

    print(msg)
    send(msg)

if __name__ == "__main__":
    main()
