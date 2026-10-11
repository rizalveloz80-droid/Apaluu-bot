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

# === FILTER V5.3 KETAT 5% ===
MIN_PRICE = 50
EXCLUDE = {"BTC","HYPE","PEPE","PENGU","SOL","ETH","BNB","XRP","DOGE","SHIB","ADA","AVAX","DOT","LINK","TRX","MATIC","LTC","BCH","ETC"}
MAX_TURUN_DARI_HIGH = 5.0 # Turun >5% dari High = SKIP! ANTI PUCUK!
# ============================

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

            if turun_high > MAX_TURUN_DARI_HIGH:
                continue

            if coin=='ONT' and jarak_low>=1:
                selesai.insert(0, f"✅ ONT/IDR {hrp} Jarak {jarak_low:.1f}% Vol {vol_mn:.0f}Mn - WAJIB IJO")
                trending['ONT'] = (999, f"🚀 ONT/IDR {hrp} +{jarak_low:.1f}% - WAJIB IJO")
                continue

            if 1.0 <= jarak_low <= 6.0 and vol_mn>30:
                selesai.append(f"✅ {coin}/IDR {hrp} Jarak {jarak_low:.1f}%")

            if jarak_low>=8 and vol_mn>10:
                trending[coin] = (jarak_low, f"🚀 {coin}/IDR {hrp} +{jarak_low:.1f}%")

        except: continue

    jam = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%H:%M WIB")
    trend_list = sorted(trending.values(), key=lambda x: x[0], reverse=True)

    if not selesai and not trend_list:
        msg = f"🔍 V5.3 SCAN {jam} - DIAM (Semua udah turun >5% dari pucuk)"
    else:
        msg = f"🔥 V5.3 ANTI-PUCUK 5% {jam}\n\n"
        if selesai: msg += "📈 SELESAI KOREKSI:\n" + "\n".join(selesai[:7]) + "\n\n"
        if trend_list: msg += "🚀 IJO ONLY:\n" + "\n".join([x[1] for x in trend_list[:7]])

    print(msg)
    if selesai or trend_list:
        send(msg)
    else:
        print("Tidak ada sinyal valid, tidak kirim")

except Exception as e:
    print(f"ERROR {e}")
    send(f"Error V5.3: {e}")
