import os, requests, pytz
from datetime import datetime

TOKEN = (os.getenv("TELEGRAM_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
CHAT_ID = (os.getenv("CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID") or "").strip()

print(f"DEBUG TOKEN ADA: {bool(TOKEN)} CHAT_ID ADA: {bool(CHAT_ID)}")

if not TOKEN or not CHAT_ID:
    print("TOKEN/CHAT_ID KOSONG!")
    exit(1)

def kirim(pesan):
    print(f"KIRIM KE TELE: {pesan[:100]}")
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": pesan, "parse_mode": "HTML"}
    r = requests.post(url, data=data, timeout=20)
    print(f"RESPON TELE: {r.status_code} {r.text[:200]}")

wib = datetime.now(pytz.timezone('Asia/Jakarta'))
jam = wib.strftime("%H:%M WIB")

try:
    tick = requests.get("https://indodax.com/api/tickers", timeout=15).json().get("tickers", {})
    BLACKLIST = {"BTC","ETH","USDT","USDC","DAI","BNB","XRP","SOL","DOGE","ADA","TRX","DOT","MATIC","LTC"}
    micin = []
    alt_kecil = []
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
            if not (0.5 <= gain <= 20.0 and 1.0 <= gain_hl <= 25.0 and 60 <= pos <= 99): continue
            if not (1_000_000 <= vol_idr <= 5_000_000_000): continue
            item = (nama, gain, gain_hl, vol_idr, pos, last)
            if last < 500: micin.append(item)
            elif last <= 10000: alt_kecil.append(item)
        except: continue
    micin = sorted(micin, key=lambda x: x[4], reverse=True)[:4]
    alt_kecil = sorted(alt_kecil, key=lambda x: x[4], reverse=True)[:3]
    hasil = micin + alt_kecil
    print(f"HASIL: {len(hasil)} coin")
    if not hasil:
        pesan = f"🔍 <b>MICIN HUNTER - {jam}</b>\n\nBelum ada micin fresh pump yang lolos filter 60-99%. Vol masih kecil. Scan lagi 5 menit!"
    else:
        txt = f"💎 <b>TOP 7 MICIN & ALT KECIL - {jam}</b>\n\n"
        txt += f"Filter: Harga <10K | Vol 1jt-5M | Pos 60-99% High\n\n"
        for i,(coin,g,ghl,vol,pos,last) in enumerate(hasil,1):
            tag = "MICIN" if last < 500 else "ALT"
            txt += f"{i}. {coin} [{tag}] | {last:.0f} IDR | Gain {g:.2f}% | Pos {pos:.0f}% | Vol {vol/1_000_000:.1f}M\n"
        txt += f"\nFokus No 1-2!\nWaktu: {wib.strftime('%d-%m %H:%M')} WIB"
        pesan = txt
except Exception as e:
    pesan = f"Error micin: {e}"
    print(f"ERROR: {e}")

kirim(pesan)
