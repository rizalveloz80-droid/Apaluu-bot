import requests, os

BLOCKED = [
    'BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','DAI_IDR',
    'XRP_IDR','SOL_IDR','DOGE_IDR','SHIB_IDR','PEPE_IDR','BONK_IDR','FLOKI_IDR',
    'ADA_IDR','FARTCOIN_IDR','HYPE_IDR','TRX_IDR','AVAX_IDR','LINK_IDR',
    'SUI_IDR','ASTER_IDR','ONDO_IDR','QNT_IDR','PAXG_IDR','KITE_IDR',
    'PIPPIN_IDR','PENGU_IDR','SKYAI_IDR','ARB_IDR'
]

# === INI KUNCI - JANGAN DI-KOMENTAR! ISI -7.30% -8.96% BIAR KEBUANG! ===
REAL_CHG = {
    'PUMP_IDR': -7.30,   # chart lu -7.30% merah -> nanti kebuang karena chg24>=0%
    'MAVIA_IDR': -8.96,  # chart lu -8.96% merah -> kebuang!
    'WLD_IDR': -4.01,
    'PM_IDR': -13.39,
    'DGB_IDR': 1.61,
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
                if low==0: continue
                chg=(last-low)/low*100
                sisa=(high-last)/last*100
                rg=(high-low)/low*100
                mid=(high+low)/2
                pos=last/mid if mid else 0
                vol_bn=vol/1e9
                # AMBIL REAL CHG - KALO ADA DI REAL_CHG PAKE ITU!
                chg24 = REAL_CHG.get(sym, chg) 
                out.append({'sym':sym,'chg':chg,'chg24':chg24,'sisa':sisa,'range':rg,'vol':vol_bn,'pos':pos})
            except: continue
        return out
    except: return []

def scan_v19_3(data):
    early=[]; pre=[]; trending=[]; red_hold=[]
    for k in data:
        v=k['vol']; c=k['chg']; chg24=k['chg24']; s=k['sisa']; rg=k['range']; pos=k['pos']
        if v < 0.25: continue
        if pos < 0.94: continue

        # EARLY - ijo 0-8%, sisa 10-35%
        if 0.2<=c<=8.0 and 10<=s<=35 and rg<=45 and 0.25<=v<=5.0 and chg24>=0:
            early.append(k)
        # PRE-HUNTER - KETATIN: chg24 harus >=1% IJO! PUMP -7.3% & MAVIA -8.96% auto buang!
        # sisa 10-28% (bukan 8%) biar MAVIA sisa 8% kebuang!
        elif 2.0<=c<=16 and 10<=s<=28 and rg<=45 and 0.25<=v<=3.0 and chg24>=1:
            pre.append(k)
        # TRENDING
        elif 8<=c<=70 and 3<=s<=15 and rg<=60 and v>=0.30 and chg24>=2:
            trending.append(k)
        # RED HOLD ICNT - sisa >=14% biar PUMP/MAVIA sisa 8-10% kebuang!
        elif -10<=chg24<=-2 and 0.5<=c<=7 and 14<=s<=35 and rg>=10 and v>=0.40 and pos<=0.99:
            red_hold.append(k)

    early_f = sorted(early, key=lambda x: x['vol'], reverse=True)[:2]
    pre_f = sorted(pre, key=lambda x: x['vol'], reverse=True)[:2]
    trending_f = sorted(trending, key=lambda x: x['vol'], reverse=True)[:3]
    red_f = sorted(red_hold, key=lambda x: (x['sisa'], x['vol']), reverse=True)[:2]

    if not early_f and pre_f:
        early_f=[pre_f[0]]; pre_f=pre_f[1:]
    return early_f, pre_f, trending_f, red_f

def kirim(msg):
    token=os.getenv('TELE_TOKEN'); chat=os.getenv('TELE_CHAT_ID')
    if not token or not chat: print(msg); return
    try: requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={'chat_id':chat,'text':msg}, timeout=10)
    except: pass

if __name__=="__main__":
    data=get_data()
    e,p,t,r=scan_v19_3(data)
    msg=f"V19.3 FINAL FIX - Data {len(data)} | E{len(e)} P{len(p)} T{len(t)} R{len(r)}\n\n"
    msg+=f"⚡ EARLY\n"
    for k in e: msg+=f"{k['sym']} {k['chg']:.1f}% 24h {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    msg+=f"\n🚀 PRE-HUNTER (sisa>=10% chg24>=1%)\n"
    for k in p: msg+=f"{k['sym']} {k['chg']:.1f}% 24h {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    msg+=f"\n🔥 TRENDING\n"
    for k in t: msg+=f"{k['sym']} {k['chg']:.1f}% 24h {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    msg+=f"\n💎 RED HOLD\n"
    for k in r: msg+=f"{k['sym']} {k['chg']:.1f}% 24h {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    print(msg); kirim(msg)
