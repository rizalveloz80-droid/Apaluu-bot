import requests, os
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def main():
    data=requests.get("https://indodax.com/api/summaries",timeout=20).json()
    tickers=data['tickers']
    prices_24h=data.get('prices_24h',{})

    early=[]
    trending_lanjutan=[]
    trending_pucuk=[]
    serok=[]

    for pair,t in tickers.items():
        if not pair.endswith('_idr'):
            continue
        try:
            vol=float(t['vol_idr'])
            last=float(t['last'])
            low=float(t['low'])
            high=float(t['high'])
            key=pair.replace('_','')
            p24=float(prices_24h.get(key,0))
            if p24==0: continue
            chg=(last-p24)/p24*100
            dist_low=(last-low)/low*100 if low>0 else 0
            dist_high=(high-last)/last*100 if last>0 else 0

            # 1. EARLY 1.5-8% - Masuk Duluan (V13) - ANTI SHORT
            if 1.5 <= chg <= 8 and vol >= 80_000_000 and 5 <= dist_low <= 50:
                early.append((pair.upper(),chg,vol,dist_low))

            # 2. TRENDING LANJUTAN 12-25% - Kayak CNG 18.7% TADI MALAM!
            # Ini yang tadi lu anggap TELAT tapi malah bagus!
            # Ciri: vol >100jt, masih 15-70% dari low, masih >5% dari high
            if 12 <= chg <= 30 and vol >= 100_000_000 and 15 <= dist_low <= 75 and dist_high >= 3:
                trending_lanjutan.append((pair.upper(),chg,vol,dist_low))

            # 3. TRENDING PUCUK >35% - Udah beneran telat, hati2
            if chg > 35:
                trending_pucuk.append((pair.upper(),chg,vol))

            # 4. SEROK BAWAH MANTUL (V13)
            if -20 <= chg <= -2 and vol >= 150_000_000 and 0 <= dist_low <= 7:
                serok.append((pair.upper(),chg,vol,dist_low))

        except: continue

    early=sorted(early,key=lambda x:x[1],reverse=True)[:5]
    trending_lanjutan=sorted(trending_lanjutan,key=lambda x:x[2],reverse=True)[:5]
    trending_pucuk=sorted(trending_pucuk,key=lambda x:x[1],reverse=True)[:4]
    serok=sorted(serok,key=lambda x:x[2],reverse=True)[:5]

    msg=f"🎯 V17 RACIK CNG - Scan {len(tickers)} (Belajar dari CNG 18%->50%)\n\n"

    if early:
        msg+=f"⚡ EARLY 1.5-8% Masuk Duluan ({len(early)}):\n"
        for i,(p,c,v,dl) in enumerate(early,1):
            msg+=f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {v/1e6:.0f}jt\n"
        msg+="\n"

    if trending_lanjutan:
        msg+=f"🚀 TRENDING LANJUTAN 12-30% [CNG KEMARIN] ({len(trending_lanjutan)}):\n"
        for i,(p,c,v,dl) in enumerate(trending_lanjutan,1):
            msg+=f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {v/1e6:.0f}jt | GAS!\n"
        msg+="\n"

    if trending_pucuk:
        msg+=f"🔥 TRENDING PUCUK >35% [Hati2] ({len(trending_pucuk)}):\n"
        for i,(p,c,v) in enumerate(trending_pucuk,1):
            msg+=f"{i}. {p} {c:.1f}% | {v/1e6:.0f}jt [PUCUK]\n"
        msg+="\n"

    if serok:
        msg+=f"💎 SEROK BAWAH ({len(serok)}):\n"
        for i,(p,c,v,dl) in enumerate(serok,1):
            msg+=f"{i}. {p} {c:.1f}% | {dl:.1f}% low | {v/1e6:.0f}jt\n"
        msg+="\n"

    print(msg)
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",data={"chat_id":CHAT_ID,"text":msg})

if __name__=="__main__":
    main()
