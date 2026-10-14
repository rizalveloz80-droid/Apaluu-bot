import requests, os, time

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('TELEGRAM_TOKEN') or os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID') or os.getenv('CHAT_ID') or os.getenv('TELEGRAM_CHAT')

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                      data={"chat_id": CHAT_ID, "text": msg}, timeout=15)
    except: pass

def get_rsi_ma20_akurat(pair_idr):
    try:
        symbol = pair_idr.replace("_", "").upper()
        now = int(time.time())
        url = f"https://indodax.com/tradingview/history?symbol={symbol}&resolution=15&from={now-90000}&to={now}"
        r = requests.get(url, timeout=8).json()
        closes = r.get('c', [])
        if not closes or len(closes) < 25:
            return None, None, None # GAGAL = fallback

        ma20 = sum(closes[-20:]) / 20
        # RSI 14
        gains, losses = [], []
        for i in range(len(closes)-15, len(closes)-1):
            diff = closes[i+1] - closes[i]
            gains.append(diff if diff>0 else 0)
            losses.append(abs(diff) if diff<0 else 0)
        avg_gain = sum(gains[-14:])/14 or 0.01
        avg_loss = sum(losses[-14:])/14 or 0.01
        rsi = 70 if avg_loss==0 else 100 - (100/(1+(avg_gain/avg_loss)))
        return round(rsi,1), round(ma20,2), closes[-1]
    except:
        return None, None, None

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
    top_candidates = candidates[:80] # SCAN 80 BIAR 15 KOIN BALIK!

    fresh, early, ijo, trending, serok, pump_tracker = [], [], [], [], [], []
    used = set()

    for pair, coin, chg, vol, dl, dh, last in top_candidates:
        pid = f"{coin}_IDR"
        if pid in used: continue

        rsi_data = get_rsi_ma20_akurat(pair)
        if rsi_data[0] is None: # FALLBACK V24 LAMA
            rsi, ma20, is_above = 50, last, False
            vol_spike = 50
        else:
            rsi, ma20, _ = rsi_data
            is_above = last > ma20
            vol_spike = round((vol/250_000_000)*100,0)

        support = round(last*0.985,0)
        resistance = round(last*1.035,0)

        # === V25.2 PUMP TRACKER (LONGGAR) ===
        if len(pump_tracker) < 5 and 40 <= rsi <= 65 and is_above and vol >= 100_000_000 and vol_spike >= 40 and 0.2 <= chg <= 8:
            pump_tracker.append((pid, coin, chg, vol, rsi, ma20, last, support, resistance, vol_spike))
            used.add(pid)
            time.sleep(0.2)
            continue

        # === V24 LOGIC TETAP (BIAR DAPET 15 KOIN LAGI) ===
        if len(fresh) < 4 and 0.5 <= chg <= 3.5 and 1 <= dl <= 10 and 80_000_000 <= vol <= 400_000_000:
            fresh.append((pid, chg, vol, dl, rsi)); used.add(pid); continue
        if len(early) < 4 and 3.5 < chg <= 8 and 8 <= dl <= 22 and vol >= 120_000_000:
            early.append((pid, chg, vol, dl, rsi)); used.add(pid); continue
        if len(ijo) < 4 and 8 < chg <= 15 and dl >= 12 and dh >= 1.5 and vol >= 150_000_000:
            ijo.append((pid, chg, vol, dl, rsi)); used.add(pid); continue
        if len(trending) < 4 and 15 < chg <= 35 and 15 <= dl <= 40 and vol >= 150_000_000:
            trending.append((pid, chg, vol, dl, rsi)); used.add(pid); continue
        if len(serok) < 4 and -5 <= chg <= -0.3 and 0 <= dl <= 2.5 and dh >= 2.5 and 100_000_000 <= vol <= 900_000_000:
            # SEROK V25.2: kalo RSI ada, harus <40, kalo fallback (50) tetep boleh
            if rsi <= 40 or rsi_data[0] is None:
                serok.append((pid, chg, vol, dl, dh, rsi, ma20, last)); used.add(pid); continue
        time.sleep(0.15)

    msg = f"🎯 V25.2 COMBO RSI+MA20 - {len(tickers)} Scan\n\n"
    if pump_tracker:
        msg += f"🤖 PUMP TRACKER RSI 40-65 ({len(pump_tracker)}):\n"
        for i,(pid, coin, chg, vol, rsi, ma20, last, sup, res, vspike) in enumerate(pump_tracker,1):
            msg += f"{i}. {pid} {chg:.1f}% | Vol {vspike}% | RSI {rsi} | >MA20\n"
            msg += f" • Rp {last:,.0f} 🛒 {sup:,.0f} 🎯 {res:,.0f}\n"
        msg += "\n"
    if fresh:
        msg += f"🌱 FRESH 0.5-3.5% ({len(fresh)}):\n"
        for i,(p,c,v,dl,rsi) in enumerate(fresh,1):
            msg += f"{i}. {p} {c:.1f}% | {dl:.0f}% low | RSI {rsi} | {v/1e6:.0f}jt\n"
        msg += "\n"
    if early:
        msg += f"⚡ EARLY 3.5-8% ({len(early)}):\n"
        for i,(p,c,v,dl,rsi) in enumerate(early,1):
            msg += f"{i}. {p} {c:.1f}% | {dl:.0f}% low | RSI {rsi} | {v/1e6:.0f}jt\n"
        msg += "\n"
    if ijo:
        msg += f"📈 IJO 8-15% ({len(ijo)}):\n"
        for i,(p,c,v,dl,rsi) in enumerate(ijo,1):
            msg += f"{i}. {p} {c:.1f}% | {dl:.0f}% low | RSI {rsi}\n"
        msg += "\n"
    if trending:
        msg += f"🚀 TRENDING 15-35% ({len(trending)}):\n"
        for i,(p,c,v,dl,rsi) in enumerate(trending,1):
            msg += f"{i}. {p} {c:.1f}% | {dl:.0f}% low | RSI {rsi}\n"
        msg += "\n"
    if serok:
        msg += f"💎 SEROK GOLDEN 0-2.5% ({len(serok)}):\n"
        for i,(p,c,v,dl,dh,rsi,ma,last) in enumerate(serok,1):
            msg += f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {dh:.0f}% high | RSI {rsi} | {v/1e6:.0f}jt\n"

    total = len(pump_tracker)+len(fresh)+len(early)+len(ijo)+len(trending)+len(serok)
    msg += f"\n✅ Total {total} koin unik! | V25.2 Combo"
    print(msg)
    send(msg)

if __name__ == "__main__":
    main()
