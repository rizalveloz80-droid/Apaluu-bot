import requests, os
from datetime import datetime

# BLACKLIST DOANG, GA PAKE WHITELIST LAGI!
FORCE_BLACKLIST = set([
    "usdt_idr","usdc_idr","idrt_idr","usde_idr","xaut_idr","paxg_idr","ouros_idr",
    "btc_idr","eth_idr","xrp_idr","sol_idr","bnb_idr","gid_idr","col_idr",
    "okusd_idr","lyfel_idr","dfg_idr","inr_idr","eur_idr","indr_idr","neorpnew_idr",
    "soon_idr","avas_idr"
])

TELE_TOKEN=os.getenv("TELE_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
TELE_CHAT_ID=os.getenv("TELE_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID")

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT_ID: return
    try: requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", data={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=20)
    except: pass

try:
    tickers=requests.get("https://indodax.com/api/tickers", timeout=20).json()["tickers"]
except Exception as e:
    print(f"GAGAL API TICKERS: {e}")
    exit()

cands=[]
blacklist_hit=0
for pair,data in tickers.items():
    pl=pair.lower()
    if not pl.endswith("_idr"): continue
    if pl in FORCE_BLACKLIST:
        blacklist_hit+=1
        continue
    try:
        last=float(data["last"]); low=float(data["low"]); high=float(data["high"]); vol=float(data["vol_idr"])
        if vol < 50000: continue
        dl=((last-low)/last*100) if last>0 else 0
        cands.append((pair.upper(),dl,vol,last))
    except:
        continue

print(f"DEBUG: TICKERS {len(tickers)} BLACKLIST {blacklist_hit} DAPET {len(cands)} COIN")

cands.sort(key=lambda x: -x[2]) # sort vol terbesar

top=cands[:15]
trending=[c for c in cands if c[1] >= 10][:5] # dl >=10%
gold=[c for c in cands if c[1] <= 3][:5] # deket low

now=datetime.now().strftime('%H:%M')
msg=f"V33 FIX WHITELIST | {now}\nSCAN {len(tickers)} BL {blacklist_hit} CANDS {len(cands)}\n\n"

msg+=f"🚨 TOP VOL ({len(top)}):\n"
for c in top:
    msg+=f"-> {c[0]} {int(c[1])}% low Vol {int(c[2]/1000000)}jt\n"
msg+="\n"

if trending:
    msg+=f"🔥 TRENDING dl>=10% ({len(trending)}):\n"
    for c in trending: msg+=f"-> {c[0]} {int(c[1])}% low Vol {int(c[2]/1000000)}jt\n"
    msg+="\n"

if gold:
    msg+=f"GOLD deket low ({len(gold)}): {', '.join([f'{c[0]} {int(c[1])}% ' for c in gold])}\n"

print(msg)
send_tele(msg)
