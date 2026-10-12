import requests, os
from datetime import datetime

TELE_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_tele(msg):
    try:
        if not TELE_TOKEN or not CHAT_ID: return
        requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",
                      json={"chat_id": CHAT_ID, "text": msg}, timeout=15)
    except: pass

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
                ratio = (vol/mc)*100
                mapping[sym] = ratio
        return mapping
    except:
        return {}

def main():
    try:
        r = requests.get("https://indodax.com/api/summaries", timeout=15).json()
        tickers = r.get("tickers", {})
    except:
        return

    cg_ratios = get_coingecko_vol_mc()
    now = datetime.now().strftime("%H:%M WIB")
    serok_bawah, selesai_koreksi, entry_duluan, ijo_over = [], [], [], []

    for pair, d in tickers.items():
        if not pair.endswith("_idr"): continue
        coin = pair.replace("_idr","").upper()
        try:
            last = float(d.get("last",0))
            low = float(d.get("low",0))
            high = float(d.get("high",0))
            vol_idr = float(d.get("vol_idr",0))
            if last==0 or low==0 or high==0: continue

            pct_low = (last - low)/low*100
            pct_high = (last - high)/high*100
            vol_mc_ratio = cg_ratios.get(coin, 0)

            if 3.0 <= pct_low <= 9.5 and pct_high < -2:
                if vol_mc_ratio >= 35 or vol_idr >= 35000000:
                    sl = last*0.97
                    tp = last*1.06
                    tag = f"{vol_mc_ratio:.1f}%" if vol_mc_ratio>0 else f"{vol_idr/1e6:.0f}jt"
                    entry_duluan.append(f"🚀 {coin} Rp{last:,.0f} +{pct_low:.1f}% Vol/MC:{tag}\nSL:Rp{sl:,.0f} TP:Rp{tp:,.0f} - CEGAT AWAL!")

            if 0 <= pct_low <= 2.5 and -5 <= pct_high <= -0.8 and vol_idr >= 40000000:
                sl = last*0.98
                tp = last*1.04
                serok_bawah.append(f"🎯 {coin} Rp{last:,.0f} {pct_high:.1f}% Vol:{vol_idr/1e6:.0f}jt\nSL:Rp{sl:,.0f} TP:Rp{tp:,.0f}")

            elif 0.3 <= pct_low <= 5 and -9 <= pct_high <= -1.2 and vol_idr >= 30000000:
                if not (0 <= pct_low <= 2.5 and vol_idr >= 40000000):
                    sl = last*0.98
                    tp = last*1.04
                    selesai_koreksi.append(f"✅ {coin} Rp{last:,.0f} {pct_high:.1f}% Vol:{vol_idr/1e6:.0f}jt\nSL:Rp{sl:,.0f} TP:Rp{tp:,.0f}")

            if pct_low >= 15:
                ijo_over.append(f"🔥 {coin} Rp{last:,.0f} +{pct_low:.1f}% JANGAN KEJAR")
        except: continue

    msg = f"🤖 V12 HYBRID Vol/MC {now}\nRumus: Vol/MC=Vol24H/MC x100% + Vol IDR\n\n"
    if entry_duluan: msg += f"⚡ ENTRY DULUAN Vol/MC>35% (Anti Ketinggalan ZRO 92%):\n" + "\n".join(entry_duluan[:10]) + "\n\n"
    else: msg += "⚡ ENTRY DULUAN: 0 koin - Belum ada Vol/MC>35%\n\n"
    if serok_bawah: msg += f"🎯 SEROK BAWAH (40jt+):\n" + "\n".join(serok_bawah[:12]) + "\n\n"
    else: msg += "🎯 SEROK BAWAH (40jt+): 0 koin\n\n"
    if selesai_koreksi: msg += f"📈 SELESAI KOREKSI (30jt+):\n" + "\n".join(selesai_koreksi[:12]) + "\n\n"
    else: msg += "📈 SELESAI KOREKSI (30jt+): 0 koin\n\n"
    if ijo_over: msg += f"🚀 IJO OVERBOUGHT JANGAN KEJAR:\n" + "\n".join(ijo_over[:10])

    print(msg)
    send_tele(msg)

if __name__ == "__main__":
    main()
