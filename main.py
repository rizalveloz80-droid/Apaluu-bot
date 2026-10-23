import requests, os

# BLOCK V19 - STRK JANGAN DI-BLOCK (sesuai request)
BLOCKED = [
    'BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','DAI_IDR',
    'XRP_IDR','SOL_IDR','DOGE_IDR','SHIB_IDR','PEPE_IDR','BONK_IDR','FLOKI_IDR',
    'ADA_IDR','FARTCOIN_IDR','HYPE_IDR','TRX_IDR','AVAX_IDR','LINK_IDR',
    'SUI_IDR','ASTER_IDR','ONDO_IDR','QNT_IDR','PAXG_IDR','KITE_IDR',
    'PIPPIN_IDR','PENGU_IDR','SKYAI_IDR','ARB_IDR'
]
# STRK_IDR GA MASUK BLOCK!

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

def scan_v18_5(data):
    early=[]; pre_hunter=[]; hunter=[]; segar=[]

    for k in data:
        if k['sym'] in BLOCKED: continue
        v=k['vol']; c=k['chg']; s=k['sisa']; rg=k['range']
        
        # ⚡ EARLY - HOLD BESOK (kayak ICNT) - V19 ketat
        if 0.5<=c<=4.0 and 15<=s<=28 and rg<=28 and 0.15<=v<=0.90:
            early.append(k)
            
        # 🚀 PRE-HUNTER - BARU! Tangkap 4-15% SEBELUM jadi 21% (GTC case)
        # GTC jam 18:00 10% sisa 12% masuk sini!
        elif 4.0<c<=15 and 3.5<s<=12 and rg<=28 and 0.20<=v<=1.0:
            pre_hunter.append(k)
            
        # 🚀 HUNTER - MAIN CEPAT SCALP - sisa <=3.5% deket pucuk
        elif 4.0<c<=20 and s<=3.5 and rg<=35 and 0.08<=v<=0.60:
            hunter.append(k)

    # --- FIX SEGAR BIAR GA USELESS TERUS ---
    early_sorted = sorted(early, key=lambda x: x['sisa'], reverse=True)
    
    # SEGAR ambil dari EARLY tapi Vol 0.15-0.60 + ANTI-DUPLIKAT E1=S1
    segar_pool = [k for k in early_sorted if 0.15 <= k['vol'] <= 0.60]
    
    # EARLY final E2
    early_final = early_sorted[:2]
    early_syms = [x['sym'] for x in early_final]

    # SEGAR final S2 - buang yang udah jadi EARLY biar ga USELESS terus
    segar_filtered = [k for k in segar_pool if k['sym'] not in early_syms]
    
    # Kalo market sepi cuma USELESS doang yang ada (jam 00:21)
    if not segar_filtered:
        # ambil dari early_sorted yang sisa paling gede (biar beda)
        segar_filtered = early_sorted[1:3] if len(early_sorted)>1 else early_sorted[:1]
    
    segar_final = sorted(segar_filtered, key=lambda x: x['vol'], reverse=True)[:2]
    
    # PRE-HUNTER & HUNTER sort
    pre_final = sorted(pre_hunter, key=lambda x: x['sisa'])[:2]
    hunter_final = sorted(hunter, key=lambda x: x['sisa'])[:2]

    return early_final, pre_final, hunter_final, segar_final

def kirim(msg):
    token=os.getenv('TELE_TOKEN'); chat=os.getenv('TELE_CHAT_ID')
    if not token or not chat: print(msg); return
    try: requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={'chat_id':chat,'text':msg}, timeout=5)
    except Exception as e: print(f"kirim gagal {e}")

if __name__=="__main__":
    data=get_data()
    e,p,h,s=scan_v18_5(data)
    msg=f"V18.5 UNIVERSAL - E/P/H/S\nData {len(data)} | E{len(e)} P{len(p)} H{len(h)} S{len(s)}\n\n"
    msg+=f"⚡ EARLY sisa15-28% range<=28%\n"
    for k in e: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% range {k['range']:.0f}% Vol {k['vol']:.2f}Bn\n"
    msg+=f"\n🚀 PRE-HUNTER BARU! sisa3.5-12% (tangkap sebelum 21%)\n"
    for k in p: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% range {k['range']:.0f}% Vol {k['vol']:.2f}Bn\n"
    msg+=f"\n🚀 HUNTER sisa<=3.5% (scalp)\n"
    for k in h: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.1f}% range {k['range']:.0f}% Vol {k['vol']:.2f}Bn\n"
    msg+=f"\n🌱 SEGAR Vol 0.15-0.60 anti-duplikat\n"
    for k in s: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    print(msg); kirim(msg)
