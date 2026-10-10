import requests
import os
from datetime import datetime
import pytz

# Ambil token dari GitHub Secrets
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or os.getenv("CHAT_ID")

def kirim_tele(pesan):
    if not BOT_TOKEN or not CHAT_ID:
        print("TOKEN/CHAT_ID KOSONG!")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": pesan, "parse_mode": "HTML"}
    try:
        r = requests.post(url, data=data, timeout=15)
        print(f"KIRIM: {r.status_code} - {r.text[:100]}")
    except Exception as e:
        print(f"Gagal kirim tele: {e}")

def scan():
    wib = pytz.timezone("Asia/Jakarta")
    jam = datetime.now(wib).strftime("%H:%M WIB %d-%m")

    try:
        # Ambil ticker 24h Binance
        print("Ambil data Binance...")
        res = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=20)
        data = res.json()

        # Filter USDT dan bukan stable
        blacklist = ["USDC", "FDUSD", "TUSD", "USDP", "DAI", "BUSD"]
        filtered = []
        for d in data:
            sym = d['symbol']
            if not sym.endswith("USDT"): continue
            coin = sym.replace("USDT","")
            if coin in blacklist: continue
            try:
                price = float(d['lastPrice'])
                vol = float(d['quoteVolume'])
                change = float(d['priceChangePercent'])
                if vol < 5000000: continue # minimal 5jt USDT volume
                if price == 0: continue
                filtered.append((coin, vol, change, price, sym))
            except: continue

        # Urutkan by volume tertinggi = borongan
        filtered.sort(key=lambda x: x[1], reverse=True)
        top7 = filtered[:7]

        if not top7:
            print("Tidak ada koin")
            return []

        hasil = []
        for coin, vol, change, price, sym in top7:
            hasil.append(f"• {coin} | Vol: ${vol/1000000:.1f}M | {change:+.1f}%")

        return hasil, jam

    except Exception as e:
        print(f"Error scan: {e}")
        return [], jam

# JALANKAN
hasil_jam = scan()
if not hasil_jam[0]:
    hasil, jam = [], ""
else:
    hasil, jam = hasil_jam

if hasil:
    pesan = f"🚨 <b>TOP 7 BORONGAN {jam}</b>\n\n" + "\n".join(hasil) + "\n\nBy: Bot Auto 5min"
    kirim_tele(pesan)
    print(f"SELESAI KIRIM {len(hasil)} koin")
else:
    # Tetap kirim biar lu tau bot hidup walaupun ga ada koin
    wib = pytz.timezone("Asia/Jakarta")
    jam = datetime.now(wib).strftime("%H:%M WIB")
    kirim_tele(f"🤖 Bot hidup {jam} - Scan 0, market sepi, next 5 menit lagi")
    print("Kirim info hidup")
