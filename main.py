import requests, os, json
from datetime import datetime

GOLD_COUNT = 5
SILVER_COUNT = 3
PRE_COUNT = 2
DALEM_COUNT = 5
BLACKLIST = ["usdt_idr","usdc_idr","btc_idr","xaut_idr","paxg_idr","eth_idr"]
CACHE_FILE = "price_cache.json"

TELE_TOKEN = os.getenv("TELE_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
TELE_CHAT_ID = os.getenv("TELE_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID") or os.getenv("CHAT_ID")

def send_tele(msg):
    try:
        url = "https://api.telegram.org/bot" + TELE_TOKEN + "/sendMessage"
        r = requests.post(url, data={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=15)
        print("TELE_SENT " + str(r.status_code))
    except Exception as e:
        print("TELE_ERR " + str(e))

def smart_candle_v28(chg, dl, dh, vol):
    sq = dl + dh
    if 0 <= dl <= 8 and sq < 12 and -2 <= chg <= 5 and vol >= 10000000:
        return "GOLD", sq
    if 0 <= dl <= 10 and sq < 18 and -2 <= chg <= 8 and vol >= 10000000:
        return "SILVER", sq
    if 0 <= dl <= 3 and sq < 8 and -5 <= chg <= 3 and vol >= 10000000:
        return "PRE", sq
    if -25 <= chg <= -2.5 and 0 <= dl <= 2.5 and sq < 15 and dh < 12 and vol >= 30000000:
        return "DALEM", sq
    if -25 <= chg <= -1.5 and 0 <= dl <= 4 and sq < 25 and vol >= 10000000:
        return "DALEM_LOOSE", sq
    return "NORMAL", sq

print("APALUU V27.8 SUPER BOTTOM " + datetime.now().strftime('%H:%M'))

cache = {}
if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE,'r') as f:
            cache = json.load(f)
    except:
        pass

tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json()["tickers"]

candidates = []
for pair, data in tickers.items():
    pl = pair.lower()
    if not pl.endswith("_idr"): continue
    if pl in BLACKLIST: continue
    try:
        last = float(data["last"])
        low = float(data["low"])
        high = float(data["high"])
        vol = float(data["vol_idr"])
        if last == 0: continue
        dl = ((last - low) / last) * 100
        dh = ((high - last) / last) * 100
        prev = cache.get(pair, last)
        chg = ((last - prev) / prev * 100) if prev else 0
        cat, sq = smart_candle_v28(chg, dl, dh, vol)
        if cat != "NORMAL":
            candidates.append((pair.upper(), chg, dl, sq, vol, cat, dh))
        cache[pair] = last
    except:
        continue

candidates.sort(key=lambda x: x[4], reverse=True)
top = candidates[:400]

with open(CACHE_FILE,'w') as f:
    json.dump(cache,f)

gold = [c for c in top if c[5] == "GOLD"][:GOLD_COUNT]
silver = [c for c in top if c[5] == "SILVER"][:SILVER_COUNT]
pre = [c for c in top if c[5] == "PRE"][:PRE_COUNT]
dalem_pas = [c for c in top if c[5] == "DALEM"][:DALEM_COUNT]
if len(dalem_pas) == 0:
    dalem_pas = [c for c in top if c[5] == "DALEM_LOOSE"][:DALEM_COUNT]
    is_loose = True
else:
    is_loose = False

now = datetime.now().strftime('%H:%M')
msg = "V27.8 SUPER BOTTOM | " + now + " | NO USDT/BTC | VOL SORT | TIK PAS\n\n"

if gold:
    msg += "GOLD JACKPOT (" + str(len(gold)) + "):\n"
    for i,c in enumerate(gold,1):
        msg += str(i) + ". " + c[0] + " " + str(round(c[1],1)) + "% | " + str(int(c[2])) + "% low | sq " + str(int(c[3])) + "% | " + str(int(c[4]/1000000)) + "jt\n"
    msg += "\n"
if silver:
    msg += "SILVER EARLY (" + str(len(silver)) + "):\n"
    for i,c in enumerate(silver, len(gold)+1):
        msg += str(i) + ". " + c[0] + " " + str(round(c[1],1)) + "% | " + str(int(c[2])) + "% low | sq " + str(int(c[3])) + "% | " + str(int(c[4]/1000000)) + "jt\n"
    msg += "\n"
if pre:
    msg += "PRE_TRENDING (" + str(len(pre)) + "):\n"
    for i,c in enumerate(pre, len(gold+silver)+1):
        msg += str(i) + ". " + c[0] + " " + str(round(c[1],1)) + "% | " + str(int(c[2])) + "% low | sq " + str(int(c[3])) + "% | " + str(int(c[4]/1000000)) + "jt | CALON!\n"
    msg += "\n"
if dalem_pas:
    label = "DALEM BOTTOM PAS" if not is_loose else "DALEM LOOSE"
    msg += label + " (" + str(len(dalem_pas)) + "):\n"
    for i,c in enumerate(dalem_pas, len(gold+silver+pre)+1):
        msg += str(i) + ". " + c[0] + " " + str(round(c[1],1)) + "% | " + str(int(c[2])) + "% low | sq " + str(int(c[3])) + "% | dh " + str(int(c[6])) + "% | " + str(int(c[4]/1000000)) + "jt | BOTTOM!\n"
    msg += "\n"

msg += "Total " + str(len(gold+silver+pre+dalem_pas)) + " RANK | SCAN " + str(len(tickers)) + " | TIK BOTTOM"

print(msg)
send_tele(msg)
