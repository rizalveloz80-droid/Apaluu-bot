
import requests
import time
from datetime import datetime, timezone, timedelta

TOKEN = "8675452184:AAExOSp0LHuOQ7gSd0-l"
CHAT_ID = "213453765"
WIB = timezone(timedelta(hours=7))

# COIN YANG UDAH DCA - JANGAN MASUK TOP 20
BLACKLIST = ['usdt_idr', 'usdc_idr', 'btc_idr', 'sol_idr', 'xrp_idr', 'eth_idr', 'fartcoin_idr', 'hype_idr', 'sui_idr', 'doge_idr', 'pepe_idr']

def kirim_tele(pesan):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": pesan}
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"Gagal kirim: {e}")

def cek_all_signal():
    try:
        r = requests.get("https://indodax.com/api/tickers", timeout=15)
        tickers = r.json().get("tickers", {})
        
        signals = []
        for pair, data in tickers.items():
            if not pair.endswith("_idr"):
                continue
            if pair in BLACKLIST:
                continue
            try:
                vol_idr = float(data.get("vol_idr", 0))
                last = float(data.get("last", 0))
                low = float(data.get("low", 0))
                if low == 0:
                    continue
                change = ((last - low) / low * 100) if low else 0

                if vol_idr < 1000000:
                    continue
                if change < 6:
                    continue

                signals.append({
                    "pair": pair.upper(),
                    "vol": vol_idr,
                    "change": change,
                    "last": last
                })
            except:
                continue
        
        signals = sorted(signals, key=lambda x: x["vol"], reverse=True)[:20]
        
        if not signals:
            print("Tidak ada signal >6%")
            return

        now_wib = datetime.now(WIB).strftime("%H:%M WIB")
        pesan = f"📊 ALL SIGNAL {now_wib} - TOP 20 TERPANAS - FILTER >6%\n"
        pesan += f"Blacklist: {len(BLACKLIST)} coin DCA di-skip\n"
        pesan += "--------------------------------\n"
        
        for s in signals:
            vol_m = s["vol"] / 1000000
            pesan += f"🔥 {s['pair']} Vol Rp{vol_m:.2f}M +{s['change']:.2f}%\n"
        
        print(pesan)
        kirim_tele(pesan)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    cek_all_signal()
