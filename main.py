import requests
import os

# FINAL BLOCK LIST - BR & ZEREBRO GA DI BLOCK!
BLOCKED = [
    'BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','DAI_IDR',
    'XRP_IDR','SOL_IDR','DOGE_IDR','SHIB_IDR','PEPE_IDR','BONK_IDR','FLOKI_IDR',
    'ADA_IDR','FARTCOIN_IDR','HYPE_IDR','TRX_IDR','AVAX_IDR','LINK_IDR','DOT_IDR',
    'SUI_IDR','ASTER_IDR','ONDO_IDR',
    'PAXG_IDR','KITE_IDR',
    'PIPPIN_IDR','PENGU_IDR',
]

def get_indodax_data():
    try:
        r = requests.get("https://indodax.com/api/tickers", timeout=20).json()
        out = []
        for pair, d in r.get('tickers', {}).items():
            if not pair.endswith('_idr'):
                continue
            try:
                last = float(d['last']); low = float(d['low']); high = float(d['high']); vol = float(d['vol_idr'])
                if low == 0: continue
                chg = (last - low) / low * 100
                th = (high - last) / last * 100 if last > 0 else 99
                out.append({'symbol': pair.upper(), 'chg': chg, 'th': th, 'vol': vol/1e9, 'last': last})
            except:
                continue
        return out
    except:
        return []

def scan_v18_7(data):
    early = []; hunter = []; segar = []
    for k in data:
        if k['symbol'] in BLOCKED:
            continue
        v = k['vol']; c = k['chg']; t = k['th']
        # EARLY - buat tahan besok, paling ketat
        if 1.0 <= c <= 4.0 and t <= 4.0 and 0.10 <= v <= 1.0:
            early.append(k)
        # HUNTER - scalp, vol max 1.0 biar BR 5.38 & ZEREBRO 3.31 auto skip
        elif 4.0 < c <= 25.0 and t <= 4.0 and 0.07 <= v <= 1.0:
            hunter.append(k)
        # SEGAR - mid vol 0.15-0.60 biar PIPPIN 0.98 & PENGU 0.76 auto skip
        elif 0.5 <= c <= 4.0 and t <= 6.0 and 0.15 <= v <= 0.60:
            segar.append(k)
    
    early = sorted(early, key=lambda x: x['chg'])[:3]
    hunter = sorted(hunter, key=lambda x: x['th'])[:3]
    segar = sorted(segar, key=lambda x: x['vol'], reverse=True)[:4]
    return early, hunter, segar

def kirim_tele(pesan):
    token = os.getenv('TELE_TOKEN')
    chat = os.getenv('TELE_CHAT_ID')
    if not token or not chat:
        print("TELE TOKEN/CHAT_ID kosong")
        return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={'chat_id': chat, 'text': pesan}, timeout=10)
    except Exception as e:
        print(f"Gagal kirim tele: {e}")

if __name__ == "__main__":
    data = get_indodax_data()
    e, h, s = scan_v18_7(data)
    msg = f"SCAN V18.7 10 KOINS - FINAL FIX\nData {len(data)} | E{len(e)} H{len(h)} S{len(s)}\n\n"
    msg += "⚡ EARLY (Tahan Besok)\n"
    for k in e: msg += f"{k['symbol']} {k['chg']:.1f}% Vol {k['vol']:.2f}Bn TH {k['th']:.1f}%\n"
    msg += "\n🚀 HUNTER (Scalp)\n"
    for k in h: msg += f"{k['symbol']} {k['chg']:.1f}% TH {k['th']:.1f}% Vol {k['vol']:.2f}Bn\n"
    msg += "\n🌱 SEGAR (Mid Vol)\n"
    for k in s: msg += f"{k['symbol']} {k['chg']:.1f}% Vol {k['vol']:.2f}Bn TH {k['th']:.1f}%\n"
    print(msg)
    kirim_tele(msg)
