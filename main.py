import requests
import time
import os

API_URL = "https://indodax.com/api/ticker/{}"
MARKETS_URL = "https://indodax.com/api/pairs"

BLACKLIST = {
    'usdt_idr','usdc_idr','dai_idr','busd_idr','btc_idr','eth_idr',
    'xrp_idr','sol_idr','doge_idr','bnb_idr','ern_idr','hype_idr'
}

# ====== MODE HUNTER (ICNT/ZEROBRO) ======
H_MIN_CHANGE = 5
H_MAX_CHANGE = 25      # koin volatile naik sampe 25%
H_MIN_TO_HIGH = 25     # masih ruang ke high >=25%
H_MIN_VOL = 100000

# ====== MODE SEGAR (koin aman) ======
S_MIN_CHANGE = 3
S_MAX_CHANGE = 10      # koin konservatif
S_MIN_TO_HIGH = 20
S_MIN_VOL = 200000

# PAKAI YANG SEBELUMNYA - GA USAH DIISI MANUAL
TELEGRAM_TOKEN = os.getenv('TELE_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELE_CHAT_ID')

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=data, timeout=10)
    except:
        pass

def get_markets():
    r = requests.get(MARKETS_URL, timeout=10)
    return [p["id"] for p in r.json()]

def analyze(pair):
    r = requests.get(API_URL.format(pair), timeout=10)
    if r.status_code != 200:
        return None
    t = r.json()["ticker"]
    last = float(t["last"])
    low = float(t["low"]) or 1
    high = float(t["high"]) or last
    base = pair.split("_")[0]
    vol = float(t[f"vol_{base}"]) * last
    change = (last - low) / low * 100
    to_high = (high - last) / last * 100 if last else 0
    return {"pair": pair, "last": last, "change": change, "to_high": to_high, "vol": vol}

def main():
    pairs = get_markets()
    for p in pairs:
        if p in BLACKLIST:
            continue
        try:
            a = analyze(p)
            if not a:
                continue

            # 1) HUNTER - koin volatile sisa gede (kaya ZEREBRO lu)
            if (a["vol"] >= H_MIN_VOL and H_MIN_CHANGE <= a["change"] <= H_MAX_CHANGE and a["to_high"] >= H_MIN_TO_HIGH):
                msg = (f"🔥 HUNTER {a['pair']}\n"
                       f"naik {a['change']:.1f}% dr low\n"
                       f"⚡ sisa ke high {a['to_high']:.1f}%\n"
                       f"vol {a['vol']/1e6:.2f}M")
                send_telegram(msg)
                print(msg)

            # 2) SEGAR - koin aman ngga volatile
            elif (a["vol"] >= S_MIN_VOL and S_MIN_CHANGE <= a["change"] <= S_MAX_CHANGE and a["to_high"] >= S_MIN_TO_HIGH):
                msg = (f"🌱 SEGAR {a['pair']}\n"
                       f"naik {a['change']:.1f}% dr low\n"
                       f"⚡ sisa ke high {a['to_high']:.1f}%\n"
                       f"vol {a['vol']/1e6:.2f}M")
                send_telegram(msg)
                print(msg)

        except Exception:
            continue
        time.sleep(0.3)

if __name__ == "__main__":
    while True:
        main()
        time.sleep(300)  # 5 menit
