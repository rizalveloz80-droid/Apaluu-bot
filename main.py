import requests, os, time, random
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('TELEGRAM_TOKEN') or os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID') or os.getenv('CHAT_ID') or os.getenv('TELEGRAM_CHAT')

def send(msg):
    try: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg}, timeout=15)
    except: pass

def smart_candle_v266(chg, dl, dh, vol):
    """V26.6 - NANGKEP SEMUA KOIN DARI BAWAH SEBELUM +25% KAYAK TIA KMNO"""
    sq = dl + dh

    # ===== BARU! INI KUNCI BIAR GA TAU-TAU UDAH TINGGI! =====
    # PRE_TRENDING - KOIN SEBELUM TERBANG - VOL KECIL TAPI SQ SEMPIT!
    # TIA & KMNO pas -12% vol 30jt sq 5% - INI KEDETEK DISINI!
    if 0 <= dl <= 3.5 and sq < 9 and -20 <= chg <= 2.5 and 10_000_000 <= vol <= 130_000_000:
        return "PRE_TRENDING", sq, vol/250_000_000

    # SEROK DALEM - DIPERLEBAR! DARI -8% JADI -20%!
    # TIA KMNO sebelum pump -12% sampai -18% - DULU GA MASUK, SEKARANG MASUK!
    if -20 <= chg <= -0.2 and 0 <= dl <= 3 and 1 <= sq <= 12:
        return "SEROK_DALEM", sq, vol/250_000_000

    # 🚨 GAINERS - POND +45% - UDAH TERBANG, JANGAN KEJAR
    if chg >= 35 and vol >= 100_000_000:
        return "GAINERS_MENDADAK", sq, vol/250_000_000

    # 🚀 TRENDING BRONZE - KMNO 29% & TIA 24% - UDAH TERBANG
    if chg >= 22 and dl >= 15 and vol >= 150_000_000:
        return "TRENDING_BRONZE", sq, vol/250_000_000
    if chg >= 10 and dl >= 12 and dh <= 28 and vol >= 150_000_000:
        return "TRENDING_BRONZE", sq, vol/250_000_000

    # 💣 GOLD V25.3 - LINK 0.5% sq7% x1.7 - JACKPOT +4-6%
    if sq < 12 and 2 <= dl <= 9 and 0.1 <= chg <= 3.5 and 50_000_000 <= vol <= 500_000_000:
        return "V_BOUNCE_GOLD", sq, vol/250_000_000

    # ⚡ SILVER V25.5 - XPL 4.9% sq13% - EARLY BEFORE GOLD
    if sq < 18 and 2 <= dl <= 12 and 0.1 <= chg <= 8 and 50_000_000 <= vol <= 600_000_000:
        return "V_BOUNCE_SILVER", sq, vol/250_000_000

    return "NORMAL", sq, 0

def main():
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
            # DARI 60JT JADI 10JT! BIAR KOIN KECIL KAYAK TIA KMNO SEBELUM PUMP KEDETEK!
            if p24==0 or low==0 or vol<10_000_000: continue
            chg=(last-p24)/p24*100; dl=(last-low)/low*100; dh=(high-last)/last*100 if last else 0
            coin=pair.replace('_idr','').upper()
            if coin in BIG_CAP: continue
            candidates.append((pair,coin,chg,vol,dl,dh,last))
        except: continue
    candidates.sort(key=lambda x:x[3], reverse=True)
    top=candidates[:200] # DARI 120 JADI 200! BIAR VOL KECIL MASUK!

    # === SETTING V26.6 RANK 15 DUAL 8 EARLY + SEROK DALEM ===
    GOLD_COUNT = 5
    SILVER_COUNT = 3
    PRE_TRENDING_COUNT = 2 # BUAT NANGKEP CALON TIA KMNO DARI BAWAH!
    BRONZE_COUNT = 0 # HAPUS BRONZE YANG UDAH TERBANG +29%!
    GAINERS_COUNT = 0 # HAPUS GAINERS +45%!
    SEROK_DALEM_COUNT = 5 # SEROK DIPERLEBAR -20%!

    gold=[]; silver=[]; pre_trending=[]; bronze=[]; gainers=[]; serok=[]; used=set()
    for pair,coin,chg,vol,dl,dh,last in top:
        pid=f"{coin}_IDR"
        if pid in used: continue
        status,sq,vr = smart_candle_v266(chg,dl,dh,vol)

        if status=="GAINERS_MENDADAK" and len(gainers)<GAINERS_COUNT:
            gainers.append((pid,chg,vol,dl,sq,vr)); used.add(pid); continue
        if status=="V_BOUNCE_GOLD" and len(gold)<GOLD_COUNT:
            gold.append((pid,chg,vol,dl,sq,vr)); used.add(pid); continue
        if status=="V_BOUNCE_SILVER" and len(silver)<SILVER_COUNT:
            silver.append((pid,chg,vol,dl,sq,vr)); used.add(pid); continue
        if status=="PRE_TRENDING" and len(pre_trending)<PRE_TRENDING_COUNT:
            pre_trending.append((pid,chg,vol,dl,sq,vr)); used.add(pid); continue
        if status=="TRENDING_BRONZE" and len(bronze)<BRONZE_COUNT:
            bronze.append((pid,chg,vol,dl,sq,vr)); used.add(pid); continue
        if status=="SEROK_DALEM" and len(serok)<SEROK_DALEM_COUNT:
            serok.append((pid,chg,vol,dl,sq,vr)); used.add(pid); continue

    gold.sort(key=lambda x: x[5], reverse=True)
    silver.sort(key=lambda x: x[5], reverse=True)
    pre_trending.sort(key=lambda x: x[1]) # paling dalem dulu
    serok.sort(key=lambda x: x[1])

    msg=f"🎯 V26.6 RANK 15 DUAL 8 EARLY + SEROK DALEM\n"
    msg+=f"ANTI-BLOCK 1000% | Scan 200 coins | Vol min 10jt\n\n"

    rank_num = 1
    if gold:
        msg+=f"💣 GOLD V25.3 JACKPOT ({len(gold)}):\n"
        for p,c,v,dl,sq,vr in gold:
            msg+=f"{rank_num}. {p} {c:.1f}% | {dl:.0f}% low | sq {sq:.0f}% | {v/1e6:.0f}jt | GOLD x{vr:.1f}\n"
            rank_num+=1
        msg+="\n"
    if silver:
        msg+=f"⚡ SILVER V25.5 EARLY ({len(silver)}):\n"
        for p,c,v,dl,sq,vr in silver:
            msg+=f"{rank_num}. {p} {c:.1f}% | {dl:.0f}% low | sq {sq:.0f}% | {v/1e6:.0f}jt | SILVER x{vr:.1f}\n"
            rank_num+=1
        msg+="\n"
    if pre_trending:
        msg+=f"🔥 PRE_TRENDING CALON TIA KMNO ({len(pre_trending)}):\n"
        for p,c,v,dl,sq,vr in pre_trending:
            msg+=f"{rank_num}. {p} {c:.1f}% | {dl:.0f}% low | sq {sq:.0f}% | {v/1e6:.0f}jt | CALON +25%!\n"
            rank_num+=1
        msg+="\n"
    if serok:
        msg+=f"💎 SEROK DALEM -20% ({len(serok)}):\n"
        for p,c,v,dl,sq,vr in serok:
            msg+=f"{rank_num}. {p} {c:.1f}% | {dl:.0f}% low | sq {sq:.0f}% | {v/1e6:.0f}jt | DALEM!\n"
            rank_num+=1

    msg+=f"\n✅ Total {len(gold)+len(silver)+len(pre_trending)+len(serok)} RANK | 8 EARLY + 7 BAWAH | NANGKEP DARI BAWAH!"
    print(msg); send(msg)

if __name__=="__main__": main()
