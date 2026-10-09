import requests
import os
from datetime import datetime, timezone, timedelta
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
WIB = timezone(timedelta(hours=7))
BLACKLIST = ['usdt_idr', 'usdc_idr', 'btc_idr', 'sol_idr', 'xrp_idr', 'eth_idr', 'fartcoin_idr', 'hype_idr', 'sui_idr', 'doge_idr', 'pepe_idr']
def kirim_tele(pesan):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": pesan}, timeout=15)
def cek_signal():
    r = requests.get("https://indodax.com/api/tickers", timeout=15)
    tickers = r.json().get("tickers", {})
    signals = []
    for pair, data in tickers.items():
        if not pair.endswith("_idr") or pair in BLACKLIST: continue
        try:
            vol=float(data.get("vol_idr",0)); last=float(data.get("last",0)); low=float(data.get("low",0))
            if low==0: continue
            change=(last-low)/low*100
            if vol<1_000_000 or change<6: continue
            signals.append({"pair":pair.upper(),"vol":vol,"change":change})
        except: continue
    signals=sorted(signals, key=lambda x: x["vol"], reverse=True)[:20]
    if not signals: return
    now=datetime.now(WIB).strftime("%H:%M WIB")
    pesan=f"🤖 @BOTTOM_HUNTER_1300_BOT {now}\n--------------------------------\n"
    for s in signals: pesan+=f"🔥 {s['pair']} +{s['change']:.2f}% Vol {s['vol']/1e6:.1f}M\n"
    kirim_tele(pesan)
if __name__ == "__main__":
    cek_signal()
