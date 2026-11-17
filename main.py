# === V26 FINAL - V25 + BANDAR V20 BALIK LAGI ===
# V25 = BANDAR GALAK 0-3% + SPIKE 5M + BANDAR 6JAM
# V26 = + BANDAR V20 LONGGAR 3-15% BIAR STIK GAK KELEWAT LAGI!

import requests, json, os, time
from datetime import datetime, timedelta, timezone

TELE_TOKEN = os.getenv("TELE_TOKEN")
TELE_CHAT_ID = os.getenv("TELE_CHAT_ID")
WIB = timezone(timedelta(hours=7))

def send_tele(msg):
    url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TELE_CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=20)
    except Exception as e:
        print("Tele error:", e)

def load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return {}

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f)

# 1. AMBIL DATA INDODAX
try:
    r = requests.get("https://indodax.com/api/tickers", timeout=30).json()
    tickers = r.get("tickers", {})
except Exception as e:
    print("Fetch error", e)
    tickers = {}

now = datetime.now(WIB)
now_ts = now.timestamp()
now_str = now.strftime("%H:%M")

vol_hist = load_json("vol_history.json")  # {koin: [[ts, vol], ...]}
price_hist = load_json("price_history.json") # {koin: {"ts": ts, "price": price}}

bandar_galak = []  # V25 - 0-3% - ENTRY TERBAIK
bandar_v20 = []    # V26 - 3-15% - UDAH JALAN, WATCHLIST!
early = []
spike = []
all_coins = []

for pair, d in tickers.items():
    if not pair.endswith("_idr"):
        continue
    koin = pair.replace("_idr", "").upper()
    try:
        price = float(d["last"])
        vol_idr = float(d["vol_idr"])
        chg_24 = float(d.get("change_24h", 0)) if d.get("change_24h") else 0
    except:
        continue

    # Simpan vol history, keep 7 jam terakhir
    lst = vol_hist.get(koin, [])
    lst.append([now_ts, vol_idr])
    lst = [x for x in lst if now_ts - x[0] <= 7*3600]
    vol_hist[koin] = lst

    # Cari vol 6 jam lalu - ambil yang paling deket 6 jam lalu
    vol_6j_lalu = None
    for ts, v in lst:
        if now_ts - ts >= 6*3600 - 300: # toleransi 5 menit
            vol_6j_lalu = v
            break
    if vol_6j_lalu is None and len(lst) > 1:
        vol_6j_lalu = lst[0][1]
    if not vol_6j_lalu or vol_6j_lalu == 0:
        vol_ratio = 0
    else:
        vol_ratio = vol_idr / vol_6j_lalu

    # SPIKE 5 MENIT - bandingin harga 5 menit lalu
    spike_pct = 0
    prev = price_hist.get(koin)
    if prev and prev.get("price"):
        try:
            spike_pct = (price - prev["price"]) / prev["price"] * 100
        except:
            spike_pct = 0
    # Update price history buat run berikutnya
    price_hist[koin] = {"ts": now_ts, "price": price}

    # Hitung OB simpel: Pos = chg_24, OB = range harga
    # OB = low 24h - high? Kita pake aproksimasi dari chg
    ob_low = int(price * 0.97)
    ob_high = int(price * 1.00) if price > 100 else round(price * 0.97, 2)

    data = {
        "koin": koin, "price": price, "vol": vol_idr,
        "chg": chg_24, "ratio": vol_ratio, "spike": spike_pct,
        "ob": f"{ob_low}-{ob_high}"
    }
    all_coins.append(data)

    # === SPIKE 5M - UDAH NGEGAS ===
    if spike_pct >= 2.0:
        spike.append(data)

    # === BANDAR GALAK V25 - 0-3% - ENTRY TERBAIK ===
    if vol_ratio >= 3 and 0 <= chg_24 <= 3 and vol_idr >= 50000000:
        bandar_galak.append(data)
    # === BANDAR V20 V26 - 3-15% - UDAH JALAN! JANGAN SAMPE KELEWAT ===
    elif vol_ratio >= 3 and 3 < chg_24 <= 15 and vol_idr >= 50000000:
        bandar_v20.append(data)
    # === EARLY RUNNER ===
    elif 1.5 <= vol_ratio < 3 and 0 <= chg_24 <= 5:
        early.append(data)

# Sort
bandar_galak = sorted(bandar_galak, key=lambda x: x["ratio"], reverse=True)[:5]
bandar_v20 = sorted(bandar_v20, key=lambda x: x["ratio"], reverse=True)[:5]
early = sorted(early, key=lambda x: x["ratio"], reverse=True)[:5]
spike = sorted(spike, key=lambda x: x["spike"], reverse=True)[:5]

save_json("vol_history.json", vol_hist)
save_json("price_history.json", price_hist)

# 2. BIKIN PESAN TELE
msg = f"=== V26 9EX + SPIKE 5M + BANDAR 6JAM {now_str} WIB - {len(all_coins)} KOINS ===\n\n"

# SPIKE
msg += "⚡ SPIKE 5 MENIT - UDAH NGEGAS, JANGAN DIKEJAR!\n"
if spike:
    for c in spike:
        msg += f"⚡ {c['koin']} Rp{c['price']} | Spike +{c['spike']:.1f}% | 24h {c['chg']:.1f}%\n"
else:
    msg += "Belum ada spike 5 menit\n"
msg += "\n"

# BANDAR GALAK
msg += "👑 BANDAR 6JAM - ENTRY TERBAIK 0-3%!\n"
if bandar_galak:
    for c in bandar_galak:
        msg += f"👑 {c['koin']} Rp{c['price']} | Vol 6J Naik {c['ratio']:.1f}x | Harga {c['chg']:.1f}% | OB {c['ob']}\n"
else:
    msg += "Belum ada bandar galak\n"
msg += "\n"

# BANDAR V20 - YANG BARU BALIK!
msg += "👀 BANDAR V20 - UDAH JALAN 3-15%! WATCHLIST!\n"
if bandar_v20:
    for c in bandar_v20:
        msg += f"👀 {c['koin']} Rp{c['price']} | Vol 6J Naik {c['ratio']:.1f}x | Harga {c['chg']:.1f}% | OB {c['ob']} | UDAH JALAN, SIAP-SIAP!\n"
else:
    msg += "Belum ada bandar V20\n"
msg += "\n"

# EARLY
msg += "🏃 EARLY RUNNER:\n"
if early:
    for c in early:
        msg += f"🏃 {c['koin']} Rp{c['price']} | Vol {c['ratio']:.1f}x | 24h {c['chg']:.1f}%\n"
else:
    msg += "Belum ada early runner\n"

print(msg)
send_tele(msg)
