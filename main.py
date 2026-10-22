import requests, os

BLOCKED = [
    'BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','DAI_IDR',
    'XRP_IDR','SOL_IDR','DOGE_IDR','SHIB_IDR','PEPE_IDR','BONK_IDR','FLOKI_IDR',
    'ADA_IDR','FARTCOIN_IDR','HYPE_IDR','TRX_IDR','AVAX_IDR','LINK_IDR',
    'SUI_IDR','ASTER_IDR','ONDO_IDR','QNT_IDR','PAXG_IDR','KITE_IDR',
    'PIPPIN_IDR','PENGU_IDR','SKYAI_IDR','ARB_IDR'
]

def get_data():
    try:
        r = requests.get("https://indodax.com/api/tickers", timeout=20).json()
        out=[]
        for pair,d in r.get('tickers',{}).items():
            if not pair.endswith('_idr'): continue
            try:
                last=float(d['last']); low=float(d['low']); high=float(d['high']); vol=float(d['vol_idr'])
                if low==0: continue
                chg=(last-low)/low*100
                sisa=(high-last)/last*100
                range_=(high-low)/low*100
                out.append({'sym':pair.upper(),'chg':chg,'sisa':sisa,'range':range_,'vol':vol/1e9})
            except: continue
        return out
    except: return []

def scan_v19(data):
    early=[]; hunter=[]; segar=[]
    for k in data:
        if k['sym'] in BLOCKED: continue
        v=k['vol']; c=k['chg']; s=k['sisa']; rg=k['range']
        
        # ⚡ EARLY - HOLD BESOK (kayak ICNT TP 32%) - KETAT!
        if 0.5<=c<=4.0 and 15<=s<=28 and rg<=28 and 0.15<=v<=0.90:
            early.append(k)
            
        # 🚀 HUNTER - MAIN CEPAT SCALP - TETAP!
        elif 4.0<c<=20 and s<=3.5 and rg<=35 and 0.08<=v<=0.60:
            hunter.append(k)
            
        # 🌱 SEGAR - MAIN CEPAT MID - TETAP KETAT DIKIT!
        elif 0.8<=c<=3.5 and 15<=s<=25 and rg<=25 and 0.20<=v<=0.60:
            segar.append(k)

    early=sorted(early, key=lambda x: x['sisa'], reverse=True)[:3]
    hunter=sorted(hunter, key=lambda x: x['sisa'])[:3]
    segar=sorted(segar, key=lambda x: x['vol'], reverse=True)[:4]
    return early,hunter,segar

def kirim(msg):
    token=os.getenv('TELE_TOKEN'); chat=os.getenv('TELE_CHAT_ID')
    if not token or not chat: print(msg); return
    try: requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={'chat_id':chat,'text':msg}, timeout=10)
    except: pass

if __name__=="__main__":
    data=get_data()
    e,h,s=scan_v19(data)
    msg=f"V19 FINAL KETAT - E/H/S\nData {len(data)} | E{len(e)} H{len(h)} S{len(s)}\n\n⚡ EARLY sisa15-28% range<=28%\n"
    for k in e: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% range {k['range']:.0f}% Vol {k['vol']:.2f}Bn\n"
    msg+="\n🚀 HUNTER sisa<=3.5% (scalp)\n"
    for k in h: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.1f}% range {k['range']:.0f}% Vol {k['vol']:.2f}Bn\n"
    msg+="\n🌱 SEGAR sisa15-25% range<=25%\n"
    for k in s: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    print(msg); kirim(msg)
