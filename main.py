import requests, os

# V42 - ALTLAYER BALIK! CUMA BOME + ONDO YANG DI BLOCK!
BLOCKED = {
    'BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','DAI_IDR','PAXG_IDR',
    'XRP_IDR','DOGE_IDR','SOL_IDR','HYPE_IDR','FARTCOIN_IDR',
    'PEPE_IDR','SHIB_IDR','TRX_IDR','AVAX_IDR','ADA_IDR','DOT_IDR','LINK_IDR','LTC_IDR','BCH_IDR','XLM_IDR','UNI_IDR','ETC_IDR','NEAR_IDR','BONK_IDR','FLOKI_IDR','WIF_IDR',
    'HBAR_IDR','XAUT_IDR','PIPPIN_IDR','PENGU_IDR','ANOA_IDR','GID_IDR','WLD_IDR','TIA_IDR',
    'BEAT_IDR','MARSCOIN_IDR','MOODENG_IDR','NOVA_IDR','SHOW_IDR','MRS_IDR','CST_IDR',
    'BOME_IDR','ONDO_IDR', # CUMA 2 INI! ALTLAYER GA DI BLOCK!
    'MITO_IDR','ERN_IDR','UNMD_IDR','LUNA_IDR','LUNC_IDR','FTM_IDR','BTT_IDR','XEM_IDR','USELESS_IDR','PUMP_IDR','MAVIA_IDR','SKYAI_IDR','ARC_IDR'
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
                if last < 15: continue # BOME 12 KE BLOCK
                vol_bn=vol/1e9
                if vol_bn < 0.15: continue
                if vol_bn > 10: continue
                chg24 = change.get(pair, 0)
                if abs(chg24) < 0.1:
                    chg24 = (last-low)/low*100 if low else 0
                if chg24 < -20: continue
                if chg24 > 100: continue
                sisa=(high-last)/last*100 if last else 0
                rg=(high-low)/low*100 if low else 0
                if sisa < 3: continue
                if sisa > 20: continue # MAX 20%! ALTLAYER 19% MASUK! BOME 18% UDAH KE BLOCK KARENA HARGA!
                if rg < 3: continue
                if rg > 80: continue
                chg_low=(last-low)/low*100 if low else 0
                out.append({'sym':sym,'chg':chg24,'low':chg_low,'sisa':sisa,'vol':vol_bn})
            except: continue
        return out
    except: return []

def scan(data):
    bottom=[]; early=[]; running=[]
    for k in data:
        c=k['chg']; s=k['sisa']; low=k['low']
        if c < 0 and 2 <= low <= 20:
            bottom.append(k)
        elif 3 <= s <= 6:
            running.append(k)
        elif 7 <= s <= 20:
            early.append(k)
    return (
        sorted(bottom, key=lambda x: x['vol'], reverse=True)[:4],
        sorted(early, key=lambda x: x['vol'], reverse=True)[:4],
        sorted(running, key=lambda x: x['vol'], reverse=True)[:4]
    )

def kirim(msg):
    token=os.getenv('TELE_TOKEN')
    chat=os.getenv('TELE_CHAT_ID')
    if not token or not chat:
        print(msg)
        return
    try:
        url = "https://api.telegram.org/bot" + token + "/sendMessage"
        requests.post(url, json={"chat_id": chat, "text": msg}, timeout=15)
    except:
        print(msg)

if __name__=="__main__":
    data=get_data()
    btm, erl, run = scan(data)
    total = len(btm)+len(erl)+len(run)
    msg=f"V42 ALTLAYER BALIK Data {len(data)} | B{len(btm)} E{len(erl)} R{len(run)} = {total}\n\n"
    if btm:
        msg+="BOTTOM\n"
        for k in btm: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg+="\n"
    if erl:
        msg+="EARLY 7-20% (ALTLAYER DISINI!)\n"
        for k in erl: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg+="\n"
    if run:
        msg+="RUNNING 3-6%\n"
        for k in run: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    print(msg)
    kirim(msg)
