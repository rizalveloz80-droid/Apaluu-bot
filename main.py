import requests, os
from datetime import datetime

FORCE_BLACKLIST = set([
    "usdt_idr","usdc_idr","idrt_idr","usde_idr","xaut_idr","paxg_idr","ouros_idr",
    "btc_idr","eth_idr","xrp_idr","sol_idr","bnb_idr","gid_idr","col_idr",
    "okusd_idr","lyfel_idr","dfg_idr","inr_idr","eur_idr","indr_idr","neorpnew_idr"
])

TELE_TOKEN=os.getenv("TELE_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
TELE_CHAT_ID=os.getenv("TELE_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID")

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT_ID: return
    try: requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", data={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=20)
    except: pass

def get_active_pairs():
    try:
        r=requests.get("https://indodax.com/api/pairs", timeout=15).json()
        if isinstance(r, list): return set([str(p).lower() for p in r])
        if isinstance(r, dict): return set([k.lower() for k in r.keys()])
        return None
    except: return None

def smart(last, low, high, vol):
    dl=((last-low)/last*100) if last else 0
    dh=((high-last)/last*100) if last else 0
    sq=dl+dh
    rng=((high-low)/low*100) if low else 0
    if last < 10 or high==low or vol < 3000000: return "DEAD",sq,dl,rng
    # UNIVERSAL - BUAT SEMUA KOIN TRENDING!
    if vol >= 1000000000: return "SUPER",sq,dl,rng  # >1Bn kayak XR
    if dl >= 4 and vol >= 30000000 and rng >= 8: return "TRENDING",sq,dl,rng  # 30jt aja!
    if dl <= 8 and sq < 15 and vol >= 5000000: return "RUNNING",sq,dl,rng
    if dl <= 4 and sq < 8 and vol >= 5000000: return "GOLD",sq,dl,rng
    if dl <= 10 and sq < 15: return "SILVER",sq,dl,rng
    return "NORMAL",sq,dl,rng

active_pairs=get_active_pairs()
tickers=requests.get("https://indodax.com/api/tickers", timeout=20).json()["tickers"]

cands=[]
for pair,data in tickers.items():
    pl=pair.lower()
    if not pl.endswith("_idr"): continue
    if pl in FORCE_BLACKLIST: continue
    if active_pairs and pl not in active_pairs: continue
    try:
        last=float(data["last"]); low=float(data["low"]); high=float(data["high"]); vol=float(data["vol_idr"])
        cat,sq,dl,rng=smart(last,low,high,vol)
        if cat!="NORMAL" and cat!="DEAD":
            cands.append((pair.upper(),dl,sq,vol,cat,last,rng))
    except: continue

cands.sort(key=lambda x: (-x[3] if x[4] in ["SUPER","TRENDING"] else x[2]))

super_t=[c for c in cands if c[4]=="SUPER"][:2]
trend=[c for c in cands if c[4]=="TRENDING"][:6]
run=[c for c in cands if c[4]=="RUNNING"][:4]
gold=[c for c in cands if c[4]=="GOLD"][:4]
silver=[c for c in cands if c[4]=="SILVER"][:3]

now=datetime.now().strftime('%H:%M')
msg=f"V30.1 UNIVERSAL ALL COIN | {now}\nSCAN {len(tickers)} WL {len(active_pairs) if active_pairs else 0}\n\n"

if super_t:
    msg+=f"🚨 SUPER VOL >1Bn ({len(super_t)}):\n"
    for c in super_t: msg+=f"-> {c[0]} {int(c[1])}% low Vol {int(c[3]/1000000000*10)/10}Bn!\n"
    msg+="\n"
if trend:
    msg+=f"🔥 TRENDING ALL COIN ({len(trend)}):\n"
    for c in trend: msg+=f"-> {c[0]} {int(c[1])}% low Vol {int(c[3]/1000000)}jt Range {int(c[6])}% \n"
    msg+="\n"
if run:
    msg+=f"🚀 RUNNING ({len(run)}):\n"
    for c in run: msg+=f"-> {c[0]} {int(c[1])}% low sq{int(c[2])}% {int(c[3]/1000000)}jt\n"
    msg+="\n"
if gold:
    msg+=f"GOLD ({len(gold)}): {', '.join([f'{c[0]} {int(c[1])}% low' for c in gold])}\n\n"
if silver:
    msg+=f"SILVER ({len(silver)}): {', '.join([f'{c[0]}' for c in silver])}\n\n"

if not trend and not super_t:
    msg+=f"TOP VOL HARI INI:\n"
    top=sorted(cands, key=lambda x: -x[3])[:5]
    for c in top: msg+=f"{c[0]} Vol {int(c[3]/1000000)}jt {int(c[1])}% low\n"

print(msg)
send_tele(msg)
