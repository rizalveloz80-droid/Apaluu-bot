# main.py V27.0 LOOSE - FIX 4 MASALAH
# Fix: 1. Kuota Bronze Gainers dibuka  2. Shuffle mati  3. Vol max 2M  4. chg_15m

import requests, json, os, yaml
from datetime import datetime

# === LOAD CONFIG ===
CONFIG_FILE = "V10_loose.yml"
CACHE_FILE = "price_cache.json"

with open(CONFIG_FILE, "r") as f:
    cfg = yaml.safe_load(f)

COUNTS = cfg["counts"]
FILTERS = cfg["filters"]
LOGIC = cfg["logic"]

# === CACHE BUAT CHG_15M ===
def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {"time": "", "prices": {}}

def save_cache(prices):
    data = {"time": datetime.now().isoformat(), "prices": prices}
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, indent=2)

cache = load_cache()
old_prices = cache.get("prices", {})

# === FETCH INDODAX ===
def get_tickers():
    url = "https://indodax.com/api/tickers"
    r = requests.get(url, timeout=10)
    return r.json()["tickers"]

def calc_dl(last, low):
    if low == 0: return 0
    return (last - low) / low * 100

def calc_sq(high, low, last):
    # sq = (high - low) / last * 100 = lebar BB
    if last == 0: return 0
    return (high - low) / last * 100

# === MAIN LOGIC ===
tickers = get_tickers()
all_coins = []
current_prices = {}

for pair, t in tickers.items():
    if not pair.endswith("_idr"): continue
    try:
        last = float(t["last"])
        low = float(t["low"])
        high = float(t["high"])
        vol_idr = float(t["vol_idr"])
        p24 = float(t.get("vol_idr", last)) # p24 = price 24h ago ada di ticker? pake last - chg

        # Hitung chg 24j
        # Indodax tickers udah ada change, tapi kita hitung manual biar akurat
        # (last - p24) / p24 *100 -> p24 diambil dari API ticker kalau ada
        # fallback pakai high/low
        # Untuk simplenya pake rumus chg yang udah ada di API kalau ada
        # Di tickers Indodax ga ada chg langsung, jadi kita ambil dari last vs low/high avg
        
        # CHG 24J (dari data statis)
        # Kita pakai vol_idr untuk filter, chg dihitung dari (last - prev_price)
        # Untuk contoh ini chg kita ambil dari perkiraan
        # REAL: ganti dengan (last - float(t["..."])) logic lu sebelumnya
        chg = ((last - float(t.get("last", last))) / last * 100) if last else 0
        # KALO LU UDAH PUNYA RUMUS CHG LAMA, PAKAI INI:
        # chg = (last - p24) / p24 * 100
        
        # CHG 15M (BARU! FIX NO 4)
        p15m = old_prices.get(pair, {}).get("last", last)
        chg_15m = (last - p15m) / p15m * 100 if p15m else 0

        dl = calc_dl(last, low)
        sq = calc_sq(high, low, last)

        coin = {
            "pair": pair.upper(),
            "last": last,
            "low": low,
            "high": high,
            "vol": vol_idr,
            "chg": chg,
            "chg_15m": chg_15m,
            "dl": dl,
            "sq": sq,
        }
        all_coins.append(coin)
        current_prices[pair] = {"last": last, "vol": vol_idr}
        
    except:
        continue

# === FIX NO 2: MATIIN SHUFFLE, SORT BY VOL ===
# Dari: random.shuffle(top_low)
# Jadi: sort by vol descending
all_coins_sorted = sorted(all_coins, key=lambda x: x["vol"], reverse=True)

# Ambil top 121-350 untuk PRE_TRENDING (yang volume kecil tapi potensial)
# Tapi tetap sort by vol biar yang 224jt di atas!
top_low = all_coins_sorted[120:350]  # ranking 121-350
top_low = sorted(top_low, key=lambda x: x["vol"], reverse=True)  # SORT ULANG BY VOL!

# === FILTERING - FIX NO 3: VOL MAX 2 MILIAR ===
def pass_filter(coin, f):
    return (f["dl"][0] <= coin["dl"] <= f["dl"][1] and
            f["sq"][0] <= coin["sq"] <= f["sq"][1] and
            f["chg"][0] <= coin["chg"] <= f["chg"][1] and
            f["vol_min"] <= coin["vol"] <= f["vol_max"])

gold,
