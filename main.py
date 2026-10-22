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

def scan_hybrid(data):
    early=[]; hunter=[]; segar=[]
    for k in data:
        if k['sym'] in BLOCKED: continue
        v=k['vol']; c=k['chg']; s=k['sisa']; rg=k['range']
        
        # ⚡ EARLY = V18.7 + V54 sisa>15% (buat hold besok kayak ICNT)
        # chg 1-4% + sisa 15-35% + range <=35% + vol 0.10-1.0 + chg>=0
        if 1.0<=c<=4.0 and 15<=s<=35 and rg<=35 and c>=0 and 0.10<=v<=1.0:
            early.append(k)
            
        # 🚀 HUNTER = V18.7 scalp, sisa kecil TH<=4% (biar ga kepucuk)
        # chg >4% + sisa <=4% + range <=40% + vol 0.07-1.0
        elif 4.0<c<=25 and s<=4.0 and rg<=40 and 0.07<=v<=1.0:
            hunter.append(k)
            
        # 🌱 SEGAR = V18.7 mid + V54 sisa>15% (anti resistance)
        # chg 0.5-4% + sisa 15-30% + range <=35% + vol 0.15-0.60
        elif 0.5<=c<=4.0 and 15<=s<=30 and rg<=35 and c>=0 and 0.15<=v<=0.60:
            segar.append(k)

    early=sorted(early, key=lambda x: x['sisa'], reverse=True)[:3]
    hunter=sorted(hunter, key=lambda x: x['sisa'])[:3]
    segar=sorted(segar, key=lambda x: x['vol'], reverse=True)[:4]
    return early,hunter,segar

def kirim(msg):
    token=os.getenv('TELE_TOKEN'); chat=os.getenv('TELE_CHAT_ID')
    if not token or not chat: return
    try: requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={'chat_id':chat,'text':msg}, timeout=10)
    except: pass

if __name__=="__main__":
    data=get_data()
    e,h,s=scan_hybrid(data)
    msg=f"HYBRID V18.7xV54 - EARLY/HUNTER/SEGAR\nData {len(data)} | E{len(e)} H{len(h)} S{len(s)}\n\n⚡ EARLY sisa>15%\n"
    for k in e: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% range {k['range']:.0f}% Vol {k['vol']:.2f}Bn\n"
    msg+="\n🚀 HUNTER sisa<=4%\n"
    for k in h: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.1f}% Vol {k['vol']:.2f}Bn\n"
    msg+="\n🌱 SEGAR sisa>15% Vol 0.15-0.60\n"
    for k in s: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    print(msg); kirim(msg)
