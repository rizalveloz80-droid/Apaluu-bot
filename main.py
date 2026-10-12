import requests, os
from datetime import datetime

TELE_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_tele(msg):
    try:
        if not TELE_TOKEN or not CHAT_ID: return
        # Potong jadi 3500 biar ga kepanjangan
        for i in range(0, len(msg), 3500):
            chunk = msg[i:i+3500]
            requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",
                          json={"chat_id": CHAT_ID, "text": chunk}, timeout=15)
    except Exception as e:
        print(f"Tele error: {e}")

def get_coingecko_vol_mc():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=idr&order=volume_desc&per_page=250&page=1&sparkline=false"
        r = requests.get(url, timeout=15).json()
        mapping = {}
        for c in r:
            sym = c.get("symbol","").upper()
            mc = c.get("market_cap",0) or 0
            vol = c.get("total_volume",0) or 0
            if mc>0:
                mapping[sym] = (vol/mc)*100
        return mapping
    except:
        return {}

def main():
    try:
        r = requests.get("https://indodax.com/api/summaries", timeout=15).json()
        tickers = r.get("tickers", {})
    except:
        return
    cg = get_coingecko_vol_mc()
    now = datetime.now().strftime("%H:%M WIB")

    entry, serok, selesai, ijo = [], [], [], []

    for pair, d in tickers.items():
        if not pair.endswith("_idr"): continue
        coin = pair.replace("_idr","").upper()
        try:
            last = float(d.get("last",0)); low = float(d.get("low",0))
            high = float(d.get("high",0)); vol_idr = float(d.get("vol_idr",0))
            if last==0 or low==0 or high==0: continue
            pct_low = (last-low)/low*100
            pct_high = (last-high)/high*100
            ratio = cg.get(coin, 0)

            # V12.1: ENTRY DULUAN hanya yang Vol/MC >35% biar ketat
            if 3.0 <= pct_low <= 9.5 and pct_high < -2:
                if ratio >= 35: # HAPUS fallback 35jt biar ga kebanyakan
                    entry.append(f"🚀 {coin} +{pct_low:.1f}% R:{ratio:.0f}% Rp{last:,.0f}")

            if 0 <= pct_low <= 2.5 and -5 <= pct_high <= -0.8 and vol_idr >= 40000000:
                serok.append(f"🎯 {coin} {pct_high:.1f}% {vol_idr/1e6:.0f}jt")

            elif 0.3 <= pct_low <= 5 and -9 <= pct_high <= -1.2 and vol_idr >= 30000000:
                if not (0 <= pct_low <= 2.5 and vol_idr >= 40000000):
                    selesai.append(f"✅ {coin} {pct_high:.1f}% {vol_idr/1e6:.0f}jt")

            if pct_low >= 15:
                ijo.append(f"🔥 {coin} +{pct_low:.1f}%")
        except: continue

    msg = f"🤖 V12.1 HYBRID {now}\nVol/MC>35% + Vol IDR\n\n"
    msg += f"⚡ ENTRY DULUAN (Vol/MC>35% Anti ZRO 92%): {len(entry)} koin\n"
    msg += ("\n".join(entry[:8]) if entry else "0 - Market sepi") + "\n\n"
    msg += f"🎯 SEROK BAWAH 40jt+: {len(serok)} koin\n"
    msg += ("\n".join(serok[:8]) if serok else "0") + "\n\n"
    msg += f"📈 SELESAI KOREKSI 30jt+: {len(selesai)} koin\n"
    msg += ("\n".join(selesai[:8]) if selesai else "0") + "\n\n"
    msg += f"🚀 IJO OVER: {len(ijo)} koin\n" + "\n".join(ijo[:5])

    print(msg)
    send_tele(msg)

if __name__ == "__main__":
    main()
