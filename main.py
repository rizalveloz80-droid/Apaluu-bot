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
    if last < 1 or vol < 500000: return "DEAD",sq,dl
    # GA ADA FILTER high==low LAGI! BIAR GA CANDS 0!
    if vol >= 2000000000: return "SUPER",sq,dl
    if dl >= 10: return "TRENDING",sq,dl
    if dl >= 3: return "RUNNING",sq,dl
    if dl <= 3: return "GOLD",sq,dl
    return "SILVER",sq,dl

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
        cat,sq,dl=smart(last,low,high,vol)
        if cat!="DEAD":
            cands.append((pair.upper(),dl,sq,vol,cat,last))
    except: continue

cands.sort(key=lambda x: -x[3]) # sort by VOL terbesar

super_t=[c for c in cands if c[4]=="SUPER"][:3]
trend=[c for c in cands if c[4]=="TRENDING"][:5]
run=[c for c in cands if c[4]=="RUNNING"][:4]
gold=[c for c in cands if c[4]=="GOLD"][:4]

now=datetime.now().strftime('%H:%M')
msg=f"V31 FINAL UNIVERSAL | {now}\nSCAN {len(tickers)} WL {len(active_pairs) if active_pairs else 0} CANDS {len(cands)}\n\n"

if super_t:
    msg+=f"🚨 SUPER >2Bn ({len(super_t)}):\n"
    for c in super_t: msg+=f"-> {c[0]} {int(c[1])}% low Vol {int(c[3]/1000000000*10)/10}Bn!\n"
    msg+="\n"
if trend:
    msg+=f"🔥 TRENDING dl>=10% ({len(trend)}):\n"
    for c in trend: msg+=f"-> {c[0]} {int(c[1])}% low Vol {int(c[3]/1000000)}jt\n"
    msg+="\n"
if run:
    msg+=f"🚀 RUNNING dl>=3% ({len(run)}):\n"
    for c in run: msg+=f"-> {c[0]} {int(c[1])}% low {int(c[3]/1000000)}jt\n"
    msg+="\n"
if gold:
    msg+=f"GOLD deket low ({len(gold)}): {', '.join([f'{c[0]} {int(c[1])}% ' for c in gold])}\n\n"

if len(cands)==0:
    msg+=f"MARKET MATI TOTAL!\n"

print(msg)
send_tele(msg)
