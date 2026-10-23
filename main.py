import requests, os

# V24.1 FINAL - FIX UNMD -18% & CATCH UCJL 120%
BLOCKED = [
    'BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','DAI_IDR',
    'XRP_IDR','SOL_IDR','DOGE_IDR','SHIB_IDR','PEPE_IDR','BONK_IDR','FLOKI_IDR',
    'XLM_IDR','ADA_IDR','TRX_IDR','AVAX_IDR','LINK_IDR','PAXG_IDR',
    'USELESS_IDR','ERN_IDR','LUNA_IDR','LUNC_IDR','FTM_IDR','BTT_IDR','XEM_IDR',
    'UNMD_IDR','MITO_IDR','ARC_IDR','SKYAI_IDR','PUMP_IDR','MAVIA_IDR'
]

MANUAL_REAL = {}  # KOSONG! Biar real +120% bukan -8% palsu!

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
                if pair in prices and prices[pair]:
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
    bottom=[]; early=[]; pre=[]; trending=[]
    for k in data:
        v=k['vol']; c=k['chg']; chg24=k['chg24']; s=k['sisa']; rg=k['range']
        if v < 0.25: continue
        if chg24 < -4: continue  # UNMD -18% MITO -11% ARC -11% SKYAI -7% KE BLOCK!
        if c < 0.5: continue     # UNMD last=low=9 c=0% KE BLOCK!
        if s < 2: continue

        # BOTTOM 0.5-8% sisa 15-65% -> UCJL pas 3% sisa 45% masuk!
        if 0.5 <= c <= 8 and 15 <= s <= 65 and rg <= 50 and 0.3 <= chg24 <= 12:
            bottom.append(k)
        # EARLY 8-25% -> NEON 13.6% masuk!
        elif 8 <= c <= 25 and 8 <= s <= 45 and rg <= 60 and 3 <= chg24 <= 30:
            early.append(k)
        # PRE 25-60% -> GTC 21.9% BR 16% masuk!
        elif 25 <= c <= 60 and 3 <= s <= 35 and rg <= 75 and 10 <= chg24 <= 70:
            pre.append(k)
        # TRENDING ULTRA 60-150% -> UCJL 120% masuk!
        elif 60 <= c <= 150 and 1 <= s <= 30 and rg <= 90 and v >= 0.35 and chg24 >= 20:
            trending.append(k)
    return (
        sorted(bottom, key=lambda x: (x['sisa'], x['vol']), reverse=True)[:4],
        sorted(early, key=lambda x: x['vol'], reverse=True)[:4],
        sorted(pre, key=lambda x: x['vol'], reverse=True)[:4],
        sorted(trending, key=lambda x: x['vol'], reverse=True)[:6]
    )

def kirim(msg):
    token=os.getenv('TELE_TOKEN'); chat=os.getenv('TELE_CHAT_ID')
    if not token or not chat:
        print(msg); return
    try:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id":chat,"text":msg}, timeout=15)
    except: pass

if __name__=="__main__":
    data=get_data()
    b, e, p, t = scan(data)
    msg = f"V24.1 BOTTOM FIX UNMD Data {len(data)} | B{len(b)} E{len(e)} P{len(p)} T{len(t)}\n\n"
    if b:
        msg += "BOTTOM (bisa 120% kayak UCJL!)\n"
        for k in b:
            msg += f"{k['sym']} {k['chg']:.1f}% 24h {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg += "\n"
    if e:
        msg += "EARLY FRESH\n"
        for k in e:
            msg += f"{k['sym']} {k['chg']:.1f}% {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg += "\n"
    if p:
        msg += "PRE\n"
        for k in p:
            msg += f"{k['sym']} {k['chg']:.1f}% {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg += "\n"
    msg += "TRENDING ULTRA\n"
    if t:
        for k in t:
            if k['chg']>=100: tag=" 🚀120%!!!"
            elif k['sisa']<7: tag=" PUCUK!"
            else: tag=""
            msg += f"{k['sym']} {k['chg']:.1f}% {k['chg24']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn{tag}\n"
    else:
        msg += "kosong\n"
    print(msg)
    kirim(msg)
