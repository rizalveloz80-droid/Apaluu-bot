import requests, os, json
from datetime import datetime

EARLY_COUNT = 5
PRE_COUNT = 5
DALEM_COUNT = 3
BLACKLIST = ["USDT_IDR","USDC_IDR","BTC_IDR","XAUT_IDR","PAXG_IDR"]
CACHE_FILE = "price_cache.json"

TELE_TOKEN = os.getenv("TELE_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
TELE_CHAT_ID = os.getenv("TELE_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID") or os.getenv("CHAT_ID")

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT_ID:
        print("TELE_SKIP")
        return
    try:
        url = "https://api.telegram.org/bot" + TELE_TOKEN + "/sendMessage"
        r = requests.post(url, data={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=15)
        print("TELE_SENT " + str(r.status_code))
    except Exception as e:
        print("TELE_ERR " + str(e))

def smart_candle(chg, dl, dh, vol):
    sq = dl + dh
    if 0 <= dl <= 5.5 and sq < 12 and -20 <= chg <= 5 and vol >= 10000000:
        return "PRE_TRENDING", sq
    if sq < 18 and 2 <= dl <= 12 and 0.1 <= chg <= 8 and vol >= 50000000:
        return "EARLY", sq
    if chg <= -1.0 and dl <= 4 and vol >= 50000000:
        return "DALEM", sq
    return "NORMAL", sq

print("APALUU V27.4 FIX START " + datetime.now().strftime('%H:%M'))

cache = {}
if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE,'r') as f:
            cache = json.load(f)
    except:
        pass

try:
    tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json()["tickers"]
except Exception as e:
    print("API ERR")
    exit()

candidates = []
for pair, data in tickers.items():
    if not pair.endswith("_IDR"):
        continue
    if pair in BLACKLIST:
        continue
    try:
        last = float(data["last"])
        low = float(data["low"])
        high = float(data["high"])
        vol = float(data["vol_idr"])
        if last == 0:
            continue
        dl = ((last - low) / last) * 100
        dh = ((high - last) / last) * 100
        prev = cache.get(pair, last)
        chg = ((last - prev) / prev * 100) if prev else 0
        cat, sq = smart_candle(chg, dl, dh, vol)
        if cat != "NORMAL":
            candidates.append((pair, chg, dl, sq, vol, cat))
        cache[pair] = last
    except:
        continue

candidates.sort(key=lambda x: x[4], reverse=True)
top = candidates[:350]

with open(CACHE_FILE,'w') as f:
    json.dump(cache,f)

early = [c for c in top if c[5] == "EARLY"][:EARLY_COUNT]
pre = [c for c in top if c[5] == "PRE_TRENDING"][:PRE_COUNT]
dalem = [c for c in top if c[5] == "DALEM"][:DALEM_COUNT]

now = datetime.now().strftime('%H:%M')
msg = "V27.4 FINAL FIX | " + now + " | NO USDT/BTC\n\n"

if early:
    msg += "EARLY SEBELUM TERBANG (" + str(len(early)) + "):\n"
    for i,c in enumerate(early,1):
        vol_jt = int(c[4]/1000000000)
        msg += str(i) + ". " + c[0] + " " + str(round(c[1],1)) + "% | " + str(int(c[2])) + "% low | sq " + str(int(c[3])) + "% | " + str(vol_jt) + "jt\n"
    msg += "\n"

if pre:
    msg += "PRE_TRENDING - SEBELUM TRENDING INDODAX (" + str(len(pre)) + "):\n"
    for i,c in enumerate(pre,1):
        vol_jt = int(c[4]/1000000000)
        msg += str(i) + ". " + c[0] + " " + str(round(c[1],1)) + "% | " + str(int(c[2])) + "% low | " + str(vol_jt) + "jt | CALON NAIK!\n"
    msg += "\n"

if dalem:
    msg += "SEROK DALEM (" + str(len(dalem)) + "):\n"
    for i,c in enumerate(dalem,1):
        vol_jt = int(c[4]/1000000000)
        msg += str(i) + ". " + c[0] + " " + str(round(c[1],1)) + "% | " + str(int(c[2])) + "% low | " + str(vol_jt) + "jt\n"
    msg += "\n"

msg += "Total " + str(len(early+pre+dalem)) + " RANK | SCAN " + str(len(top)) + " | ANTI USDT/BTC"

print(msg)
send_tele(msg)
