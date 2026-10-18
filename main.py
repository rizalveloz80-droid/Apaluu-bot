import requests, os, json, time
from datetime import datetime

GOLD_COUNT=5; SILVER_COUNT=3; EARLY_COUNT=2; DALEM_COUNT=5; RUNNING_COUNT=2
BLACKLIST=["usdt_idr","usdc_idr","xaut_idr","paxg_idr","idrt_idr","ouros_idr","inr_idr","eur_idr","btc_idr","eth_idr","xrp_idr","sol_idr","hype_idr","sui_idr","bnb_idr","indr_idr","neorpnew_idr"]
CACHE_FILE="price_cache.json"

TELE_TOKEN=os.getenv("TELE_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
TELE_CHAT_ID=os.getenv("TELE_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID")

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT_ID: return
    try: requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", data={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=20)
    except: pass

def smart(chg, dl, dh, vol, last):
    sq=dl+dh
    if last < 20: return "SKIP_MURAH",sq
    if chg <= -15: return "SKIP",sq

    # RUMUS LIVE KAYAK HBAR + TSLAX TADI!
    # 1. RUNNING - lagi jalan 3-20% + masih 4-10% low
    if 2.5 <= chg <= 20 and 0 <= dl <= 10 and sq < 20 and vol >= 15000000:
        return "RUNNING",sq
    # 2. GOLD LIVE - SAMA KAYAK RUNNING TAPI BELUM JALAN! 0-4% low sq 0-7% chg -1 s/d 3.8%
    if -1.0 <= chg <= 3.8 and 0 <= dl <= 4 and sq < 7 and vol >= 20000000:
        return "GOLD",sq
    # 3. SILVER LIVE - udah agak naik 4-8% low tapi masih sq kecil
    if -1.0 <= chg <= 4.5 and 2 <= dl <= 8 and sq < 16 and vol >= 15000000:
        return "SILVER",sq
    # 4. EARLY - vol kecil 15-150jt 0-2% low
    if -1.5 <= chg <= 2.5 and 0 <= dl <= 2.5 and sq < 8 and 15000000 <= vol <= 150000000:
        return "EARLY",sq
    # 5. DALEM LIVE - harga terkini lagi di bottom
    if -8 <= chg <= -2.0 and 0 <= dl <= 4 and sq < 20 and vol >= 15000000:
        return "DALEM",sq
    return "NORMAL",sq

cache={}
if os.path.exists(CACHE_FILE):
    try: 
        with open(CACHE_FILE,'r') as f: cache=json.load(f)
    except: pass

tickers=None
for _ in range(3):
    try:
        tickers=requests.get("https://indodax.com/api/tickers", timeout=20).json()["tickers"]
        break
    except: time.sleep(2)
if not tickers: exit()

cands=[]; now_ts=datetime.now().timestamp()
for pair,data in tickers.items():
    pl=pair.lower()
    if not pl.endswith("_idr"): continue
    if pl in BLACKLIST: continue
    try:
        last=float(data["last"]); low=float(data["low"]); high=float(data["high"]); vol=float(data["vol_idr"])
        if last==0: continue
        dl=((last-low)/last)*100; dh=((high-last)/last)*100
        prev=cache.get(pair,{}).get("price",last) if isinstance(cache.get(pair),dict) else cache.get(pair,last)
        chg=((last-prev)/prev*100) if prev else 0
        cat,sq=smart(chg,dl,dh,vol,last)
        if cat not in ["NORMAL","SKIP_MURAH","SKIP"]:
            cands.append((pair.upper(),chg,dl,sq,vol,cat,last))
        cache[pair]={"price":last,"ts":now_ts}
    except: continue

with open(CACHE_FILE,'w') as f: json.dump(cache,f)

# SORT: RUNNING dulu, baru sq terkecil biar selalu update!
cands.sort(key=lambda x: (0 if x[5]=="RUNNING" else 1 if x[5]=="GOLD" else 2, x[3], x[2]))

gold=[c for c in cands if c[5]=="GOLD"][:GOLD_COUNT]
early=[c for c in cands if c[5]=="EARLY"][:EARLY_COUNT]
running=[c for c in cands if c[5]=="RUNNING"][:RUNNING_COUNT]
silver=[c for c in cands if c[5]=="SILVER"][:SILVER_COUNT]
dalem=[c for c in cands if c[5]=="DALEM"][:DALEM_COUNT]

now=datetime.now().strftime('%H:%M')
msg=f"V28.8 LIVE HBAR RUMUS | {now}\n"
if running: msg+=f"🚀 RUNNING:{len(running)} "
msg+=f"GOLD:{len(gold)} SILVER:{len(silver)} DALEM:{len(dalem)} SCAN {len(tickers)}\n\n"

if running:
    msg+=f"🚀 RUNNING LIVE (2):\n"
    for c in running: msg+=f"-> {c[0]} {c[1]:+.1f}% {int(c[2])}% low sq{int(c[3])}% {int(c[4]/1000000)}jt GAS!\n"
    msg+="\n"
if gold:
    msg+=f"GOLD LIVE (5):\n"
    for c in gold: msg+=f"{c[0]} {c[1]:+.1f}% {int(c[2])}% low sq{int(c[3])}% {int(c[4]/1000000)}jt\n"
    msg+="\n"
if silver:
    msg+=f"SILVER LIVE (3):\n"
    for c in silver: msg+=f"{c[0]} {c[1]:+.1f}% {int(c[2])}% low sq{int(c[3])}% LIVE\n"
    msg+="\n"
if dalem:
    msg+=f"DALEM LIVE (5):\n"
    for c in dalem: msg+=f"{c[0]} {c[1]:+.1f}% {int(c[2])}% low BOTTOM\n"
    msg+="\n"
if early:
    msg+=f"EARLY ({len(early)}):\n"
    for c in early: msg+=f"{c[0]} {c[1]:+.1f}% {int(c[2])}% low\n"
    msg+="\n"

print(msg)
send_tele(msg)
