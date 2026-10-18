import requests, os
from datetime import datetime

# BLACKLIST FINAL - CUMA STABLE + BTC/ETH + GHOST BENERAN (ERN)
FORCE_BLACKLIST = set([
    "usdt_idr","usdc_idr","idrt_idr","usde_idr","xaut_idr","paxg_idr","ouros_idr",
    "btc_idr","eth_idr","xrp_idr","sol_idr","bnb_idr","gid_idr","col_idr",
    "okusd_idr","lyfel_idr","dfg_idr","inr_idr","eur_idr","indr_idr","neorpnew_idr",
    "ern_idr"  # <-- CUMA ERN DOANG YANG HANTU! AIH & XR UDAH GUE BALIKIN!
])

TELE_TOKEN=os.getenv("TELE_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
TELE_CHAT_ID=os.getenv("TELE_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID")

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT_ID: return
    try: requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", data={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=20)
    except: pass

tickers=requests.get("https://indodax.com/api/tickers", timeout=20).json()["tickers"]

cands=[]
for pair,data in tickers.items():
    pl=pair.lower()
    if not pl.endswith("_idr"): continue
    if pl in FORCE_BLACKLIST: continue
    try:
        last=float(data["last"]); low=float(data["low"]); high=float(data["high"]); vol=float(data["vol_idr"])
        if vol < 100000 or last==0 or low==0: continue
        dl=((last-low)/last*100) if last>0 else 0
        if dl>80: continue
        cands.append((pair.upper(),dl,vol))
    except: continue

cands.sort(key=lambda x: -x[2])

super_t=[c for c in cands if c[2]>=3000000000][:3]
trend=[c for c in cands if c[1]>=15][:5]

now=datetime.now().strftime('%H:%M')
msg=f"V36 FIX AIH XR BALIK | {now}\nSCAN {len(tickers)} CANDS {len(cands)}\n\n"

if super_t:
    msg+=f"🚨 SUPER >3Bn ({len(super_t)}):\n"
    for c in super_t: msg+=f"-> {c[0]} {int(c[1])}% low Vol {int(c[2]/1000000000*10)/10}Bn\n"
    msg+="\n"
if trend:
    msg+=f"🔥 TRENDING >=15% ({len(trend)}):\n"
    for c in trend: msg+=f"-> {c[0]} {int(c[1])}% low Vol {int(c[2]/1000000)}jt\n"
    msg+="\n"

print(msg)
send_tele(msg)
