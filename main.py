import requests, os, datetime

VOL_MIN = 500000000  # naikin jadi 500Mn biar ga 0.1Bn kayak ONT
S_MIN = 1.5
H_MIN = 4.0
MAX_CHG = 30.0
TH_MAX_SEGAR = 15.0  # segar ga boleh jauh dari high >15%
TH_MAX_HUNTER = 10.0 # hunter ga boleh jauh >10%
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

now = datetime.datetime.now().strftime("%H:%M WIB")
segar = []
hunter = []

for pair, data in tickers.items():
    if not pair.endswith("_idr"): continue
    try:
        last = float(data.get("last", 0))
        low = float(data.get("low", 0))
        high = float(data.get("high", 0))
        vol = float(data.get("vol_idr", 0))
        if low == 0 or vol < VOL_MIN: continue
        chg = ((last-low)/low)*100
        if chg < S_MIN or chg > MAX_CHG: continue
        th = ((high-last)/last)*100 if last>0 else 0
        if th < 0: continue
        
        # FILTER ANTI NYANGKUT BARU
        if chg <= H_MIN:
            if th > TH_MAX_SEGAR: continue  # segar tapi udah jatuh 37% buang!
            segar.append((pair, chg, vol, th))
        else:
            if th > TH_MAX_HUNTER: continue  # hunter tapi udah jatuh 29% buang!
            hunter.append((pair, chg, vol, th))
    except: continue

segar = sorted(segar, key=lambda x: x[2], reverse=True)[:5]
hunter = sorted(hunter, key=lambda x: x[1], reverse=True)[:5]

if not segar and not hunter:
    send_tele(f"KOSONG SCAN {now} V15.5 ANTI NYANGKUT Vol 500Mn")
else:
    msg = f"SCAN {now} V15.5 ANTI NYANGKUT\n"
    if segar:
        msg += f"\n-- SEGAR 1.5-4% TH<15% --\n"
        for p,c,v,th in segar:
            msg += f"{p.upper()} {c:.2f}% Vol {v/1e9:.1f}Bn TH {th:.1f}%\n"
    if hunter:
        msg += f"\n-- HUNTER 4-30% TH<10% --\n"
        for p,c,v,th in hunter:
            msg += f"{p.upper()} {c:.2f}% Vol {v/1e9:.1f}Bn TH {th:.1f}%\n"
    send_tele(msg)

print(f"SCAN {now} segar:{len(segar)} hunter:{len(hunter)}")
