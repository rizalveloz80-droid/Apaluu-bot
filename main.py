import requests, os

BLOCKED = [
    'BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','PAXG_IDR',
    'LUNA_IDR','LUNC_IDR','FTM_IDR'
]

def get_data():
    try:
        tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers',{})
        summ = requests.get("https://indodax.com/api/summaries", timeout=10).json()
        change_24h = {k: float(v.get('percent_change',0)) for k,v in summ.get('tickers',{}).items()}
        out=[]
        for pair,d in tickers.items():
            if not pair.endswith('_idr'): continue
            if pair.upper() in BLOCKED: continue
            try:
                last=float(d['last']); low=float(d['low']); high=float(d['high']); vol=float(d['vol_idr'])
                vol_bn=vol/1e9
                if vol_bn < 0.15: continue
                chg24=change_24h.get(pair,0)
                if chg24 < -4: continue # UNMD -18% ALT -35% AUTO BUANG!
                if chg24 < 0.5: continue
                sisa=(high-last)/last*100 if last else 0
                rg=(high-low)/low*100 if low else 0
                
                # ANTI PUCUK: sisa <8% BUANG! BMT 40.5% sisa 4% GA MASUK!
                if sisa < 8: continue
                if sisa > 70: continue
                if rg > 80: continue

                out.append({'sym':pair.upper(),'chg':chg24,'sisa':sisa,'range':rg,'vol':vol_bn})
            except: continue
        return out
    except:
        return []

def scan(data):
    bottom=[]; early=[]
    for k in data:
        v=k['vol']; c=k['chg']; s=k['sisa']
        # BMT malem: 2.7% sisa 42% Vol 0.12Bn -> MASUK! BMT siang 40.5% sisa 4% -> KE BLOCK!
        if 0.5 <= c <= 12 and 15 <= s <= 65:
            bottom.append(k)
        elif 12 <= c <= 30 and 12 <= s <= 50:
            early.append(k)
    return (
        sorted(bottom, key=lambda x: (x['vol'], x['sisa']), reverse=True)[:5],
        sorted(early, key=lambda x: x['vol'], reverse=True)[:5]
    )

def kirim(msg):
    token=os.getenv('TELE_TOKEN'); chat=os.getenv('TELE_CHAT_ID')
    if not token or not chat:
        print(msg); return
    try:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id":chat,"text":msg}, timeout=15)
    except: pass

if __name__=="__main__":
    data=get_data()
    b, e = scan(data)
    msg = f"V25.2 EARLY SEGAR Data {len(data)} | B{len(b)} E{len(e)}\n\n"
    if b:
        msg += "BOTTOM SEGAR (entry disini!)\n"
        for k in b:
            msg += f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg += "\n"
    if e:
        msg += "EARLY FRESH (jangan sampe telat!)\n"
        for k in e:
            msg += f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg += "\n"
    if not b and not e:
        msg += "Ga ada yang segar, semua udah pucuk kayak BMT 40% sisa 4%! Tunggu pump baru!\n"
    print(msg)
    kirim(msg)
