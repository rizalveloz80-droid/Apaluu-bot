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
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except: pass

# ambil ticker 1x aja
try:
    tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json().get("tickers", {})
except:
    tickers = {}

now = datetime.datetime.now().strftime("%H:%M WIB")

# FILTER 1: saring dulu pake ticker aja biar cepet
candidates = []
for pair, data in tickers.items():
    if not pair.endswith("_idr"): continue
    try:
        last = float(data.get("last", 0))
        low = float(data.get("low", 0))
        high = float(data.get("high", 0))
        vol_idr = float(data.get("vol_idr", 0))
        if low == 0 or last == 0: continue
        if vol_idr < VOL_MIN: continue
        chg = ((last - low) / low) * 100
        if chg < S_MIN_CHG or chg > MAX_CHG: continue
        th = ((high - last) / last) * 100 if last>0 else 0
        if th < 0: continue
        if th < TH_MIN and chg > 10: continue
        candidates.append((pair, chg, vol_idr, last, th))
    except: continue

# urutkan vol terbesar, ambil 30 teratas aja biar ga muter lama
candidates = sorted(candidates, key=lambda x: x[2], reverse=True)[:30]

hasil_segar = []
hasil_hunter = []

# FILTER 2: baru cek depth & trades cuma 30 koin ini aja
for pair, chg, vol_idr, last, th in candidates:
    try:
        # cek depth
        r = requests.get(f"https://indodax.com/api/depth/{pair}", timeout=8).json()
        buy_vol = sum([float(x[1])*float(x[0]) for x in r.get("buy", [])[:10]])
        sell_vol = sum([float(x[1])*float(x[0]) for x in r.get("sell", [])[:10]])
        ratio = 999 if sell_vol==0 else buy_vol/sell_vol
        if ratio < RATIO_MIN: continue

        # cek trades ijo
        tr = requests.get(f"https://indodax.com/api/trades/{pair}", timeout=8).json().get("trades", [])[:10]
        green = sum(1 for t in tr if t.get("type")=="buy")
        need = 3 if chg > 15 else GREEN_MIN
        if green < need: continue

        txt = f"{pair.upper()} {chg:.2f}% Vol {vol_idr/1e9:.1f}Bn B/S {ratio:.2f}x Ijo {green}x"
        if chg <= H_MIN_CHG:
            hasil_segar.append(f"Segar {txt}")
        else:
            hasil_hunter.append(f"Hunter {txt}")
    except:
        continue

if not hasil_segar and not hasil_hunter:
    send_tele(f"KOSONG SCAN {now} V15.3 LIGHT - cek {len(candidates)} koin")
else:
    msg = f"SCAN {now} V15.3 LIGHT\n"
    if hasil_segar:
        msg += "\n".join(hasil_segar[:5]) + "\n"
    if hasil_hunter:
        msg += "\n".join(hasil_hunter[:5])
    send_tele(msg)

print(f"SCAN {now} candidates:{len(candidates)} segar:{len(hasil_segar)} hunter:{len(hasil_hunter)}")
