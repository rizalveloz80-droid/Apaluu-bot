import requests, os, datetime

BOT = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('TELEGRAM_TOKEN') or os.getenv('BOT_TOKEN')
CHAT = os.getenv('TELEGRAM_CHAT_ID') or os.getenv('CHAT_ID') or os.getenv('TELEGRAM_CHAT')

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT}/sendMessage", data={"chat_id": CHAT, "text": msg})
    except:
        pass

MIN_PRICE = 50
EXCLUDE = {"BTC","HYPE","PEPE","PENGU","SOL","ETH","BNB","XRP","DOGE","SHIB","ADA","AVAX","DOT","LINK","TRX","MATIC","LTC","BCH","ETC"}

try:
    r = requests.get("https://indodax.com/api/tickers", timeout=15).json()
    tickers = r.get('tickers', {})
    serok = []
    selesai = []
    trending = {}

    for pair, d in tickers.items():
        if not pair.endswith('_idr'):
            continue
        try:
            last = float(d['last'])
            low = float(d['low'])
            high = float(d['high'])
            vol_idr = float(d.get('vol_idr', 0))
            if low==0 or high==0 or last < MIN_PRICE:
                continue
            coin = pair.replace('_idr','').upper()
            if coin in EXCLUDE:
                continue

            vol_mn = vol_idr/1_000_000
            hrp = f"Rp{last:,.0f}".replace(',', '.')
            jarak_low = (last-low)/low*100
            turun_high = (high-last)/high*100

            # ANTI PUCUK - RSI 75+ SKIP
            if turun_high < 0.5:
                continue
            if turun_high > 5.0:
                continue

            sl = last * 0.98
            tp = last * 1.04
            sl_hrp = f"Rp{sl:,.0f}".replace(',', '.')
            tp_hrp = f"Rp{tp:,.0f}".replace(',', '.')

            # MODE 1: SEROK BAWAH - Vol harus 40jt (baru mau naik)
            if 0.5 <= jarak_low <= 3.0 and 1.0 <= turun_high <= 3.5 and vol_mn > 40:
                serok.append(f"🎯 {coin} {hrp} -{turun_high:.1f}% Vol:{vol_mn:.0f}jt SL:{sl_hrp} TP:{tp_hrp}")

            # MODE 2: SELESAI KOREKSI - Vol boleh 30jt
            elif 1.0 <= jarak_low <= 6.0 and 0.5 <= turun_high <= 5.0 and vol_mn > 30:
                selesai.append(f"✅ {coin} {hrp} -{turun_high:.1f}% Vol:{vol_mn:.0f}jt SL:{sl_hrp} TP:{tp_hrp}")

            # MODE 3: IJO ONLY
            elif jarak_low>=8 and turun_high <= 3.0 and vol_mn > 15:
                trending[coin] = (jarak_low, f"🚀 {coin} {hrp} +{jarak_low:.1f}% JANGAN KEJAR")

        except:
            continue

    jam = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%H:%M WIB")
    trend_list = sorted(trending.values(), key=lambda x: x[0], reverse=True)

    msg = f"🤖 V6 FINAL 40/30 {jam}\nAnti Pucuk + Risk 1:2\n\n"
    if serok:
        msg += f"🎯 SEROK BAWAH (40jt+):\n" + "\n".join(serok[:5]) + "\n\n"
    if selesai:
        msg += f"📈 SELESAI KOREKSI (30jt+):\n" + "\n".join(selesai[:5]) + "\n\n"
    if trend_list:
        msg += f"🚀 IJO OVERBOUGHT:\n" + "\n".join([x[1] for x in trend_list[:3]])

    if serok or selesai:
        print(msg)
        send(msg)
    else:
        print("DIAM - Ga ada sinyal 40/30")

except Exception as e:
    send(f"Error V6: {e}")
