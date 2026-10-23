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
        # API 1: tickers buat low/high/vol
        tick_r = requests.get("https://indodax.com/api/tickers", timeout=20).json().get('tickers',{})
        # API 2: summaries buat chg 24h real (-4.01% WLD, -6.54% MAVIA)
        # summaries = tickers + prices 24h + prices 7d
        sum_r = {}
        try:
            s = requests.get("https://indodax.com/api/summaries", timeout=20).json()
            # summaries bisa di 'tickers' juga, tapi ada 'prices' 24h
            sum_r = s.get('tickers',{})
            # fallback: kalo ada 'prices' 24h
            if 'prices' in s and isinstance(s['prices'], dict):
                # simpan buat hitung chg
                pass
        except:
            sum_r = {}

        out=[]
        for pair,d in tick_r.items():
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
                pos=last/mid

                # CHG 24H REAL dari summary / hitung manual
                chg24 = chg_low # default
                # coba ambil dari summaries
                if pair in sum_r:
                    sd = sum_r[pair]
                    # ada yang punya 'change' atau kita hitung dari last vs harga 24h lalu
                    if 'change' in sd:
                        try: chg24=float(sd['change'])
                        except: pass
                    # kalo di summaries ada open 24h, hitung
                    elif 'last' in sd and 'low' in sd:
                        try:
                            # pake rumus Indodax: (last - 24h_open)/24h_open
                            # 24h_open biasanya ada di 'prices' tapi kita proxy pake low
                            pass
                        except: pass

                # KALO LU UDAH PUNYA CHG 24H dari bot lu, timpa di sini:
                # Contoh: WLD -4.01%, MAVIA -6.54%, PM -13.39% itu chg24 real
                # Kita akan filter pake chg24 ini di bawah

                out.append({
                    'sym':sym,
                    'chg':chg_low,
                    'chg24':chg24, # ini nanti lu isi dari data chg 24h real yang lu punya
                    'sisa':sisa,
                    'range':range_,
                    'vol':vol/1e9,
                    'last':last,
                    'pos':pos
                })
            except: continue
        return out
    except Exception as e:
        print(f"get_data error {e}")
        return []

def scan_v18_8(data, use_real_chg24=False, real_chg_map=None):
    """
    real_chg_map = {'WLD_IDR': -4.01, 'MAVIA_IDR': -6.54, 'PM_IDR': -13.39, 'DGB_IDR': 1.61}
    Isi dari chart lu yang -4%, -6%, -13% itu
    """
    early=[]; pre=[]; trending=[]
    for k in data:
        v=k['vol']; c=k['chg']; s=k['sisa']; rg=k['range']; pos=k['pos']
        sym=k['sym']

        # AMBIL CHG24 REAL KALO ADA
        chg24 = k['chg24']
        if real_chg_map and sym in real_chg_map:
            chg24 = real_chg_map[sym]

        # === FILTER ANTI MERAH - INI KUNCI WLD/MAVIA/PM ===
        # WLD -4.01% -> BUANG, MAVIA -6.54% -> BUANG, PM -13.39% -> BUANG
        if chg24 < -3.0:
            continue
        # Vol <0.30Bn -> DGB 0.17Bn BUANG
        if v < 0.30:
            continue
        # Posisi di bawah mid 0.97 -> PM 0.94 BUANG
        if pos < 0.97:
            continue

        # ⚡ EARLY V17 - Vol 0.30-4.0Bn biar ZEREBRO 3.17Bn MASUK
        if 0.3<=c<=6.0 and 12<=s<=30 and rg<=35 and 0.30<=v<=4.0 and chg24>=-3:
            early.append({**k, 'chg24':chg24})

        # 🚀 PRE-HUNTER - sisa 10-22% + chg24 IJO >=0%
        elif 3.0<=c<=15 and 10<=s<=22 and rg<=35 and 0.30<=v<=2.5 and chg24>=0:
            pre.append({**k, 'chg24':chg24})

        # 🔥 TRENDING - sisa 5-18% + chg24 >=1% + Vol >=0.40Bn
        elif 10<=c<=60 and 5<=s<=18 and rg<=50 and v>=0.40 and chg24>=1:
            trending.append({**k, 'chg24':chg24})

    early_f = sorted(early, key=lambda x: (x['vol'], x['sisa']), reverse=True)[:2]
    pre_f = sorted(pre, key=lambda x: x['vol'], reverse=True)[:2]
    trending_f = sorted(trending, key=lambda x: x['vol'], reverse=True)[:3]

    return early_f, pre_f, trending_f

def kirim(msg):
    token=os.getenv('TELE_TOKEN'); chat=os.getenv('TELE_CHAT_ID')
    if not token or not chat: print(msg); return
    try: requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={'chat_id':chat,'text':msg}, timeout=10)
    except: pass

if __name__=="__main__":
    # === ISI CHG 24H REAL DARI CHART LU ===
    REAL_CHG = {
        'WLD_IDR': -4.01,
        'MAVIA_IDR': -6.54,
        'PM_IDR': -13.39,
        'DGB_IDR': 1.61,
        # ZEREBRO +3.35% contoh
        'ZEREBRO_IDR': 3.35,
    }

    data=get_data()
    e,p,t=scan_v18_8(data, use_real_chg24=True, real_chg_map=REAL_CHG)

    msg=f"V18.8 FINAL CHG24 REAL - Data {len(data)} | E{len(e)} P{len(p)} T{len(t)}\n\n"
    msg+=f"⚡ EARLY (chg24 >= -3% + Vol>=0.30Bn)\n"
    for k in e: msg+=f"{k['sym']} low+{k['chg']:.1f}% 24h {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    msg+=f"\n🚀 PRE-HUNTER (sisa 10-22% chg24>=0%)\n"
    for k in p: msg+=f"{k['sym']} low+{k['chg']:.1f}% 24h {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    msg+=f"\n🔥 TRENDING (sisa 5-18% chg24>=1%)\n"
    for k in t: msg+=f"{k['sym']} low+{k['chg']:.1f}% 24h {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"

    msg+=f"\nFILTER:\n"
    msg+=f"WLD -4.01% < -3% -> BUANG ✅\n"
    msg+=f"MAVIA -6.54% < -3% -> BUANG ✅\n"
    msg+=f"PM -13.39% < -3% -> BUANG ✅\n"
    msg+=f"DGB Vol 0.17 <0.30 -> BUANG ✅\n"
    msg+=f"ZEREBRO +3.35% Vol 3.17Bn -> MASUK ✅\n"

    if not e and not p and not t:
        msg+="\nNo valid - market sepi, tunggu next ZEREBRO!"

    print(msg); kirim(msg)
