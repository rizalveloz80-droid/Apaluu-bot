import requests, os

# V17 BLOCK LIST + STABLE COIN - sesuai request lu!
BLOCKED = [
    'BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','DAI_IDR',  # STABLE COIN DI BLOCK!
    'XRP_IDR','SOL_IDR','DOGE_IDR','SHIB_IDR','PEPE_IDR','BONK_IDR','FLOKI_IDR',
    'ADA_IDR','FARTCOIN_IDR','HYPE_IDR','TRX_IDR','AVAX_IDR','LINK_IDR','SUI_IDR',
    'ASTER_IDR','ONDO_IDR','QNT_IDR','PAXG_IDR','KITE_IDR','PIPPIN_IDR','PENGU_IDR','SKYAI_IDR','ARB_IDR'
]

def get_data():
    try:
        print("Fetching tickers V17...")
        tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers',{})
        out=[]
        for pair,d in tickers.items():
            if not pair.endswith('_idr'): continue
            sym=pair.upper()
            if sym in BLOCKED: continue
            try:
                last=float(d['last']); low=float(d['low']); high=float(d['high']); vol=float(d['vol_idr'])
                if low==0 or last==0: continue
                chg=(last-low)/low*100
                sisa=(high-last)/last*100 if last else 0
                rg=(high-low)/low*100 if low else 0
                mid=(high+low)/2
                pos=last/mid if mid else 0
                vol_bn=vol/1e9
                out.append({'sym':sym,'chg':chg,'sisa':sisa,'range':rg,'vol':vol_bn,'pos':pos})
            except: continue
        return out
    except Exception as e:
        print(f"ERROR: {e}")
        return []

def scan(data):
    early=[]; pre=[]; trending=[]; red_hold=[]
    for k in data:
        v=k['vol']; c=k['chg']; s=k['sisa']; rg=k['range']; pos=k['pos']
        if v < 0.30: continue  # DGB 0.17Bn ke buang
        if pos < 0.90: continue

        # V17 LOGIC ORIGINAL TANGGAL 19-20 - SIMPEL!
        if 0.2 <= c <= 8.5 and 10 <= s <= 35 and rg <= 45 and 0.25 <= v <= 5.0:
            early.append(k)
        elif 2.0 <= c <= 16 and 10 <= s <= 28 and rg <= 45 and 0.25 <= v <= 3.0:
            pre.append(k)
        elif 8 <= c <= 70 and 3 <= s <= 15 and rg <= 60 and v >= 0.30:
            trending.append(k)
        elif -8 <= c <= -2 and 1 <= c <= 6 and 15 <= s <= 35 and rg >= 10 and v >= 0.35:
            # RED HOLD ICNT STYLE - c ini salah, maksudnya chg merah tapi low+ ijo?
            # V17 red hold: chg -8 sampai -2 tapi sisa gede
            pass

    # V17 RED HOLD FIX - yang merah -8% sampai -2% tapi sisa gede
    for k in data:
        v=k['vol']; c=k['chg']; s=k['sisa']; rg=k['range']; pos=k['pos']
        if v < 0.35: continue
        if -8 <= c <= -2: # ini sebenernya buat ICNT, tapi di V17 pake chg low+ jadi ga kepake, mimin benerin:
            if 15 <= s <= 35 and rg >= 10 and v >= 0.40:
                red_hold.append(k)

    # V17 RED HOLD YANG BENER: pakai chg negatif dari low+? Di V17 original ga ada, jadi kita pakai simpel:
    # Kalo mau red hold beneran, kita cek yang chg kecil tapi sisa gede
    red_hold = [] # reset biar ga dobel
    for k in data:
        if k['vol']>=0.40 and 0.5<=k['chg']<=6 and 15<=k['sisa']<=35 and k['range']>=12 and k['pos']<=0.97:
            # Ini yang sisa gede tapi chg kecil - mirip ICNT
            if len(red_hold)<2:
                # Jangan masukin yang udah di early/pre/trending
                if k not in early and k not in pre and k not in trending:
                    red_hold.append(k)

    early_f = sorted(early, key=lambda x: x['vol'], reverse=True)[:2]
    pre_f = sorted(pre, key=lambda x: x['vol'], reverse=True)[:2]
    trending_f = sorted(trending, key=lambda x: x['vol'], reverse=True)[:3]
    red_f = sorted(red_hold, key=lambda x: (x['sisa'], x['vol']), reverse=True)[:2]

    # ANTI E0 V17
    if not early_f and pre_f:
        early_f = [pre_f[0]]
        pre_f = pre_f[1:]

    return early_f, pre_f, trending_f, red_f

def kirim(msg):
    token=os.getenv('TELE_TOKEN'); chat=os.getenv('TELE_CHAT_ID')
    print(f"TOKEN: {'ADA' if token else 'KOSONG'} CHAT: {'ADA' if chat else 'KOSONG'}")
    if not token or not chat:
        print(msg)
        return
    try:
        r=requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id":chat,"text":msg}, timeout=15)
        print(f"TELE: {r.status_code} {r.text[:200]}")
    except Exception as e:
        print(f"TELE ERROR: {e}")

if __name__=="__main__":
    data=get_data()
    e,p,t,r=scan(data)
    msg=f"V17 STABLE BLOCK - Data {len(data)} | E{len(e)} P{len(p)} T{len(t)} R{len(r)}\n\n"
    msg+=f"⚡ EARLY\n"
    for k in e: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    if p:
        msg+=f"\n🚀 PRE-HUNTER\n"
        for k in p: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    if t:
        msg+=f"\n🔥 TRENDING\n"
        for k in t: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    if r:
        msg+=f"\n💎 RED HOLD\n"
        for k in r: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    if not e and not p and not t and not r:
        msg+=f"\nMarket sepi - ga ada yang memenuhi V17\n"
    print(msg)
    kirim(msg)
