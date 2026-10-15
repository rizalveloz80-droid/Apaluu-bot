import requests, os, time, random
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('TELEGRAM_TOKEN') or os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID') or os.getenv('CHAT_ID') or os.getenv('TELEGRAM_CHAT')

def send(msg):
    try: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg}, timeout=15)
    except: pass

def smart_candle_v265(chg, dl, dh, vol):
    """V26.5 DUAL FILTER + ANTI-BLOCK 1000% - NANGKEP SN SEBELUM +23%"""
    sq = dl + dh

    # 🚨 GAINERS MENDADAK - ZEREBRO 58% & PUFFER 108% - JANGAN KEJAR
    if chg >= 40 and vol >= 100_000_000:
        return "GAINERS_MENDADAK", sq, vol/250_000_000

    # 🚀 TRENDING BRONZE - SN 23,51% & ARC 42% - udah terbang
    if chg >= 22 and dl >= 15 and vol >= 150_000_000:
        return "TRENDING_BRONZE", sq, vol/250_000_000
    if chg >= 10 and dl >= 12 and dh <= 28 and vol >= 150_000_000:
        return "TRENDING_BRONZE", sq, vol/250_000_000

    # DUMP - UCJL -36% - calon GOLD besok
    if chg <= -5 and dh >= 8 and dl <= 2.5:
        return "DUMP", sq, 0

    # 💣 GOLD TIER - META 0,7% sq 4% & NOVA 1,1% sq 8% = JACKPOT +49% - TRIO LU!
    if sq < 12 and 2 <= dl <= 9 and 0.1 <= chg <= 3.5 and 70_000_000 <= vol <= 450_000_000:
        return "V_BOUNCE_GOLD", sq, vol/250_000_000

    # ⚡ SILVER TIER - BARU! - DUSK 11,3% & SN 8-12% SEBELUM JADI 23% - EARLY!
    if sq < 18 and 2 <= dl <= 12 and 0.1 <= chg <= 8 and 70_000_000 <= vol <= 600_000_000:
        return "V_BOUNCE_SILVER", sq, vol/250_000_000

    # SQUEEZE
    if sq < 10 and 1 <= dl <= 12:
        return "SQUEEZE", sq, 0

    return "NORMAL", sq, 0

def main():
    # ANTI-BLOCK 1000% - JITTER + USER-AGENT
    time.sleep(random.uniform(0.5, 2.5))
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    try:
        data = requests.get("https://indodax.com/api/summaries", timeout=20, headers=headers).json()
    except:
        time.sleep(5)
        data = requests.get("https://indodax.com/api/summaries", timeout=20, headers=headers).json()

    tickers = data['tickers']; prices_24h = data.get('prices_24h',{})
    BIG_CAP = {"BTC","ETH","SOL","XRP","HYPE","BNB","DOGE","SHIB","PEPE","PENGU","USDT","USDC","AVAX","TRX","DOT","WIF","BONK"}
    candidates=[]
    for pair,t in tickers.items():
        if not pair.endswith('_idr'): continue
        try:
            vol=float(t['vol_idr']); last=float(t['last']); low=float(t['low']); high=float(t['high'])
            key=pair.replace('_',''); p24=float(prices_24h.get(key,0))
            if p24==0 or low==0 or vol<60_000_000: continue
            chg=(last-p24)/p24*100; dl=(last-low)/low*100; dh=(high-last)/last*100 if last else 0
            coin=pair.replace('_idr','').upper()
            if coin in BIG_CAP: continue
            candidates.append((pair,coin,chg,vol,dl,dh,last))
        except: continue
    candidates.sort(key=lambda x:x[3], reverse=True)
    top=candidates[:120] # dari 100 jadi 120 biar SN 241jt ke-detect!

    gold=[]; silver=[]; bronze=[]; gainers=[]; dump_list=[]; serok=[]; used=set()
    for pair,coin,chg,vol,dl,dh,last in top:
        pid=f"{coin}_IDR"
        if pid in used: continue
        status,sq,vr = smart_candle_v265(chg,dl,dh,vol)

        if status=="GAINERS_MENDADAK" and len(gainers)<3:
            gainers.append((pid,chg,vol,dl,sq,vr)); used.add(pid); continue
        if status=="DUMP" and len(dump_list)<3:
            dump_list.append((pid,chg,sq)); used.add(pid); continue
        if status=="V_BOUNCE_GOLD" and len(gold)<5:
            gold.append((pid,chg,vol,dl,sq,vr)); used.add(pid); continue
        if status=="V_BOUNCE_SILVER" and len(silver)<5:
            silver.append((pid,chg,vol,dl,sq,vr)); used.add(pid); continue
        if status=="TRENDING_BRONZE" and len(bronze)<5:
            bronze.append((pid,chg,vol,dl,sq,vr)); used.add(pid); continue
        if len(serok)<5 and -8<=chg<=-0.2 and 0<=dl<=2.5 and dh>=2:
            serok.append((pid,chg,vol,dl,dh)); used.add(pid); continue

    msg=f"🎯 V26.5 DUAL + ANTI-BLOCK 1000%\n\n"
    if gold:
        msg+=f"💣 GOLD sq<12% JACKPOT ({len(gold)}):\n"
        for i,(p,c,v,dl,sq,vr) in enumerate(gold,1):
            msg+=f"{i}. {p} {c:.1f}% | {dl:.0f}% low | sq {sq:.0f}% | {v/1e6:.0f}jt | GOLD x{vr:.1f}\n"
        msg+="\n"
    if silver:
        msg+=f"⚡ SILVER sq<18% EARLY ({len(silver)}):\n"
        for i,(p,c,v,dl,sq,vr) in enumerate(silver,1):
            msg+=f"{i}. {p} {c:.1f}% | {dl:.0f}% low | sq {sq:.0f}% | {v/1e6:.0f}jt | SILVER x{vr:.1f}\n"
        msg+="\n"
    if bronze:
        msg+=f"💨 BRONZE TRENDING ({len(bronze)}):\n"
        for i,(p,c,v,dl,sq,vr) in enumerate(bronze,1):
            msg+=f"{i}. {p} {c:.1f}% | {dl:.0f}% low | sq {sq:.0f}% | Vol x{vr:.1f} | {v/1e6:.0f}jt\n"
        msg+="\n"
    if gainers:
        msg+=f"🚨 GAINERS JANGAN KEJAR! ({len(gainers)}):\n"
        for i,(p,c,v,dl,sq,vr) in enumerate(gainers,1):
            msg+=f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {v/1e6:.0f}jt | TUNGGU -30%\n"
        msg+="\n"
    if serok:
        msg+=f"💎 SEROK ({len(serok)}):\n"
        for i,(p,c,v,dl,dh) in enumerate(serok,1):
            msg+=f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {v/1e6:.0f}jt\n"

    msg+=f"\n✅ Total {len(gold)+len(silver)+len(bronze)+len(serok)+len(gainers)} | ANTI-BLOCK 1000% (Jitter+UA+120coins)"
    print(msg); send(msg)

if __name__=="__main__": main()
