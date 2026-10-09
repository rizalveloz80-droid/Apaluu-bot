
import requests
import time

TOKEN = "8675452184:AAHlWcaNYQg62ioe3p3yI1wUO5zXMyFBkVw"
CHAT_ID = "213453765"

def kirim_tele(pesan):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": pesan, "parse_mode": "Markdown"}
        requests.post(url, data=data, timeout=15)
    except Exception as e:
        print(f"Gagal kirim: {e}")

def cek_all_signal():
    try:
        r = requests.get("https://indodax.com/api/tickers", timeout=10).json()
        tickers = r.get("tickers", {})

        signals = []
        for pair, data in tickers.items():
            if not pair.endswith("_idr"): continue
            try:
                last = float(data.get("last", 0))
                vol_idr = float(data.get("vol_idr", 0))
                high = float(data.get("high", 0))
                low = float(data.get("low", 0))
                if low == 0: continue
                change = (last - low) / low * 100

                if vol_idr > 500_000_000:
                    signals.append(f"🔥 {pair.upper()} Vol Rp{vol_idr/1e9:.2f}M - {last}")
                if change > 5:
                    signals.append(f"📈 {pair.upper()} PUMP +{change:.1f}% - {last}")
                if high > 0 and ((high-last)/high*100) < 2 and change > 3:
                    signals.append(f"🚀 {pair.upper()} BREAKOUT dekat High {high}!")
            except: continue

        # Cek order book TIA khusus kayak di gambar kamu
        try:
            depth = requests.get("https://indodax.com/api/tia_idr/depth", timeout=10).json()
            asks = depth.get("asks", [])[:3]
            if asks:
                total_wall = sum(float(a[0])*float(a[1]) for a in asks)
                if total_wall > 50_000_000:
                    signals.append(f"🧱 TIA Tembok Jual Rp{total_wall/1e6:.0f}jt di {asks[0][0]}")
        except: pass

        jam = time.strftime("%H:%M")
        if signals:
            pesan = f"📊 *ALL SIGNAL {jam}*\n\n" + "\n".join(signals[:20])
            kirim_tele(pesan)
        else:
            kirim_tele(f"✅ Market kalem {jam} - Bot cek semua signal jalan min!")

    except Exception as e:
        print(f"Error: {e}")

print("BOT ALL SIGNAL NYALA!")
kirim_tele("🤖 *BOT ALL SIGNAL NYALA!*\nNgecek Volume, Pump, Breakout semua koin IDR tiap 5 menit min!")

while True:
    cek_all_signal()
    time.sleep(300)
