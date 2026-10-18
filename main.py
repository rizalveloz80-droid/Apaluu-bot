import requests, os, json, time
from datetime import datetime

GOLD_COUNT=5; RUNNING_COUNT=3; TRENDING_COUNT=3; SILVER_COUNT=3; DALEM_COUNT=3
CACHE_FILE="price_cache.json"

FORCE_BLACKLIST = set([
    "usdt_idr","usdc_idr","idrt_idr","usde_idr","xaut_idr","paxg_idr","ouros_idr",
    "btc_idr","eth_idr","xrp_idr","sol_idr","bnb_idr","hype_idr","sui_idr",
    "gid_idr","col_idr","okusd_idr","lyfel_idr","dfg_idr","inr_idr","eur_idr",
    "indr_idr","neorpnew_idr","soon_idr","avas_idr"
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

def smart(chg, dl, dh, vol, last, high, low, is_first_run):
    sq=dl+dh
    if last < 20: return "SKIP",sq
    if high == low: return "DEAD",sq
    if vol < 15000000: return "DEAD",sq
    if chg <= -25: return "SKIP",sq
    if is_first_run:
        if dl >= 10 and vol >= 80000000: return "TRENDING",sq
        if dl <= 5 and sq < 8: return "GOLD",sq
    if chg >= 3.5 and 5 <= dl <= 85 and vol >= 80000000: return "TRENDING",sq
    if 1.5 <= chg <= 20 and 0 <= dl <= 10 and sq < 20 and vol >= 15000000: return "RUNNING",sq
    if -2 <= chg <= 4 and 0 <= dl <= 5 and sq < 8 and vol >= 15000000: return "GOLD",sq
    if -2 <= chg <= 5 and 2 <= dl <= 10 and sq < 18 and vol >= 15000000: return "SILVER",sq
    if -12 <= chg <= -1.5 and 0 <= dl <= 5 and sq < 22 and vol >= 15000000: return "DALEM",sq
    return "NORMAL",sq

active_pairs = get_active_pairs()
now_ts = datetime.now().timestamp()

# CACHE AUTO RESET - GA USAH HAPUS MANUAL!
cache={}; is_first_run=True
if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE,'r') as f: cache=json.load(f)
        # cek umur cache, kalo >1 jam reset biar ga kosong kayak SS lu
        try:
            oldest = min([v.get("ts",0) for v in cache.values() if isinstance(v,dict)], default=now_ts)
            if now_ts - oldest > 3600: 
                print("RESET CACHE >1 JAM")
                cache={}
            else:
                if len(cache) > 20: is_first_run=False
        except: is_first_run=False
    except: cache={}

tickers=None
for _ in range(3):
    try:
        tickers=requests.get("https://indodax.com/api/tickers", timeout=20).json()["tickers"]
        break
    except: time.sleep(2)
if not tickers: exit()

cands=[]
for pair,data in tickers.items():
    pl=pair.lower()
    if not pl.endswith("_idr"): continue
    if pl in FORCE_BLACKLIST: continue
    if active_pairs and pl not in active_pairs: continue
    try:
        last=float(data["last"]); low=float(data["low"]); high=float(data["high"]); vol=float(data["vol_idr"])
        if last==0: continue
        dl=((last-low)/last)*100; dh=((high-last)/last)*100
        prev_obj=cache.get(pair); prev=prev_obj.get("price",last) if isinstance(prev_obj,dict) else prev_obj
        if prev is None: prev=last
        chg=((last-prev)/prev*100) if prev else 0
        cat,sq=smart(chg,dl,dh,vol,last,high,low,is_first_run)
        if cat not in ["NORMAL","SKIP","DEAD"]:
            cands.append((pair.upper(),chg,dl,sq,vol,cat,last))
        cache[pair]={"price":last,"ts":now_ts}
    except: continue

with open(CACHE_FILE,'w') as f: json.dump(cache,f)

cands.sort(key=lambda x: (0 if x[5]=="TRENDING" else 1 if x[5]=="RUNNING" else 2, -x[4] if x[5]=="TRENDING" else x[3]))

trending=[c for c in cands if c[5]=="TRENDING"][:TRENDING_COUNT]
running=[c for c in cands if c[5]=="RUNNING"][:RUNNING_COUNT]
gold=[c for c in cands if c[5]=="GOLD"][:GOLD_COUNT]
silver=[c for c in cands if c[5]=="SILVER"][:SILVER_COUNT]
dalem=[c for c in cands if c[5]=="DALEM"][:DALEM_COUNT]

now=datetime.now().strftime('%H:%M')
msg=f"V29.4 AUTO RESET | {now}\nSCAN {len(tickers)} WL {len(active_pairs) if active_pairs else 0}\n\n"
if trending:
    msg+=f"🔥 TRENDING ({len(trending)}):\n"
    for c in trending: msg+=f"-> {c[0]} {c[1]:+.1f}% {int(c[4]/1000000)}jt!\n"
    msg+="\n"
if running:
    msg+=f"🚀 RUNNING ({len(running)}):\n"
    for c in running: msg+=f"-> {c[0]} {c[1]:+.1f}% sq{int(c[3])}% GAS!\n"
    msg+="\n"
if gold:
    msg+=f"GOLD LIVE ({len(gold)}):\n"
    for c in gold: msg+=f"{c[0]} {c[1]:+.1f}% {int(c[2])}% low\n"
    msg+="\n"
if silver: msg+=f"SILVER: {', '.join([f'{s[0]}' for s in silver])}\n\n"
if dalem: msg+=f"DALEM: {', '.join([f'{s[0]}' for s in dalem])}\n\n"
if not trending and not running and not gold:
    msg+=f"SCANNING... TUNGGU 15 MENIT LAGI\n"

print(msg)
send_tele(msg)
