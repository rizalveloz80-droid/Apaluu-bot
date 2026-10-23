import requests, os

# === BLOCKED TETAP YA MIN ===
BLOCKED = [
    'BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','DAI_IDR',
    'XRP_IDR','SOL_IDR','DOGE_IDR','SHIB_IDR','PEPE_IDR','BONK_IDR','FLOKI_IDR',
    'ADA_IDR','FARTCOIN_IDR','HYPE_IDR','TRX_IDR','AVAX_IDR','LINK_IDR',
    'SUI_IDR','ASTER_IDR','ONDO_IDR','QNT_IDR','PAXG_IDR','KITE_IDR',
    'PIPPIN_IDR','PENGU_IDR','SKYAI_IDR','ARB_IDR'
]

# ISI CHG 24H REAL KALO LIAT MERAH DI CHART
REAL_CHG = {
    # 'PUMP_IDR': -7.30,  # sisa 9% -> kebuang karena sisa <14%
    # 'MAVIA_IDR': -8.96, # sisa 9% -> kebuang!
    # 'ICNT_IDR': -6.0,   # sisa 18% -> masuk RED HOLD!
}

def get_data():
    try:
        r = requests.get("https://indodax.com/api/tickers", timeout=20).json().get('tickers',{})
        out=[]
        for pair,d in r.items():
            if not pair.endswith('_idr'): continue
            sym=pair.upper()
            if sym in BLOCKED: continue
            try:
                last=float(d['last']); low=float(d['low']); high=float(d['high']); vol=float(d['vol_idr'])
                if low==0 or last==0: continue
                chg=(last-low)/low*100
                sisa=(high-last)/last*100
                rg=(high-low)/low*100
                mid=(high+low)/2
                pos=last/mid if mid else 0
                vol_bn=vol/1e9
                chg24 = REAL_CHG.get(sym, chg)
                out.append({'sym':sym,'chg':chg,'chg24':chg24,'sisa':sisa,'range':rg,'vol':vol_bn,'pos':pos})
            except: continue
        return out
    except: return []

def scan_v19_2(data):
    early=[]; pre=[]; trending=[]; red_hold=[]
    for k in data:
        v=k['vol']; c=k['chg']; chg24=k['chg24']; s=k['sisa']; rg=k['range']; pos=k['pos']

        # FILTER DASAR
        if v < 0.25: continue # DGB 0.17Bn BUANG
        if pos < 0.94: continue # terlalu bawah banget, kecuali red hold

        # === 1. EARLY IJO SCALPING (ARC, CST, ZEREBRO) ===
        # Dilonggarin biar ga E0: sisa 10-35%, vol 0.25-5Bn, chg24 >= -1% (boleh merah tipis)
        if 0.2<=c<=8.0 and 10<=s<=35 and rg<=45 and 0.25<=v<=5.0 and chg24>=-1:
            early.append(k)
        # === 2. PRE-HUNTER IJO (sisa 8-28%) ===
        # Diketatin: chg24 harus >=0% IJO! PUMP -7.3% & MAVIA -8.96% merah KEGUGURAN!
        elif 2.0<=c<=16 and 8<=s<=28 and rg<=45 and 0.25<=v<=3.0 and chg24>=0:
            pre.append(k)
        # === 3. TRENDING IJO (NEON, GTC, XR) ===
        elif 8<=c<=70 and 3<=s<=18 and rg<=60 and v>=0.30 and chg24>=2:
            trending.append(k)
        # === 4. MERAH BOUNCE HOLD ICNT STYLE (ENAK DI HOLD!) ===
        # Merah -10% sampai -2%, TAPI harus: c 0.5-7% deket Low, sisa GEDE >=14%, Vol >=0.40Bn, pos <=0.99
        # PUMP -7.3% s 9% <14% -> BUANG! MAVIA -8.96% s 9% <14% -> BUANG! ICNT -6% s 18% -> MASUK!
        elif -10<=chg24<=-2 and 0.5<=c<=7 and 14<=s<=35 and rg>=10 and v>=0.40 and pos<=0.99:
            red_hold.append(k)

    early_f = sorted(early, key=lambda x: (x['vol'], x['sisa']), reverse=True)[:2]
    pre_f = sorted(pre, key=lambda x: x['vol'], reverse=True)[:2]
    trending_f = sorted(trending, key=lambda x: x['vol'], reverse=True)[:3]
    red_f = sorted(red_hold, key=lambda x: (x['sisa'], x['vol']), reverse=True)[:2]

    # ANTI E0 FALLBACK
    if not early_f and pre_f:
        early_f = [pre_f[0]]; pre_f = pre_f[1:]
    if not early_f and red_f:
        early_f = [red_f[0]]

    return early_f, pre_f, trending_f, red_f

def kirim(msg):
    token=os.getenv('TELE_TOKEN'); chat=os.getenv('TELE_CHAT_ID')
    if not token or not chat: print(msg); return
    try: requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={'chat_id':chat,'text':msg}, timeout=10)
    except: pass

if __name__=="__main__":
    data=get_data()
    e,p,t,r = scan_v19_2(data)
    msg=f"V19.2 FINAL - Data {len(data)} | E{len(e)} P{len(p)} T{len(t)} R{len(r)}\n\n"
    msg+=f"⚡ EARLY SCALP (ijo, TP cepet)\n"
    for k in e: msg+=f"{k['sym']} {k['chg']:.1f}% 24h {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    msg+=f"\n🚀 PRE-HUNTER (ijo sisa 8-28% chg24>=0%)\n"
    for k in p: msg+=f"{k['sym']} {k['chg']:.1f}% 24h {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    msg+=f"\n🔥 TRENDING (ijo gede)\n"
    for k in t: msg+=f"{k['sym']} {k['chg']:.1f}% 24h {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    msg+=f"\n💎 RED HOLD ICNT (merah bounce enak hold)\n"
    for k in r: msg+=f"{k['sym']} {k['chg']:.1f}% 24h {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn HOLD!\n"
    if not e and not p and not t and not r:
        msg+="\nNo valid - market sepi!"
    print(msg); kirim(msg)
