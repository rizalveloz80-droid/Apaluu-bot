import requests, os
from datetime import datetime, timedelta

TELE_TOKEN = os.getenv("TELE_TOKEN")
TELE_CHAT_ID = os.getenv("TELE_CHAT_ID")

VERSI = "V10 ANTI ERN FINAL" # <- ini buat tanda

def send_tele(msg):
    try:
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELE_CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except: pass

def main():
    print(f"{VERSI} JALAN...")
    try:
        active_pairs = requests.get("https://indodax.com/api/pairs", timeout=10).json()
        active_ids = set([p['id'] for p in active_pairs])
        data = requests.get("https://indodax.com/api/tickers", timeout=10).json()['tickers']
    except: return

    now_wib = datetime.utcnow() + timedelta(hours=7)
    jam_str = now_wib.strftime("%H:%M")

    BLACKLIST = ["ern_idr", "bome_idr", "luna_idr"] # ERN PASTI KE-FILTER DISINI

    hasil = []
    for pair, t in data.items():
        if pair not in active_ids: continue
        if pair in BLACKLIST: 
            print(f"SKIP BLACKLIST {pair}")
            continue
        if not pair.endswith("_idr"): continue
        try:
            last = float(t['last']); high = float(t['high']); low = float(t['low']); vol = float(t['vol_idr'])
            if low==0 or high==0 or last==0: continue
            naik = (last - low) / low * 100
            sisa = (high - last) / high * 100 if high>0 else 0
            if vol < 80000000 or not (1 <= naik <= 12) or sisa < 10: continue

            coin = pair.replace("_idr","").upper()
            vstr = f"{vol/1e9:.2f} Bn" if vol>=1e9 else f"{vol/1e6:.0f} Mn"
            tipe = "🌱 DINI" if naik <=4 else "🚀 RUN"
            hasil.append((vol, f"{coin} 🎯 {tipe}\nNaik {naik:.1f}% | Sisa {sisa:.0f}% | Vol {vstr}"))
        except: continue

    hasil.sort(key=lambda x: x[0], reverse=True)

    if hasil:
        pesan = f"🚨 SCAN DINI {jam_str} WIB | {VERSI}\n{len(active_ids)} koin aktif\n\n"
        for i, (vol, txt) in enumerate(hasil[:8], 1):
            pesan += f"{i}. {txt}\n\n"
        send_tele(pesan)
    else:
        send_tele(f"🚨 SCAN DINI {jam_str} WIB | {VERSI}\n\nKOSONG - ERN udah ke-filter ✅")

if __name__ == "__main__":
    main()
