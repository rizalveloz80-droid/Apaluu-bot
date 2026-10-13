import requests, os, time
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
WATCHLIST_DEX = ["RSR","BR","ONT","W","STRK","BONK","FLOKI","PLUME"]

def main():
    data=requests.get("https://indodax.com/api/tickers",timeout=20).json()
    tickers=data['tickers']
    prices_24h=data.get('prices_24h',{})
    early=[]
    trending=[]
    serok_mantul=[]

    for pair,t in tickers.items():
        if not pair.endswith('_idr'):
            continue
        try:
            vol=float(t['vol_idr'])
            last=float(t['last'])
            low=float(t['low'])
            high=float(t['high'])
            p24=float(prices_24h.get(pair,0))
            if p24==0:
                continue
            chg=(last-p24)/p24*100
            dist_low=(last-low)/low*100 if low>0 else 0

            # 1. EARLY dari 1% TETEP ADA
            if 1.0 <= chg <= 9.9 and vol >= 10000000:
                early.append((pair.upper(),chg,vol,dist_low))

            # 2. TRENDING TELAT TETEP ADA
            if chg >= 10 and vol >= 10000000:
                trending.append((pair.upper(),chg,vol))

            # 3. SEROK MANTUL COMBO - YANG KAYAK BR
            # Minus kecil -1 sampai -8%, vol gede >300jt, udah di low 0-4% = siap mantul
            if -8 <= chg <= -1 and vol >= 300000000 and 0 <= dist_low <= 4:
                serok_mantul.append((pair.upper(),chg,vol,dist_low))

        except:
            continue

    early=sorted(early,key=lambda x:x[1],reverse=True)[:10]
    trending=sorted(trending,key=lambda x:x[1],reverse=True)[:5]
    serok_mantul=sorted(serok_mantul,key=lambda x:x[2],reverse=True)[:5]

    # DEX RADAR
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
            time.sleep(0.3)
        except:
            continue

    msg=f"🎯 V14.7 COMBO (1% + MANTUL + TELAT + DEX) - Scan {len(tickers)}\n\n"

    if serok_mantul:
        msg+=f"💎 SEROK MANTUL {len(serok_mantul)} (Siap pantul kayak BR)\n"
        for i,(p,c,v,d) in enumerate(serok_mantul,1):
            msg+=f"{i}. {p} {c:.1f}% | {d:.1f}% dr LOW | {v/1e6:.0f}jt [MANTUL]\n"
        msg+="\n"

    if early:
        msg+=f"⚡ EARLY dari 1% ({len(early)})\n"
        for i,(p,c,v,d) in enumerate(early,1):
            msg+=f"{i}. {p} {c:.1f}% | {d:.0f}% dr low | {v/1e6:.0f}jt\n"
        msg+="\n"

    if trending:
        msg+=f"🔥 TRENDING {len(trending)} [TELAT]\n"
        for i,(p,c,v) in enumerate(trending,1):
            msg+=f"{i}. {p} {c:.1f}% | {v/1e6:.0f}jt [TELAT]\n"
        msg+="\n"

    if dex_found>0:
        msg+=f"🚀 DEX RADAR {dex_found}\n"+dex_text+"\n"

    if not early and not trending and not serok_mantul and dex_found==0:
        msg+=f"Sepi min, gak ada setup 1% / mantul / trending jam ini"

    print(msg)
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",data={"chat_id":CHAT_ID,"text":msg})

if __name__=="__main__":
    main()
