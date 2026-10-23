import requests, os

BLOCKED = {
    'BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','DAI_IDR','PAXG_IDR',
    'XRP_IDR','DOGE_IDR','SOL_IDR','HYPE_IDR','FARTCOIN_IDR',
    'PEPE_IDR','SHIB_IDR','TRX_IDR','AVAX_IDR','ADA_IDR','DOT_IDR','LINK_IDR','LTC_IDR','BCH_IDR','XLM_IDR','UNI_IDR','ETC_IDR','NEAR_IDR','BONK_IDR','FLOKI_IDR','WIF_IDR',
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
            if sym in BLOCKED: continue
            try:
                last=float(d['last']); low=float(d['low']); high=float(d['high']); vol=float(d['vol_idr'])
                if last < 10: continue
                vol_bn=vol/1e9
                if vol_bn < 0.005: continue

                chg24 = change.get(pair, 0)
                if abs(chg24) < 0.1:
                    chg24 = (last-low)/low*100 if low else 0

                if chg24 < -40: continue
                if chg24 > 300: continue

                sisa=(high-last)/last*100 if last else 0
                rg=(high-low)/low*100 if low else 0
                if sisa < 0.5: continue
                if sisa > 95: continue
                if rg > 400: continue

                chg_low=(last-low)/low*100 if low else 0
                out.append({'sym':sym,'chg':chg24,'low':chg_low,'sisa':sisa,'vol':vol_bn})
            except: continue
        return out
    except: return []

def scan(data):
    bottom=[]; early=[]; running=[]
    for k in data:
        c=k['chg']; s=k['sisa']; low=k['low']
        
        # === KOREKSI MERAH! ===
        # MERAH -15% tapi BOUNCE +2% dari low sisa 23% = BOTTOM! Kayak ALT!
        if c < 0:
            # ALT: -15.88% low+2.13% sisa 23% -> MASUK BOTTOM BOUNCE!
            if 1.0 <= low <= 30 and 5 <= s <= 70:
                bottom.append(k)
            continue # merah yang ga bounce jangan masuk early/running

        # HIJAU
        if 0.5 <= s < 9 and 1 <= c <= 50:
            running.append(k) # STIK 11.7% sisa 7%
        elif 9 <= s <= 40 and 3 <= c <= 60:
            early.append(k)
        elif s >= 12 and c < 12:
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
    try: requests.post(f"https://api.telegram.org/bot{token}/sendMessage
