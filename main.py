import requests, os

BLOCKED_HARD = {
    'BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','PAXG_IDR','DAI_IDR',
    'MITO_IDR','ERN_IDR','UNMD_IDR','ALT_IDR','ALTLAYER_IDR',
    'ARC_IDR','SKYAI_IDR','PUMP_IDR','MAVIA_IDR','LUNA_IDR','LUNC_IDR','FTM_IDR','BTT_IDR','XEM_IDR','USELESS_IDR'
}

def get_data():
    tickers={}
    change={}
    try:
        tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers',{})
    except:
        return []
    try:
        summ = requests.get("https://indodax.com/api/summaries", timeout=15).json()
        for k,v in summ.get('tickers',{}).items():
            try: change[k]=float(v.get('percent_change',0))
            except: pass
    except:
        change={}

    out=[]
    for pair,d in tickers.items():
        if not pair.endswith('_idr'): continue
        sym=pair.upper()
        if sym in BLOCKED_HARD: continue # MITO ERN UNMD ALT LANGSUNG BUANG!
        try:
            last=float(d['last']); low=float(d['low']); high=float(d['high']); vol=float(d['vol_idr'])
            if last < 25: continue # UNMD harga 11 BUANG!
            vol_bn=vol/1e9
            if vol_bn < 0.12: continue

            # chg24 real kalo ada, kalo API down pake chg_low
            chg24 = change.get(pair, 0)
            if abs(chg24) < 0.1:
                chg24 = (last-low)/low*100 if low else 0
            
            if chg24 < -4: continue # ALT -35% tetep ke block!
            if chg24 < 0.5: continue
            if chg24 > 70: continue

            sisa=(high-last)/last*100 if last else 0
            rg=(high-low)/low*100 if low else 0
            if sisa < 6: continue
            if sisa > 65: continue
            if rg > 75: continue

            out.append({'sym':sym,'chg':chg24,'sisa':sisa,'range':rg,'vol':vol_bn})
        except: continue
    return out

def scan(data):
    bottom=[]; early=[]
    for k in data:
        c=k['chg']; s=k['sisa']
        if 0.5 <= c <= 15 and 10 <= s <= 65:
            bottom.append(k)
        elif 15 < c <= 40 and 8 <= s <= 50:
            early.append(k)
    return (
        sorted(bottom, key=lambda x: x['vol'], reverse=True)[:6],
        sorted(early, key=lambda x: x['vol'], reverse=True)[:6]
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
    msg = f"V27 FINAL Data {len(data)} | B{len(b)} E{len(e)}\n\n"
    if b:
        msg+="BOTTOM SEGAR\n"
        for k in b: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg+="\n"
    if e:
        msg+="EARLY FRESH\n"
        for k in e: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg+="\n"
    if not b and not e:
        msg+=f"Data {len(data)} tapi ga ada yang segar, tunggu!\n"
    print(msg)
    kirim(msg)
