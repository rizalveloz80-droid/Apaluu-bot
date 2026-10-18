import requests, os, json
from datetime import datetime

GOLD_COUNT = 5
SILVER_COUNT = 3
PRE_COUNT = 2
DALEM_COUNT = 5

BLACKLIST = ["usdt_idr","usdc_idr","xaut_idr","paxg_idr","idrt_idr","ouros_idr","btc_idr","eth_idr","xrp_idr","sol_idr","hype_idr","sui_idr"]
CACHE_FILE = "price_cache.json"

TELE_TOKEN = os.getenv("TELE_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
TELE_CHAT_ID = os.getenv("TELE_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID") or os.getenv("CHAT_ID")

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT_ID: 
        print("TELE ENV KOSONG!")
        return
    try:
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        r = requests.post(url, data={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=15)
        print(f"TELE SEND: {r.status_code}")
    except Exception as e:
        print("TELE_ERR "+str(e))

def smart(chg, dl, dh, vol):
    sq = dl + dh
    # 1. SKIP ASLI - cuma -8% ke bawah, jadi PEPE -2.8% ga ke-skip lagi!
    if chg <= -8 and vol >= 10000000: return "SKIP", sq
    if chg <= -20: return "SKIP", sq
    
    # 2. GOLD JACKPOT AMAN - vol 10jt+, sq <14, chg -2.5 s/d 6%
    if 0 <= dl <= 10 and sq < 14 and -2.5 <= chg <= 6 and vol >= 10000000: return "GOLD", sq
    
    # 3. GOLD FAST MOVER - BUAT NANGKEP BR! naik 3-12% tapi masih deket low 8%
    if 0 <= dl <= 8 and sq < 18 and 3 <= chg <= 12 and vol >= 20000000: return "GOLD", sq
    
    # 4. SILVER - lebih longgar dikit
    if 0 <= dl <= 12 and sq < 18 and -2.5 <= chg <= 8 and vol >= 10000000: return "SILVER", sq
    
    # 5. PRE - vol 100jt+ biar UB/SOON 22jt ga masuk
    if 0 <= dl <= 3 and sq < 10 and -2 <= chg <= 3 and vol >= 100000000: return "PRE", sq
    
    # 6. DALEM - buat -2% s/d -30%
    if -30 <= chg <= -2.0 and 0 <= dl <= 5 and sq < 22 and vol >= 15000000: return "DALEM", sq
    return "NORMAL", sq

# --- AUTO RESET CACHE 24 JAM BIAR UPDATE TERUS! ---
if os.path.exists(CACHE_FILE):
    try:
        age_hours = (datetime.now().timestamp() - os.path.getmtime(CACHE_FILE)) / 3600
        if age_hours > 24:
            os.remove(CACHE_FILE)
            print(f"CACHE RESET {age_hours:.1f}h > 24h")
    except: pass

cache = {}
if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE,'r') as f: cache = json.load(f)
    except: pass

try:
    tickers = requests.get("https://indodax.com/api/tickers", timeout=20).json()["tickers"]
except:
    exit()

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
        cat,sq=smart(chg,dl,dh,vol)
        if cat!="NORMAL": candidates.append((pair.upper(),chg,dl,sq,vol,cat))
        cache[pair]=last
    except: continue

with open(CACHE_FILE,'w') as f: json.dump(cache,f)

candidates.sort(key=lambda x: x[4], reverse=True)
top=candidates[:500]
gold=[c for c in top if c[5]=="GOLD"][:GOLD_COUNT]
silver=[c for c in top if c[5]=="SILVER"][:SILVER_COUNT]
pre=[c for c in top if c[5]=="PRE"][:PRE_COUNT]
dalem=[c for c in top if c[5]=="DALEM"][:DALEM_COUNT]
skip=[c for c in top if c[5]=="SKIP"]

now=datetime.now().strftime('%H:%M')
msg=f"V28.5 AMAN UPDATE | {now}\n"
msg+=f"GOLD:{len(gold)} SILVER:{len(silver)} DALEM:{len(dalem)} | SCAN {len(tickers)}\n\n"

if gold:
    msg+=f"GOLD JACKPOT ({len(gold)}):\n"
    for i,c in enumerate(gold,1): 
        tag=" FAST!" if c[1]>=3 else ""
        msg+=f"{i}. {c[0]} {c[1]:+.1f}% {int(c[2])}% low sq{int(c[3])}% {int(c[4]/1000000)}jt{tag}\n"
    msg+="\n"
if silver:
    msg+=f"SILVER ({len(silver)}):\n"
    for i,c in enumerate(silver,len(gold)+1): msg+=f"{i}. {c[0]} {c[1]:+.1f}% {int(c[2])}% low sq{int(c[3])}%\n"
    msg+="\n"
if dalem:
    msg+=f"DALEM BOTTOM ({len(dalem)}):\n"
    for i,c in enumerate(dalem,len(gold+silver+pre)+1): msg+=f"{i}. {c[0]} {c[1]:+.1f}% BOTTOM {int(c[2])}% low\n"
    msg+="\n"
if skip and len(skip)<=5:
    msg+=f"SKIP ({len(skip)}): {', '.join([f'{s[0]} {s[1]:.1f}%' for s in skip[:3]])}\n\n"

print(msg)
send_tele(msg)
