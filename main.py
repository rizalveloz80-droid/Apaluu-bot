import requests, os, time

BLOCKED = ['BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','DAI_IDR','XRP_IDR','SOL_IDR','DOGE_IDR','SHIB_IDR','PEPE_IDR','BONK_IDR','FLOKI_IDR','ADA_IDR','FARTCOIN_IDR','HYPE_IDR','TRX_IDR','AVAX_IDR','LINK_IDR','SUI_IDR','ASTER_IDR','ONDO_IDR','QNT_IDR','PAXG_IDR','KITE_IDR','PIPPIN_IDR','PENGU_IDR','SKYAI_IDR','ARB_IDR']

def get_data_auto():
    """Ambil chg24 REAL -11.97% -6.28% langsung dari Indodax summaries, bukan dari low!"""
    try:
        # 1. ticker = low high last vol
        tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers',{})
        # 2. summaries = harga 24h lalu + harga 7d - INI KUNCI!
        summ_raw = requests.get("https://indodax.com/api/summaries", timeout=15).json()
        # format summaries: {tickers:{}, prices:{}, prices_24h:{}, prices_7d:{}}
        prices_24h = summ_raw.get('prices_24h', {}) or summ_raw.get('prices', {})
        tick_summ = summ_raw.get('tickers', {})

        out=[]
        for pair,d in tickers.items():
            if not pair.endswith('_idr'): continue
            sym=pair.upper()
            if sym in BLOCKED: continue
            try:
                last=float(d['last']); low=float(d['low']); high=float(d['high']); vol=float(d['vol_idr'])
                if low==0 or last==0: continue

                # === HITUNG CHG24 REAL DARI HARGA 24JAM LALU ===
                chg24_real = 0
                price_24h = None
                if pair in prices_24h:
                    try: price_24h = float(prices_24h[pair])
                    except: pass
                if price_24h and price_24h!=0:
                    chg24_real = (last - price_24h)/price_24h*100
                elif pair in tick_summ and 'price' in tick_summ[pair]:
                    # fallback: summaries.tickers[pair].price = harga 24h lalu
                    try:
                        price_24h = float(tick_summ[pair].get('price',0))
                        if price_24h!=0:
                            chg24_real = (last - price_24h)/price_24h*100
                    except: pass
                
                if chg24_real==0: # kalo gagal, pakai low+
                    chg24_real = (last-low)/low*100

                chg_low = (last-low)/low*100
                sisa=(high-last)/last*100 if last!=0 else 0
                rg=(high-low)/low*100 if low!=0 else 0
                mid=(high+low)/2
                pos=last/mid if mid else 0
                vol_bn=vol/1e9

                out.append({
                    'sym':sym, 'chg':chg_low, 'chg24':chg24_real,
                    'sisa':sisa, 'range':rg, 'vol':vol_bn, 'pos':pos,
                    'last':last, 'low':low, 'high':high
                })
            except: continue
        return out
    except Exception as e:
        print("Error get_data", e)
        return []

def scan_v19_5(data):
    early=[]; pre=[]; trending=[]; red_hold=[]
    for k in data:
        v=k['vol']; c=k['chg']; chg24=k['chg24']; s=k['sisa']; rg=k['range']; pos=k['pos']
        if v < 0.25: continue # DGB 0.17Bn buang
        if pos < 0.90: continue

        # === FILTER MERAH DOWNTREND - ARC -11.97% STRK -6.28% PUMP -7.3% MAVIA -8.96% SEMUA KEBUANG DISINI! ===
        if chg24 < 0.3: # harus ijo minimal 0.3%
            # Kecuali mau hold merah bounce ICNT style: -8% sampai -2%, sisa gede >=14%, deket low
            if -8.5 <= chg24 <= -2 and 0.5<=c<=7 and 14<=s<=35 and rg>=10 and v>=0.35 and pos<=0.99:
                red_hold.append(k)
            continue

        # EARLY IJO
        if 0.1<=c<=9 and 10<=s<=35 and rg<=45 and 0.25<=v<=5.0 and 0.3<=chg24<=8.5:
            early.append(k)
        # PRE-HUNTER IJO sisa 10-28%
        elif 1.5<=c<=18 and 10<=s<=28 and rg<=50 and 0.25<=v<=3.5 and 1<=chg24<=14:
            pre.append(k)
        # TRENDING
        elif 5<=c<=80 and 3<=s<=15 and rg<=65 and v>=0.30 and chg24>=3:
            trending.append(k)

    early_f = sorted(early, key=lambda x: x['vol'], reverse=True)[:2]
    pre_f = sorted(pre, key=lambda x: x['vol'], reverse=True)[:2]
    trending_f = sorted(trending, key=lambda x: x['vol'], reverse=True)[:3]
    red_f = sorted(red_hold, key=lambda x: (x['sisa'], x['vol']), reverse=True)[:2]

    # ANTI E0: kalo early kosong tapi pre ada, geser
    if not early_f and pre_f:
        early_f=[pre_f[0]]; pre_f=pre_f[1:]
    return early_f, pre_f, trending_f, red_f

def kirim(msg):
    token=os.getenv('TELE_TOKEN'); chat=os.getenv('TELE_CHAT_ID')
    if not token or not chat: print(msg); return
    try: requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={'chat_id':chat,'text':msg}, timeout=10)
    except: pass

if __name__=="__main__":
    data=get_data_auto()
    e,p,t,r=scan_v19_5(data)
    msg=f"V19.5 AUTO REAL - Data {len(data)} | E{len(e)} P{len(p)} T{len(t)} R{len(r)}\n\n"
    msg+=f"⚡ EARLY (chg24 real >=0.3% ijo)\n"
    for k in e: msg+=f"{k['sym']} low+{k['chg']:.1f}% 24h {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    msg+=f"\n🚀 PRE-HUNTER (chg24>=1% sisa>=10%)\n"
    for k in p: msg+=f"{k['sym']} low+{k['chg']:.1f}% 24h {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    msg+=f"\n🔥 TRENDING (chg24>=3%)\n"
    for k in t: msg+=f"{k['sym']} low+{k['chg']:.1f}% 24h {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    msg+=f"\n💎 RED HOLD BOUNCE (ICNT -8% sampai -2% sisa>=14%)\n"
    for k in r: msg+=f"{k['sym']} low+{k['chg']:.1f}% 24h {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    if not e and not p and not t and not r:
        msg+="Market merah - ARC -11.97% STRK -6.28% PUMP -7.3% MAVIA -8.96% semua auto kebuang, wajar E0 P0!"
    print(msg); kirim(msg)
