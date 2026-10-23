import requests, os

BLOCKED = ['BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','DAI_IDR','PAXG_IDR','MITO_IDR','ERN_IDR','UNMD_IDR','LUNA_IDR','LUNC_IDR','FTM_IDR','BTT_IDR']

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
                if last < 25: continue
                vol_bn=vol/1e9
                if vol_bn < 0.10: continue # turunin biar STIK 0.28Bn masuk!
                chg24 = change.get(pair, 0)
                if abs(chg24) < 0.1:
                    chg24 = (last-low)/low*100 if low else 0
                if chg24 < -25: continue
                if chg24 < 0.3: 
                    # bounce merah boleh
                    chg_low=(last-low)/low*100 if low else 0
                    if not (chg24 <0 and 1.5 <= chg_low <= 15):
                        continue

                sisa=(high-last)/last*100 if last else 0
                rg=(high-low)/low*100 if low else 0
                if sisa > 70: continue
                if rg > 85: continue

                chg_low=(last-low)/low*100 if low else 0
                out.append({'sym':sym,'chg':chg24,'low':chg_low,'sisa':sisa,'rg':rg,'vol':vol_bn})
            except: continue
        return out
    except: return []

def scan(data):
    bottom=[]; early=[]; pucuk=[]
    for k in data:
        c=k['chg']; s=k['sisa']
        chg_low=k['low']
        is_bounce = c < 0 and 1.5 <= chg_low <= 15

        if is_bounce:
            if s < 10: pucuk.append(k)
            else: bottom.append(k)
        else:
            if s < 8: # STIK 7.89% -> PUCUK!
                pucuk.append(k)
            elif 8 <= s <= 25 and c <= 20:
                if c <= 12: bottom.append(k)
                else: early.append(k)
            elif 25 < s <= 65 and c <= 15:
                bottom.append(k)
            elif 10 <= s <= 50 and 12 < c <= 35:
                early.append(k)
    
    return (
        sorted(bottom, key=lambda x: x['vol'], reverse=True)[:5],
        sorted(early, key=lambda x: x['vol'], reverse=True)[:5],
        sorted(pucuk, key=lambda x: x['vol'], reverse=True)[:5]
    )

def kirim(msg):
    token=os.getenv('TELE_TOKEN'); chat=os.getenv('TELE_CHAT_ID')
    if not token or not chat:
        print(msg); return
    try: requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id":chat,"text":msg}, timeout=15)
    except: pass

if __name__=="__main__":
    data=get_data()
    btm, erl, pck = scan(data)
    msg=f"V29 ANTI LOLOS Data {len(data)} | B{len(btm)} E{len(erl)} P{len(pck)}\n\n"
    if btm:
        msg+="BOTTOM SEGAR\n"
        for k in btm: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg+="\n"
    if erl:
        msg+="EARLY FRESH\n"
        for k in erl: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg+="\n"
    if pck:
        msg+="⚠️ PUCUK! JANGAN ENTRY! (STIK BMT)\n"
        for k in pck:
            # STIK 11.76% sisa 7% Vol 0.28Bn -> PUCUK!
            msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn PUCUK!\n"
    print(msg)
    kirim(msg)
