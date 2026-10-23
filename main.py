import requests, os

BLOCKED = [
    'BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','DAI_IDR','PAXG_IDR',
    'MITO_IDR','ERN_IDR','UNMD_IDR', # delisting + harga 11
    'LUNA_IDR','LUNC_IDR','FTM_IDR','BTT_IDR','XEM_IDR','USELESS_IDR',
    'ARC_IDR','SKYAI_IDR','PUMP_IDR','MAVIA_IDR'
]

def get_data():
    try:
        tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers',{})
        summ = requests.get("https://indodax.com/api/summaries", timeout=15).json()
        change = {}
        for k,v in summ.get('tickers',{}).items():
            try:
                change[k] = float(v.get('percent_change', 0))
            except:
                pass
        
        out = []
        for pair,d in tickers.items():
            if not pair.endswith('_idr'):
                continue
            sym = pair.upper()
            if sym in BLOCKED:
                continue
            try:
                last = float(d['last'])
                low = float(d['low'])
                high = float(d['high'])
                vol = float(d['vol_idr'])
                
                if last < 25:  # harga 11 kayak UNMD buang!
                    continue
                    
                vol_bn = vol / 1e9
                if vol_bn < 0.12:
                    continue

                chg24 = change.get(pair, 0)
                if abs(chg24) < 0.1:
                    chg24 = (last - low) / low * 100 if low else 0

                # MERAH BOLEH SAMPE -25%, -35% BARU BLOCK!
                if chg24 < -25:
                    continue
                
                chg_low = (last - low) / low * 100 if low else 0
                sisa = (high - last) / last * 100 if last else 0
                rg = (high - low) / low * 100 if low else 0

                # 🔴 BOUNCE MERAH: -15.88% low+5.1% sisa 23% = kaya ALT lu +2.13%!
                is_bounce = chg24 < 0 and 1.5 <= chg_low <= 15 and 10 <= sisa <= 45
                # BOTTOM HIJAU: 0.5% - 40% sisa 8-65%
                is_green = 0.5 <= chg24 <= 40 and 8 <= sisa <= 65

                if not (is_bounce or is_green):
                    continue
                if rg > 80:
                    continue

                out.append({
                    'sym': sym,
                    'chg': chg24,
                    'low': chg_low,
                    'sisa': sisa,
                    'range': rg,
                    'vol': vol_bn,
                    'bounce': is_bounce
                })
            except:
                continue
        return out
    except Exception as e:
        print(f"ERR get_data {e}")
        return []

def scan(data):
    bounce = []
    bottom = []
    early = []
    for k in data:
        if k['bounce']:
            bounce.append(k)
        elif 0.5 <= k['chg'] <= 12:
            bottom.append(k)
        elif 12 < k['chg'] <= 35:
            early.append(k)
    
    return (
        sorted(bounce, key=lambda x: (x['vol'], x['sisa']), reverse=True)[:4],
        sorted(bottom, key=lambda x: x['vol'], reverse=True)[:4],
        sorted(early, key=lambda x: x['vol'], reverse=True)[:4]
    )

def kirim(msg):
    token = os.getenv('TELE_TOKEN')
    chat = os.getenv('TELE_CHAT_ID')
    if not token or not chat:
        print(msg)
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat, "text": msg},
            timeout=15
        )
    except:
        pass

if __name__ == "__main__":
    data = get_data()
    bnc, btm, erl = scan(data)
    
    msg = f"V28 RED BOUNCE Data {len(data)} | 🔴{len(bnc)} B{len(btm)} E{len(erl)}\n\n"
    
    if bnc:
        msg += "🔴 BOUNCE MERAH PROFIT\n"
        for k in bnc:
            msg += f"{k['sym']} {k['chg']:.1f}% low+{k['low']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg += "\n"
    
    if btm:
        msg += "BOTTOM SEGAR\n"
        for k in btm:
            msg += f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg += "\n"
        
    if erl:
        msg += "EARLY FRESH\n"
        for k in erl:
            msg += f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    
    if not bnc and not btm and not erl:
        msg += f"Ga ada yang segar Data {len(data)}\n"
    
    print(msg)
    kirim(msg)
