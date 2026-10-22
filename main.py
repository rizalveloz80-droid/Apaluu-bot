import requests, os, datetime

VOL_MIN = 10000000
S_MIN = 0.8
H_MAX = 30.0
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_tele(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except: pass

try:
    tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json().get("tickers", {})
except:
    tickers = {}

now = datetime.datetime.now().strftime("%H:%M WIB")
hasil = []

for pair, data in tickers.items():
    if not pair.endswith("_idr"): continue
    try:
        last = float(data.get("last", 0))
        low = float(data.get("low", 0))
        high = float(data.get("high", 0))
        vol = float(data.get("vol_idr", 0))
        if low == 0 or vol < VOL_MIN: continue
        chg = ((last-low)/low)*100
        if chg < S_MIN or chg > H_MAX: continue
        th = ((high-last)/last)*100 if last>0 else 0
        if th < 0: continue
        hasil.append((pair, chg, vol, th))
    except: continue

hasil = sorted(hasil, key=lambda x: x[2], reverse=True)

if not hasil:
    send_tele(f"KOSONG SCAN {now} V15.3 ULTRA LIGHT Vol 10Mn")
else:
    msg = f"SCAN {now} V15.3 ULTRA LIGHT\n"
    for p,c,v,th in hasil[:8]:
        msg += f"{p.upper()} {c:.2f}% Vol {v/1e9:.1f}Bn TH {th:.1f}%\n"
    send_tele(msg)

print(f"SCAN {now} hasil:{len(hasil)}")
