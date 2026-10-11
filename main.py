import requests, os, datetime

# BACA 2 VERSI NAMA BIAR GA BINGUNG LAGI
BOT = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('TELEGRAM_TOKEN') or os.getenv('BOT_TOKEN')
CHAT = os.getenv('TELEGRAM_CHAT_ID') or os.getenv('CHAT_ID') or os.getenv('TELEGRAM_CHAT')

print(f"TOKEN ADA: {bool(BOT)} CHAT ADA: {bool(CHAT)}")

def send(msg):
    try:
        r = requests.post(f"https://api.telegram.org/bot{BOT}/sendMessage", data={"chat_id": CHAT, "text": msg})
        print(f"TELEGRAM STATUS: {r.status_code}")
        print(r.text[:500])
    except Exception as e:
        print(f"ERROR KIRIM: {e}")

# === FILTER BARU V5.2 ===
MIN_PRICE = 50 # Filter receh < Rp50
EXCLUDE = {"BTC","HYPE","PEPE","PENGU","SOL","ETH","BNB","XRP","DOGE","SHIB","ADA","AVAX","DOT","LINK","TRX","MATIC","LTC","BCH","ETC"} # Coin hold lu - ONT TIDAK DI FILTER
# ========================

try:
    r = requests.get("https://indodax.com/api/tickers", timeout=15).json()
    tickers = r.get('tickers', {})
    selesai = []
    trending = {}

    for pair, d in tickers.items():
        if not pair.endswith('_idr'): continue
        try:
            last = float(d['last']); low = float(d['low']); vol_idr = float(d.get('vol_idr', 0))
            if low==0: continue

            # === FILTER 1: HARGA RECEH ===
            if last < MIN_PRICE: continue

            vol_mn = vol_idr/1_000_000
            coin = pair.replace('_idr','').upper()
            hrp = f"Rp{last:,.0f}".replace(',', '.')

            # === FILTER 2: COIN HOLD (KECUALI ONT) ===
            if coin in EXCLUDE: continue

            jarak = (last-low)/low*100

            if coin=='ONT' and jarak>=1:
                selesai.insert(0, f"✅ ONT/IDR {hrp} Jarak {jarak:.1f}% Vol {vol_mn:.0f}Mn - WAJIB IJO")
                trending['ONT'] = (999, f"🚀 ONT/IDR {hrp} +{jarak:.1f}% - WAJIB IJO")
                continue

            if 1.0 <= jarak <= 6.0 and vol_mn>30:
                selesai.append(f"✅ {coin}/IDR {hrp} Jarak {jarak:.1f}%")

            if jarak>=8 and vol_mn>10:
                trending[coin] = (jarak, f"🚀 {coin}/IDR {hrp} +{jarak:.1f}%")

        except: continue

    jam = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%H:%M WIB")
    trend_list = sorted(trending.values(), key=lambda x: x[0], reverse=True)

    if not selesai and not trend_list:
        msg = f"🔍 V5.1 SCAN {jam} - DIAM"
    else:
        msg = f"🔥 V5.1 BULLISH {jam}\n\n"
        if selesai: msg += "📈 SELESAI KOREKSI:\n" + "\n".join(selesai[:7]) + "\n\n"
        if trend_list: msg += "🚀 IJO ONLY:\n" + "\n".join([x[1] for x in trend_list[:7]])

    print(msg)
    if selesai or trend_list:
        send(msg)
    else:
        print("Tidak ada sinyal, tidak kirim telegram")
        # send(msg) # kalo mau tetap kirim DIAM, uncomment

except Exception as e:
    print(f"ERROR {e}")
    send(f"Error: {e}")
