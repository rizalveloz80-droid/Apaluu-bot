import requests, os, time

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('TELEGRAM_TOKEN') or os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID') or os.getenv('CHAT_ID') or os.getenv('TELEGRAM_CHAT')

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                      data={"chat_id": CHAT_ID, "text": msg}, timeout=15)
    except: pass

def main():
    data = requests.get("https://indodax.com/api/summaries", timeout=20).json()
    tickers = data['tickers']
    prices_24h = data.get('prices_24h', {})

    BIG_CAP = {"BTC","ETH","SOL","XRP","HYPE","BNB","DOGE","SHIB","PEPE","PENGU","USDT","USDC","AVAX","TRX","DOT","WIF","BONK"}

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
            if p24 == 0 or low == 0 or vol < 70_000_000: continue
            chg = (last-p24)/p24*100
            dl = (last-low)/low*100
            dh = (high-last)/last*100 if last>0 else 0
            coin = pair.replace('_idr','').upper()
            if coin in BIG_CAP: continue
            candidates.append((pair, coin, chg, vol, dl, dh, last))
        except: continue

    candidates.sort(key=lambda x: x[3], reverse=True)
    top_candidates = candidates[:100]

    # === YANG LAMA TETAP, CUMA TAMBAH pre_early ===
    pre_early, fresh, early, ijo, trending, serok, pump_tracker = [], [], [], [], [], [], []
    used = set()

    for pair, coin, chg, vol, dl, dh, last in top_candidates:
        pid = f"{coin}_IDR"
        if pid in used: continue
        rsi = 50

        squeeze = dl + dh

        # === BARU: PRE-EARLY UNIVERSAL - UNTUK KOIN LAIN! ===
        # Setting umum buat semua koin, bukan cuma ZEREBRO/KITE!
        if len(pre_early) < 5 and 0.1 <= chg <= 2.5 and squeeze < 15 and 2 <= dl <= 8 and 80_000_000 <= vol <= 400_000_000:
            pre_early.append((pid, chg, vol, dl, squeeze))
            used.add(pid)
            continue

        # === YANG DI BAWAH INI TETAP KAYAK V25.3 - GAK DIRUBAH! ===

        # PUMP TRACKER TETAP
        vol_spike = round((vol/250_000_000)*100,0)
        if len(pump_tracker) < 5 and 0.5 <= chg <= 5 and vol >= 150_000_000:
            pump_tracker.append((pid, coin, chg, vol, rsi, last, vol_spike))
            used.add(pid)
            continue

        # FRESH TETAP
        if len(fresh) < 4 and 0.5 <= chg <= 3.5 and 1 <= dl <= 10 and 80_000_000 <= vol <= 400_000_000:
            fresh.append((pid, chg, vol, dl, rsi)); used.add(pid); continue

        # EARLY TETAP - INI YANG ZEREBRO & KITE 6-7%
        if len(early) < 4 and 3.5 < chg <= 8 and 8 <= dl <= 22 and vol >= 120_000_000:
            early.append((pid, chg, vol, dl, rsi)); used.add(pid); continue

        # IJO TETAP
        if len(ijo) < 4 and 8 < chg <= 15 and dl >= 12 and dh >= 1.5 and vol >= 150_000_000:
            ijo.append((pid, chg, vol, dl, rsi)); used.add(pid); continue

        # TRENDING TETAP
        if len(trending) < 4 and 15 < chg <= 35 and 15 <= dl <= 40 and vol >= 150_000_000:
            trending.append((pid, chg, vol, dl, rsi)); used.add(pid); continue

        # SEROK GOLDEN TETAP - INI YANG MAGIC 1.996 TADI!
        if len(serok) < 5 and -8 <= chg <= -0.2 and 0 <= dl <= 2.5 and dh >= 2.0 and 100_000_000 <= vol <= 900_000_000:
            serok.append((pid, chg, vol, dl, dh, rsi)); used.add(pid); continue

    msg = f"🎯 V25.5 FINAL - PRE-EARLY + V25.3 TETAP\n\n"

    if pre_early:
        msg += f"💣 PRE-EARLY SQUEEZE (MAU PUMP!) ({len(pre_early)}):\n"
        for i,(p,c,v,dl,sq) in enumerate(pre_early,1):
            msg += f"{i}. {p} {c:.1f}% | {dl:.0f}% low | squeeze {sq:.0f}% | {v/1e6:.0f}jt\n"
        msg += "\n"

    # YANG LAIN TETAP SAMA PERSIS KAYAK V25.3!
    if pump_tracker:
        msg += f"🤖 PUMP TRACKER ({len(pump_tracker)}):\n"
        for i,(pid, coin, chg, vol, rsi, last, vspike) in enumerate(pump_tracker,1):
            msg += f"{i}. {pid} {chg:.1f}% | Vol {vspike}%\n"
        msg += "\n"
    if fresh:
        msg += f"🌱 FRESH 0.5-3.5% ({len(fresh)}):\n"
        for i,(p,c,v,dl) in enumerate(fresh,1):
            msg += f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {v/1e6:.0f}jt\n"
        msg += "\n"
    if early:
        msg += f"⚡ EARLY 3.5-8% ({len(early)}):\n"
        for i,(p,c,v,dl) in enumerate(early,1):
            msg += f"{i}. {p} {c:.1f}% | {dl:.0f}% low\n"
        msg += "\n"
    if ijo:
        msg += f"📈 IJO 8-15% ({len(ijo)}):\n"
        for i,(p,c,v,dl) in enumerate(ijo,1):
            msg += f"{i}. {p} {c:.1f}% | {dl:.0f}% low\n"
        msg += "\n"
    if trending:
        msg += f"🚀 TRENDING 15-35% ({len(trending)}):\n"
        for i,(p,c,v,dl) in enumerate(trending,1):
            msg += f"{i}. {p} {c:.1f}% | {dl:.0f}% low\n"
        msg += "\n"
    if serok:
        msg += f"💎 SEROK GOLDEN -8% to 0% ({len(serok)}):\n"
        for i,(p,c,v,dl,dh,rsi) in enumerate(serok,1):
            msg += f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {dh:.0f}% high | {v/1e6:.0f}jt\n"

    total = len(pre_early)+len(fresh)+len(early)+len(ijo)+len(trending)+len(serok)+len(pump_tracker)
    msg += f"\n✅ Total {total} koin | Yang lain tetap!"

    print(msg)
    send(msg)

if __name__ == "__main__":
    main()
