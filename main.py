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
    except:
        return 0,0

def get_trades(pair):
    try:
        r = requests.get(f"https://indodax.com/api/{pair}/trades", timeout=5).json()
        return r[:15] # 15 trade terakhir
    except:
        return []

def main():
    print("SCANNING CEPET MODE...")
    try:
        tickers = requests.get("https://indodax.com/api/tickers", timeout=10).json()['tickers']
    except Exception as e:
        print(f"Gagal ambil tickers: {e}")
        return

    for pair, t in tickers.items():
        if not pair.endswith("_idr"): continue
        try:
            last = float(t['last'])
            high = float(t['high'])
            low = float(t['low'])
            vol_idr = float(t['vol_idr'])
            # vol_btc = float(t['vol_btc']) # kalo perlu

            if vol_idr < 10000000: continue # skip yang sepi di bawah 10jt

            # === LOGIKA SEGAR: BARU NAIK, HIGH MASIH JAUH ===
            # high jauh minimal 10% di atas harga sekarang = masih segar, bukan pucuk
            if high == 0: continue
            jarak_high = (high - last) / high * 100
            if jarak_high < 8: continue # kalo udah deket high (pucuk) skip

            # === LOGIKA NO DROP: CEK 15 TRADE TERAKHIR, JANGAN ADA NYELAM DALEM ===
            trades = get_trades(pair)
            drop = False
            for tr in trades:
                price = float(tr['price'])
                # kalo ada trade yang anjlok >3% dari harga sekarang = pernah drop
                if price < last * 0.97:
                    drop = True
                    break
            if drop: continue

            # === LOGIKA HUNTER: BUY DOMINAN ===
            buy_vol, sell_vol = get_depth(pair)
            if sell_vol == 0: continue
            ratio = buy_vol / sell_vol
            if ratio < 2.0: continue # hunter minimal buy 2x sell

            # LOLOS SEMUA = KIRIM TELE
            coin = pair.replace("_idr","").upper()
            pesan = f"🔥 *HUNTER SEGAR* 🔥\n\n💰 {coin}/IDR\n📈 Last: {last}\n🚀 High: {high} (jauh {jarak_high:.1f}%)\n💵 Vol: Rp {vol_idr:,.0f}\n⚖️ Buy/Sell: {ratio:.2f}x\n✅ No Drop"
            print(pesan)
            send_tele(pesan)
            time.sleep(0.5) # jeda biar ga spam tele

        except: continue

    print("SELESAI CEPET!")

if __name__ == "__main__":
    main()
