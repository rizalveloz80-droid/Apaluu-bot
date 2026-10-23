import requests, os

BLOCKED = ['BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','PAXG_IDR','LUNA_IDR','LUNC_IDR','FTM_IDR']

def get_data():
    tickers={}
    change_24h={}
    try:
        tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers',{})
    except:
        return []
    try:
        summ = requests.get("https://indodax.com/api/summaries", timeout=10).json()
        for k,v in summ.get('tickers',{}).items():
            try: change_24h[k]=float(v.get('percent_change',0))
            except: pass
    except:
        change_24h={} # API down, fallback nanti

    out=[]
    for pair,d in tickers.items():
        if not pair.endswith('_idr'): continue
        if pair.upper() in BLOCKED: continue
        try:
            last=float(d['last']); low=float(d['low']); high=float(d['high']); vol=float(d['vol_idr'])
            vol_bn=vol/1e9
            if vol_bn < 0.15: continue

            chg24 = change_24h.get(pair, 0)
            # FIX DATA 0: kalo chg24 0 karena API down, pake (last-low)/low tapi jangan minus!
            chg_low = (last-low)/low*100 if low else 0
            if abs(chg24) < 0.1:
                chg24 = chg_low # fallback biar ga Data 0!

            if chg24 < -4: continue # ALT -35% UNMD -18% tetep ke block!
            if chg24 < 0.5: continue
            sisa=(high-last)/last*100 if last else 0
            rg=(high-low)/low*100 if low else 0
            if sisa < 8: continue # BMT 4% PUCUK BUANG!
            if sisa > 70: continue
            if rg > 80: continue
            out.append({'sym':pair.upper(),'chg':chg24,'sisa':sisa,'range':rg,'vol':vol_bn})
        except: continue
    return out

def scan(data):
    bottom=[]; early=[]
    for k in data:
        c=k['chg']; s=k['sisa']
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
    msg = f"V25.3 ANTI DATA0 Data {len(data)} | B{len(b)} E{len(e)}\n\n"
    if b:
        msg += "BOTTOM SEGAR\n"
        for k in b: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg+="\n"
    if e:
        msg += "EARLY FRESH\n"
        for k in e: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg+="\n"
    if not b and not e:
        if len(data)==0:
            msg+="API Indodax down! Coba lagi 1 menit!\n"
        else:
            msg+="Ga ada yang segar, tunggu pump baru!\n"
    print(msg)
    kirim(msg)
