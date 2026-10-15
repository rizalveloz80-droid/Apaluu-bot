import requests, os
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('TELEGRAM_TOKEN') or os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID') or os.getenv('CHAT_ID') or os.getenv('TELEGRAM_CHAT')

def send(msg):
    try: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg}, timeout=15)
    except: pass

def smart_candle(chg, dl, dh, vol):
    """V26.4 SMART CANDLE + GAINERS DARURAT - NO API BLOCK"""
    sq = dl + dh

    # MODUL 2: GAINERS DARURAT - buat CYBER +61% yang miss dari jam 4 subuh
    if chg >= 40 and vol >= 100_000_000:
        return "GAINERS_MENDADAK", sq, vol/250_000_000

    # TRENDING RUN
    if chg >= 25 and dl >= 30 and vol >= 200_000_000:
        return "TRENDING_RUN", sq, vol/250_000_000
    if chg >= 10 and dl >= 15 and dh <= 25:
        return "TRENDING_RUN", sq, vol/250_000_000
    # DUMP
    if chg <= -5 and dh >= 8 and dl <= 2:
        return "DUMP", sq, 0
    # V-BOUNCE ENTRY - buat JELLY & UAI & PUFFER 463
    if sq < 12 and 2 <= dl <= 9 and 0.1 <= chg <= 3.5 and 80_000_000 <= vol <= 400_000_000:
        return "V_BOUNCE_ENTRY", sq, vol/250_000_000
    if sq < 10 and 1 <= dl <= 12:
        return "SQUEEZE", sq, 0
    return "NORMAL", sq, 0

def main():
    data = requests.get("https://indodax.com/api/summaries", timeout=20).json()
    tickers = data['tickers']; prices_24h = data.get('prices_24h',{})
    BIG_CAP = {"BTC","ETH","SOL","XRP","HYPE","BNB","DOGE","SHIB","PEPE","PENGU","USDT","USDC","AVAX","TRX","DOT","WIF","BONK"}
    candidates=[]
    for pair,t in tickers.items():
        if not pair.endswith('_idr'): continue
        try:
            vol=float(t['vol_idr']); last=float(t['last']); low=float(t['low']); high=float(t['high'])
            key=pair.replace('_',''); p24=float(prices_24h.get(key,0))
            if p24==0 or low==0 or vol<70_000_000: continue
            chg=(last-p24)/p24*100; dl=(last-low)/low*100; dh=(high-last)/last*100 if last else 0
            coin=pair.replace('_idr','').upper()
            if coin in BIG_CAP: continue
            candidates.append((pair,coin,chg,vol,dl,dh,last))
        except: continue
    candidates.sort(key=lambda x:x[3], reverse=True)
    top=candidates[:100]

    pre_early=[]; trending=[]; serok=[]; dump_list=[]; gainers=[]; used=set()
    for pair,coin,chg,vol,dl,dh,last in top:
        pid=f"{coin}_IDR"
        if pid in used: continue
        status,sq,vr = smart_candle(chg,dl,dh,vol)

        if status=="GAINERS_MENDADAK" and len(gainers)<3:
            gainers.append((pid,chg,vol,dl,sq,vr)); used.add(pid); continue

        if status=="DUMP" and len(dump_list)<3:
            dump_list.append((pid,chg,sq)); used.add(pid); continue

        if len(pre_early)<5 and status=="V_BOUNCE_ENTRY":
            pre_early.append((pid,chg,vol,dl,sq,vr))
            used.add(pid); continue

        if len(trending)<5 and status=="TRENDING_RUN":
            trending.append((pid,chg,vol,dl,sq,vr))
            used.add(pid); continue

        if len(serok)<5 and -8<=chg<=-0.2 and 0<=dl<=2.5 and dh>=2:
            serok.append((pid,chg,vol,dl,dh)); used.add(pid); continue

    msg=f"🎯 V26.4 COMBO + GAINERS DARURAT\n\n"
    if pre_early:
        msg+=f"💣 PRE-EARLY V-BOUNCE ({len(pre_early)}):\n"
        for i,(p,c,v,dl,sq,vr) in enumerate(pre_early,1):
            msg+=f"{i}. {p} {c:.1f}% | {dl:.0f}% low | sq {sq:.0f}% | {v/1e6:.0f}jt | V_BOUNCE x{vr:.1f}\n"
        msg+="\n"
    if trending:
        msg+=f"🚀 TRENDING RUN ({len(trending)}):\n"
        for i,(p,c,v,dl,sq,vr) in enumerate(trending,1):
            msg+=f"{i}. {p} {c:.1f}% | {dl:.0f}% low | sq {sq:.0f}% | Vol x{vr:.1f} | {v/1e6:.0f}jt\n"
        msg+="\n"
    if gainers:
        msg+=f"🚨 GAINERS MENDADAK - JANGAN KEJAR! ({len(gainers)}):\n"
        for i,(p,c,v,dl,sq,vr) in enumerate(gainers,1):
            msg+=f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {v/1e6:.0f}jt | TUNGGU KOREKSI -30%\n"
        msg+="\n"
    if serok:
        msg+=f"💎 SEROK ({len(serok)}):\n"
        for i,(p,c,v,dl,dh) in enumerate(serok,1):
            msg+=f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {v/1e6:.0f}jt\n"

    msg+=f"\n✅ Total {len(pre_early)+len(trending)+len(serok)+len(gainers)} | ANTI-BLOCK MODE (60 detik)"
    print(msg); send(msg)

if __name__=="__main__": main()
