import requests, os

# BLOCK TETAP! YANG SAMPAH TETAP DI BLOCK!
BLOCKED = {
    # Major gede spam sisa 0%
    'BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','DAI_IDR','PAXG_IDR',
    'XRP_IDR','DOGE_IDR','SOL_IDR','HYPE_IDR','FARTCOIN_IDR',
    'PEPE_IDR','SHIB_IDR','TRX_IDR','AVAX_IDR','ADA_IDR','DOT_IDR','LINK_IDR','LTC_IDR','BCH_IDR','XLM_IDR','UNI_IDR','ETC_IDR','NEAR_IDR','BONK_IDR','FLOKI_IDR','WIF_IDR',
    # Delisting sampah
    'MITO_IDR','ERN_IDR','UNMD_IDR','LUNA_IDR','LUNC_IDR','FTM_IDR','BTT_IDR','XEM_IDR','USELESS_IDR','PUMP_IDR','MAVIA_IDR'
}

def get_data():
    try:
        tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers',{})
        summ = requests.get("https://indodax.com/api/summaries", timeout=15).json()
        change={}
        for k,v in summ.get('tickers',{}).items():
            try: change[k]=float(v.get('percent_change',0))
            except: pass
        
        out=[]
        for pair,d in tickers.items():
            if not pair.endswith('_idr'): continue
            sym=pair.upper()
            if sym in BLOCKED: continue # BLOCK TETAP!
            try:
                last=float(d['last']); low=float(d['low']); high=float(d['high']); vol=float(d['vol_idr'])
                if last < 10: continue # harga 10 pun masuk, tapi UNMD 11 ke block di atas!
                vol_bn=vol/1e9
                if vol_bn < 0.005: continue # 30 JUTA pun masuk! Dari 0.15 jadi 0.03! Data 21 jadi 250+!

                chg24 = change.get(pair, 0)
                if abs(chg24) < 0.1:
                    chg24 = (last-low)/low*100 if low else 0

                if chg24 < -40: continue # ALT -15% masuk!
                if chg24 > 100: continue

                sisa=(high-last)/last*100 if last else 0
                rg=(high-low)/low*100 if low else 0

                if sisa < 0.5: continue # XRP 0% udah ke block di atas, tapi sisa 3% masih masuk RUNNING!
                if sisa > 95: continue
                if rg > 400: continue

                chg_low=(last-low)/low*100 if low else 0
                out.append({'sym':sym,'chg':chg24,'low':chg_low,'sisa':sisa,'vol':vol_bn,'last':last})
            except: continue
        return out
    except: return []

def scan(data):
    bottom=[]; early=[]; running=[]
    for k in data:
        c=k['chg']; s=k['sisa']; low=k['low']
        # BOUNCE MERAH: ALT -15.88% low+5% sisa 23% -> BOTTOM!
        if c < 0 and 1 <= low <= 25 and 5 <= s <= 60:
            bottom.append(k)
        elif 3 <= s < 9:
            running.append(k) # STIK 11.7% sisa 7% Vol 0.28Bn MASUK SINI!
        elif 9 <= s <= 35 and 5 <= c <= 50:
            early.append(k)
        elif s >= 15 and c < 10:
            bottom.append(k)

    return (
        sorted(bottom, key=lambda x: x['vol'], reverse=True)[:10],
        sorted(early, key=lambda x: x['vol'], reverse=True)[:10],
        sorted(running, key=lambda x: x['vol'], reverse=True)[:10]
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
    btm, erl, run = scan(data)
    msg=f"V34 BLOCK TETAP LONGGAR Data {len(data)} | B{len(btm)} E{len(erl)} R{len(run)}\n\n"
    if btm:
        msg+="BOTTOM ADA BUYER\n"
        for k in btm: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg+="\n"
    if erl:
        msg+="EARLY FRESH\n"
        for k in erl: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg+="\n"
    if run:
        msg+="🏃 LAGI RUNNING (STIK DISINI!)\n"
        for k in run: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    print(msg)
    kirim(msg)
