import requests, os
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def get_mc_map():
    mc_map = {}
    try:
        for page in [1,2]:
            url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=idr&order=market_cap_desc&per_page=250&page={page}"
            data = requests.get(url, timeout=20).json()
            for c in data:
                mc_map[c['symbol'].upper()] = c['market_cap']
    except: pass
    return mc_map

def main():
    mc_map = get_mc_map()
    data = requests.get("https://indodax.com/api/summaries", timeout=20).json()
    tickers = data['tickers']
    prices_24h = data.get('prices_24h', {})

    entry, trending, serok = [], [], []

    for pair, t in tickers.items():
        if not pair.endswith('_idr'): continue
        try:
            vol = float(t['vol_idr'])
            last = float(t['last'])
            high = float(t['high']); low = float(t['low'])
            symbol = pair.replace('_idr','').upper()

            # HITUNG % YANG BENER DARI prices_24h
            key_24h = pair.replace('_','') # btc_idr -> btcidr
            price_24h = float(prices_24h.get(key_24h, 0) or 0)
            if price_24h == 0: continue
            chg = ((last - price_24h) / price_24h) * 100

            mc = mc_map.get(symbol, 0)
            if mc == 0: continue
            vol_mc = (vol / mc) * 100

            # V12.6 FIX
            # 1. SNIPER 2-15% -> ini UAI +13% bakal masuk!
            if 2 <= chg <= 15 and vol >= 50_000_000 and vol_mc >= 20:
                entry.append({'pair':pair.upper(),'chg':chg,'vol':vol,'vol_mc':vol_mc})
            # 2. TRENDING >15% -> RSR +53% bakal masuk sini
            elif chg > 15 and vol >= 200_000_000:
                trending.append({'pair':pair.upper(),'chg':chg,'vol':vol})
            # 3. SEROK BAWAH
            range_hl = high - low if high != low else 1
            pos_low = (last - low) / range_hl
            if -15 <= chg <= -2 and vol >= 30_000_000 and pos_low < 0.3:
                serok.append({'pair':pair.upper(),'chg':chg,'vol':vol})
        except: continue

    entry = sorted(entry, key=lambda x: x['vol_mc'], reverse=True)[:5]
    trending = sorted(trending, key=lambda x: x['chg'], reverse=True)[:5]
    serok = sorted(serok, key=lambda x: x['chg'])[:5]

    msg = f"🎯 V12.6 FIX % - Scan {len(tickers)} koin\n\n"
    if entry:
        msg += f"⚡ ENTRY SNIPER {len(entry)} (2-15%):\n"
        for i,c in enumerate(entry,1):
            msg += f"{i}. {c['pair']} {c['chg']:.1f}% | M/C {c['vol_mc']:.1f}% | {c['vol']/1e6:.0f}jt\n"
        msg += "\n"
    if trending:
        msg += f"🔥 TRENDING PUMP {len(trending)} (>15% - Hati2 Pucuk):\n"
        for i,c in enumerate(trending,1):
            msg += f"{i}. {c['pair']} {c['chg']:.1f}% | Vol {c['vol']/1e6:.0f}jt\n"
        msg += "\n"
    if serok:
        msg += f"💎 SEROK BAWAH {len(serok)}:\n"
        for i,c in enumerate(serok,1):
            msg += f"{i}. {c['pair']} {c['chg']:.1f}% | {c['vol']/1e6:.0f}jt\n"
    
    if not entry and not trending and not serok:
        msg += "Market sepi min, skip."

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id":CHAT_ID,"text":msg})
    print(msg)

if __name__ == "__main__":
    main()
