import requests, os
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def main():
    data=requests.get("https://indodax.com/api/summaries",timeout=20).json()
    tickers=data['tickers']
    prices_24h=data.get('prices_24h',{})

    fresh=[]
    early=[]
    ijo_trending=[]
    trending_lanjutan=[]
    serok=[]

    for pair,t in tickers.items():
        if not pair.endswith('_idr'): continue
        try:
            vol=float(t['vol_idr'])
            last=float(t['last'])
            low=float(t['low'])
            high=float(t['high'])
            key=pair.replace('_','') # FIX BUG TIA/POL
            p24=float(prices_24h.get(key,0))
            if p24==0 or low==0 or last==0: continue
            chg=(last-p24)/p24*100
            dist_low=(last-low)/low*100 if low>0 else 0
            dist_high=(high-last)/last*100 if last>0 else 0

            # ANTI PUCUK PAS - jangan beli pas di high persis
            if dist_high < 0.3: continue

            # 1. FRESH PUMP 0.5-3.5% (V5.5) - Baru melek, belum banyak yang liat
            if 0.5 <= chg <= 3.5 and vol >= 50_000_000 and 1 <= dist_low <= 25:
                fresh.append((pair.upper(),chg,vol,dist_low))

            # 2. EARLY 1.5-8% (V17) - Masuk duluan
            if 1.5 <= chg <= 8 and vol >= 80_000_000 and 5 <= dist_low <= 50:
                early.append((pair.upper(),chg,vol,dist_low,dist_high))

            # 3. IJO ONLY TRENDING 3-15% (V6 FINAL) - Vol gede ijo stabil
            if 3 <= chg <= 15 and vol >= 120_000_000 and 5 <= dist_low <= 60 and dist_high >= 1:
                ijo_trending.append((pair.upper(),chg,vol,dist_low))

            # 4. TRENDING LANJUTAN 12-30% CNG (V17) - Masih ada bensin
            if 12 <= chg <= 30 and vol >= 100_000_000 and 10 <= dist_low <= 75 and dist_high >= 2:
                trending_lanjutan.append((pair.upper(),chg,vol,dist_low))

            # 5. SEROK BAWAH V18 BARU - Biar gak itu-itu aja! Longgarin
            # Dulu -20 to -2 + dist_low 0-7 + vol 150jt = sepi
            # Sekarang -10 to -0.5 + dist_low 0-8 + vol 80jt = rame!
            if -10 <= chg <= -0.5 and vol >= 80_000_000 and 0 <= dist_low <= 8 and dist_high <= 12:
                serok.append((pair.upper(),chg,vol,dist_low,dist_high))

        except: continue

    # Mix 20 koin
    fresh=sorted(fresh,key=lambda x:x[2],reverse=True)[:4]
    early=sorted(early,key=lambda x:x[2],reverse=True)[:4]
    ijo_trending=sorted(ijo_trending,key=lambda x:x[2],reverse=True)[:4]
    trending_lanjutan=sorted(trending_lanjutan,key=lambda x:x[2],reverse=True)[:4]
    serok=sorted(serok,key=lambda x:x[2],reverse=True)[:4]

    msg=f"🎯 V18 SUPER MIX 20 KOIN - {len(tickers)} Scan (No Bug)\n\n"

    if fresh:
        msg+=f"🌱 FRESH PUMP 0.5-3.5% (V5.5) ({len(fresh)}):\n"
        for i,(p,c,v,dl) in enumerate(fresh,1):
            msg+=f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {v/1e6:.0f}jt\n"
        msg+="\n"

    if early:
        msg+=f"⚡ EARLY 1.5-8% (V17) ({len(early)}):\n"
        for i,(p,c,v,dl,dh) in enumerate(early,1):
            msg+=f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {v/1e6:.0f}jt\n"
        msg+="\n"

    if ijo_trending:
        msg+=f"📈 IJO ONLY TRENDING 3-15% (V6) ({len(ijo_trending)}):\n"
        for i,(p,c,v,dl) in enumerate(ijo_trending,1):
            msg+=f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {v/1e6:.0f}jt\n"
        msg+="\n"

    if trending_lanjutan:
        msg+=f"🚀 TRENDING LANJUTAN 12-30% [CNG] ({len(trending_lanjutan)}):\n"
        for i,(p,c,v,dl) in enumerate(trending_lanjutan,1):
            msg+=f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {v/1e6:.0f}jt | GAS!\n"
        msg+="\n"

    if serok:
        msg+=f"💎 SEROK BAWAH BARU -10 to -0.5% ({len(serok)}):\n"
        for i,(p,c,v,dl,dh) in enumerate(serok,1):
            msg+=f"{i}. {p} {c:.1f}% | {dl:.1f}% low | -{dh:.1f}% high | {v/1e6:.0f}jt\n"
        msg+="\n"

    # Kalo sepi kasih tau
    total = len(fresh)+len(early)+len(ijo_trending)+len(trending_lanjutan)+len(serok)
    if total == 0:
        msg+=f"😴 Sepi min, market lagi galau, jangan maksa entry!\n"

    print(msg)
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",data={"chat_id":CHAT_ID,"text":msg})

if __name__=="__main__":
    main()
