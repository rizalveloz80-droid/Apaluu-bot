import requests, os, time

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

WATCHLIST_DEX = ["RSR","BR","ONT","W","STRK","BONK","FLOKI","PLUME","POLY","SKYA","METIS"]

def get_mc_map():
    mc_map = {}
    try:
        for page in [1,2,3]:
            url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page={page}"
            r = requests.get(url, timeout=20).json()
            for c in r:
                mc_map[c['symbol'].upper()] = c['market_cap']
    except:
        pass
    return mc_map

def check_dex_radar():
    dex_msg = ""
    found = 0
    for sym in WATCHLIST_DEX:
        try:
            r = requests.get(f"https://api.dexscreener.com/latest/dex/search/?q={sym}", timeout=10).json()
            pairs = r.get('pairs', [])
            if not pairs: continue
            top = sorted(pairs, key=lambda x: float(x.get('volume',{}).get('h24',0) or 0), reverse=True)[0]
            chg5 = float(top.get('priceChange',{}).get('m5',0) or 0)
            if chg5 > 8:
                dex_msg += f"🚀 {sym} +{chg5}% (5m) di {top.get('chainId')} | ${top.get('priceUsd')}\n"
                found += 1
            time.sleep(0.5)
        except: continue
    return dex_msg, found

def main():
    mc_map = get_mc_map()
    data = requests.get("https://indodax.com/api/tickers", timeout=20).json()
    tickers = data['tickers']
    prices_24h = data.get('prices_24h', {})

    early, trending = [], []

    for pair, t in tickers.items():
        if not pair.endswith('_idr'): continue
        try:
            vol = float(t['vol_idr'])
            last = float(t['last'])
            high = float(t['high'])
            low = float(t['low'])
            symbol = pair.replace('_idr','').upper()
            price_24h = float(prices_24h.get(pair, 0))
            if price_24h==0: continue
            chg = ((last-price_24h)/price_24h*100)
            mc = mc_map.get(symbol,0)
            vol_mc = (vol/mc*100) if mc>0 else 999
            dist_low = ((last-low)/low*100) if low>0 else 0

            # 1. EARLY 2 ONLY - VERSI AMAN (1.5-8% + Vol 200-600jt + >15% dr low)
            # Hapus yang 80jt, ganti jadi 200jt biar gak sampah
            if 1.5 <= chg <= 8 and 200_000_000 <= vol <= 600_000_000 and dist_low > 15:
                if (mc>0 and vol_mc>=25) or (mc==0):
                    early.append({'pair':pair.upper(),'chg':chg,'vol':vol,'vol_mc':vol_mc,'mc':mc,'dist':dist_low})

            # 2. TRENDING >12% - BIARIN (buat TP kayak GTC 70%)
            if chg > 12 and vol >= 150_000_000:
                trending.append({'pair':pair.upper(),'chg':chg,'vol':vol})

            # 3. SEROK BAWAH - MATIIN TOTAL (ini penyebab PM & NEON nyangkut)

        except: continue

    early = sorted(early, key=lambda x: x['vol_mc'], reverse=True)[:10]
    trending = sorted(trending, key=lambda x: x['chg'], reverse=True)[:5]

    if not early and not trending:
        print("Sepi - gak ada yang lolos filter aman")
        # return # biarin tetep cek dex

    msg = f"🎯 V14 SAFE (TRENDING + EARLY 2 + DEX) - Scan {len(tickers)}\n\n"
    if early:
        msg += f"⚡ EARLY 2 ({len(early)}) (1.5-8% - Aman Entry)\n"
        for i,c in enumerate(early,1):
            label = "PRO" if c['mc']>0 else "MICIN"
            mc_txt = f"{c['vol_mc']:.0f}%" if c['vol_mc']!=999 else "NEW"
            msg += f"{i}. {c['pair']} {c['chg']:.1f}% | {c['dist']:.0f}% dr low | {label} {mc_txt}\n"
        msg += "\n"
    if trending:
        msg += f"🔥 TRENDING {len(trending)} (>12% - TP)\n"
        for i,c in enumerate(trending,1):
            msg += f"{i}. {c['pair']} {c['chg']:.1f}% Vol {c['vol']/1e9:.1f}M\n"
        msg += "\n"

    # === DEX RADAR 11 KOIN ===
    dex_text, dex_found = check_dex_radar()
    if dex_found > 0:
        msg += f"🚀 DEX RADAR LEADING {dex_found} (DEX pump duluan)\n" + dex_text

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                  data={"chat_id": CHAT_ID, "text": msg})
    print(msg)

if __name__ == "__main__":
    main()
