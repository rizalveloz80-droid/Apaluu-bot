import requests, os, json, time
from datetime import datetime

GOLD_COUNT=4; RUNNING_COUNT=2; TRENDING_COUNT=3; SILVER_COUNT=2; DALEM_COUNT=3
CACHE_FILE="price_cache.json"

TELE_TOKEN=os.getenv("TELE_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
TELE_CHAT_ID=os.getenv("TELE_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID")

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT_ID: return
    try: requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", data={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=20)
    except: pass

def get_active_pairs():
    # AMBIL LIST AKTIF RESMI DARI INDODAX - INI KUNCINYA!
    try:
        r=requests.get("https://indodax.com/api/pairs", timeout=10).json()
        # pairs return list of string "btc_idr", "eth_idr" etc
        active=set([p.lower() for p in r])
        return active
    except:
        return None

def smart(chg, dl, dh, vol, last, high, low):
    sq=dl+dh
    if last < 20: return "SKIP_MURAH",sq
    if high == low: return "DEAD",sq
    if vol < 15000000: return "DEAD",sq
    if chg <= -20: return "SKIP",sq
    # TRENDING buat XR +51% GTC +25%
    if chg >= 4 and 5 <= dl <= 85 and vol >= 100000000 and sq < 95:
        return "TRENDING",sq
    if 2.0 <= chg <= 20 and 0 <= dl <= 10 and sq < 20 and vol >= 15000000:
        return "RUNNING",sq
    if -1.0 <= chg <= 3.8 and 0 <= dl <= 4 and sq < 7 and vol >= 20000000:
        return "GOLD",sq
    if -1.0 <= chg <= 4.5 and 2 <= dl <= 8 and sq < 16 and vol >= 15000000:
        return "SILVER",sq
    if -1.5 <= chg <= 2.5 and 0 <= dl <= 2.5 and sq < 8 and 15000000 <= vol <= 150000000:
        return "EARLY",sq
    if -10 <= chg <= -2.0 and 0 <= dl <= 4 and sq < 20 and vol >= 15000000:
        return "DALEM",sq
    return "NORMAL",sq

# 1. AMBIL WHITELIST AKTIF
active_pairs = get_active_pairs()
if active_pairs:
    print(f"ACTIVE PAIRS: {len(active_pairs)} from Indodax")
else:
    print("PAIRS GAGAL, PAKAI SEMUA")

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
    # FILTER PALING AMAN: CUMA YANG ADA DI active_pairs RESMI INDODAX!
    if active_pairs and pl not in active_pairs:
        continue  # GID, COL, OKUSD, LYFEL, DFG, INDR, NEORPNEW AUTO KE-SKIP DISINI!
    try:
        last=float(data["last"]); low=float(data["low"]); high=float(data["high"]); vol=float(data["vol_idr"])
        if last==0: continue
        dl=((last-low)/last)*100; dh=((high-last)/last)*100
        prev=cache.get(pair,{}).get("price",last) if isinstance(cache.get(pair),dict) else cache.get(pair,last)
        chg=((last-prev)/prev*100) if prev else 0
        cat,sq=smart(chg,dl,dh,vol,last,high,low)
        if cat not in ["NORMAL","SKIP_MURAH","SKIP","DEAD"]:
            cands.append((pair.upper(),chg,dl,sq,vol,cat,last))
        cache[pair]={"price":last,"ts":now_ts}
    except: continue

with open(CACHE_FILE,'w') as f: json.dump(cache,f)

cands.sort(key=lambda x: (0 if x[5]=="TRENDING" else 1 if x[5]=="RUNNING" else 2 if x[5]=="GOLD" else 3, -x[4] if x[5]=="TRENDING" else x[3]))

trending=[c for c in cands if c[5]=="TRENDING"][:TRENDING_COUNT]
running=[c for c in cands if c[5]=="RUNNING"][:RUNNING_COUNT]
gold=[c for c in cands if c[5]=="GOLD"][:GOLD_COUNT]
silver=[c for c in cands if c[5]=="SILVER"][:SILVER_COUNT]
dalem=[c for c in cands if c[5]=="DALEM"][:DALEM_COUNT]

now=datetime.now().strftime('%H:%M')
msg=f"V29.1 WHITELIST INDODAX | {now}\n"
msg+=f"SCAN {len(tickers)} ACTIVE {len(active_pairs) if active_pairs else 0} | TREND:{len(trending)} RUN:{len(running)} GOLD:{len(gold)}\n\n"

if trending:
    msg+=f"🔥 TRENDING ({len(trending)}):\n"
    for c in trending: msg+=f"-> {c[0]} {c[1]:+.1f}% {int(c[2])}% low {int(c[4]/1000000)}jt!\n"
    msg+="\n"
if running:
    msg+=f"🚀 RUNNING ({len(running)}):\n"
    for c in running: msg+=f"-> {c[0]} {c[1]:+.1f}% {int(c[2])}% low sq{int(c[3])}% GAS!\n"
    msg+="\n"
if gold:
    msg+=f"GOLD LIVE ({len(gold)}):\n"
    for c in gold: msg+=f"{c[0]} {c[1]:+.1f}% {int(c[2])}% low sq{int(c[3])}%\n"
    msg+="\n"
if silver: msg+=f"SILVER ({len(silver)}): {', '.join([f'{s[0]} {s[1]:+.1f}%' for s in silver])}\n\n"
if dalem: msg+=f"DALEM ({len(dalem)}): {', '.join([f'{s[0]} {s[1]:+.1f}%' for s in dalem])}\n\n"

print(msg)
send_tele(msg)
