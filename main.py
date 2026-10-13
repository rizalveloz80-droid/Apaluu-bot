import requests, os
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def main():
    data=requests.get("https://indodax.com/api/summaries",timeout=20).json()
    tickers=data['tickers']
    prices_24h=data.get('prices_24h',{})

    entry=[]
    trending=[]
    serok=[]

    for pair,t in tickers.items():
        if not pair.endswith('_idr'):
            continue
        try:
            vol=float(t['vol_idr'])
            last=float(t['last'])
            low=float(t['low'])
            high=float(t['high'])
            key=pair.replace('_','') # FIX BUG V12
            p24=float(prices_24h.get(key,0))
            if p24==0:
                continue
            chg=(last-p24)/p24*100
            dist_low=(last-low)/low*100 if low>0 else 0
            dist_high=(high-last)/last*100 if last>0 else 0

            # 1. ENTRY 2-15% M/C NEW - ala V12.7 tapi ANTI-SHORT
            # vol >100jt, 5-45% dari low, masih jauh dari high
            if 2 <= chg <= 15 and vol >= 100_000_000 and 5 <= dist_low <= 45 and dist_high >= 3:
                entry.append((pair.upper(),chg,vol,dist_low))

            # 2. TRENDING PUMP >15% - ala V12.6
            if chg > 15 and vol >= 50_000_000:
                trending.append((pair.upper(),chg,vol))

            # 3. SEROK BAWAH MANTUL - ala V12.6 tapi SAFE kayak BR
            # -12% sampai -2%, vol >150jt, 0-5% dari low = siap mantul
            if -12 <= chg <= -2 and vol >= 150_000_000 and 0 <= dist_low <= 5:
                serok.append((pair.upper(),chg,vol,dist_low))

        except:
            continue

    entry=sorted(entry,key=lambda x:x[1],reverse=True)[:5]
    trending=sorted(trending,key=lambda x:x[1],reverse=True)[:5]
    serok=sorted(serok,key=lambda x:x[2],reverse=True)[:5]

    msg=f"🎯 V16 RACIK V12.6+V12.7 FIX - Scan {len(tickers)}\n\n"

    if entry:
        msg+=f"⚡ ENTRY 2-15% M/C NEW ({len(entry)}) [ANTI-SHORT]:\n"
        for i,(p,c,v,dl) in enumerate(entry,1):
            msg+=f"{i}. {p} {c:.1f}% | {dl:.0f}% dr low | {v/1e6:.0f}jt\n"
        msg+="\n"

    if trending:
        msg+=f"🔥 TRENDING PUMP >15% ({len(trending)}) [Hati2 Pucuk]:\n"
        for i,(p,c,v) in enumerate(trending,1):
            msg+=f"{i}. {p} {c:.1f}% | {v/1e6:.0f}jt\n"
        msg+="\n"

    if serok:
        msg+=f"💎 SEROK BAWAH MANTUL ({len(serok)}) [Kayak BR]:\n"
        for i,(p,c,v,dl) in enumerate(serok,1):
            msg+=f"{i}. {p} {c:.1f}% | {dl:.1f}% low | {v/1e6:.0f}jt\n"
        msg+="\n"

    if not entry and not trending and not serok:
        msg+=f"Sepi aman min, gak ada setup V12.6/V12.7 jam ini"

    print(msg)
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",data={"chat_id":CHAT_ID,"text":msg})

if __name__=="__main__":
    main()
