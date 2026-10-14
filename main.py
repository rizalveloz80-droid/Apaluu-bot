import requests, os, time

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('TELEGRAM_TOKEN') or os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID') or os.getenv('CHAT_ID') or os.getenv('TELEGRAM_CHAT')

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                      data={"chat_id": CHAT_ID, "text": msg}, timeout=15)
    except: pass

def get_rsi_ma20_antiblock(pair_idr):
    """
    V25.3 ANTI BLOCK - Pake /api/trades + User-Agent
    Gak pake tradingview/history lagi yang bikin RSI 50 semua!
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        url = f"https://indodax.com/api/{pair_idr}/trades"
        r = requests.get(url, timeout=8, headers=headers).json()

        # Format Indodax kadang dict {trades: []} kadang list langsung
        trades = r.get('trades', r) if isinstance(r, dict) else r
        if not trades or len(trades) < 30:
            return None, None, None

        # Ambil 100 harga terakhir, reverse biar urut waktu
        prices = [float(x['price']) for x in trades[:100]][::-1]

        # MA20
        ma20 = sum(prices[-20:]) / 20
        last_price = prices[-1]

        # RSI 14 yang bener
        gains, losses = [], []
        for i in range(len(prices)-15, len(prices)-1):
            diff = prices[i+1] - prices[i]
            if diff > 0:
                gains.append(diff)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(diff))

        # Rata-rata 14 terakhir
        avg_gain = sum(gains[-14:]) / 14 if gains else 0.01
        avg_loss = sum(losses[-14:]) / 14 if losses else 0.01

        if avg_loss == 0:
            rsi = 70
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

        return round(rsi, 1), round(ma20, 2), round(last_price, 2)

    except Exception as e:
        # print(f"RSI fail {pair_idr}: {e}")
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
    top_candidates = candidates[:80]

    fresh, early, ijo, trending, serok, pump_tracker = [], [], [], [], [], []
    used = set()

    for pair, coin, chg, vol, dl, dh, last in top_candidates:
        pid = f"{coin}_IDR"
        if pid in used: continue

        # === V25.3 ANTI BLOCK RSI ===
        rsi_data = get_rsi_ma20_antiblock(pair)
        if rsi_data[0] is None:
            rsi, ma20, is_above = 50, last, False
            is_rsi_valid = False
        else:
            rsi, ma20, _ = rsi_data
            is_above = last > ma20
            is_rsi_valid = True

        vol_spike = round((vol/250_000_000)*100,0)
        support = round(last*0.985,0)
        resistance = round(last*1.035,0)

        # PUMP TRACKER - RSI 40-65 + >MA20 + Vol 40%
        # Kalo RSI valid, pake filter ketat, kalo gak valid fallback longgar
        if len(pump_tracker) < 5:
            if is_rsi_valid:
                if 40 <= rsi <= 65 and is_above and vol >= 100_000_000 and vol_spike >= 40 and 0.2 <= chg <= 8:
                    pump_tracker.append((pid, coin, chg, vol, rsi, ma20, last, support, resistance, vol_spike))
                    used.add(pid)
                    time.sleep(0.25)
                    continue
            else:
                # Fallback kalo RSI gagal tapi chg bagus
                if 0.5 <= chg <= 5 and vol >= 150_000_000:
                    pump_tracker.append((pid, coin, chg, vol, rsi, ma20, last, support, resistance, vol_spike))
                    used.add(pid)
                    continue

        # FRESH, EARLY, IJO, TRENDING
        if len(fresh) < 4 and 0.5 <= chg <= 3.5 and 1 <= dl <= 10 and 80_000_000 <= vol <= 400_000_000:
            fresh.append((pid, chg, vol, dl, rsi)); used.add(pid); continue
        if len(early) < 4 and 3.5 < chg <= 8 and 8 <= dl <= 22 and vol >= 120_000_000:
            early.append((pid, chg, vol, dl, rsi)); used.add(pid); continue
        if len(ijo) < 4 and 8 < chg <= 15 and dl >= 12 and dh >= 1.5 and vol >= 150_000_000:
            ijo.append((pid, chg, vol, dl, rsi)); used.add(pid); continue
        if len(trending) < 4 and 15 < chg <= 35 and 15 <= dl <= 40 and vol >= 150_000_000:
            trending.append((pid, chg, vol, dl, rsi)); used.add(pid); continue

        # SEROK GOLDEN - FILTER BARU: -8% s/d -0.2% BIAR MAGIC 2.024 MASUK!
        if len(serok) < 5 and -8 <= chg <= -0.2 and 0 <= dl <= 2.5 and dh >= 2.0 and 100_000_000 <= vol <= 900_000_000:
            if is_rsi_valid:
                if rsi <= 42: # RSI oversold beneran
                    serok.append((pid, chg, vol, dl, dh, rsi, ma20, last)); used.add(pid); continue
            else:
                serok.append((pid, chg, vol, dl, dh, rsi, ma20, last)); used.add(pid); continue

        time.sleep(0.15)

    msg = f"🎯 V25.3 ANTI-BLOCK RSI+MA20 - {len(tickers)} Scan\n\n"

    if pump_tracker:
        msg += f"🤖 PUMP TRACKER ({len(pump_tracker)}):\n"
        for i,(pid, coin, chg, vol, rsi, ma20, last, sup, res, vspike) in enumerate(pump_tracker,1):
            valid_tag = "✅" if rsi!=50 else "⚠️"
            msg += f"{i}. {pid} {chg:.1f}% | RSI {rsi}{valid_tag} | >MA20 {is_above} | Vol {vspike}%\n"
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
            msg += f"{i}. {p} {c:.1f}% | {dl:.0f}% low | RSI {rsi}\n"
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
        msg += f"💎 SEROK GOLDEN -8% to 0% ({len(serok)}):\n"
        for i,(p,c,v,dl,dh,rsi,ma,last) in enumerate(serok,1):
            msg += f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {dh:.0f}% high | RSI {rsi} | {v/1e6:.0f}jt\n"

    total = len(pump_tracker)+len(fresh)+len(early)+len(ijo)+len(trending)+len(serok)
    msg += f"\n✅ Total {total} koin | V25.3 Anti-Block"

    print(msg)
    send(msg)

if __name__ == "__main__":
    main()
