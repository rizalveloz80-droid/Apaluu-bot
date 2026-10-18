import requests, os, json
from datetime import datetime

GOLD_COUNT = 5
SILVER_COUNT = 3
EARLY_COUNT = 2
DALEM_COUNT = 5

BLACKLIST = ["usdt_idr","usdc_idr","xaut_idr","paxg_idr","idrt_idr","ouros_idr","btc_idr","eth_idr","xrp_idr","sol_idr","hype_idr","sui_idr"]
CACHE_FILE = "price_cache.json"

TELE_TOKEN = os.getenv("TELE_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
TELE_CHAT_ID = os.getenv("TELE_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID") or os.getenv("CHAT_ID")

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT_ID: return
    try:
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=15)
    except: pass

def smart(chg, dl, dh, vol, last_price):
    sq = dl + dh
    # FILTER HARGA 12 PERAK - JANGAN KENA!
    if last_price < 20:
        return "SKIP_MURAH", sq
    # SKIP ASLI
    if chg <= -8 and vol >= 10000000: return "SKIP", sq
    if chg <= -20: return "SKIP", sq
    # EARLY V25 - YANG LU KANGENIN! Vol 15-150jt 0-2.5% low sq<8
    if 0 <= dl <= 2.5 and sq < 8 and -1.5 <= chg <= 2.5 and 15000000 <= vol <= 150000000:
        return "EARLY", sq
    # GOLD MURNI V25.3 - vol cuma 15jt+ biar ga itu-itu aja
    if 0 <= dl <= 5 and sq < 10 and -2.5 <= chg <= 6 and vol >= 15000000:
        return "GOLD", sq
    # GOLD FAST - BUAT BR!
    if 0 <= dl <= 6 and sq < 15 and 3 <= chg <= 12 and vol >= 15000000:
        return "GOLD", sq
    # SILVER
    if 0 <= dl <= 10 and sq < 16 and -2.5 <= chg <= 8 and vol >= 15000000:
        return "SILVER", sq
    # DALEM
    if -30 <= chg <= -2.0 and 0 <= dl <= 5 and sq < 22 and vol >= 15000000:
        return "DALEM", sq
    return "NORMAL", sq

# RESET CACHE 24 JAM BIAR UPDATE TERUS!
if os.path.exists(CACHE_FILE):
    try:
        age = (datetime.now().timestamp() - os.path.getmtime(CACHE_FILE))/3600
        if age > 24: os.remove(CACHE_FILE)
    except: pass

cache = {}
if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE,'r') as f: cache=json.load(f)
    except: pass

try:
    tickers = requests.get("https://indodax.com/api/tickers", timeout=20).json()["tickers"]
except: exit()

candidates=[]
for pair,data in tickers.items():
    pl=pair.lower()
    if not pl.endswith("_idr"): continue
    if pl in BLACKLIST: continue
    try:
        last=float(data["last"]); low=float(data["low"]); high=float(data["high"]); vol=float(data["vol_idr"])
        if last==0: continue
        dl=((last-low)/last)*100; dh=((high-last)/last)*100
        prev=cache.get(pair,last); chg=((last-prev)/prev*100) if prev else 0
        cat,sq=smart(chg,dl,dh,vol,last)
        if cat not in ["NORMAL","SKIP_MURAH","SKIP"]:
            candidates.append((pair.upper(),chg,dl,sq,vol,cat,last))
        cache[pair]=last
    except: continue

with open(CACHE_FILE,'w') as f: json.dump(cache,f)

# SORT BY SQ TERKECIL BIAR GA ITU-ITU AJA! BUKAN BY VOL!
candidates.sort(key=lambda x: (x[3], x[2]))

top=candidates[:500]
gold=[c for c in top if c[5]=="GOLD"][:GOLD_COUNT]
early=[c for c in top if c[5]=="EARLY"][:EARLY_COUNT]
silver=[c for c in top if c[5]=="SILVER"][:SILVER_COUNT]
dalem=[c for c in top if c[5]=="DALEM"][:DALEM_COUNT]

now=datetime.now().strftime('%H:%M')
msg=f"V28.6 V25 REMAKE + EARLY | {now}\n"
msg+=f"GOLD:{len(gold)} EARLY:{len(early)} SILVER:{len(silver)} DALEM:{len(dalem)} | SCAN {len(tickers)}\n\n"

if early:
    msg+=f"EARLY V25 ({len(early)}):\n"
    for i,c in enumerate(early,1):
        msg+=f"{i}. {c[0]} {c[1]:+.1f}% {int(c[2])}% low sq{int(c[3])}% {int(c[4]/1000000)}jt\n"
    msg+="\n"
if gold:
    msg+=f"GOLD JACKPOT ({len(gold)}):\n"
    for i,c in enumerate(gold,1):
        tag=" FAST!" if c[1]>=3 else ""
        msg+=f"{i}. {c[0]} {c[1]:+.1f}% {int(c[2])}% low sq{int(c[3])}% {int(c[4]/1000000)}jt{tag}\n"
    msg+="\n"
if silver:
    msg+=f"SILVER ({len(silver)}):\n"
    for i,c in enumerate(silver,len(gold+early)+1):
        msg+=f"{i}. {c[0]} {c[1]:+.1f}% {int(c[2])}% low sq{int(c[3])}% {int(c[6])} IDR\n"
    msg+="\n"
if dalem:
    msg+=f"DALEM BOTTOM ({len(dalem)}):\n"
    for i,c in enumerate(dalem,len(gold+early+silver)+1):
        msg+=f"{i}. {c[0]} {c[1]:+.1f}% BOTTOM {int(c[2])}% low\n"
    msg+="\n"

msg+=f"Total {len(gold+early+silver+dalem)} Valid | Harga <20 auto SKIP"
print(msg)
send_tele(msg)
