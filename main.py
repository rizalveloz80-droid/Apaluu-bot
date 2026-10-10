import os, requests, pytz
from datetime import datetime

TOKEN = (os.getenv("TELEGRAM_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
CHAT_ID = (os.getenv("CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID") or "").strip()

def kirim(pesan):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": pesan, "parse_mode": "HTML"}, timeout=20)

wib = datetime.now(pytz.timezone('Asia/Jakarta'))
jam = wib.strftime("%H:%M WIB")

try:
    data = requests.get("https://indodax.com/api/tickers", timeout=20).json().get("tickers", {})
    BLACKLIST = {"BTC","ETH","USDT","USDC","DAI","BNB","XRP","SOL","TRX","DOT","MATIC","LTC"}

    calon = []
    for koin, d in data.items():
        if not koin.endswith("_idr"): continue
        nama = koin.upper().replace("_IDR","")
        if nama in BLACKLIST: continue
        try:
            last = float(d.get("last",0))
            low = float(d.get("low",0))
            high = float(d.get("high",0))
            vol = float(d.get("vol_idr",0))
            if low==0 or high==0: continue
            if not (last < 10000 and vol >= 500_000): continue

            gain = ((last-low)/low)*100
            pos = ((last-low)/(high-low)*100) if high!=low else 0
            hl = ((high-low)/low)*100

            # ALL COIN MICIN - baru mau pump
            if not (0.3 <= gain <= 20 and pos >= 65 and hl >= 1.5): continue

            skor = pos*0.7 + gain*0.3
            calon.append((nama, last, gain, pos, vol, skor))
        except: continue

    calon = sorted(calon, key=lambda x: x[5], reverse=True)[:7]

    if not calon:
        pesan = f"🔍 <b>MICIN HUNTER - {jam}</b>\n\nBelum ada micin siap pump. Market sepi. Scan lagi 5 menit!"
    else:
        txt = f"🚀 <b>TOP {len(calon)} MICIN & ALT ALL COIN - {jam}</b>\n"
        txt += f"Filter: Harga <10K | Vol >0.5jt | Pos >65% (Semua koin, bukan cuma STIK/DUPE)\n\n"
        for i,(coin,last,gain,pos,vol,skor) in enumerate(calon,1):
            tag = "MICIN GACOR" if last < 700 else "ALT KECIL"
            tp50 = last*1.5
            txt += f"{i}. <b>{coin}</b> [{tag}]\n"
            txt += f" 💰 {last:.0f} | Gain {gain:.1f}% | Pos {pos:.0f}% | Vol {vol/1_000_000:.1f}jt\n"
            txt += f" 🎯 TP 50% ~ {tp50:.0f} IDR\n\n"
        txt += f"⚡ Fokus No 1-2! Potensi kayak STIK/DUPE/MAGIC!\n⏰ {wib.strftime('%d-%m %H:%M')} WIB"
        pesan = txt

except Exception as e:
    pesan = f"Error: {e}"

kirim(pesan)
