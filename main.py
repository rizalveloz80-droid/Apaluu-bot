import requests
import time
from datetime import datetime, timezone, timedelta

TOKEN = "8675452184:AAHlWcaNYQg62ioe3p3yI1wUO5zXMyFBkVw"
CHAT_ID = "213453765"
WIB = timezone(timedelta(hours=7))

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
                if low == 0 or last == 0: continue

                change = (last - low) / low * 100

                # V2 FILTER KETAT
                if vol_idr > 1_000_000_000: # Cuma Vol diatas 1 Miliar
                    signals.append((vol_idr, f"🔥 {pair.upper()} Vol Rp{vol_idr/1e9:.2f}M - {last:,.0f}"))

                if change > 6: # Cuma PUMP diatas 6%
                    signals.append((change, f"📈 {pair.upper()} PUMP +{change:.1f}% - {last:,.0f}"))

                if high > 0 and ((high-last)/high*100) < 2.5 and change > 4:
                    signals.append((change+20, f"🚀 {pair.upper()} BREAKOUT dekat High {high:,.0f}! Last {last:,.0f}"))

            except: continue

        # Sort dari yang paling panas
        signals.sort(key=lambda x: x[0], reverse=True)

        jam = datetime.now(WIB).strftime("%H:%M WIB")

        if signals:
            top_signals = [s[1] for s in signals[:10]] # Cuma Top 10
            pesan = f"📊 *ALL SIGNAL {jam} - TOP 10 TERPANAS*\n\n" + "\n".join(top_signals)
            kirim_tele(pesan)
        else:
            kirim_tele(f"✅ Market kalem {jam} - Gak ada pump gede min, bot tetep jagain!")

    except Exception as e:
        print(f"Error: {e}")

print("BOT ALL SIGNAL V2 NYALA!")
kirim_tele("🤖 *BOT V2 NYALA!*\nFilter ketat: Vol >1M, Pump >6%, Top 10 aja biar gak spam! Jam WIB udah bener min!")

while True:
    cek_all_signal()
    time.sleep(300)
