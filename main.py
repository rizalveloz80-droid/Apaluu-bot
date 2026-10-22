import requests
import os

# BLOCK LIST FINAL V18.6 - SEMUA GEDE & STABLE DI BLOCK!
BLOCKED = [
    'BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','DAI_IDR',
    'XRP_IDR','SOL_IDR','DOGE_IDR','SHIB_IDR','PEPE_IDR','BONK_IDR','FLOKI_IDR',
    'ADA_IDR','FARTCOIN_IDR','HYPE_IDR','TRX_IDR','AVAX_IDR','LINK_IDR','DOT_IDR',
    # Tambahan baru yang lu minta:
    'SUI_IDR','ASTER_IDR','ONDO_IDR','QNT_IDR', # gede vol 1-2Bn
    'PAXG_IDR', # emas
    'KITE_IDR', # dump chart tadi
    'BMT_IDR' # hunter 31% kegedean
]

def get_indodax_data():
    r = requests.get("https://indodax.com/api/tickers", timeout=15).json()
    out=[]
    for pair,d in r['tickers'].items():
        if not pair.endswith('_idr'): continue
        try:
            last=float(d['last']); low=float(d['low']); high=float(d['high']); vol=float(d['vol_idr'])
            if low==0: continue
            chg=(last-low)/low*100; th=(high-last)/last*100 if last>0 else 0
            out.append({'symbol':pair.upper(),'chg':chg,'th':th,'vol':vol/1e9,'last':last,'low':low})
        except: continue
    return out

def scan_v18_6(data):
    early=[]; hunter=[]; segar=[]
    for k in data:
        if k['symbol'] in BLOCKED: continue
        if k['vol']<0.025: continue
        # EARLY DIKETATIN: vol naik 0.10Bn, TH max 4% (tadi 5%)
        if 1.0<=k['chg']<=4.0 and k['th']<=4.0 and k['vol']>=0.10 and k['last']>k['low']:
            early.append(k)
        # HUNTER tetap
        elif k['chg']>4.0 and k['th']<=6.0 and k['vol']>=0.07:
            hunter.append(k)
        # SEGAR DIKETATIN: vol 0.15 - 1.0Bn aja, di atas 1.0 auto skip SUI/ASTER
        elif 0.2<=k['chg']<=4.0 and k['th']<=8.0 and 0.15<=k['vol']<=1.0:
            segar.append(k)
    return sorted(early,key=lambda x:x['chg'])[:3], sorted(hunter,key=lambda x:x['th'])[:3], sorted(segar,key=lambda x:x['vol'],reverse=True)[:4]

def kirim_tele(pesan):
    token=os.getenv('TELE_TOKEN'); chat=os.getenv('TELE_CHAT_ID')
    if not token or not chat: return
    url=f"https://api.telegram.org/bot{token}/sendMessage"
    try: requests.post(url, json={'chat_id':chat,'text':pesan}, timeout=10)
    except: pass

if __name__=="__main__":
    data=get_indodax_data()
    e,h,s=scan_v18_6(data)
    msg=f"SCAN V18.6 10 KOINS - FINAL\nData {len(data)} | E{len(e)} H{len(h)} S{len(s)}\n\n"
    msg+="⚡ EARLY (Tahan Besok)\n"
    for k in e: msg+=f"{k['symbol']} {k['chg']:.1f}% Vol {k['vol']:.2f}Bn TH {k['th']:.1f}%\n"
    msg+="\n🚀 HUNTER (Scalp)\n"
    for k in h: msg+=f"{k['symbol']} {k['chg']:.1f}% TH {k['th']:.1f}% Vol {k['vol']:.2f}Bn\n"
    msg+="\n🌱 SEGAR (Mid Vol)\n"
    for k in s: msg+=f"{k['symbol']} {k['chg']:.1f}% Vol {k['vol']:.2f}Bn TH {k['th']:.1f}%\n"
    print(msg)
    kirim_tele(msg)
