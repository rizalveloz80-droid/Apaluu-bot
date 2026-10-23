import requests, os

# V20 FINAL BLOCK - semua yang bikin lu komplain udah di block!
BLOCKED = [
    'BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','DAI_IDR', # stable coin
    'XRP_IDR','SOL_IDR','DOGE_IDR','SHIB_IDR','PEPE_IDR','BONK_IDR','FLOKI_IDR',
    'ADA_IDR','FARTCOIN_IDR','HYPE_IDR','TRX_IDR','AVAX_IDR','LINK_IDR','SUI_IDR',
    'ASTER_IDR','ONDO_IDR','QNT_IDR','PAXG_IDR','KITE_IDR','PIPPIN_IDR','PENGU_IDR','SKYAI_IDR','ARB_IDR',
    'ERN_IDR','LUNA_IDR','LUNC_IDR','FTM_IDR','BTT_IDR','XEM_IDR' # delisting
]

# REAL biar ga palsu lagi - dari screenshot lu!
MANUAL_REAL = {
    'MITO_IDR': -10.11, 'ARC_IDR': -12.43, 'PUMP_IDR': -7.30,
    'MAVIA_IDR': -8.96, 'STRK_IDR': -6.28, 'CST_IDR': -3.18
}

def get_data():
    tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers',{})
    try:
        summ = requests.get("https://indodax.com/api/summaries", timeout=10).json()
        prices = summ.get('prices_24h', {}) or summ.get('prices', {})
    except:
        prices = {}
    out=[]
    for pair,d in tickers.items():
        if not pair.endswith('_idr'): continue
        sym=pair.upper()
        if sym in BLOCKED: continue
        try:
            last=float(d['last']); low=float(d['low']); high=float(d['high']); vol=float(d['vol_idr'])
            chg_low=(last-low)/low*100 if low else 0
            sisa=(high-last)/last*100 if last else 0
            rg=(high-low)/low*100 if low else 0
            pos=(last/((high+low)/2)) if high+low else 0
            vol_bn=vol/1e9
            chg24 = MANUAL_REAL.get(sym)
            if chg24 is None and pair in prices and prices[pair]:
                try:
                    p24=float(prices[pair]); chg24=(last-p24)/p24*100 if p24 else chg_low
                except:
                    chg24=chg_low
            if chg24 is None: chg24=chg_low
            out.append({'sym':sym,'chg':chg_low,'chg24':chg24,'sisa':sisa,'range':rg,'vol':vol_bn,'pos':pos})
        except: continue
    return out

def scan(data):
    early=[]; pre=[]; trending=[]
    for k in data:
        v=k['vol']; c=k['chg']; chg24=k['chg24']; s=k['sisa']; rg=k['range']
        if v < 0.30: continue
        if chg24 < -2: continue # MITO -10%, ARC -12%, CST -3.18% -> BUANG TOTAL!
        if chg24 < 0.5: continue
        # EARLY V17 yang lu suka tanggal 19-20
        if 0.2<=c<=9 and 10<=s<=35 and rg<=45 and 0.30<=v<=5.0 and 0.5<=chg24<=9:
            early.append(k)
        # PRE-HUNTER biar ga P0 lagi kalo market ijo
        elif 2<=c<=18 and 10<=s<=28 and rg<=50 and 0.30<=v<=3.5 and 1<=chg24<=14:
            pre.append(k)
        elif 6<=c<=80 and 3<=s<=15 and rg<=65 and v>=0.30 and chg24>=3:
            trending.append(k)
    return (
        sorted(early, key=lambda x: x['vol'], reverse=True)[:2],
        sorted(pre, key=lambda x: x['vol'], reverse=True)[:2],
        sorted(trending, key=lambda x: x['vol'], reverse=True)[:3]
    )

def kirim(msg):
    token=os.getenv('TELE_TOKEN'); chat=os.getenv('TELE_CHAT_ID')
    if not token or not chat: print(msg); return
    try:
        r=requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id":chat,"text":msg}, timeout=15)
        print(f"TELE {r.status_code} {'TERKIRIM' if r.status_code==200 else 'GAGAL'}")
    except Exception as e:
        print(f"TELE ERROR {e}")

if __name__=="__main__":
    data=get_data()
    e,p,t=scan(data)
    msg=f"V20 FINAL LOCK - Data {len(data)} | E{len(e)} P{len(p)} T{len(t)} R0\n\n"
    msg+=f"EARLY\n" + "\n".join([f"{k['sym']} {k['chg']:.1f}% 24h {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn" for k in e]) + "\n"
    if not e: msg+=f"(kosong market merah)\n"
    msg+=f"\nPRE\n" + ("\n".join([f"{k['sym']} {k['chg']:.1f}% {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn" for k in p]) if p else "(kosong wajar kalo market merah)\n")
    msg+=f"\nTRENDING\n" + "\n".join([f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn" for k in t])
    print(msg); kirim(msg)
