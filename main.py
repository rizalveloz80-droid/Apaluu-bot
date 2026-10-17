import requests, os, json
from datetime import datetime

BREAKOUT_COUNT = 5
BOUNCE_COUNT = 5
ACCUM_COUNT = 3
BLACKLIST = ["usdt_idr","usdc_idr","btc_idr","xaut_idr","paxg_idr","eth_idr","idrt_idr","ouros_idr"]
CACHE_FILE = "price_cache.json"

TELE_TOKEN = os.getenv("TELE_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
TELE_CHAT_ID = os.getenv("TELE_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID") or os.getenv("CHAT_ID")

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT_ID:
        print("TELE_ERR: Token kosong!")
        return
    try:
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        r = requests.post(url, data={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=15)
        print(f"TELE_SENT {r.status_code}")
    except Exception as e:
        print("TELE_ERR " + str(e))

def deteksi_momentum_v29(chg_1m, dl, dh, vol_24h):
    total_range = dl + dh
    if vol_24h < 200000000: 
        return "NORMAL"
    # FILTER OGN JEBOL - JANGAN ANTRI!
    if chg_1m <= -2.0 and dl <= 2.0:
        return "JANGAN_ANTRI_JEBOL"
    if chg_1m >= 0.7 and dh <= 2.5 and vol_24h >= 500000000:
        return "BREAKOUT"
    if chg_1m >= 0.4 and total_range >= 7 and dl <= 1.2 and vol_24h >= 300000000:
        return "BOUNCE"
    if -0.3 <= chg_1m <= 0.4 and total_range <= 4.0 and vol_24h >= 1000000000:
        return "ACCUMULATION"
    return "NORMAL"

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
    print(f"Gagal API: {e}")
    exit()

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
        if last == 0 or high == 0: continue
        dl = ((last - low) / last) * 100
        dh = ((high - last) / last) * 100
        prev = cache.get(pair, last)
        chg_1m = ((last - prev) / prev * 100) if prev else 0
        cat = deteksi_momentum_v29(chg_1m, dl, dh, vol)
        if cat != "NORMAL":
            candidates.append({"pair": pair.upper().replace("_IDR",""), "chg_1m": chg_1m, "dl": dl, "dh": dh, "vol": vol, "cat": cat})
        cache[pair] = last
    except:
        continue

with open(CACHE_FILE,'w') as f:
    json.dump(cache,f)

candidates.sort(key=lambda x: x["vol"], reverse=True)
breakout = [c for c in candidates if c["cat"] == "BREAKOUT"][:BREAKOUT_COUNT]
bounce = [c for c in candidates if c["cat"] == "BOUNCE"][:BOUNCE_COUNT]
accum = [c for c in candidates if c["cat"] == "ACCUMULATION"][:ACCUM_COUNT]
jangan = [c for c in candidates if c["cat"] == "JANGAN_ANTRI_JEBOL"]

now = datetime.now().strftime('%H:%M')
msg = f"🚀 INDODAX V28.2 FIX OGN | {now}\n\n"

if breakout:
    msg += f"🔥 BREAKOUT ({len(breakout)}):\n"
    for i,c in enumerate(breakout,1):
        msg += f"{i}. {c['pair']} +{c['chg_1m']:.2f}% Vol:{c['vol']/1000000000:.1f}M\n"
    msg += "\n"
if bounce:
    msg += f"🛡️ BOUNCE VALID ({len(bounce)}):\n"
    for i,c in enumerate(bounce,len(breakout)+1):
        msg += f"{i}. {c['pair']} +{c['chg_1m']:.2f}% Low:{c['dl']:.1f}% Vol:{c['vol']/1000000:.0f}jt\n"
    msg += "\n"
if accum:
    msg += f"📦 AKUMULASI ({len(accum)}):\n"
    for i,c in enumerate(accum,len(breakout)+len(bounce)+1):
        msg += f"{i}. {c['pair']} Vol:{c['vol']/1000000000:.1f}M\n"
    msg += "\n"
if jangan:
    msg += f"⛔ SKIP JEBOL ({len(jangan)}):\n"
    for c in jangan[:3]:
        msg += f"- {c['pair']} {c['chg_1m']:.2f}% - SKIP KAYAK OGN!\n"
    msg += "\n"

total = len(breakout)+len(bounce)+len(accum)
if total > 0:
    msg += f"Total:{total} Valid | Scan:{len(tickers)} | ANTI OGN"
    print(msg)
    send_tele(msg)
else:
    print(f"[{now}] 0 Valid, {len(jangan)} Jebol skip")
    if jangan:
        send_tele(f"V28.2 | {now} | 0 Valid | {len(jangan)} Jebol SKIP | Scan {len(tickers)}")
