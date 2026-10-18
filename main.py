import requests, os, json, time
from datetime import datetime

GOLD_COUNT = 5
SILVER_COUNT = 3
EARLY_COUNT = 2
DALEM_COUNT = 5
RUNNING_COUNT = 2

BLACKLIST = ["usdt_idr","usdc_idr","xaut_idr","paxg_idr","idrt_idr","ouros_idr","btc_idr","eth_idr","xrp_idr","sol_idr","hype_idr","sui_idr"]
CACHE_FILE = "price_cache.json"

TELE_TOKEN = os.getenv("TELE_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
TELE_CHAT_ID = os.getenv("TELE_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID")

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT_ID: return
    try:
        requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", data={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=20)
    except: pass

def smart(chg, dl, dh, vol, last_price):
    sq = dl + dh
    if last_price < 20: return "SKIP_MURAH", sq
    if chg <= -15: return "SKIP", sq

    # RUNNING - INI BIAR GA KETINGGALAN! naik 3-20% + vol gede + masih deket low!
    if 3 <= chg <= 20 and 0 <= dl <= 10 and vol >= 20000000 and sq < 20:
        return "RUNNING", sq
    
    if 0 <= dl <= 2.5 and sq < 8 and -1.5 <= chg <= 2.5 and 15000000 <= vol <= 150000000:
        return "EARLY", sq
    if 0 <= dl <= 5 and sq < 10 and -2.5 <= chg <= 6 and vol >= 15000000:
        return "GOLD", sq
    if 0 <= dl <= 10 and sq < 16 and -2.5 <= chg <= 8 and vol >= 15000000:
        return "SILVER", sq
    if -30 <= chg <= -2.0 and 0 <= dl <= 5 and sq < 22 and vol >= 15000000:
        return "DALEM", sq
    return "NORMAL", sq

# --- CACHE ANTI KETINGGALAN: SIMPAN JAM + HARGA ---
cache = {}
if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE,'r') as f: cache = json.load(f)
    except: cache = {}

# --- AMBIL HARGA TERBARU LIVE DARI INDODAX - RETRY 3x BIAR GA MISS ---
tickers = None
for _ in range(3):
    try:
        r = requests.get("https://indodax.com/api/tickers", timeout=20)
        tickers = r.json()["tickers"]
        break
    except: time.sleep(2)

if not tickers: exit()

candidates=[]
now_ts = datetime.now().timestamp()

for pair,data in tickers.items():
    pl=pair.lower()
    if not pl.endswith("_idr"): continue
    if pl in BLACKLIST: continue
    try:
        last=float(data["last"]); low=float(data["low"]); high=float(data["high"]); vol=float(data["vol_idr"])
        if last==0: continue
        dl=((last-low)/last)*100; dh=((high-last)/last)*100
        
        # CHG SELALU UPDATE: bandingin sama harga 1-2 jam lalu di cache, kalo ga ada, anggap 0
        prev_data = cache.get(pair, {})
        prev_price = prev_data.get("price", last) if isinstance(prev_data, dict) else prev_data
        # Simpan cache baru dengan timestamp biar selalu fresh
        chg = ((last - prev_price)/prev_price*100) if prev_price else 0
        
        cat,sq=smart(chg,dl,dh,vol,last)
        if cat not in ["NORMAL","SKIP_MURAH","SKIP"]:
            candidates.append((pair.upper(),chg,dl,sq,vol,cat,last))
        
        # UPDATE CACHE DENGAN HARGA TERBARU LIVE!
        cache[pair] = {"price": last, "ts": now_ts}
    except: continue

# SIMPAN CACHE TERBARU
with open(CACHE_FILE,'w') as f: json.dump(cache,f)

# SORT BY: RUNNING dulu, baru sq terkecil!
candidates.sort(key=lambda x: (0 if x[5]=="RUNNING" else 1, x[3], x[2]))

gold=[c for c in candidates if c[5]=="GOLD"][:GOLD_COUNT]
early=[c for c in candidates if c[5]=="EARLY"][:EARLY_COUNT]
running=[c for c in candidates if c[5]=="RUNNING"][:RUNNING_COUNT]
silver=[c for c in candidates if c[5]=="SILVER"][:SILVER_COUNT]
dalem=[c for c in candidates if c[5]=="DALEM"][:DALEM_COUNT]

now=datetime.now().strftime('%H:%M')
msg=f"V28.7 LIVE UPDATE | {now} | API AMAN\n"
if running: msg+=f"🚀 RUNNING:{len(running)} "
msg+=f"GOLD:{len(gold)} EARLY:{len(early)} | SCAN {len(tickers)}\n\n"

if running:
    msg+=f"🚀 RUNNING ANTI KETINGGALAN ({len(running)}):\n"
    for c in running:
        msg+=f"-> {c[0]} {c[1]:+.1f}% {int(c[2])}% low sq{int(c[3])}% {int(c[4]/1000000)}jt GAS!\n"
    msg+="\n"
if early:
    msg+=f"EARLY V25 ({len(early)}):\n"
    for i,c in enumerate(early,1): msg+=f"{i}. {c[0]} {c[1]:+.1f}% {int(c[2])}% low sq{int(c[3])}%\n"
    msg+="\n"
if gold:
    msg+=f"GOLD ({len(gold)}):\n"
    for i,c in enumerate(gold,1): msg+=f"{i}. {c[0]} {c[1]:+.1f}% {int(c[2])}% low sq{int(c[3])}% {int(c[4]/1000000)}jt\n"
    msg+="\n"
if silver:
    msg+=f"SILVER ({len(silver)}):\n"
    for i,c in enumerate(silver,1): msg+=f"{i}. {c[0]} {c[1]:+.1f}% {int(c[2])}% low\n"
    msg+="\n"
if dalem:
    msg+=f"DALEM ({len(dalem)}):\n"
    for i,c in enumerate(dalem,1): msg+=f"{i}. {c[0]} {c[1]:+.1f}% BOTTOM\n"
    msg+="\n"

print(msg)
send_tele(msg)
