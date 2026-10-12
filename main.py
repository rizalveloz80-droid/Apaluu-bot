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
    except:
        pass
    return mc_map

def main():
    mc_map = get_mc_map()
    summaries = requests.get("https://indodax.com/api/summaries", timeout=20).json()['tickers']

    entry = []
    serok = []
    selesai = []

    for pair, t in summaries.items():
        if not pair.endswith('_idr'): continue
        try:
            vol = float(t['vol_idr'])
            chg = float(t.get('price_change_percent', 0) or 0)
            symbol = pair.replace('_idr','').upper()
            mc = mc_map.get(symbol, 0)
            if mc == 0: continue
            vol_mc = (vol / mc) * 100
            last = float(t['last'])
            high = float(t['high'])
            low = float(t['low'])

            # 1. ENTRY TOP 20 - Pump awal
            if 1.5 <= chg <= 8 and vol >= 100_000_000 and vol_mc >= 60:
                entry.append({'pair':pair.upper(),'chg':chg,'vol':vol,'vol_mc':vol_mc})

            # 2. SEROK BAWAH - Yang bottom / oversold
            # Ciri: turun banyak -3% s/d -12% tapi deket low (bottom)
            # (last - low) / (high - low) < 0.2 artinya deket dasar
            range_hl = high - low if high != low else 1
            pos_from_low = (last - low) / range_hl
            if -12 <= chg <= -3 and vol >= 40_000_000 and pos_from_low < 0.25:
                serok.append({'pair':pair.upper(),'chg':chg,'vol':vol,'pos':pos_from_low})

            # 3. SELESAI KOREKSI - Abis turun mau naik lagi
            # Ciri: chg -1% s/d +1.5% tapi tadi sempat turun dalem, vol tetep ada
            if -1 <= chg <= 1.5 and vol >= 30_000_000 and pos_from_low > 0.4:
                 # filter tambahan: kalo low jauh dari high = abis koreksi
                 if (high - low)/low > 0.05:
                    selesai.append({'pair':pair.upper(),'chg':chg,'vol':vol})

        except:
            continue

    entry = sorted(entry, key=lambda x: x['vol_mc'], reverse=True)[:20]
    serok = sorted(serok, key=lambda x: x['chg'])[:10] # paling dalem dulu
    selesai = sorted(selesai, key=lambda x: x['vol'], reverse=True)[:10]

    msg = f"🤖 V12.3 TOP20 + BOTTOM {len(entry)+len(serok)+len(selesai)} koin\n"
    msg += f"Scan {len(summaries)} koin\n\n"

    if entry:
        msg += f"⚡ ENTRY TERPANAS TOP {len(entry)} (1.5-8% | Vol>100jt | Vol/MC>60%):\n"
        for i,c in enumerate(entry,1):
            msg += f"{i}. {c['pair']} {c['chg']:.1f}% | M/C {c['vol_mc']:.1f}% | {c['vol']/1e6:.0f}jt\n"
        msg += "\n"
    else:
        msg += "⚡ ENTRY: 0 koin (market sepi pump)\n\n"

    if serok:
        msg += f"💎 SEROK BAWAH {len(serok)} (Bottom -3 s/d -12%):\n"
        for i,c in enumerate(serok,1):
            msg += f"{i}. {c['pair']} {c['chg']:.1f}% | Vol {c['vol']/1e6:.0f}jt | Deket low\n"
        msg += "\n"

    if selesai:
        msg += f"🔄 SELESAI KOREKSI {len(selesai)} (-1 s/d +1.5%):\n"
        for i,c in enumerate(selesai,1):
            msg += f"{i}. {c['pair']} {c['chg']:.1f}% | Vol {c['vol']/1e6:.0f}jt\n"

    if not entry and not serok and not selesai:
        msg += "Sepi min, gak ada yang menarik. Skip dulu!"

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id":CHAT_ID,"text":msg})
    print(msg)

if __name__ == "__main__":
    main()
