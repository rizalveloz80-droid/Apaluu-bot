import requests, os, json
from datetime import datetime

# ====== V27.4 FINAL SIMPLE - ANTI PUSING - ANTI USDT/BTC ======
EARLY_COUNT = 5
PRE_COUNT = 5
DALEM_COUNT = 3
BLACKLIST = ["USDT_IDR","USDC_IDR","BTC_IDR","XAUT_IDR","PAXG_IDR","ETH_IDR"]
CACHE_FILE = "price_cache.json"

TELE_TOKEN = os.getenv("TELE_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
TELE_CHAT_ID = os.getenv("TELE_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID") or os.getenv("CHAT_ID")

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT_ID:
        print(f"TELE_SKIP")
        return
    try:
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        r = requests.post(url, data={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=15)
        print(f"TELE_SENT {r.status_code} {r.text[:150]}")
    except Exception as e:
        print(f"TELE_ERR {e}")

def smart_candle(chg, dl, dh, vol):
    sq = dl + dh
    # PRE_TRENDING - sebelum trending Indodax (0-5.5% low, sq kecil)
    if 0 <= dl <= 5.5 and sq < 12 and -20 <= chg <= 5 and vol >= 10_000_000:
        return "PRE_TRENDING", sq
    # EARLY - masih awal mau terbang
    if sq < 18 and 2 <= dl <= 12 and 0.1 <= chg <= 8 and vol >= 50_000_000:
        return "EARLY", sq
    # DALEM - bottom hunter
    if chg <= -1.0 and dl <= 4 and vol >= 50_000_000:
        return "DALEM", sq
    return "NORMAL", sq

print(f"⚡ APALUU V27.4 FINAL {datetime.now().strftime('%H:%M')}")

cache = {}
if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE,'r') as f:
            cache = json.load(f)
        print(f"Cache loaded {len(cache)}")
    except:
        pass

try:
    resp = requests.get("https://indodax.com/api/tickers", timeout=15).json()
    tickers = resp["tickers"]
except Exception as e:
    print(f"API ERR {e}")
    exit()

candidates = []
for pair, data in tickers.items():
    if not pair.endswith("_IDR"): continue
    if pair in BLACKLIST: continue
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
            candidates.append((pair, chg, dl, sq, vol, cat))
        cache[pair] = last
    except:
        continue

# NO SHUFFLE - SORT BY VOL MURNI
candidates.sort(key=lambda x: x[4], reverse=True)
top = candidates[:350]

print(f"SCAN {len(tickers)} -> {len(candidates)} CANDIDATES -> TOP {len(top)} BY VOL")

with open(CACHE_FILE,'w') as f:
    json.dump(cache,f)

early = [c for c in top if c[5] == "EARLY"][:EARLY_COUNT]
pre = [c for c in top if c[5] == "PRE_TRENDING"][:PRE_COUNT]
dalem = [c for c in top if c[5] == "DALEM"][:DALEM_COUNT]

now = datetime.now().strftime('%H:%M')
msg = f"🎯 V27.4 FINAL | {now} | NO USDT/BTC | VOL SORT\n\n"

if early:
    msg += f"⚡ EARLY SEBELUM TERBANG ({len(early)}):\n"
    for i,c in enumerate(early,1):
        msg += f"{i}. {
