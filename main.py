import requests, os, time

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('TELEGRAM_TOKEN') or os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID') or os.getenv('CHAT_ID') or os.getenv('TELEGRAM_CHAT')

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                      data={"chat_id": CHAT_ID, "text": msg}, timeout=15)
    except: pass

def get_rsi_ma20_akurat(pair_idr):
    """
    Ambil RSI 14 & MA20 AKURAT dari TradingView Indodax
    pair_idr contoh: magic_idr, btc_idr
    """
    try:
        symbol = pair_idr.replace("_", "").upper() # magic_idr -> MAGICIDR
        now = int(time.time())
        # Ambil 100 candle 15 menit terakhir (15*100 = 1500 menit = 25 jam)
        url = f"https://indodax.com/tradingview/history?symbol={symbol}&resolution=15&from={now-90000}&to={now}"
        r = requests.get(url, timeout=12).json()
        closes = r.get('c', [])
        if not closes or len(closes) < 25:
            return 50, 0, 0, 0

        # MA20 dari 20 close terakhir
        ma20 = sum(closes[-20:]) / 20
        last_close = closes[-1]

        # RSI 14
        gains, losses = [], []
        # Ambil 14 perubahan terakhir
        for i in range(len(closes)-15, len(closes)-1):
            diff = closes[i+1] - closes[i]
            if diff > 0:
                gains.append(diff)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(diff))

        avg_gain = sum(gains[-14:]) / 14 if gains else 0.01
        avg_loss = sum(losses[-14:]) / 14 if losses else 0.01

        if avg_loss == 0:
            rsi = 70
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

        # Volume spike approximation (dari vol_idr nanti di main)
        return round(rsi, 1), round(ma20, 2), round(last_close, 2), len(closes)

    except Exception as e:
        # print(f"RSI error {pair_idr}: {e}")
        return 50, 0, 0, 0

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
            if p24 == 0 or low == 0 or vol < 80_000_000: continue
            chg = (last-p24)/p24*100
            dl = (last-low)/low*100
            dh = (high-last)/last*100 if last>0 else 0
            coin = pair.replace('_idr','').upper()
            if coin in BIG_CAP: continue
            candidates.append((pair, coin, chg, vol, dl, dh, last))
        except: continue

    # Cuma scan top 35 by volume biar gak kena rate limit TradingView
    candidates.sort(key=lambda x: x[3], reverse=True)
    top_candidates = candidates[:35]

    fresh, early, ijo, trending, serok, pump_tracker = [], [], [], [], [], []
    used = set()

    for pair, coin, chg, vol, dl, dh, last in top_candidates:
        pid = f"{coin}_IDR"
        if pid in used: continue

        # === AMBIL RSI & MA20 AKURAT (15 MENIT CANDLE) ===
        rsi, ma20, last_candle, cnt = get_rsi_ma20_akurat(pair)
        is_above_ma = last > ma20 if ma20 > 0 else False
        support = round(last * 0.985, 0)
        resistance = round(last * 1.035, 0)
        vol_spike = round((vol / 250_000_000) * 100, 0) # >100% = spike

        # === PUMP TRACKER - SESUAI TEMPLATE BARU LU ===
        # Kondisi 1: Volume > 1.5x rata2 (kita pake vol >=150jt + spike >60%)
        # Kondisi 2: RSI 45-60
        # Kondisi 3: Harga > MA20
        if len(pump_tracker) < 5 and 45 <= rsi <= 60 and is_above_ma and vol >= 150_000_000 and vol_spike >= 60 and 0.3 <= chg <= 8:
            pump_tracker.append((pid, coin, chg, vol, rsi, ma20, last, support, resistance, vol_spike))
            used.add(pid)
            time.sleep(0.4)
            continue

        # FRESH 0.5-3.5%
        if len(fresh) < 4 and 0.5 <= chg <= 3.5 and 1 <= dl <= 10 and 80_000_000 <= vol <= 400_000_000:
            fresh.append((pid, chg, vol, dl, rsi)); used.add(pid); continue

        # EARLY 3.5-8%
        if len(early) < 4 and 3.5 < chg <= 8 and 8 <= dl <= 22 and vol >= 120_000_000:
            early.append((pid, chg, vol, dl, rsi)); used.add(pid); continue

        # IJO 8-15%
        if len(ijo) < 4 and 8 < chg <= 15 and dl >= 12 and dh >= 1.5 and vol >= 150_000_000:
            ijo.append((pid, chg, vol, dl, rsi)); used.add(pid); continue

        # TRENDING 15-35%
        if len(trending) < 4 and 15 < chg <= 35 and 15 <= dl <= 40 and vol >= 150_000_000:
            trending.append((pid, chg, vol, dl, rsi)); used.add(pid); continue

        # SEROK GOLDEN POCKET V25.1 - FILTER RSI AKURAT BIAR GAK NYANGKUT DI 2.049!
        if len(serok) < 4 and -6 <= chg <= -0.2 and 0 <= dl <= 2.5 and dh >= 2.5 and 100_000_000 <= vol <= 900_000_000:
            if rsi <= 38 and not is_above_ma: # Oversold beneran + di bawah MA20
                serok.append((pid, chg, vol, dl, dh, rsi, ma20, last)); used.add(pid); continue

        time.sleep(0.35)

    # === FORMAT PESAN SESUAI TEMPLATE LU ===
    msg = f"🎯 V25.1 AKURAT RSI+MA20 - {len(tickers)} Scan\n\n"

    if pump_tracker:
        msg += f"🤖 INDODAX PUMP TRACKER 🤖 ({len(pump_tracker)}):\n"
        for i, (pid, coin, chg, vol, rsi, ma20, last, sup, res, vspike) in enumerate(pump_tracker, 1):
            msg += f"{i}. {pid}\n"
            msg += f" • Harga: Rp {last:,.0f} • 1J: +{chg:.2f}% • Vol Spike: {vspike}% \n"
            msg += f" • RSI: {rsi} | MA20: Rp {ma20:,.0f} | >MA20 ✅\n"
            msg += f" 🛒 Beli di dekat: Rp {sup:,.0f} 🎯 TP: Rp {res:,.0f}\n"
        msg += "\n*Disclaimer: deteksi bot volume pasar. uang dingin*\n\n"

    if serok:
        msg += f"💎 SEROK GOLDEN POCKET RSI<38 ({len(serok)}):\n"
        for i, (p,c,v,dl,dh,rsi,ma,last) in enumerate(serok,1):
            msg += f"{i}. {p} {c:.1f}% | {dl:.0f}% low | RSI {rsi} | MA {ma:,.0f} | Rp {last:,.0f}\n"
        msg += "\n"

    if fresh:
        msg += f"🌱 FRESH ({len(fresh)}): {', '.join([x[0] for x in fresh])}\n"
    if early:
        msg += f"⚡ EARLY ({len(early)}): {', '.join([x[0] for x in early])}\n"

    total = len(pump_tracker)+len(fresh)+len(early)+len(ijo)+len(trending)+len(serok)
    msg += f"\n✅ Total {total} koin | V25.1 RSI Akurat"

    print(msg)
    send(msg)

if __name__ == "__main__":
    main()
