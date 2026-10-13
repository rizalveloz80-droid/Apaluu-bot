import requests, os, time
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
WATCHLIST_DEX = ["RSR","BR","ONT","W","STRK","BONK","FLOKI"]

def main():
    data=requests.get("https://indodax.com/api/tickers",timeout=20).json()
    tickers=data['tickers']
    prices_24h=data.get('prices_24h',{})
    early=[]
    trending=[]
    for pair,t in tickers.items():
        if not pair.endswith('_idr'):
            continue
        try:
            vol=float(t['vol_idr'])
            last=float(t['last'])
            low=float(t['low'])
            p24=float(prices_24h.get(pair,0))
            if p24==0:
                continue
            chg=(last-p24)/p24*100
            dist=(last-low)/low*100 if low>0 else 0
            # LONGARIN: vol 50jt aja, dist 2% aja
            if 1.0 <= chg <= 9.9 and vol >= 50000000 and dist > 2:
                early.append((pair.upper(),chg,vol,dist))
            if chg >= 10 and vol >= 50000000:
                trending.append((pair.upper(),chg,vol))
        except:
            continue
    early=sorted(early,key=lambda x:x[1],reverse=True)[:10]
    trending=sorted(trending,key=lambda x:x[1],reverse=True)[:5]

    dex_text=""
    dex_found=0
    for sym in WATCHLIST_DEX:
        try:
            r=requests.get(f"https://api.dexscreener.com/latest/dex/search/?q={sym}",timeout=8).json()
            pairs=r.get('pairs',[])
            if not pairs:
                continue
            top=sorted(pairs,key=lambda x: float(x.get('volume',{}).get('h24',0) or 0),reverse=True)[0]
            chg5=float(top.get('priceChange',{}).get('m5',0) or 0)
            chg60=float(top.get('priceChange',{}).get('h1',0) or 0)
            if chg5>8 or chg60>20:
                dex_text+=f"- {sym} +{chg5}% 5m / +{chg60}% 1j [{top.get('chainId')}]\n"
                dex_found+=1
            time.sleep(0.4)
        except:
            continue

    # KALO SEPI TETEP KIRIM TELE BIAR TAU BOT HIDUP
    if not early and not trending and dex_found==0:
        msg=f"V14.5 - Scan {len(tickers)} - Sepi\nMarket lagi sepi min, gak ada yg 1%+ vol 50jt"
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",data={"chat_id":CHAT_ID,"text":msg})
        print(msg)
        return

    msg=f"V14.5 FINAL - Scan {len(tickers)}\n\n"
    if early:
        msg+=f"EARLY dari 1% ({len(early)})\n"
        for i,(p,c,v,d) in enumerate(early,1):
            msg+=f"{i}. {p} {c:.1f}% | {d:.0f}% dr low | {v/1e6:.0f}jt\n"
        msg+="\n"
    if trending:
        msg+=f"TRENDING ({len(trending)}) >10% [TELAT]\n"
        for i,(p,c,v) in enumerate(trending,1):
            msg+=f"{i}. {p} {c:.1f}% | {v/1e6:.0f}jt [TELAT]\n"
        msg+="\n"
    if dex_found>0:
        msg+=f"DEX RADAR {dex_found}\n"+dex_text
    print(msg)
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",data={"chat_id":CHAT_ID,"text":msg})

if __name__=="__main__":
    main()
