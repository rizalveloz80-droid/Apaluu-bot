import requests, os, datetime

BOT = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('TELEGRAM_TOKEN') or os.getenv('BOT_TOKEN')
CHAT = os.getenv('TELEGRAM_CHAT_ID') or os.getenv('CHAT_ID') or os.getenv('TELEGRAM_CHAT')
print(f"TOKEN ADA: {bool(BOT)} CHAT ADA: {bool(CHAT)}")

def send(msg):
    try:
        r = requests.post(f"https://api.telegram.org/bot{BOT}/sendMessage", data={"chat_id": CHAT, "text": msg})
        print(f"TELEGRAM STATUS: {r.status_code}")
    except Exception as e:
        print(f"ERROR: {e}")

# === FILTER V5.4 ANTI BELI PUCUK PAS ===
MIN_PRICE = 50
EXCLUDE = {"BTC","HYPE","PEPE","PENGU","SOL","ETH","BNB","XRP","DOGE","SHIB","ADA","AVAX","DOT","LINK","TRX","MATIC","LTC","BCH","ETC"}
MAX_TURUN_DARI_HIGH = 5.0
MIN_TURUN_SELESAI_KOREKSI = 0.5 # Harus udah turun minimal 0.5% dari High, biar ga beli pas pucuk pas!
# =======================================

try:
    r = requests.get("https://indodax.com/api/tickers", timeout=15).json()
    tickers = r.get('tickers', {})
    selesai = []
    trending = {}

    for pair, d in tickers.items():
        if not pair.endswith('_idr'): continue
        try:
            last = float(d['last']); low = float(d['low']); high = float(d['high']); vol_idr = float(d.get('vol_idr', 0))
            if low==0 or high==0: continue
            if last < MIN_PRICE: continue

            coin = pair.replace('_idr','').upper()
            if coin in EXCLUDE: continue

            vol_mn = vol_idr/1_000_000
            hrp = f"Rp{last:,.0f}".replace(',', '.')

            jarak_low = (last-low)/low*100
            turun_high = (high-last)/high*100

            # FILTER 1: Kalo udah junam >5% dari High, SKIP SEMUA!
            if turun_high > MAX_TURUN_DARI_HIGH:
                continue

            if coin=='ONT' and jarak_low>=1:
                # ONT wajib lolos tapi tetap harus ga pas di pucuk
                if turun_high >= MIN_TURUN_SELESAI_KOREKSI:
                    selesai.insert(0, f"✅ ONT/IDR {hrp} Jarak {jarak_low:.1f}% Vol {vol_mn:.0f}Mn - WAJIB IJO")
                continue

            # FILTER 2: SELESAI KOREKSI = Harus udah turun 0.5% - 5% dari High (JANGAN PAS DI HIGH!)
            if 1.0 <= jarak_low <= 6.0 and vol_mn>30:
                if MIN_TURUN_SELESAI_KOREKSI <= turun_high <= MAX_TURUN_DARI_HIGH:
                    selesai.append(f"✅ {coin}/IDR {hrp} Jarak {jarak_low:.1f}% Turun {turun_high:.1f}% dr High")

            # FILTER 3: IJO ONLY = Masih deket High (boleh 0% - 5%)
            if jarak_low>=8 and vol_mn>10:
                if turun_high <= MAX_TURUN_DARI_HIGH:
                    trending[coin] = (jarak_low, f"🚀 {coin}/IDR {hrp} +{jarak_low:.1f}%")

        except: continue

    jam = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%H:%M WIB")
    trend_list = sorted(trending.values(), key=lambda x: x[0], reverse=True)

    if not selesai and not trend_list:
        msg = f"🔍 V5.4 SCAN {jam} - DIAM (Semua masih di pucuk pas atau udah junam)"
    else:
        msg = f"🔥 V5.4 ANTI-PUCUK PAS {jam}\n\n"
        if selesai: msg += "📈 SELESAI KOREKSI (Udah turun dikit, aman entri):\n" + "\n".join(selesai[:7]) + "\n\n"
        if trend_list: msg += "🚀 IJO ONLY:\n" + "\n".join([x[1] for x in trend_list[:7]])

    print(msg)
    if selesai or trend_list:
        send(msg)
    else:
        print("Tidak ada sinyal valid, tidak kirim")

except Exception as e:
    print(f"ERROR {e}")
    send(f"Error V5.4: {e}")
