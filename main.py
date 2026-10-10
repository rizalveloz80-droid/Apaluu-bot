import os, requests, pytz
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID")
if not TOKEN or not CHAT_ID: exit(0)

def kirim(pesan):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": pesan, "parse_mode": "HTML"}
    requests.post(url, data=data, timeout=20)

wib = datetime.now(pytz.timezone('Asia/Jakarta'))
jam = wib.strftime("%H:%M WIB")

try:
    tick = requests.get("https://indodax.com/api/tickers", timeout=15).json().get("tickers", {})

    # COIN GEDE & STABLE JANGAN MASUK
    BLACKLIST = {"BTC","ETH","USDT","USDC","DAI","BNB","XRP","SOL","DOGE","ADA","TRX","DOT","MATIC","LTC"}

    micin = [] # harga < 500 IDR
    alt_kecil = [] # harga 500 - 10000 IDR

    for koin, d in tick.items():
        if not koin.endswith("_idr"): continue
        nama = koin.upper().replace("_IDR","")
        if nama in BLACKLIST: continue

        try:
            last = float(d.get("last",0))
            low = float(d.get("low",0))
            high = float(d.get("high",0))
            vol_idr = float(d.get("vol_idr",0))
            if low==0 or last==0 or vol_idr < 1_000_000: continue

            gain = ((last-low)/low)*100
            gain_hl = ((high-low)/low)*100 if low else 0
            pos = ((last-low)/(high-low)*100) if high!=low else 0

            # FILTER MICIN & ALT KECIL YANG BARU MAU PUMP
            # Gain 1-15%, H-L 2-20%, Posisi 75-99% deket High
            if not (1.0 <= gain <= 15.0 and 2.0 <= gain_hl <= 20.0 and 75 <= pos <= 99): continue
            if not (5_000_000 <= vol_idr <= 1_500_000_000): continue # Vol 5jt - 1.5M, baru rame

            item = (nama, gain, gain_hl, vol_idr, pos, last)

            if last < 500: # MICIN MURAH BANGET
                micin.append(item)
            elif last <= 10000: # ALT KECIL
                alt_kecil.append(item)

        except: continue

    micin = sorted(micin, key=lambda x: x[4], reverse=True)[:4]
    alt_kecil = sorted(alt_kecil, key=lambda x: x[4], reverse=True)[:3]
    hasil = micin + alt_kecil

    if not hasil:
        pesan = f"🔍 <b>MICIN HUNTER - {jam}</b>\n\nBelum ada micin fresh pump, vol masih <5jt. Next 5 menit lagi scan!"
    else:
        txt = f"💎 <b>TOP 7 MICIN & ALT KECIL - {jam}</b>\n\n"
        txt += f"Filter: Harga <10K | Vol 5jt-1.5M | Pos 75-99% High\nMicin Fresh Pump\n\n"
        for i,(coin,g,ghl,vol,pos,last) in enumerate(hasil,1):
            tag = "MICIN" if last < 500 else "ALT"
            txt += f"{i}. {coin} [{tag}] | {last:.0f} IDR | Gain {g:.2f}% | Pos {pos:.0f}% | Vol {vol/1_000_000:.1f}M\n"
        txt += f"\nFokus No 1-2 Micin!\nWaktu: {wib.strftime('%d-%m %H:%M')} WIB"
        pesan = txt

except Exception as e:
    pesan = f"Error micin: {e}"

kirim(pesan)
