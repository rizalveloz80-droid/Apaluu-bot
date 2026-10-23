import requests, os

# === BLOCKED TETAP ===
BLOCKED = [
    'BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','DAI_IDR',
    'XRP_IDR','SOL_IDR','DOGE_IDR','SHIB_IDR','PEPE_IDR','BONK_IDR','FLOKI_IDR',
    'ADA_IDR','FARTCOIN_IDR','HYPE_IDR','TRX_IDR','AVAX_IDR','LINK_IDR',
    'SUI_IDR','ASTER_IDR','ONDO_IDR','QNT_IDR','PAXG_IDR','KITE_IDR',
    'PIPPIN_IDR','PENGU_IDR','SKYAI_IDR','ARB_IDR'
]

# === CHG 24H REAL DARI CHART LU - TAMBAHIN KALO ADA ===
# Format: 'SYMBOL_IDR': chg24_real
# Contoh lu: WLD -4.01%, MAVIA -6.54%, PM -13.39%
REAL_CHG = {
    # 'WLD_IDR': -4.01,
    # 'MAVIA_IDR': -6.54,
    # 'PM_IDR': -13.39,
}

def get_data():
    try:
        r = requests.get("https://indodax.com/api/tickers", timeout=20).json().get('tickers',{})
        out=[]
        for pair,d in r.items():
            if not pair.endswith('_idr'): continue
            sym = pair.upper()
            if sym in BLOCKED: continue
            try:
                last=float(d['last']); low=float(d['low']); high=float(d['high']); vol=float(d['vol_idr'])
                if low==0 or last==0: continue
                chg_low=(last-low)/low*100
                sisa=(high-last)/last*100
                range_=(high-low)/low*100
                mid=(high+low)/2
                pos=last/mid if mid else 0
                vol_bn=vol/1e9

                chg24 = chg_low
                if sym in REAL_CHG:
                    chg24 = REAL_CHG[sym]

                out.append({
                    'sym':sym,
                    'chg':chg_low,
                    'chg24':chg24,
                    'sisa':sisa,
                    'range':range_,
                    'vol':vol_bn,
                    'pos':pos
                })
            except: continue
        return out
    except:
        return []

def scan_v18_9(data):
    early=[]; pre=[]; trending=[]
    
    for k in data:
        v=k['vol']; c=k['chg']; chg24=k['chg24']; s=k['sisa']; rg=k['range']; pos=k['pos']

        # === FILTER BUANG BERSIH - INI KUNCI ===
        if v < 0.20: continue  # DGB 0.17Bn BUANG
        if pos < 0.95: continue  # PM pos 0.94 BUANG
        if chg24 < -5.0: continue  # MAVIA -6.54% & PM -13.39% BUANG, WLD -4.01% MASIH LOLOS

        # ⚡ EARLY - LONGGARIN BIAR GA E0
        # Sisa 10-35% (dulu 12-30) Vol 0.20-5.0Bn
        if 0.2<=c<=8.0 and 10<=s<=35 and rg<=40 and 0.20<=v<=5.0:
            early.append(k)
        # 🚀 PRE-HUNTER - Sisa 8-25% chg24>= -1% (biar ga merah parah)
        elif 2.5<=c<=16 and 8<=s<=25 and rg<=40 and 0.20<=v<=3.0 and chg24>=-1:
            pre.append(k)
        # 🔥 TRENDING - Sisa 4-20% chg24>=0% Vol>=0.25Bn
        elif 8<=c<=70 and 4<=s<=20 and rg<=55 and v>=0.25 and chg24>=0:
            trending.append(k)

    early_f = sorted(early, key=lambda x: (x['vol'], x['sisa']), reverse=True)[:2]
    pre_f = sorted(pre, key=lambda x: x['vol'], reverse=True)[:2]
    trending_f = sorted(trending, key=lambda x: x['vol'], reverse=True)[:3]

    # === ANTI E0 FALLBACK ===
    if not early_f and pre_f:
        early_f = [pre_f[0]]
        pre_f = pre_f[1:]
    if not early_f and trending_f:
        cand = [x for x in trending_f if x['sisa']>=8]
        if cand:
            early_f = [cand[0]]

    return early_f, pre_f, trending_f

def kirim(msg):
    token=os.getenv('TELE_TOKEN'); chat=os.getenv('TELE_CHAT_ID')
    if not token or not chat: 
        print(msg); return
    try:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                      json={'chat_id':chat,'text':msg}, timeout=10)
    except: pass

if __name__=="__main__":
    data=get_data()
    e,p,t=scan_v18_9(data)
    
    msg=f"V18.9 ANTI E0 - Data {len(data)} | E{len(e)} P{len(p)} T{len(t)}\n\n"
    
    msg+=f"⚡ EARLY (Vol>=0.20 sisa 10-35%)\n"
    if e:
        for k in e: msg+=f"{k['sym']} low+{k['chg']:.1f}% 24h {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    else:
        msg+="Kosong - market sepi\n"
    
    msg+=f"\n🚀 PRE-HUNTER (sisa 8-25% chg24>=-1%)\n"
    if p:
        for k in p: msg+=f"{k['sym']} low+{k['chg']:.1f}% 24h {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    else:
        msg+="Kosong\n"
    
    msg+=f"\n🔥 TRENDING (sisa 4-20% chg24>=0%)\n"
    if t:
        for k in t: msg+=f"{k['sym']} low+{k['chg']:.1f}% 24h {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    else:
        msg+="Kosong\n"

    print(msg)
    kirim(msg)
