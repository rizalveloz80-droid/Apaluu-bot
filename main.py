import requests, os, time
from datetime import datetime, timedelta

TELE_TOKEN = os.getenv("TELE_TOKEN")
TELE_CHAT_ID = os.getenv("TELE_CHAT_ID")

def send_tele(msg):
    try:
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELE_CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=15)
    except Exception as e:
        print(e)

def main():
    print("SCAN DINI RUN MODE...")
    try:
        data = requests.get("https://indodax.com/api/tickers", timeout=10).json()['tickers']
    except: return

    now_wib = datetime.utcnow() + timedelta(hours=7)
    jam_str = now_wib.strftime("%H:%M")
    total_koin = len([k for k in data.keys() if k.endswith("_idr")])

    hasil = []
    for pair, t in data.items():
        if not pair.endswith("_idr"): continue
        try:
            last = float(t['last']); high = float(t['high']); low = float(t['low']); vol = float(t['vol_idr'])
            if low==0 or high==0: continue

            naik_low = (last - low) / low * 100
            sisa_high = (high - last) / high * 100 if high>0 else 0

            # RUMUS PERSIS ZEREBRO & SHOW DI SCREENSHOT LU:
            # Naik 6-9% dari low, Sisa 10-40% ke high, Vol gede
            if 4 <= naik_low <= 12 and sisa_high >= 10 and vol > 100000000: # vol >100jt
                # Format vol
                if vol >= 1e9:
                    vol_str = f"{vol/1e9:.2f} Bn"
                else:
                    vol_str = f"{vol/1e6:.0f} Mn"

                coin = pair.replace("_idr","").upper()
                hasil.append((vol, f"{coin} 🎯 RUN\nNaik {naik_low:.1f}% dari low | Sisa {sisa_high:.0f}% ke high\nVol {vol_str}"))
        except: continue

    # Sort vol gede di atas kayak ZEREBRO 6.99Bn paling atas
    hasil.sort(key=lambda x: x[0], reverse=True)

    if hasil:
        pesan = f"🚨 SCAN DINI {jam_str} WIB | {total_koin} koin\n\n"
        for i, (vol, txt) in enumerate(hasil[:10], 1): # Top 10 aja biar ga spam
            pesan += f"{i}. {txt}\n\n"
        send_tele(pesan)
    else:
        pesan = f"🚨 SCAN DINI {jam_str} WIB | {total_koin} koin\n\nKOSONG - market tenang, jangan maksa entry."
        send_tele(pesan)

    print("SELESAI")

if __name__ == "__main__":
    main()
