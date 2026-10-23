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

def scan_v18_6(data):
    early=[]; pre=[]; hunter=[]; trending=[]
    for k in data:
        if k['sym'] in BLOCKED: continue
        v=k['vol']; c=k['chg']; s=k['sisa']; rg=k['range']
        
        # ⚡ EARLY KETAT 0.5-4% sisa 15-28% - hold besok
        if 0.5<=c<=4.0 and 15<=s<=28 and rg<=28 and 0.15<=v<=0.90:
            early.append(k)
        # 🚀 PRE-HUNTER 4-15% sisa 3.5-12% - sebelum trending
        elif 4.0<c<=15 and 3.5<s<=12 and rg<=28 and 0.20<=v<=1.0:
            pre.append(k)
        # 🚀 HUNTER 4-20% sisa <=3.5% - scalp pucuk
        elif 4.0<c<=20 and s<=3.5 and rg<=35 and 0.08<=v<=0.60:
            hunter.append(k)
        # 🔥 TRENDING LONGGAR - UCJL 88-100% GTC 36% masuk sini!
        elif 15<=c<=120 and s<=10 and rg<=100 and v>=0.15:
            trending.append(k)

    early_f = sorted(early, key=lambda x: x['sisa'], reverse=True)[:2]
    pre_f = sorted(pre, key=lambda x: x['sisa'])[:2]
    hunter_f = sorted(hunter, key=lambda x: x['sisa'])[:2]
    trending_f = sorted(trending, key=lambda x: (x['vol'], x['chg']), reverse=True)[:3]

    # ANTI-DUPLIKAT DGB
    early_syms = [x['sym'] for x in early_f]
    trending_f = [k for k in trending_f if k['sym'] not in early_syms]
    
    return early_f, pre_f, hunter_f, trending_f

def kirim(msg):
    token=os.getenv('TELE_TOKEN'); chat=os.getenv('TELE_CHAT_ID')
    if not token or not chat: print(msg); return
    try: requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={'chat_id':chat,'text':msg}, timeout=5)
    except: pass

if __name__=="__main__":
    data=get_data()
    e,p,h,t=scan_v18_6(data)
    msg=f"V18.6 CUAN UCJL 100% - Data {len(data)} | E{len(e)} P{len(p)} H{len(h)} T{len(t)}\n\n"
    msg+=f"⚡ EARLY (hold besok)\n"
    for k in e: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    msg+=f"\n🚀 PRE-HUNTER (sebelum trending)\n"
    for k in p: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    msg+=f"\n🚀 HUNTER (scalp pucuk)\n"
    for k in h: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.1f}% Vol {k['vol']:.2f}Bn\n"
    msg+=f"\n🔥 TRENDING LONGGAR (UCJL 100% masuk!)\n"
    for k in t: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.1f}% Vol {k['vol']:.2f}Bn\n"
    print(msg); kirim(msg)
