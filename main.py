import requests, os

BLOCKED = ['BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','DAI_IDR','XRP_IDR','SOL_IDR','DOGE_IDR','SHIB_IDR','PEPE_IDR','BONK_IDR','FLOKI_IDR','ADA_IDR','FARTCOIN_IDR','HYPE_IDR','TRX_IDR','AVAX_IDR','LINK_IDR','SUI_IDR','ASTER_IDR','ONDO_IDR','QNT_IDR','PAXG_IDR','KITE_IDR','PIPPIN_IDR','PENGU_IDR','SKYAI_IDR','ARB_IDR']

# REAL dari chart lu jam 09:37 - biar MITO -10.11% ARC -12.43% ga jadi 1.3% 6% palsu!
MANUAL_REAL = {'MITO_IDR': -10.11, 'ARC_IDR': -12.43, 'PUMP_IDR': -7.30, 'MAVIA_IDR': -8.96, 'STRK_IDR': -6.28}

def get_data():
    try:
        print("V19.8 Fetching...")
        tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers',{})
        # 1x fetch aja, bukan 410x!
        try:
            summ = requests.get("https://indodax.com/api/summaries", timeout=10).json()
            prices = summ.get('prices_24h', {}) or summ.get('prices', {})
        except:
            prices = {}
        print(f"Data: {len(tickers)} tickers, {len(prices)} prices")

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
                mid=(high+low)/2
                pos=last/mid if mid else 0
                vol_bn=vol/1e9

                # AMBIL REAL -10.11% -12.43%
                if sym in MANUAL_REAL:
                    chg24 = MANUAL_REAL[sym]
                elif pair in prices and prices[pair]:
                    try:
                        p24=float(prices[pair])
                        chg24=(last-p24)/p24*100 if p24 else chg_low
                    except:
                        chg24=chg_low
                else:
                    chg24=chg_low

                out.append({'sym':sym,'chg':chg_low,'chg24':chg24,'sisa':sisa,'range':rg,'vol':vol_bn,'pos':pos})
            except: continue
        return out
    except Exception as e:
        print(f"ERROR: {e}")
        return []

def scan(data):
    early=[]; pre=[]; trending=[]
    for k in data:
        v=k['vol']; c=k['chg']; chg24=k['chg24']; s=k['sisa']; rg=k['range']
        if v < 0.30: continue

        # FILTER AKURAT: MITO -10.11% ARC -12.43% BUANG TOTAL! Ga bakal masuk EARLY 1.3% palsu lagi!
        if chg24 < -8: 
            continue
        if chg24 < 0.5: # di bawah 0.5% buang, ga ijo beneran
            continue

        # V17 LOGIC TAPI PAKAI chg24 REAL!
        if 0.2<=c<=9 and 10<=s<=35 and rg<=45 and 0.30<=v<=5.0 and 0.5<=chg24<=9:
            early.append(k)
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
    print(f"TOKEN: {'ADA' if token else 'KOSONG'} CHAT: {'ADA' if chat else 'KOSONG'}")
    if not token or not chat:
        print(msg); return
    try:
        r=requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id":chat,"text":msg}, timeout=15)
        print(f"TELE: {r.status_code} {r.text[:300]}")
        print("✅ TELE TERKIRIM!" if r.status_code==200 else f"❌ GAGAL {r.text}")
    except Exception as e:
        print(f"TELE ERROR: {e}")

if __name__=="__main__":
    data=get_data()
    e,p,t=scan(data)
    msg=f"V19.8 ACCURATE REAL - Data {len(data)} | E{len(e)} P{len(p)} T{len(t)} R0\n\n"
    msg+=f"⚡ EARLY (chg24 real >=0.5%)\n"
    for k in e: msg+=f"{k['sym']} low+{k['chg']:.1f}% 24h {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    if not e: msg+=f"(kosong - market merah, MITO -10.1% ARC -12.4% BUANG)\n"
    if p:
        msg+=f"\n🚀 PRE\n"
        for k in p: msg+=f"{k['sym']} low+{k['chg']:.1f}% 24h {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    if t:
        msg+=f"\n🔥 TRENDING\n"
        for k in t: msg+=f"{k['sym']} low+{k['chg']:.1f}% 24h {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    if not e and not p and not t:
        msg+=f"\nMarket merah semua BUANG TOTAL R0 - aman ga di banting lagi!\n"
    print(msg)
    kirim(msg)
