import requests, os

# INI YANG DI BLOCK - GA AKAN KELUAR LAGI!
BLOCKED = {
    # Major gede sisa 0% spam PUCUK!
    'BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','DAI_IDR','PAXG_IDR',
    'XRP_IDR','DOGE_IDR','SOL_IDR','HYPE_IDR','FARTCOIN_IDR',
    'PEPE_IDR','SHIB_IDR','TRX_IDR','AVAX_IDR','ADA_IDR','DOT_IDR','LINK_IDR','LTC_IDR','BCH_IDR','XLM_IDR','UNI_IDR','ETC_IDR','NEAR_IDR',
    # Delisting
    'MITO_IDR','ERN_IDR','UNMD_IDR','LUNA_IDR','LUNC_IDR','FTM_IDR','BTT_IDR','XEM_IDR','USELESS_IDR',
    # Meme gede vol 4-6Bn sisa 0%
    'BONK_IDR','FLOKI_IDR','WIF_IDR'
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
            if sym in BLOCKED: continue # XRP DOGE SOL HYPE FARTCOIN LANGSUNG HILANG!
            try:
                last=float(d['last']); low=float(d['low']); high=float(d['high']); vol=float(d['vol_idr'])
                if last < 30: continue # UNMD 11 hilang
                vol_bn=vol/1e9
                if vol_bn < 0.15: continue

                chg24 = change.get(pair, 0)
                if abs(chg24) < 0.1:
                    chg24 = (last-low)/low*100 if low else 0

                if chg24 < -20: continue
                if chg24 > 60: continue
                if chg24 < 0.5 and chg24 > -0.5:
                    # cek bounce merah
                    chg_low=(last-low)/low*100 if low else 0
                    if not (chg24 <0 and 2 <= chg_low <= 12):
                        continue

                sisa=(high-last)/last*100 if last else 0
                rg=(high-low)/low*100 if low else 0

                # CROSSCHECK: sisa <5% kayak XRP 0% DOGE 0% FARTCOIN 1% LANGSUNG BLOCK! GA MASUK PUCUK!
                if sisa < 5: continue
                if sisa > 65: continue
                if rg > 75: continue

                chg_low=(last-low)/low*100 if low else 0
                out.append({'sym':sym,'chg':chg24,'low':chg_low,'sisa':sisa,'vol':vol_bn})
            except: continue
        return out
    except: return []

def scan(data):
    bottom=[]; early=[]
    for k in data:
        c=k['chg']; s=k['sisa']
        # BOTTOM SEGAR: yang masih bawah 0.5-15% sisa 15-65%
        if 0.5 <= c <= 15 and 15 <= s <= 65:
            bottom.append(k)
        # EARLY FRESH: 15-40% sisa 8-35% 
        elif 12 <= c <= 40 and 8 <= s <= 35:
            early.append(k)
    return (
        sorted(bottom, key=lambda x: (x['sisa'], x['vol']), reverse=True)[:5],
        sorted(early, key=lambda x: x['vol'], reverse=True)[:5]
    )

def kirim(msg):
    token=os.getenv('TELE_TOKEN'); chat=os.getenv('TELE_CHAT_ID')
    if not token or not chat:
        print(msg); return
    try: requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id":chat,"text":msg}, timeout=15)
    except: pass

if __name__=="__main__":
    data=get_data()
    btm, erl = scan(data)
    msg=f"V30 CROSSCHECK Data {len(data)} | B{len(btm)} E{len(erl)}\n\n"
    if btm:
        msg+="BOTTOM SEGAR\n"
        for k in btm: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg+="\n"
    if erl:
        msg+="EARLY FRESH\n"
        for k in erl: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    if not btm and not erl:
        msg+="Ga ada yang segar\n"
    print(msg)
    kirim(msg)
