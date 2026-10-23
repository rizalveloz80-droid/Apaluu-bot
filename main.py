import requests, os

# 1. BLOCKED PERMANEN - DELISTING + SAMPAH!
BLOCKED_HARD = [
    'BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','PAXG_IDR',
    # DELISTING / MAU DELISTING INDODAX!
    'MITO_IDR','ERN_IDR','UNMD_IDR','ARC_IDR','SKYAI_IDR','PUMP_IDR','MAVIA_IDR',
    'LUNA_IDR','LUNC_IDR','FTM_IDR','BTT_IDR','XEM_IDR','USELESS_IDR',
    # ALT FAKE - REAL -35%!
    'ALT_IDR','ALTLAYER_IDR',
    # HARGA <20 auto block di bawah!
]

def get_data():
    try:
        tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers',{})
        summ = requests.get("https://indodax.com/api/summaries", timeout=15).json()
        change_24h = {}
        for k,v in summ.get('tickers',{}).items():
            try: change_24h[k]=float(v.get('percent_change',0))
            except: pass
        
        # Kalo summaries 0 semua = API down, JANGAN fallback! Return kosong aja!
        if len([v for v in change_24h.values() if abs(v)>0.1]) < 10:
            print("API summaries down! Skip biar ga Data 18 palsu!")
            return []

        out=[]
        for pair,d in tickers.items():
            if not pair.endswith('_idr'): continue
            sym=pair.upper()
            if sym in BLOCKED_HARD: continue
            try:
                last=float(d['last']); low=float(d['low']); high=float(d['high']); vol=float(d['vol_idr'])
                # 2. FILTER HARGA 11 RUPIAH! UNMD HARGA 11 = BUANG!
                if last < 20: continue
                if low < 10: continue

                vol_bn=vol/1e9
                if vol_bn < 0.20: continue

                chg24 = change_24h.get(pair, 0)
                if chg24 == 0: continue # jangan fallback chg_low palsu!
                if chg24 < -4: continue # ALT -35% auto block!
                if chg24 < 0.5: continue
                if chg24 > 80: continue # biar ga kejar pucuk 100%+

                sisa=(high-last)/last*100 if last else 0
                rg=(high-low)/low*100 if low else 0
                if sisa < 8: continue # BMT 4% PUCUK block!
                if sisa > 65: continue
                if rg > 75: continue

                out.append({'sym':sym,'chg':chg24,'sisa':sisa,'range':rg,'vol':vol_bn})
            except: continue
        return out
    except Exception as e:
        print(f"ERR {e}")
        return []

def scan(data):
    bottom=[]; early=[]
    for k in data:
        c=k['chg']; s=k['sisa']
        if 0.5 <= c <= 12 and 15 <= s <= 65:
            bottom.append(k)
        elif 12 <= c <= 35 and 10 <= s <= 50:
            early.append(k)
    return (
        sorted(bottom, key=lambda x: x['vol'], reverse=True)[:5],
        sorted(early, key=lambda x: x['vol'], reverse=True)[:5]
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
    b, e = scan(data)
    msg = f"V26 ANTI SAMPAH Data {len(data)} | B{len(b)} E{len(e)}\n\n"
    if b:
        msg += "BOTTOM SEGAR\n"
        for k in b: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg+="\n"
    if e:
        msg += "EARLY FRESH\n"
        for k in e: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg+="\n"
    if not b and not e:
        msg += "Ga ada yang segar, API down atau semua pucuk. Tunggu!\n"
    print(msg)
    kirim(msg)
