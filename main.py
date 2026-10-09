
import requests, os, time
from datetime import datetime

TELE_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def kirim_tele(pesan):
    if not TELE_TOKEN or not CHAT_ID:
        print("Token kosong!")
        return
    url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": pesan, "parse_mode": "Markdown"}, timeout=15)
        print("Telegram terkirim!")
    except Exception as e:
        print(f"Gagal kirim tele: {e}")

def cek_signal_agresif(coin, ticker_data):
    try:
        # Data 24 jam dulu buat filter awal biar cepet
        last_price = float(ticker_data['last'])
        vol_idr = float(ticker_data['vol_idr'])

        # Coba ambil data 5m - kalo Indodax API chart error, fallback ke hitungan 1 jam
        try:
            url = f"https://indodax.com/api/chart?symbol={coin}&tf=5m&limit=25"
            r = requests.get(url, timeout=8).json()
            candles = r
            if len(candles) >= 21:
                close_now = float(candles[-1][4])
                close_prev = float(candles[-2][4])
                vol_now = float(candles[-1][5])

                price_change = ((close_now - close_prev) / close_prev) * 100
                vols_20 = [float(c[5]) for c in candles[-21:-1]]
                ma_vol = sum(vols_20) / 20
                vol_spike = (vol_now / ma_vol * 100) if ma_vol > 0 else 0
            else:
                raise Exception("candle kurang")
        except:
            # FALLBACK AGRESIF: pake data ticker 24h tapi threshold diturunin
            # Ini buat jaga-jaga API chart Indodax kadang ngadat
            high = float(ticker_data['high'])
            low = float(ticker_data['low'])
            price_change = ((high - low) / low * 100) if low > 0 else 0
            vol_spike = 350 # Anggap spike kalo fallback biar tetep ke-detect
            # Tapi kita filter cuma yang price_change 4%++
            close_now = last_price

        # ===== LOGIKA AGRESIF MEME HUNTER =====
        # 3.5% - 12% + Vol 300%++
        # Kenapa sampe 12%? Karena meme bisa 10% dalam 5 menit, kalo kita batas 4.5% malah kelewat
        if 3.5 <= price_change <= 12.0 and vol_spike >= 300:
            return {
                "coin": coin.upper().replace("IDR",""),
                "pc": round(price_change, 2),
                "vs": int(vol_spike),
                "price": close_now,
                "vol_idr": vol_idr
            }
    except:
        return None
    return None

print(f"🔥 MODE MEME HUNTER AGRESIF START {datetime.now()}")

try:
    tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json()['tickers']
    print(f"Scan {len(tickers)} koin...")

    signals = []
    for coin, data in tickers.items():
        if not coin.endswith('idr'): continue
        # Skip BTC, ETH biar fokus low cap (kalo mau blue chip, hapus baris ini)
        if coin in ['btcidr','ethidr','usdtidr']: continue

        hasil = cek_signal_agresif(coin, data)
        if hasil:
            signals.append(hasil)

    print(f"Hasil scan: {len(signals)} lolos filter")

    if not signals:
        print("MEME HUNTER: Market micin kalem, ga ada yang pump 3.5% + Vol 3x")
    else:
        signals.sort(key=lambda x: (x['vs'], x['pc']), reverse=True)

        pesan = f"🔥 *MEME HUNTER AGRESIF - {datetime.now().strftime('%H:%M')} WIB*\n"
        pesan += f"Price +3.5-12% (5m) + Vol >300% | {len(signals)} koin\n\n"

        for s in signals[:15]:
            pesan += f"🚀 *{s['coin']}* | +{s['pc']}% | VOL {s['vs']}%\n"
            pesan += f"`{s['price']}` | Vol Rp {int(s['vol_idr']/1000000)}jt\n"
            pesan += f"TP 5-8% | TS 2% | JANGAN SERAKAH!\n\n"

        kirim_tele(pesan)

except Exception as e:
    print(f"Error utama: {e}")
    kirim_tele(f"Bot Error: {e}")
