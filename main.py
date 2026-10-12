import requests, os
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def get_mc_map():
    mc_map = {}
    try:
        for page in [1,2,3]:
            url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=idr&order=market_cap_desc&per_page=250&page={page}"
            r = requests.get(url, timeout=20).json()
            for c in r: 
                mc_map[c['symbol'].upper()] = c['market_cap']
    except: 
        pass
    return mc_map

def main():
    mc_map = get_mc_map()
    data = requests.get("https://indodax.com/api/summaries", timeout=20).json()
    tickers = data['tickers']
    prices_24h = data.get('prices_24h', {})

    early, trending, serok = [], [], []

    for pair, t in tickers.items():
        if not pair.endswith('_idr'): 
            continue
        try:
            vol = float(t['vol_idr'])
            last = float(t['last'])
            high = float(t['high'])
            low = float(t['low'])
            symbol = pair.replace('_idr','').upper()
            price_24h = float(prices_24h.get(pair.replace('_',''),0) or 0)
            if price_24h==0: 
                continue
            chg = ((last-price_24h)/price_24h)*100
            mc = mc_map.get(symbol,0)
            vol_mc = (vol/mc*100) if mc>0 else 999

            # 1. EARLY PUMP 1.5-8% - Masuk duluan sebelum trending (GTC pas 5%, PM 2.5%)
            if 1.5 <= chg <= 8 and vol >= 80000000:
                if (mc>0 and vol_mc>=25) or (mc==0 and vol>=150_000_000):
                    early.append({'pair':pair.upper(),'chg':chg,'vol':vol,'vol_mc':vol_mc,'mc':mc})

            # 2. TRENDING >12% - Udah telat (GTC 75%)
            if chg > 12 and vol >= 150_000_000:
                trending.append({'pair':pair.upper(),'chg':chg,'vol':vol})

            # 3. SEROK BAWAH - Minus tapi mantul (ONT -28% & BR -9% punya lu)
            range_hl = high - low if high!=low else 1
            pos_low = (last - low) / range_hl
            if -30 <= chg <= -5 and vol >= 150_000_000 and pos_low < 0.20:
                serok.append({'pair':pair.upper(),'chg':chg,'vol':vol,'pos':pos_low*100,'low':low,'last':last})

        except: 
            continue

    early = sorted(early, key=lambda x: x['vol_mc'], reverse=True)[:5]
    trending = sorted(trending, key=lambda x: x['chg'], reverse=True)[:5]
    serok = sorted(serok, key=lambda x: x['pos'])[:5]

    if not early and not trending and not serok: 
        print("Sepi")
        return

    msg = f"🎯 V13 EARLY + SEROK - Scan {len(tickers)} koin\n\n"
    if early:
        msg += f"⚡ EARLY {len(early)} (1.5-8% - Masuk duluan):\n"
        for i,c in enumerate(early,1):
            label = "PRO" if c['mc']>0 else "MICIN"
            mc_txt = f"{c['vol_mc']:.0f}%" if c['vol_mc']!=999 else "NEW"
            msg += f"{i}. {c['pair']} {c['chg']:.1f}% | {label} {mc_txt} | {c['vol']/1e6:.0f}jt\n"
        msg += "\n"
    if serok:
        msg += f"💰 SEROK BAWAH {len(serok)} (Minus mantul ONT/BR):\n"
        for i,c in enumerate(serok,1):
            msg += f"{i}. {c['pair']} {c['chg']:.1f}% | LOW {c['low']:.0f} -> {c['last']:.0f} ({c['pos']:.0f}% dr low) | Vol {c['vol']/1e6:.0f}jt\n"
        msg += "\n"
    if trending:
        msg += f"🔥 TRENDING {len(trending)} (>12% - Udah telat):\n"
        for i,c in enumerate(trending,1):
            msg += f"{i}. {c['pair']} {c['chg']:.1f}% | {c['vol']/1e6:.0f}jt [TELAT]\n"

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id":CHAT_ID,"text":msg})
    print(msg)

if __name__ == "__main__":
    main()
