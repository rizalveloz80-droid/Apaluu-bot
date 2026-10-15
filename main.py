import requests, os, time, math
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('TELEGRAM_TOKEN') or os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID') or os.getenv('CHAT_ID') or os.getenv('TELEGRAM_CHAT')

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg}, timeout=15)
    except: pass

def get_candles(pair):
    try:
        symbol = pair.replace('_','').upper()
        now = int(time.time())
        frm = now - 3*3600
        url = f"https://indodax.com/tradingview/history?symbol={symbol}&resolution=5&from={frm}&to={now}"
        r = requests.get(url, timeout=8).json()
        if r.get('s')!= 'ok' or len(r.get('c',[])) < 20:
            return []
        return [{'o':o,'h':h,'l':l,'c':c,'v':v} for o,h,l,c,v in zip(r['o'],r['h'],r['l'],r['c'],r['v'])]
    except:
        return []

def bb_analyze(candles):
    if len(candles) < 20:
        return "NO_DATA", 99, 0, 0
    closes = [x['c'] for x in candles]
    ma20 = sum(closes[-20:])/20
    std = math.sqrt(sum((x-ma20)**2 for x in closes[-20:])/20)
    upper = ma20 + 2*std
    lower = ma20 - 2*std
    squeeze = (upper-lower)/ma20*100
    last = candles[-1]
    prev = candles[-2]
    avg_vol = sum(x['v'] for x in candles[-20:-1])/19

    # 1. ZEREBRO MODE = TRENDING BREAKOUT
    if last['c'] > upper and last['v'] > avg_vol*2:
        return "TRENDING_RUN", squeeze, (last['c']-upper)/upper*100, last['v']/avg_vol

    # 2. DUMP WARNING = kayak JELLY 905k jam 08:40
    wick = last['h']-last['l']
    body = abs(last['c']-last['o'])
    if (last['c'] < lower or (wick > body*3 and last['c'] < last['o'])) and last['v'] > avg_vol*1.4:
        return "DUMP", squeeze, 0, last['v']/avg_vol

    # 3. PRE-EARLY V-BOUNCE = ZEREBRO 491 -> 562 -> 863!
    if squeeze < 7 and prev['l'] <= lower and last['c'] > ma20 and last['c'] < upper*1.01:
        return "V_BOUNCE_ENTRY", squeeze, (last['c']-ma20)/ma20*100, last['v']/avg_vol

    if squeeze < 7:
        return "SQUEEZE", squeeze, 0, 0

    return "NORMAL", squeeze, 0, 0

def main():
    data = requests.get("https://indodax.com/api/summaries", timeout=20).json()
    tickers = data['tickers']
    prices_24h = data.get('prices_24h',{})
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
    top=candidates[:60]

    pre_early=[]; trending=[]; dump_list=[]; serok=[]; used=set()

    for pair,coin,chg,vol,dl,dh,last in top:
        pid=f"{coin}_IDR"
        if pid in used: continue
        squeeze_sum=dl+dh

        # Cuma cek candle untuk yang berpotensi PRE-EARLY / TRENDING
        status="SKIP"; csq=0; vol_ratio=0
        if (0.1<=chg<=10 and squeeze_sum<20) or chg>15:
            candles=get_candles(pair)
            status,csq,extra,vol_ratio=bb_analyze(candles)
            time.sleep(0.2)

        if status=="DUMP":
            dump_list.append((pid,chg,csq))
            used.add(pid); continue

        if len(pre_early)<5 and 0.1<=chg<=2.8 and squeeze_sum<15 and 2<=dl<=8 and 80_000_000<=vol<=400_000_000:
            if status in ("V_BOUNCE_ENTRY","SQUEEZE","NO_DATA","SKIP"):
                pre_early.append((pid,chg,vol,dl,squeeze_sum,status,csq,vol_ratio))
                used.add(pid); continue

        if len(trending)<5 and chg>=4 and vol>=120_000_000:
            if status=="TRENDING_RUN" or (chg>15 and status!="DUMP"):
                trending.append((pid,chg,vol,dl,status,csq,vol_ratio))
                used.add(pid); continue

        if len(serok)<5 and -8<=chg<=-0.2 and 0<=dl<=2.5 and dh>=2 and vol>=100_000_000:
            serok.append((pid,chg,vol,dl,dh)); used.add(pid); continue

    msg=f"🎯 V26.0 CANDLE READER - ANTI BUTA\n\n"
    if pre_early:
        msg+=f"💣 PRE-EARLY V-BOUNCE ({len(pre_early)}):\n"
        for i,(p,c,v,dl,sq,st,csq,vr) in enumerate(pre_early,1):
            msg+=f"{i}. {p} {c:.1f}% | {dl:.0f}% low | sq {sq:.0f}% | {v/1e6:.0f}jt | {st} {csq:.1f}%\n"
        msg+="\n"
    if trending:
        msg+=f"🚀 TRENDING RUN - HOLD JANGAN ENTRY ({len(trending)}):\n"
        for i,(p,c,v,dl,st,csq,vr) in enumerate(trending,1):
            msg+=f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {st} | Vol x{vr:.1f}\n"
        msg+="\n"
    if dump_list:
        msg+=f"⚠️ DUMP WARNING ({len(dump_list)}):\n"
        for i,(p,c,sq) in enumerate(dump_list,1):
            msg+=f"{i}. {p} {c:.1f}% | {sq:.1f}%\n"
        msg+="\n"
    if serok:
        msg+=f"💎 SEROK GOLDEN ({len(serok)}):\n"
        for i,(p,c,v,dl,dh) in enumerate(serok,1):
            msg+=f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {dh:.0f}% high | {v/1e6:.0f}jt\n"

    msg+=f"\n✅ Total {len(pre_early)+len(trending)+len(serok)} | ZEREBRO MODE ON"
    print(msg)
    send(msg)

if __name__=="__main__":
    main()
