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
    if last == 0: return "DEAD",0,0
    dl=((last-low)/last*100) if last else 0
    dh=((high-last)/last*100) if last else 0
    sq=dl+dh
    if last < 5: return "DEAD",sq,dl
    if high == low: return "DEAD",sq,dl
    if vol < 1000000: return "DEAD",sq,dl # 1jt aja!
    
    # ULTRA LOOSE BUAT SEMUA KOIN!
    if vol >= 1000000000: return "SUPER",sq,dl
    if dl >= 2 and vol >= 10000000: return "TRENDING",sq,dl # dl 2% aja + vol 10jt = trending!
    if dl <= 10 and vol >= 3000000: return "RUNNING",sq,dl
    if dl <= 6 and vol >= 3000000: return "GOLD",sq,dl
    if vol >= 3000000: return "SILVER",sq,dl # sisa vol gede masuk silver!
    return "NORMAL",sq,dl

active_pairs=get_active_pairs()
try:
    tickers=requests.get("https://indodax.com/api/tickers", timeout=20).json()["tickers"]
except:
    exit()

cands=[]
for pair,data in tickers.items():
    pl=pair.lower()
    if not pl.endswith("_idr"): continue
    if pl in FORCE_BLACKLIST: continue
    if active_pairs and pl not in active_pairs: continue
    try:
        last=float(data["last"]); low=float(data["low"]); high=float(data["high"]); vol=float(data["vol_idr"])
        cat,sq,dl=smart(last,low,high,vol)
        if cat not in ["NORMAL","DEAD"]:
            cands.append((pair.upper(),dl,sq,vol,cat,last))
    except: continue

# DEBUG - BIAR KETAUAN KENAPA KOSONG!
print(f"DEBUG: TOTAL CANDS {len(cands)} dari {len(tickers)}")

cands.sort(key=lambda x: (-x[3] if x[4] in ["SUPER","TRENDING"] else x[2]))

super_t=[c for c in cands if c[4]=="SUPER"][:3]
trend=[c for c in cands if c[4]=="TRENDING"][:8]
run=[c for c in cands if c[4]=="RUNNING"][:5]
gold=[c for c in cands if c[4]=="GOLD"][:5]
silver=[c for c in cands if c[4]=="SILVER"][:5]

# ANTI KOSONG 100% - KALO MASIH KOSONG, AMBIL TOP 10 VOL!
if len(cands) == 0:
    print("CANDS KOSONG! AMBIL TOP VOL PAKSA!")
    all_pairs=[]
    for pair,data in tickers.items():
        if pair.lower() in FORCE_BLACKLIST: continue
        if not pair.lower().endswith("_idr"): continue
        try:
            last=float(data["last"]); vol=float(data["vol_idr"]); low=float(data["low"])
            dl=((last-low)/last*100) if last else 0
            all_pairs.append((pair.upper(),dl,0,vol,"GOLD",last))
        except: continue
    all_pairs.sort(key=lambda x: -x[3])
    cands=all_pairs[:10]
    gold=cands[:5]
    trend=cands[5:8]

now=datetime.now().strftime('%H:%M')
msg=f"V30.2 ULTRA LOOSE | {now}\nSCAN {len(tickers)} WL {len(active_pairs) if active_pairs else 0} CANDS {len(cands)}\n\n"

if super_t:
    msg+=f"🚨 SUPER >1Bn ({len(super_t)}):\n"
    for c in super_t: msg+=f"-> {c[0]} {int(c[1])}% low {int(c[3]/1000000000*10)/10}Bn\n"
    msg+="\n"
if trend:
    msg+=f"🔥 TRENDING ALL ({len(trend)}):\n"
    for c in trend: msg+=f"-> {c[0]} {int(c[1])}% low Vol {int(c[3]/1000000)}jt\n"
    msg+="\n"
if run:
    msg+=f"🚀 RUNNING ({len(run)}):\n"
    for c in run: msg+=f"-> {c[0]} {int(c[1])}% low sq{int(c[2])}%\n"
    msg+="\n"
if gold:
    msg+=f"GOLD ({len(gold)}):\n"
    for c in gold: msg+=f"-> {c[0]} {int(c[1])}% low Vol {int(c[3]/1000000)}jt\n"
    msg+="\n"
if silver:
    msg+=f"SILVER ({len(silver)}): {', '.join([f'{c[0]}' for c in silver])}\n\n"

print(msg)
send_tele(msg)
