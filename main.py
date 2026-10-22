import requests
import os

# INI BLOCK LIST LENGKAP LU - YANG GA MAU MASUK! TAMBAHIN DISINI!
BLOCKED = [
    'BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','DAI_IDR',
    'XRP_IDR','SOL_IDR','DOGE_IDR','SHIB_IDR','PEPE_IDR','BONK_IDR',
    'FLOKI_IDR','ADA_IDR','FARTCOIN_IDR','HYPE_IDR','XRP_IDR'
    # <- tambahin semua koin yang lu block di V18.4 disini!
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

def scan_v18_5(data):
    early=[]; hunter=[]; segar=[]
    for k in data:
        if k['symbol'] in BLOCKED: continue
        if k['vol']<0.025: continue
        if 1.0<=k['chg']<=4.0 and k['th']<=5.0 and k['vol']>=0.08 and k['last']>k['low']:
            early.append(k)
        elif k['chg']>4.0 and k['th']<=10.0 and k['vol']>=0.07:
            hunter.append(k)
        elif k['chg']<=4.0 and k['th']<=12.0 and k['vol']>=0.15:
            segar.append(k)
    return sorted(early,key=lambda x:x['chg'])[:3], sorted(hunter,key=lambda x:x['th'])[:3], sorted(segar,key=lambda x:x['vol'],reverse=True)[:4]

def kirim_tele(pesan):
    token=os.getenv('TELE_TOKEN'); chat=os.getenv('TELE_CHAT_ID')
    if not token or not chat: print("TELE TOKEN/CHAT_ID kosong"); return
    url=f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={'chat_id':chat,'text':pesan}, timeout=10)

if __name__=="__main__":
    data=get_indodax_data()
    e,h,s=scan_v18_5(data)
    msg=f"SCAN V18.5 10 KOINS\nData {len(data)} | E{len(e)} H{len(h)} S{len(s)}\n\n"
    msg+="⚡ EARLY\n"
    for k in e: msg+=f"{k['symbol']} {k['chg']:.1f}% Vol {k['vol']:.2f}Bn TH {k['th']:.1f}%\n"
    msg+="\n🚀 HUNTER\n"
    for k in h: msg+=f"{k['symbol']} {k['chg']:.1f}% TH {k['th']:.1f}% Vol {k['vol']:.2f}Bn\n"
    msg+="\n🌱 SEGAR\n"
    for k in s: msg+=f"{k['symbol']} {k['chg']:.1f}% Vol {k['vol']:.2f}Bn TH {k['th']:.1f}%\n"
    print(msg)
    kirim_tele(msg)
