import requests, os, time, math
from collections import defaultdict
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('TELEGRAM_TOKEN') or os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID') or os.getenv('CHAT_ID') or os.getenv('TELEGRAM_CHAT')

def send(msg):
    try: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg}, timeout=15)
    except: pass

def get_candles(pair, limit=30):
    """FIX: pake /api/trades terus rakit jadi candle 5m - anti NO_DATA"""
    try:
        # 1. Coba tradingview dulu
        symbol = pair.replace('_','').upper()
        now = int(time.time())
        frm = now - 4*3600
        url = f"https://indodax.com/tradingview/history?symbol={symbol}&resolution=5&from={frm}&to={now}"
        r = requests.get(url, timeout=6).json()
        if r.get('s') == 'ok' and len(r.get('c',[])) >= 20:
            return [{'o':o,'h':h,'l':l,'c':c,'v':v} for o,h,l,c,v in zip(r['o'][-limit:], r['h'][-limit:], r['l'][-limit:], r['c'][-limit:], r['v'][-limit:])]

        # 2. Fallback: rakit dari trades (PASTI ADA)
        tr = requests.get(f"https://indodax.com/api/trades/{pair}", timeout=8).json()
        trades = tr.get('trades', [])[:150] # 150 trade terakhir
        if not trades: return []

        # Kelompokin per 5 menit
        buckets = defaultdict(list)
        for t in trades:
            ts = int(t['tid']) if 'tid' in t else int(time.time()) # tid bukan waktu, pake urutan
            # Indodax trades ga ada timestamp, jadi kita buat bucket dari urutan
            # Lebih simple: buat candle dari urutan trade
            buckets[ts // 5].append(float(t['price']))

        # Karena trades Indodax ga ada timestamp, kita buat candle manual dari urutan
        # 150 trades -> 30 candle (5 trades = 1 candle 5m)
        candles=[]
        for i in range(0, len(trades), 5):
            chunk = trades[i:i+5]
            if len(chunk)<2: continue
            prices=[float(x['price']) for x in chunk]
            vols=[float(x.get('amount',0)) for x in chunk]
            candles.append({'o':prices[-1],'h':max(prices),'l':min(prices),'c':prices[0],'v':sum(vols)})
            if len(candles)>=limit: break
        candles = candles[::-1] # balik biar terbaru di belakang
        return candles
    except Exception as e:
        # print(f"error {pair} {e}")
        return []

def bb_analyze(candles):
    if len(candles) < 15: return "NO_DATA", 99, 0, 0
    closes=[x['c'] for x in candles]
    ma20=sum(closes[-20:])/20 if len(closes)>=20 else sum(closes)/len(closes)
    std=math.sqrt(sum((x-ma20)**2 for x in closes[-20:])/20) if len(closes)>=20 else 0.01*ma20
    upper=ma20+2*std; lower=ma20-2*std
    squeeze=(upper-lower)/ma20*100
    last=candles[-1]; prev=candles[-2] if len(candles)>=2 else last
    avg_vol=sum(x['v'] for x in candles[:-1])/max(len(candles)-1,1)

    if last['c'] > upper and last['v'] > avg_vol*1.8:
        return "TRENDING_RUN", squeeze, (last['c']-upper)/upper*100, last['v']/max(avg_vol,1)
    wick=last['h']-last['l']; body=abs(last['c']-last['o'])
    if (last['c'] < lower or (wick > body*2.5 and last['c'] < last['o'])) and last['v'] > avg_vol*1.3:
        return "DUMP", squeeze, 0, 0
    if squeeze < 8 and prev['l'] <= lower and last['c'] > ma20 and last['c'] < upper*1.02:
        return "V_BOUNCE_ENTRY", squeeze, (last['c']-ma20)/ma20*100, last['v']/max(avg_vol,1)
    if squeeze < 8:
        return "SQUEEZE", squeeze, 0, 0
    return "NORMAL", squeeze, 0, 0

def main():
    data=requests.get("https://indodax.com/api/summaries",timeout=20).json()
    tickers=data['tickers']; prices_24h=data.get('prices_24h',{})
    BIG_CAP={"BTC","ETH","SOL","XRP","HYPE","BNB","DOGE","SHIB","PEPE","PENGU","USDT","USDC","AVAX","TRX","DOT","WIF","BONK"}
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
    candidates.sort(key=lambda x:x[3],reverse=True)
    top=candidates[:50]

    pre_early=[]; trending=[]; serok=[]; used=set()
    for pair,coin,chg,vol,dl,dh,last in top:
        pid=f"{coin}_IDR"
        if pid in used: continue
        sq_sum=dl+dh
        status="SKIP"; csq=0; vr=0
        if (0.1<=chg<=10 and sq_sum<22) or chg>=8:
            candles=get_candles(pair)
            status,csq,extra,vr=bb_analyze(candles)
            time.sleep(0.15)

        if status=="DUMP":
            used.add(pid); continue

        if len(pre_early)<5 and 0.1<=chg<=2.8 and sq_sum<15 and 2<=dl<=8 and 80_000_000<=vol<=400_000_000:
            if status in ("V_BOUNCE_ENTRY","SQUEEZE","NO_DATA","SKIP"):
                pre_early.append((pid,chg,vol,dl,sq_sum,status,csq,vr))
                used.add(pid); continue
            elif status=="DUMP": continue

        if len(trending)<5 and chg>=4:
            if status=="TRENDING_RUN" or (chg>20 and sq_sum>15):
                trending.append((pid,chg,vol,dl,status,csq,vr))
                used.add(pid); continue
            elif chg>15 and status in ("SKIP","NORMAL"):
                trending.append((pid,chg,vol,dl,"TRENDING_RUN",csq,vr))
                used.add(pid); continue

        if len(serok)<5 and -8<=chg<=-0.2 and 0<=dl<=2.5 and dh>=2:
            serok.append((pid,chg,vol,dl,dh)); used.add(pid); continue

    msg=f"🎯 V26.1 FIX NO_DATA - CANDLE READER\n\n"
    if pre_early:
        msg+=f"💣 PRE-EARLY V-BOUNCE ({len(pre_early)}):\n"
        for i,(p,c,v,dl,sq,st,csq,vr) in enumerate(pre_early,1):
            msg+=f"{i}. {p} {c:.1f}% | {dl:.0f}% low | sq {sq:.0f}% | {v/1e6:.0f}jt | {st} {csq:.1f}%\n"
        msg+="\n"
    if trending:
        msg+=f"🚀 TRENDING RUN ({len(trending)}):\n"
        for i,(p,c,v,dl,st,csq,vr) in enumerate(trending,1):
            msg+=f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {st} x{vr:.1f} | sq{csq:.0f}%\n"
        msg+="\n"
    if serok:
        msg+=f"💎 SEROK ({len(serok)}):\n"
        for i,(p,c,v,dl,dh) in enumerate(serok,1):
            msg+=f"{i}. {p} {c:.1f}% | {dl:.0f}% low | {v/1e6:.0f}jt\n"
    msg+=f"\n✅ Total {len(pre_early)+len(trending)+len(serok)} | JELLY= {len([x for x in pre_early if 'JELLY' in x[0]])} ZEREBRO MODE ON"
    print(msg); send(msg)

if __name__=="__main__": main()
