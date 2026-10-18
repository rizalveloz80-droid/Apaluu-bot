import requests, os
from datetime import datetime

# V36 - ERN DOANG YANG BLACKLIST, AIH & XR BALIK!
FORCE_BLACKLIST = set([
    "usdt_idr","usdc_idr","idrt_idr","usde_idr","xaut_idr","paxg_idr","ouros_idr",
    "btc_idr","eth_idr","xrp_idr","sol_idr","bnb_idr","gid_idr","col_idr",
    "okusd_idr","lyfel_idr","dfg_idr","inr_idr","eur_idr","indr_idr","neorpnew_idr",
    "ern_idr"
])

TELE_TOKEN = os.getenv("TELE_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
TELE_CHAT_ID = os.getenv("TELE_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID")

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT_ID:
        print("TELE_TOKEN / CHAT_ID kosong!")
        return
    try:
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        data = {"chat_id": TELE_CHAT_ID, "text": msg}
        r = requests.post(url, data=data, timeout=20)
        print(f"Telegram status: {r.status_code}")
    except Exception as e:
        print(f"Gagal kirim tele: {e}")

try:
    url_tickers = "https://indodax.com/api/tickers"
    resp = requests.get(url_tickers, timeout=20)
    tickers = resp.json()["tickers"]
    print(f"DEBUG: TICKERS {len(tickers)}")

    cands = []
    for pair, data in tickers.items():
        pl = pair.lower()
        if not pl.endswith("_idr"):
            continue
        if pl in FORCE_BLACKLIST:
            continue
        try:
            last = float(data["last"])
            low = float(data["low"])
            high = float(data["high"])
            vol = float(data["vol_idr"])
            if vol < 100000 or last == 0 or low == 0:
                continue
            dl = ((last - low) / last * 100) if last > 0 else 0
            dh = ((high - last) / last * 100) if last > 0 else 0
            if dl > 80:
                continue
            # hitung % 24h buat crosscheck (ga ada di API tickers, jadi pake rumus low aja)
            cands.append((pair.upper(), dl, dh, vol, last, low, high))
        except:
            continue

    print(f"DEBUG: CANDS {len(cands)}")

    cands.sort(key=lambda x: -x[3])

    super_t = [c for c in cands if c[3] >= 3000000000][:3]
    trend = [c for c in cands if c[1] >= 15][:5]
    gold = [c for c in cands if c[1] <= 2.5][:5]

    now = datetime.now().strftime('%H:%M')
    msg = f"V36 FIX AIH XR BALIK | {now}\n"
    msg += f"SCAN {len(tickers)} CANDS {len(cands)}\n\n"

    if super_t:
        msg += f"🚨 SUPER >3Bn ({len(super_t)}):\n"
        for c in super_t:
            vol_bn = round(c[3] / 1000000000, 2)
            msg += f"-> {c[0]} {int(c[1])}% low Vol {vol_bn}Bn\n"
        msg += "\n"

    if trend:
        msg += f"🔥 TRENDING >=15% ({len(trend)}):\n"
        for c in trend:
            msg += f"-> {c[0]} {int(c[1])}% low Vol {int(c[3]/1000000)}jt\n"
        msg += "\n"

    if gold:
        msg += f"⭐ GOLD deket low ({len(gold)}):\n"
        for c in gold:
            msg += f"-> {c[0]} {int(c[1])}% low Vol {int(c[3]/1000000)}jt\n"

    msg += f"\nICNT cek: { [c for c in cands if 'ICNT' in c[0]] }"

    print(msg)
    send_tele(msg)

except Exception as e:
    err = f"ERROR V36: {e}"
    print(err)
    send_tele(err)
