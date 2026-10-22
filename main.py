import requests, os, datetime

VOL_SEGAR = 100000000   # deteksi dini 100Mn aja
VOL_HUNTER = 500000000  # hunter harus 500Mn
S_MIN = 1.2  # balikin ke 1.2 biar ZEREBRO 1.12% masuk
H_MIN = 4.0
MAX_CHG = 30.0
TH_MAX_SEGAR = 15.0
TH_MAX_HUNTER = 10.0
BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID") or os.getenv("TELE_CHAT_ID")

def send_tele(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except: pass

try:
    tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json().get("tickers", {})
except:
    tickers = {}

wib = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
now = wib.strftime("%H:%M WIB")

segar = []
hunter = []

for pair, data in tickers.items():
    if not pair.endswith("_idr"): continue
    try:
        last = float(data.get("last", 0))
        low = float(data.get("low", 0))
        high = float(data.get("high", 0))
        vol = float(data.get("vol_idr", 0))
        if low == 0: continue
        chg = ((last-low)/low)*100
        if chg < S_MIN or chg > MAX_CHG: continue
        th = ((high-last)/last)*100 if last>0 else 0
        if th < 0: continue
        
        if chg <= H_MIN:
            if vol < VOL_SEGAR: continue
            if th > TH_MAX_SEGAR: continue
            segar.append((pair, chg, vol, th))
        else:
            if vol < VOL_HUNTER: continue
            if th > TH_MAX_HUNTER: continue
            hunter.append((pair, chg, vol, th))
    except: continue

segar = sorted(segar, key=lambda x: x[2], reverse=True)[:5]
hunter = sorted(hunter, key=lambda x: x[1], reverse=True)[:5]

if not segar and not hunter:
    send_tele(f"KOSONG SCAN {now} V15.6 DETEKSI DINI")
else:
    msg = f"SCAN {now} V15.6 DETEKSI DINI\n"
    if segar:
        msg += f"\n-- 🌱 SEGAR 1.2-4% (dini) --\n"
        for p,c,v,th in segar:
            msg += f"{p.upper()} {c:.2f}% Vol {v/1e9:.2f}Bn TH {th:.1f}%\n"
    if hunter:
        msg += f"\n-- 🚀 HUNTER 4-30% --\n"
        for p,c,v,th in hunter:
            msg += f"{p.upper()} {c:.2f}% Vol {v/1e9:.1f}Bn TH {th:.1f}%\n"
    send_tele(msg)

print(f"SCAN {now} segar:{len(segar)} hunter:{len(hunter)}")
