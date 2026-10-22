 # main.py - V18.5 10 KOINS - FIX SYNTAX ERROR
import requests

BLOCKED = [
    'BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','DAI_IDR',
    'SHIB_IDR','DOGE_IDR','PEPE_IDR','BONK_IDR','FLOKI_IDR'
]

def scan_v18_5(data):
    early = []
    hunter = []
    segar = []
    for koin in data:
        symbol = koin.get('symbol','')
        chg = float(koin.get('chg',0))
        th = float(koin.get('th',0))
        vol = float(koin.get('vol',0))
        last = float(koin.get('last',0))
        low = float(koin.get('low',1))
        if symbol in BLOCKED:
            continue
        if vol < 0.025:
            continue
        if 1.0 <= chg <= 4.0 and th <= 5.0 and vol >= 0.08 and last > low:
            early.append(koin)
        elif chg > 4.0 and th <= 10.0 and vol >= 0.07:
            hunter.append(koin)
        elif chg <= 4.0 and th <= 12.0 and vol >= 0.15:
            segar.append(koin)
    early = sorted(early, key=lambda x: float(x['chg']))[:3]
    hunter = sorted(hunter, key=lambda x: float(x['th']))[:3]
    segar = sorted(segar, key=lambda x: float(x['vol']), reverse=True)[:4]
    return early, hunter, segar

def format_tele(early, hunter, segar):
    msg = "SCAN V18.5 10 KOINS\n"
    msg += f"Early {len(early)} Hunter {len(hunter)} Segar {len(segar)}\n\n"
    for k in early:
        msg += f"EARLY {k['symbol']} {k['chg']}% TH {k['th']}% Vol {k['vol']}Bn\n"
    for k in hunter:
        msg += f"HUNTER {k['symbol']} {k['chg']}% TH {k['th']}% Vol {k['vol']}Bn\n"
    for k in segar:
        msg += f"SEGAR {k['symbol']} {k['chg']}% TH {k['th']}% Vol {k['vol']}Bn\n"
    return msg

# contoh run
if __name__ == "__main__":
    data = []  # isi data indodax lu disini
    e,h,s = scan_v18_5(data)
    print(format_tele(e,h,s))
