import requests, os, time
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

WATCHLIST_DEX = ["RSR","BR","ONT","W","STRK","BONK","FLOKI","PLUME","POLY","SKYA","METIS"]

def main():
    data=requests.get("https://indodax.com/api/tickers", timeout=20).json()
    tickers=data['tickers']
    prices_24h=data.get('prices_24h',{})
    early,trending=[],[]

    for pair,t in tickers.items():
        if not pair.endswith('_idr'): continue
        try:
            vol=float(t['vol_idr']); last=float(t['last']); low=float(t['low'])
            price_24h=float(prices_24h.get(pair,0))
            if price_24h==0: continue
            chg=((last-price_24h)/price_24h*100)
            dist=((last-low)/low*100) if low>0 else 0

            # === 1% TETEP ADA ===
            if 1.0 <= chg <= 9.9 and vol >= 100_000_000 and dist > 8:
                early.append({'pair':pair.upper(),'chg':chg,'vol':vol,'dist':dist})

            # === TRENDING [TELAT] TETEP ADA ===
            if chg >= 10 and vol >= 100_000_000:
                trending.append({'pair':pair.upper(),'chg':chg,'vol':vol})

            # === SEROK HAPUS ===

        except: continue

    early=sorted(early, key=lambda x: x['chg'], reverse=True)[:10]
    trending=sorted(trending, key=lambda x: x['chg'], reverse=True)[:5]

    # === DEX SCREENER 11 KOIN - RSR BR W DLL ===
    dex_text=""; dex_found=0
    for sym in WATCHLIST_DEX:
        try:
            r=requests.get(f"https://api.dexscreener.com/latest/dex/search/?q={sym}", timeout=8).json()
            pairs=r.get('pairs',[])
            if not pairs: continue
            # ambil yang volume paling gede
            top=sorted(pairs, key=lambda x: float(x.get('volume',{}).get('h24',0) or 0), reverse=True)[0]
            chg5=float(top.get('priceChange',{}).get('m5',0) or 0)
            chg60=float(top.get('priceChange',{}).get('h1',0) or 0)
            # kalau di DEX udah pump 5m >8% atau 1j >20%
            if chg5 > 8 or chg60 > 20:
                dex_text+=f"🚀 {sym} +{chg5}% (5m) / +{chg60}% (1j) di {top.get('chainId')} ${top.get('priceUsd')}\n"
                dex_found+=1
            time.sleep(0.4)
        except: continue

    if not early and not trending and dex_found==0:
        print("Sepi")
        return

    msg=f"🎯 V14.3 FINAL (1% + TELAT + DEX) - Scan {len(tickers)}\n\n"
    if early:
        msg+=f"⚡ EARLY dari 1% ({len(early)})\n"
        for i,c in enumerate(early,1):
            msg+=f"{i}. {c['pair']} {c['chg']:.1f}% | {c['dist']:.0f}% dr low | {c['vol']/1e6:.0f}jt\n"
        msg+="\n"
    if trending:
        msg+=f"🔥 TRENDING {len(trending)} (>10% - [TELAT])\n"
        for i,c in enumerate(trending,1):
            msg+=f"{i}. {c['pair']} {c['chg']:.1f}% | {c['vol']/1e6:.0f}jt [TELAT]\n"
        msg+="\n"
    if dex_found>0:
        msg+=f"🌐 DEX RADAR LEADING {dex_found}\n"+dex_text+"(DEX pump duluan, Indodax nyusul)\n"

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id":CHAT_ID,"text":msg})
    print(msg)

if __name__=="__main__": main()
