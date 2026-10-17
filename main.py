import requests, os, json
from datetime import datetime

GOLD_COUNT = 5
SILVER_COUNT = 3
PRE_COUNT = 2
DALEM_COUNT = 5
BLACKLIST = ["usdt_idr","usdc_idr","btc_idr","xaut_idr","paxg_idr","eth_idr","idrt_idr","ouros_idr"]
CACHE_FILE = "price_cache.json"

TELE_TOKEN = os.getenv("TELE_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
TELE_CHAT_ID = os.getenv("TELE_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID") or os.getenv("CHAT_ID")

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT_ID:
        print("TELE_ERR Token kosong")
        return
    try:
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        r = requests.post(url, data={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=15)
        print(f"TELE_SENT {r.status_code}")
    except Exception as e:
        print("TELE_ERR " + str(e))

def smart_candle_v28_3(chg, dl, dh, vol):
    """
    V28.3 HYBRID:
    - V28.0 Logic yang valid di screenshot lu (GOLD 0% low sq 3% vol 5M)
    - + Filter OGN JEBOL biar ga antri pas masih turun
    """
    sq = dl + dh

    # === FILTER ANTI NYANGKUT OGN - HARUS DI ATAS! ===
    # Kalo 1 menit masih terjun >1.5% + nempel low = JANGAN ANTRI!
    # OGN 525->521 -3.3% bakal ke-filter disini, ga masuk BOTTOM!
    if chg <= -1.5 and dl <= 2.0 and vol >= 50000000:
        return "JANGAN_ANTRI", sq

    # === GOLD JACKPOT - XRP -0.9% 0% low sq 3% 5027jt VALID! ===
    if 0 <= dl <= 8 and sq < 12 and -1.5 <= chg <= 4 and vol >= 15000000:
        return "GOLD", sq

    # === SILVER EARLY ===
    if 0 <= dl <= 10 and sq < 16 and -1.5 <= chg <= 6 and vol >= 15000000:
        return "SILVER", sq

    # === PRE_TRENDING ASLI - DIPERKETAT -2% ONLY! OGN GA MASUK! ===
    if 0 <= dl <= 2.5 and sq < 9 and -2 <= chg <= 2.5 and vol >= 10000000:
        return "PRE", sq

    # === DALEM BOTTOM PAS - WLD -4.6% OGN -3.3% OP -3.6% VALID! ===
    # Tapi baru masuk kalo udah ga terjun lagi (di-filter di atas)
    if -15 <= chg <= -2.2 and 0 <= dl <= 1.5 and sq < 15 and vol >= 20000000:
        return "DALEM", sq
    if -25 <= chg <= -2.2 and 0 <= dl <= 2.5 and sq < 20 and vol >= 20000000:
        return "DALEM", sq

    return "NORMAL", sq

print("APALUU V28.3 HYBRID " + datetime.now().strftime('%H:%M'))

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
        if last == 0: continue
        dl = ((last - low) / last) * 100
        dh = ((high - last) / last) * 100
        prev = cache.get(pair, last)
        chg = ((last - prev) / prev * 100) if prev else 0
        cat, sq = smart_candle_v28_3(chg, dl, dh, vol)
        if cat != "NORMAL":
            candidates.append((pair.upper(), chg, dl, sq, vol, cat, dh))
        cache[pair] = last
    except:
        continue

candidates.sort(key=lambda x: x[4], reverse=True)
top = candidates[:500]

with open(CACHE_FILE,'w') as f:
    json.dump(cache,f)

gold = [c for c in top if c[5] == "GOLD"][:GOLD_COUNT]
silver = [c for c in top if c[5] == "SILVER"][:SILVER_COUNT]
pre = [c for c in top if c[5] == "PRE"][:PRE_COUNT]
dalem = [c for c in top if c[5] == "DALEM"][:DALEM_COUNT]
jangan = [c for c in top if c[5] == "JANGAN_ANTRI"]

now = datetime.now().strftime('%H:%M')
msg = f"V28.3 HYBRID | {now} | GOLD+BOTTOM+ANTI OGN\n\n"

if gold:
    msg += f"GOLD JACKPOT ({len(gold)}):\n"
    for i,c in enumerate(gold,1):
        msg += f"{i}. {c[0]} {c[1]:.1f}% | {int(c[2])}% low | sq {int(c[3])}% | {int(c[4]/1000000)}jt\n"
    msg += "\n"
if silver:
    msg += f"SILVER EARLY ({len(silver)}):\n"
    for i,c in enumerate(silver, len(gold)+1):
        msg += f"{i}. {c[0]} {c[1]:.1f}% | {int(c[2])}% low | sq {int(c[3])}% | {int(c[4]/1000000)}jt\n"
    msg += "\n"
if pre:
    msg += f"PRE_TRENDING ({len(pre)}):\n"
    for i,c in enumerate(pre, len(gold+silver)+1):
        msg += f"{i}. {c[0]} {c[1]:.1f}% | {int(c[2])}% low | sq {int(c[3])}% | {int(c[4]/1000000)}jt | CALON!\n"
    msg += "\n"
if dalem:
    msg += f"DALEM BOTTOM PAS ({len(dalem)}):\n"
    for i,c in enumerate(dalem, len(gold+silver+pre)+1):
        msg += f"{i}. {c[0]} {c[1]:.1f}% | {int(c[2])}% low | sq {int(c[3])}% | {int(c[4]/1000000)}jt | BOTTOM!\n"
    msg += "\n"
if jangan:
    msg += f"⛔ JANGAN ANTRI ({len(jangan)}):\n"
    for c in jangan[:3]:
        msg += f"- {c[0]} {c[1]:.1f}% | SKIP OGN MODE!\n"
    msg += "\n"

msg += f"Total {len(gold+silver+pre+dalem)} Valid | {len(jangan)} Skip | SCAN {len(tickers)}"

print(msg)
send_tele(msg)
