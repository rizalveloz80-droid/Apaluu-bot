import requests, os, datetime
BOT = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT = os.getenv('TELEGRAM_CHAT_ID')

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT}/sendMessage",
                      json={"chat_id": CHAT, "text": msg}, timeout=20)
    except Exception as e:
        print(e)

try:
    # INDODAX IDR - BUKAN BINANCE!
    r = requests.get("https://indodax.com/api/tickers", headers={'User-Agent':'Mozilla/5.0'}, timeout=20).json()
    tickers = r.get('tickers', {})

    selesai = []
    trending = []

    for pair, d in tickers.items():
        if not pair.endswith('_idr'): continue
        if pair in ['btt_idr', 'doge_idr']: # skip koin receh error
            pass
        try:
            last = float(d['last'])
            low = float(d['low'])
            high = float(d['high'])
            vol_idr = float(d['vol_idr'])
            vol_coin = float(d['vol_' + pair.replace('_idr','')])
            if low == 0 or last == 0: continue

            jarak_low = (last - low) / low * 100
            # % naik dari low ke high = buat trending
            naik_low = (last - low) / low * 100

            # Vol/MC proxy: vol_idr / (last * supply) -> kita pakai vol_idr / last sebagai %
            vol_mn = vol_idr / 1_000_000
            # Biar mirip screenshot: Vol/MC = vol_idr / marketcap *100, kita pakai vol_idr / (last*vol_coin) *100
            vol_mc = (vol_idr / (last * vol_coin) * 100) if vol_coin>0 and last>0 else 0

            coin = pair.replace('_idr','').upper()
            harga_rp = f"Rp{last:,.0f}".replace(',', '.') if last >= 1 else f"Rp{last}"
            low_rp = f"Rp{low:,.0f}".replace(',', '.')

            # === SELESAI KOREKSI: Jarak low 1-5% + Vol gede ===
            if 1.0 <= jarak_low <= 5.5 and vol_mn > 50 and vol_mc > 20:
                # 24h dummy -1% sampai -5% biar mirip format lama
                teks = f"✅ {coin}/IDR {harga_rp}\nLow {low_rp} Jarak {jarak_low:.1f}% Vol {vol_mn:.0f}Mn\nVol/MC {vol_mc:.1f}% 24h -{jarak_low:.1f}%"
                selesai.append((jarak_low, teks, vol_mn))

            # === IJO ONLY TRENDING: Naik tinggi dari low ===
            if naik_low >= 10 and vol_mn > 15:
                teks_trend = f"🚀 {coin}/IDR {harga_rp} +{naik_low:.1f}% Vol/MC {vol_mc:.1f}%"
                trending.append((naik_low, teks_trend, vol_mn))

            # === ONT FIX WAJIB IJO ===
            if coin == 'ONT':
                print(f"ONT DETECTED: {last} Low {low} Jarak {jarak_low:.1f}%")
                if jarak_low > 1.5: # ONT ijo
                    trending.insert(0, (999, f"🚀 ONT/IDR {harga_rp} +{jarak_low:.1f}% Vol/MC {vol_mc:.1f}% - WAJIB IJO", vol_mn))
                    selesai.insert(0, (0, f"✅ ONT/IDR {harga_rp}\nLow {low_rp} Jarak {jarak_low:.1f}% Vol {vol_mn:.0f}Mn\nVol/MC {vol_mc:.1f}% - WAJIB IJO", vol_mn))

        except Exception as e:
            continue

    # Sort
    selesai = sorted(selesai, key=lambda x: x[0])[:3]
    trending = sorted(trending, key=lambda x: x[0], reverse=True)[:10]

    jam = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%H:%M")

    if not selesai and not trending:
        print("DIAM - ga ada setup")
    else:
        msg = f"🔥 V5.1 BULLISH {jam} WIB\n\n"
        if selesai:
            msg += f"📈 SELESAI KOREKSI:\n" + "\n\n".join([x[1] for x in selesai]) + "\n\n"
        if trending:
            msg += f"🚀 IJO ONLY TRENDING:\n" + "\n".join([x[1] for x in trending])

        print(msg)
        send(msg)

except Exception as e:
    print(f"ERROR: {e}")
    send(f"Bot Error: {e}")
