import requests, os, datetime

VOL_MIN = 10000000
RATIO_MIN = 0.6
S_MIN_CHG = 0.8
H_MIN_CHG = 4.0
MAX_CHG = 30.0
GREEN_MIN = 2
TH_MIN = 2.0
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_tele(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except:
        pass

def get_ticker():
    try:
        r = requests.get("https://indodax.com/api/tickers", timeout=15).json()
        return r.get("tickers", {})
    except:
        return {}

def get_trades(pair, limit=10):
    try:
        url = f"https://indodax.com/api/trades/{pair}"
        r = requests.get(url, timeout=10).json()
        trades = r.get("trades", [])[:limit]
        green = 0
        for t in trades:
            if t.get("type") == "buy":
                green += 1
        return green
    except:
        return 0

def get_depth_ratio(pair):
    try:
        url = f"https://indodax.com/api/depth/{pair}"
        r = requests.get(url, timeout=10).json()
        buy_vol = sum([float(x[1]) * float(x[0]) for x in r.get("buy", [])[:10]])
        sell_vol = sum([float(x[1]) * float(x[0]) for x in r.get("sell", [])[:10]])
        if sell_vol == 0:
            return 999
        return buy_vol / sell_vol
    except:
        return 0

tickers = get_ticker()
now = datetime.datetime.now().strftime("%H:%M WIB")
hasil_segar = []
hasil_hunter = []

for pair, data in tickers.items():
    if not pair.endswith("_idr"):
        continue
    try:
        last = float(data.get("last", 0))
        low = float(data.get("low", 0))
        high = float(data.get("high", 0))
        vol_idr = float(data.get("vol_idr", 0))
        if low == 0 or last == 0:
            continue
        if vol_idr < VOL_MIN:
            continue
        chg = ((last - low) / low) * 100
        if chg < S_MIN_CHG:
            continue
        if chg > MAX_CHG:
            continue
        th = ((high - last) / last) * 100 if last > 0 else 0
        if th < TH_MIN and chg > 10:
            continue
        if th < 0:
            continue
        ratio = get_depth_ratio(pair)
        if ratio < RATIO_MIN:
            continue
        green = get_trades(pair, 10)
        need_green = GREEN_MIN
        if chg > 15:
            need_green = 3
        if green < need_green:
            continue
        if chg <= H_MIN_CHG:
            hasil_segar.append(f"Segar {pair.upper()} {chg:.2f}% Vol {vol_idr/1e9:.1f}Bn B/S {ratio:.2f}x Ijo {green}x")
        else:
            hasil_hunter.append(f"Hunter {pair.upper()} {chg:.2f}% Vol {vol_idr/1e9:.1f}Bn B/S {ratio:.2f}x Ijo {green}x")
    except:
        continue

if not hasil_segar and not hasil_hunter:
    send_tele(f"KOSONG SCAN {now} V15.3 UNIVERSAL")
else:
    msg = f"SCAN {now} V15.3 UNIVERSAL\n"
    if hasil_segar:
        msg += "\n".join(hasil_segar[:5]) + "\n"
    if hasil_hunter:
        msg += "\n".join(hasil_hunter[:5])
    send_tele(msg)

print(f"SCAN {now} Segar:{len(hasil_segar)} Hunter:{len(hasil_hunter)}")
