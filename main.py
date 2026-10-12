import requests, os, datetime, time

BOT = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('TELEGRAM_TOKEN') or os.getenv('BOT_TOKEN')
CHAT = os.getenv('TELEGRAM_CHAT_ID') or os.getenv('CHAT_ID') or os.getenv('TELEGRAM_CHAT')

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT}/sendMessage", data={"chat_id": CHAT, "text": msg}, timeout=10)
    except Exception as e:
        print(f"Gagal send: {e}")

def get_ema(prices, period):
    k = 2 / (period + 1)
    ema = prices[0]
    for p in prices[1:]:
        ema = p * k + ema * (1-k)
    return ema

try:
    r = requests.get("https://indodax.com/api/tickers", timeout=20).json()
    tickers = r.get('tickers', {})

    all_coins = []
    for pair, d in tickers.items():
        if not pair.endswith('_idr'): continue
        try:
            vol_mn = float(str(d.get('vol_idr','0')))/1_000_000
            if vol_mn < 15: continue # LONGGARIN dari 35jt ke 15jt!
            last = float(d['last'])
            low = float(d['low'])
            high = float(d['high'])
            if last < 5: continue
            coin = pair.replace('_idr','').upper()
            if coin in {"BTC","ETH","USDT"}: continue
            chg = ((last-low)/low*100) if low else 0
            drop_high = ((high-last)/high*100) if high else 0
            near_low = ((last-low)/low*100) if low else 0
            all_coins.append((vol_mn, chg, coin, last, low, high, drop_high, near_low))
        except: continue

    early = []
    koreksi = []
    bottom = []
    trending = []

    now = int(time.time())
    from_ts = now - (60*3600)

    for vol_mn, chg, coin, last, low, high, drop_high, near_low in sorted(all_coins, key=lambda x: x[0], reverse=True)[:120]:
        try:
            url = f"https://indodax.com/tradingview/history?symbol={coin}IDR&resolution=15&from={from_ts}&to={now}"
            hist = requests.get(url, timeout=8).json()
            closes = hist.get('c', [])
            if len(closes) < 20: continue
            ema9 = get_ema(closes[-9:], 9)
            ema21 = get_ema(closes[-21:], 21)
            hrp = f"Rp{last:,.0f}".replace(',', '.')

            # 1. ENTRY DULUAN - LONGGARIN
            if 1.5 <= chg <= 18 and ema9 > ema21*0.995:
                early.append((vol_mn, f"⚡ {coin} {hrp} +{chg:.1f}% V:{vol_mn:.0f}jt"))

            # 2. SELESAI KOREKSI - INI YANG LU CARI MIN!
            if 3 <= drop_high <= 15 and chg >= 1 and vol_mn > 15:
                koreksi.append((vol_mn, f"✅ {coin} {hrp} -{drop_high:.1f}% dari high, masih +{chg:.1f}% Vol:{vol_mn:.0f}jt - SEROK KOREKSI"))

            # 3. SEROK BOTTOM - LONGGARIN BANGET
            if near_low <= 8 and drop_high >= 3:
                bottom.append((vol_mn, f"💎 {coin} {hrp} dekat low +{near_low:.1f}% drop -{drop_high:.1f}% V:{vol_mn:.0f}jt - BOTTOM"))

            # 4. TRENDING
            if chg >= 15:
                trending.append((chg, f"🚀 {coin} +{chg:.0f}% {hrp}"))

        except: continue

    jam = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%H:%M WIB")
    msg = f"🤖 V10.1 LOOSE {jam}\nScan {len(all_coins)} koin Vol>15jt\n"

    msg += f"\n⚡ ENTRY DULUAN (+1.5-18%): {len(early)} koin\n"
    msg += "\n".join([x[1] for x in sorted(early, reverse=True)[:4]]) if early else "Belum ada"

    msg += f"\n\n✅ SELESAI KOREKSI: {len(koreksi)} koin\n"
    msg += "\n".join([x[1] for x in sorted(koreksi, reverse=True)[:5]]) if koreksi else "Belum ada yang koreksi"

    msg += f"\n\n💎 SEROK BOTTOM: {len(bottom)} koin\n"
    msg += "\n".join([x[1] for x in sorted(bottom, reverse=True)[:5]]) if bottom else "Belum ada bottom"

    if trending:
        msg += "\n\n🚀 UDAH TRENDING:\n" + "\n".join([x[1] for x in sorted(trending, reverse=True)[:4]])

    print(msg)
    send(msg)

except Exception as e:
    err = f"Error V10.1: {e}"
    print(err)
    send(err)
