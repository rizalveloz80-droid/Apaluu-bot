import requests, os, json
from datetime import datetime

GOLD_COUNT = 5
SILVER_COUNT = 3
PRE_COUNT = 2
DALEM_COUNT = 5
BLACKLIST = ["usdt_idr","usdc_idr","btc_idr","xaut_idr","paxg_idr"]
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

def smart_candle(chg, dl, dh, vol):
    sq = dl + dh
    if sq < 12 and 2 <= dl <= 9 and -2 <= chg <= 5 and 10000000 <= vol <= 600000000:
        return "GOLD", sq
    if sq < 18 and 2 <= dl <= 12 and -2 <= chg <= 8 and 10000000 <= vol <= 800000000:
        return "SILVER", sq
    if 0 <= dl <= 5.5 and sq < 12 and -20 <= chg <= 5 and vol >= 10000000:
        return "PRE", sq
    if chg <= 0 and dl <= 4 and vol >= 10000000:
        return "DALEM", sq
    return "NORMAL", sq

print("APALUU V27.7 COMEBACK " + datetime.now().strftime('%H:%M'))

cache = {}
if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE,'r') as f:
            cache = json.load(f)
    except:
        pass

tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json()["tickers"]
print("SCAN " + str(len(tickers)))

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
        cat, sq = smart_candle(chg, dl, dh, vol)
        if cat != "NORMAL":
            candidates.append((pair.upper(), chg, dl, sq, vol, cat))
        cache[pair] = last
    except:
        continue

candidates.sort(key=lambda x: x[4], reverse=True)
top = candidates[:350]

with open(CACHE_FILE,'w') as f:
    json.dump(cache,f)

gold = [c for c in top if c[5] == "GOLD"][:GOLD_COUNT]
silver = [c for c in top if c[5] == "SILVER"][:SILVER_COUNT]
pre = [c for c in top if c[5] == "PRE"][:PRE_COUNT]
dalem = [c for c in top if c[5] == "DALEM"][:DALEM_COUNT]

now = datetime.now().strftime('%H:%M')
msg = "V27.7 COMEBACK | " + now + " | 15 DUAL 8 EARLY + 7 BAWAH | NO USDT/BTC | VOL SORT\n\n"

if gold:
    msg += "GOLD V25.3 JACKPOT (" + str(len(gold)) + "):\n"
    for i,c in enumerate(gold,1):
        msg += str(i) + ". " + c[0] + " " + str(round(c[1],1)) + "% | " + str(int(c[2])) + "% low | sq " + str(int(c[3])) + "% | " + str(int(c[4]/1000000)) + "jt | GOLD\n"
    msg += "\n"
if silver:
    msg += "SILVER V25.5 EARLY (" + str(len(silver)) + "):\n"
    for i,c in enumerate(silver, len(gold)+1):
        msg += str(i) + ". " + c[0] + " " + str(round(c[1],1)) + "% | " + str(int(c[2])) + "% low | sq " + str(int(c[3])) + "% | " + str(int(c[4]/1000000)) + "jt | SILVER\n"
    msg += "\n"
if pre:
    msg += "PRE_TRENDING CALON TIA KMNO (" + str(len(pre)) + "):\n"
    for i,c in enumerate(pre, len(gold+silver)+1):
        msg += str(i) + ". " + c[0] + " " + str(round(c[1],1)) + "% | " + str(int(c[2])) + "% low | sq " + str(int(c[3])) + "% | " + str(int(c[4]/1000000)) + "jt | CALON +25%!\n"
    msg += "\n"
if dalem:
    msg += "SEROK DALEM -20% (" + str(len(dalem)) + "):\n"
    for i,c in enumerate(dalem, len(gold+silver+pre)+1):
        msg += str(i) + ". " + c[0] + " " + str(round(c[1],1)) + "% | " + str(int(c[2])) + "% low | sq " + str(int(c[3])) + "% | " + str(int(c[4]/1000000)) + "jt | DALEM!\n"
    msg += "\n"

if len(gold+silver+pre+dalem) == 0:
    msg += "MARKET SEPI - TOP VOL:\n"
    allp = []
    for pair, data in tickers.items():
        if not pair.lower().endswith("_idr"): continue
        if pair.lower() in BLACKLIST: continue
        try:
            allp.append((pair.upper(), float(data["vol_idr"])))
        except:
            continue
    allp.sort(key=lambda x: x[1], reverse=True)
    for i,p in enumerate(allp[:5],1):
        msg += str(i) + ". " + p[0] + " vol " + str(int(p[1]/1000000)) + "jt\n"

msg += "\nTotal " + str(len(gold+silver+pre+dalem)) + " RANK | 8 EARLY + 7 BAWAH | NANGKEP DARI BAWAH!"

print(msg)
send_tele(msg)
