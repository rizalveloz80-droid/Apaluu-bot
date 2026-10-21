import requests
import os
import time

TELE_TOKEN = os.getenv("TELE_TOKEN")
TELE_CHAT_ID = os.getenv("TELE_CHAT_ID")

def send_tele(msg):
    try:
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELE_CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except: pass

def get_depth(pair):
    try:
        r = requests.get(f"https://indodax.com/api/{pair}/depth", timeout=5).json()
        buy = sum(float(x[0])*float(x[1]) for x in r.get('buy', [])[:30])
        sell = sum(float(x[0])*float(x[1]) for x in r.get('sell', [])[:30])
        return buy, sell
    except: return 0,0

def main():
    print("BOT 2 MODE ANTI DUMP JALAN...")
    try:
        tickers = requests.get("https://indodax.com/api/tickers", timeout=10).json()['tickers']
    except Exception as e:
        print(f"Gagal tickers: {e}")
        return

    for pair, t in tickers.items():
        if not pair.endswith("_idr"): continue
        try:
            last = float(t['last'])
            high = float(t['high'])
            low = float(t['low'])
            vol_idr = float(t['vol_idr'])
            if low == 0 or high == 0: continue
            coin = pair.replace("_idr","").upper()

            try: change = float(t.get('change','0') or 0)
            except: change = 0

            # ========== MODE 1: HUNTER SEGAR (BUAT SIANG) ==========
            jarak_high = (high - last) / high * 100 if high>0 else 0
            if vol_idr > 10000000 and jarak_high > 8:
                buy, sell = get_depth(pair)
                if sell > 0 and buy / sell >= 2.0:
                    send_tele(f"🔥 *HUNTER SEGAR*\n\n💰 {coin}/IDR\n📈 Last: {last}\n🚀 Jauh High: {jarak_high:.1f}%\n⚖️ Buy/Sell: {buy/sell:.2f}x\n💵 Vol: Rp {vol_idr:,.0f}")
                    time.sleep(0.5)

            # ========== MODE 2: MANTUL OVERNIGHT ANTI DUMP (TIPE SHOW/SN/ICNT LU) ==========
            posisi_dari_low = (last - low) / low * 100 if low>0 else 999
            
            # SYARAT ANTI DUMP:
            if -25 <= change <= -4 and 5 <= posisi_dari_low <= 18 and vol_idr > 80000000:
                buy, sell = get_depth(pair)
                if sell == 0: continue
                ratio = buy / sell
                if not (1.3 <= ratio <= 5.0): continue # skip fake wall

                # CEK 10 TRADE TERAKHIR HARUS BANYAK YANG NAIK
                try:
                    trades = requests.get(f"https://indodax.com/api/{pair}/trades", timeout=4).json()[:10]
                    naik = 0
                    for i in range(len(trades)-1):
                        if float(trades[i]['price']) >= float(trades[i+1]['price']):
                            naik += 1
                    if naik >= 5: # minimal 5 dari 10 trade naik = konfirm mantul
                        send_tele(f"🌙 *MANTUL AMAN (TIPE SHOW/SN)*\n\n💰 {coin}/IDR\n📉 24h: {change}%\n📍 Last: {last} (Low: {low})\n✅ Mantul {posisi_dari_low:.1f}% dari low\n⚖️ Buy/Sell: {ratio:.2f}x\n📈 Trade ijo: {naik}/10\n💵 Vol: Rp {vol_idr:,.0f}\n👉 Entry aman, hold pagi")
                        time.sleep(0.5)
                except: pass

        except: continue

    print("SELESAI AMAN!")

if __name__ == "__main__":
    main()
