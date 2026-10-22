# main.py - V18.5 10 KOINS - FIX DATA KOSONG
import requests

BLOCKED = ['BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','DAI_IDR','SHIB_IDR','DOGE_IDR']

def get_indodax_data():
    url = "https://indodax.com/api/tickers"
    r = requests.get(url, timeout=15).json()
    out = []
    for pair, d in r['tickers'].items():
        if not pair.endswith('_idr'):
            continue
        try:
            last = float(d['last'])
            low = float(d['low'])
            high = float(d['high'])
            vol_idr = float(d['vol_idr'])
            if low == 0:
                continue
            chg = (last - low) / low * 100
            th = (high - last) / last * 100 if last>0 else 0
            vol_bn = vol_idr / 1_000_000_000
            out.append({
                'symbol': pair.upper(),
                'chg': chg,
                'th': th,
                'vol': vol_bn,
                'last': last,
                'low': low,
                'high': high
            })
        except:
            continue
    return out

def scan_v18_5(data):
    early=[]; hunter=[]; segar=[]
    for koin in data:
        s=koin['symbol']; chg=koin['chg']; th=koin['th']; vol=koin['vol']; last=koin['last']; low=koin['low']
        if s in BLOCKED: continue
        if vol < 0.025: continue
        if 1.0 <= chg <= 4.0 and th <= 5.0 and vol >= 0.08 and last > low:
            early.append(koin)
        elif chg > 4.0 and th <= 10.0 and vol >= 0.07:
            hunter.append(koin)
        elif chg <= 4.0 and th <= 12.0 and vol >= 0.15:
            segar.append(koin)
    early=sorted(early, key=lambda x: x['chg'])[:3]
    hunter=sorted(hunter, key=lambda x: x['th'])[:3]
    segar=sorted(segar, key=lambda x: x['vol'], reverse=True)[:4]
    return early,hunter,segar

if __name__ == "__main__":
    data = get_indodax_data()
    early,hunter,segar = scan_v18_5(data)
    print(f"SCAN V18.5 10 KOINS")
    print(f"Total data {len(data)} | Early {len(early)} Hunter {len(hunter)} Segar {len(segar)}")
    for k in early:
        print(f"EARLY {k['symbol']} {k['chg']:.1f}% TH {k['th']:.1f}% Vol {k['vol']:.2f}Bn")
    for k in hunter:
        print(f"HUNTER {k['symbol']} {k['chg']:.1f}% TH {k['th']:.1f}% Vol {k['vol']:.2f}Bn")
    for k in segar:
        print(f"SEGAR {k['symbol']} {k['chg']:.1f}% TH {k['th']:.1f}% Vol {k['vol']:.2f}Bn")
