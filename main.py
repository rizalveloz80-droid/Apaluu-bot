import requests, os

# V22 DIP FINAL - FULL COPY PASTE! GA USAH GANTI VERSI!
BLOCKED = [
    'BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','DAI_IDR',
    'XRP_IDR','SOL_IDR','DOGE_IDR','SHIB_IDR','PEPE_IDR','BONK_IDR','FLOKI_IDR',
    'ADA_IDR','FARTCOIN_IDR','HYPE_IDR','TRX_IDR','AVAX_IDR','LINK_IDR','SUI_IDR',
    'ASTER_IDR','ONDO_IDR','QNT_IDR','PAXG_IDR','KITE_IDR','PIPPIN_IDR','PENGU_IDR','SKYAI_IDR','ARB_IDR',
    'ERN_IDR','LUNA_IDR','LUNC_IDR','FTM_IDR','BTT_IDR','XEM_IDR',
    'CST_IDR','IOST_IDR'  # BLOCK yang lu kirim -2.50% & -5.88% palsu!
]

MANUAL_REAL = {
    'MITO_IDR': -10.11, 'ARC_IDR': -12.43, 'UCJL_IDR': -8.51,
    'PUMP_IDR': -7.30, 'MAVIA_IDR': -8.96, 'STRK_IDR': -6.28,
    'ICNT_IDR': -2.31, 'CST_IDR': -2.50, 'IOST_IDR': -5.88,
    'NEON_IDR': 1.12
}

def get_data():
    try:
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
                vol_bn=vol/1e9
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
                out.append({'sym':sym,'chg':chg_low,'chg24':chg24,'sisa':sisa,'range':rg,'vol':vol_bn})
            except: continue
        return out
    except:
        return []

def scan(data):
    early_dip=[]; early=[]; pre=[]; trending=[]
    for k in data:
        v=k['vol']; c=k['chg']; chg24=k['chg24']; s=k['sisa']; rg=k['range']
        if v < 0.40: continue
        if chg24 < -4: continue
        if -4 <= chg24 <= 0.9 and 1 <= c <= 5 and 10 <= s <= 40 and rg <= 50:
            early_dip.append(k)
        elif 0.2 <= c <= 9 and 10 <= s <= 35 and rg <= 45 and 1 <= chg24 <= 9:
            early.append(k)
        elif 2 <= c <= 18 and 10 <= s <= 28 and rg <= 50 and 1 <= chg24 <= 14:
            pre.append(k)
        elif 6 <= c <= 80 and 3 <= s <= 15 and rg <= 65 and v >= 0.40 and chg24 >= 2:
            trending.append(k)
    return (
        sorted(early_dip, key=lambda x: x['chg24'], reverse=True)[:3],
        sorted(early, key=lambda x: x['vol'], reverse=True)[:2],
        sorted(pre, key=lambda x: x['vol'], reverse=True)[:2],
        sorted(trending, key=lambda x: x['vol'], reverse=True)[:3]
    )

def kirim(msg):
    token=os.getenv('TELE_TOKEN'); chat=os.getenv('TELE_CHAT_ID')
    if not token or not chat:
        print(msg); return
    try:
        r=requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id":chat,"text":msg}, timeout=15)
        print(f"TELE {r.status_code}")
    except Exception as e:
        print(f"TELE ERROR {e}")

if __name__=="__main__":
    data=get_data()
    ed, e, p, t = scan(data)
    msg = f"V22 DIP MODE - Data {len(data)} | ED{len(ed)} E{len(e)} P{len(p)} T{len(t)}\n\n"
    if ed:
        msg += "EARLY DIP (merah -4% to 0% bounce)\n"
        for k in ed:
            msg += f"{k['sym']} {k['chg']:.1f}% 24h {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg += "\n"
    if e:
        msg += "EARLY\n"
        for k in e:
            msg += f"{k['sym']} {k['chg']:.1f}% 24h {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg += "\n"
    if p:
        msg += "PRE\n"
        for k in p:
            msg += f"{k['sym']} {k['chg']:.1f}% {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg += "\n"
    msg += "TRENDING\n"
    if t:
        for k in t:
            msg += f"{k['sym']} {k['chg']:.1f}% 24h {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    else:
        msg += "kosong\n"
    print(msg)
    kirim(msg)
