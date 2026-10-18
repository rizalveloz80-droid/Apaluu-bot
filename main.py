import requests, os, json
from datetime import datetime

GOLD_COUNT = 5
SILVER_COUNT = 3
PRE_COUNT = 2
DALEM_COUNT = 5

# DCA LU SEMUA KITA BLACKLIST BIAR GA MASUK GOLD LAGI!
BLACKLIST = [
    "usdt_idr","usdc_idr","xaut_idr","paxg_idr","idrt_idr","ouros_idr",
    "btc_idr","eth_idr","xrp_idr","sol_idr","hype_idr","sui_idr"
]
CACHE_FILE = "price_cache.json"

TELE_TOKEN = os.getenv("TELE_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
TELE_CHAT_ID = os.getenv("TELE_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID") or os.getenv("CHAT_ID")

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=15)
    except Exception as e:
        print("TELE_ERR "+str(e))

def smart_candle_v25_v28(chg, dl, dh, vol):
    """Gabungan V25.3/V25.5 yang valid + Filter OGN V28.3"""
    sq = dl + dh

    # FILTER OGN - JANGAN ANTRI PAS MASIH TERJUN!
    if chg <= -1.5 and dl <= 2.0 and vol >= 30000000:
        return "JANGAN_ANTRI", sq

    # GOLD V25.3 - JACKPOT MURNI ALTCOIN! (XRP/SOL/HYPE udah ga masuk)
    # 0% low + sq <12 + vol 15jt+ = ini rumus v25.3 lu yang valid!
    if 0 <= dl <= 8 and sq < 12 and -1.5 <= chg <= 4 and vol >= 15000000:
        return "GOLD", sq

    # SILVER V25.5
    if 0 <= dl <= 10 and sq < 16 and -1.5 <= chg <= 6 and vol >= 15000000:
        return "SILVER", sq

    # PRE_TRENDING - DIPERKETAT KAYA V28.0! Vol gede biar ga kaya UB/SOON 22jt!
    if 0 <= dl <= 2.5 and sq < 9 and -2 <= chg <= 2.5 and vol >= 100000000:
        return "PRE", sq

    # DALEM BOTTOM PAS - V25.5 ORIGINAL!
    if -15 <= chg <= -2.2 and 0 <= dl <= 1.5 and sq < 15 and vol >= 20000000:
        return "DALEM", sq
    if -25 <= chg <= -2.2 and 0 <= dl <= 2.5 and sq < 20 and vol >= 20000000:
        return "DALEM", sq

    return "NORMAL", sq

# --- SCAN ---
cache = {}
if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE,'r') as f:
            cache = json.load(f)
    except:
        pass

try:
    tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json()["tickers"]
except:
    exit()

candidates = []
for pair, data in tickers.items():
    pl = pair.lower()
    if not pl.endswith("_idr"): continue
    if pl in BLACKLIST: continue
    try:
        last = float(data["last"]); low = float(data["low"]); high = float(data["high"]); vol = float(data["vol_idr"])
        if last == 0: continue
        dl = ((last - low)/last)*100; dh = ((high - last)/last)*100
        prev = cache.get(pair, last)
        chg = ((last - prev)/prev*100) if prev else 0
        cat, sq = smart_candle_v25_v28(chg, dl, dh, vol)
        if cat != "NORMAL":
            candidates.append((pair.upper(), chg, dl, sq, vol, cat))
        cache[pair] = last
    except:
        continue

with open(CACHE_FILE,'w') as f:
    json.dump(cache,f)

candidates.sort(key=lambda x: x[4], reverse=True)
top = candidates[:500]
gold = [c for c in top if c[5]=="GOLD"][:GOLD_COUNT]
silver = [c for c in top if c[5]=="SILVER"][:SILVER_COUNT]
pre = [c for c in top if c[5]=="PRE"][:PRE_COUNT]
dalem = [c for c in top if c[5]=="DALEM"][:DALEM_COUNT]
jangan = [c for c in top if c[5]=="JANGAN_ANTRI"]

now = datetime.now().strftime('%H:%M')
msg = f"V28.4 ALTCOIN MURNI | {now} | V25.3+V25.5+ANTI OGN\n\n"
if gold:
    msg+=f"GOLD JACKPOT ({len(gold)}):\n"
    for i,c in enumerate(gold,1):
        msg+=f"{i}. {c[0]} {c[1]:.1f}% | {int(c[2])}% low | sq {int(c[3])}% | {int(c[4]/1000000)}jt\n"
    msg+="\n"
if silver:
    msg+=f"SILVER ({len(silver)}):\n"
    for i,c in enumerate(silver,len(gold)+1):
        msg+=f"{i}. {c[0]} {c[1]:.1f}% | {int(c[2])}% low | sq {int(c[3])}% | {int(c[4]/1000000)}jt\n"
    msg+="\n"
if pre:
    msg+=f"PRE_TRENDING ({len(pre)}):\n"
    for i,c in enumerate(pre,len(gold+silver)+1):
        msg+=f"{i}. {c[0]} {c[1]:.1f}% | {int(c[2])}% low | sq {int(c[3])}% | {int(c[4]/1000000)}jt\n"
    msg+="\n"
if dalem:
    msg+=f"DALEM BOTTOM ({len(dalem)}):\n"
    for i,c in enumerate(dalem,len(gold+silver+pre)+1):
        msg+=f"{i}. {c[0]} {c[1]:.1f}% | {int(c[2])}% low | sq {int(c[3])}% | {int(c[4]/1000000)}jt\n"
    msg+="\n"
if jangan:
    msg+=f"⛔ SKIP JEBOL ({len(jangan)}):\n"
    for c in jangan[:3]:
        msg+=f"- {c[0]} {c[1]:.1f}% | SKIP!\n"
    msg+="\n"
msg+=f"Total {len(gold+silver+pre+dalem)} Valid | SCAN {len(tickers)}"
print(msg)
send_tele(msg)
