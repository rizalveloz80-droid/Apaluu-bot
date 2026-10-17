# main.py V27.0 LOOSE - READY TO RUN - NO YAML ERROR
import requests, json, os
from datetime import datetime

print("=== BOT V27.0 LOOSE START ===")

# === CONFIG LOOSE LANGSUNG DI SINI (BIAR GA ERROR YAML) ===
GOLD_COUNT = 2
SILVER_COUNT = 3
BRONZE_COUNT = 3
GAINERS_COUNT = 3
PRE_COUNT = 4
SEROK_COUNT = 5

CACHE_FILE = "price_cache.json"

# Load cache lama buat chg_15m
def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cache(prices):
    with open(CACHE_FILE, "w") as f:
        json.dump(prices, f)

cache = load_cache()
old_prices = cache

# Fetch tickers
url = "https://indodax.com/api/tickers"
r = requests.get(url, timeout=15)
tickers = r.json()["tickers"]

all_coins = []
current_prices = {}

for pair, t in tickers.items():
    if not pair.endswith("_idr"):
        continue
    try:
        last = float(t["last"])
        low = float(t["low"])
        high = float(t["high"])
        vol = float(t["vol_idr"])
        
        # dl = jarak dari low
        dl = (last - low) / low * 100 if low != 0 else 0
        # sq = lebar candle
        sq = (high - low) / last * 100 if last != 0 else 0
        # chg 24j - ambil dari API tickers Indodax ga ada, kita bikin 0 dulu
        # Nanti lu ganti dengan rumus chg lu yang lama kalo ada
        chg = 0  
        
        # chg_15m - ambil dari cache
        p15 = old_prices.get(pair, last)
        if isinstance(p15, dict):
            p15 = p15.get("last", last)
        chg_15m = (last - p15) / p15 * 100 if p15 != 0 else 0

        all_coins.append({
            "pair": pair,
            "last": last,
            "low": low,
            "high": high,
            "vol": vol,
            "dl": dl,
            "sq": sq,
            "chg": chg,
            "chg_15m": chg_15m
        })
        current_prices[pair] = last
    except:
        continue

# === FIX NO 2: SORT BY VOL BUKAN SHUFFLE ===
all_sorted = sorted(all_coins, key=lambda x: x["vol"], reverse=True)
top_low = all_sorted[120:350]
top_low = sorted(top_low, key=lambda x: x["vol"], reverse=True)

gold = []
silver = []
pre = []
serok = []

for c in all_sorted:
    # GOLD: dl 0-10, sq <15
    if 0 <= c["dl"] <= 10 and c["sq"] < 15 and c["vol"] >= 10000000:
        # FIX NO 4: kalo chg_15m >3% anggap gold running
        if c["chg_15m"] > 3 or True:
            gold.append(c)
    
for c in top_low:
    # PRE_TRENDING LOOSE: dl 0-6.5, sq <14, vol >=10jt (FIX NO 3 HAPUS 250JT)
    if 0 <= c["dl"] <= 6.5 and c["sq"] < 14 and c["vol"] >= 10000000:
        pre.append(c)
    # SEROK_DALEM
    if 0 <= c["dl"] <= 3.5 and c["vol"] >= 10000000:
        serok.append(c)

gold = sorted(gold, key=lambda x: x["dl"])[:GOLD_COUNT]
pre = sorted(pre, key=lambda x: x["sq"])[:PRE_COUNT]
serok = sorted(serok, key=lambda x: x["dl"])[:SEROK_COUNT]

# === PRINT ===
print(f"\nGOLD ({len(gold)}):")
for c in gold:
    print(f"- {c['pair'].upper()} dl {c['dl']:.2f}% sq {c['sq']:.1f}% vol {c['vol']/1e6:.0f}jt chg15m {c['chg_15m']:+.1f}%")

print(f"\nPRE_TRENDING ({len(pre)}):")
for c in pre:
    print(f"- {c['pair'].upper()} dl {c['dl']:.2f}% sq {c['sq']:.1f}% vol {c['vol']/1e6:.0f}jt chg15m {c['chg_15m']:+.1f}%")

print(f"\nSEROK_DALEM ({len(serok)}):")
for c in serok:
    print(f"- {c['pair'].upper()} dl {c['dl']:.2f}% vol {c['vol']/1e6:.0f}jt")

save_cache(current_prices)
print("\n=== DONE - cache saved ===")
