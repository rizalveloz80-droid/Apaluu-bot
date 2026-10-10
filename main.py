import os, requests
from datetime import datetime, timezone, timedelta

TOKEN=os.getenv("TELEGRAM_TOKEN")
CHAT=os.getenv("CHAT_ID")
WIB=datetime.now(timezone.utc)+timedelta(hours=7)
JAM=WIB.strftime("%H:%M WIB - %d %b")

def kirim(txt):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id":CHAT,"text":txt,"parse_mode":"HTML"}, timeout=20)

# AMBIL DATA INDODAX
try:
    r=requests.get("https://indodax.com/api/tickers", timeout=15).json()
    tickers=r.get("tickers",{})
    micin=[]
    for k,v in tickers.items():
        if "_idr" not in k: continue
        try:
            last=float(v.get("last",0)); vol=float(v.get("vol_idr",0))
            # filter micin: harga < 5000, vol > 50jt, naik
            if last<5000 and vol>50000000 and float(v.get("last",0))>0:
                change = ((last - float(v.get("low",last))) / float(v.get("low",last))*100) if float(v.get("low",0))>0 else 0
                micin.append((k.upper().replace("_IDR",""), last, vol, change))
        except: pass
    micin=sorted(micin, key=lambda x: x[2], reverse=True)[:7]
    if not micin:
        kirim(f"🔍 <b>MICIN HUNTER {JAM}</b>\n\nBelum ada micin siap pump, vol masih sepi. Cek lagi 5 menit!")
    else:
        pesan=f"🚀 <b>TOP 7 MICIN & ALT ALL COIN - {JAM}</b>\n\n"
        for i,(coin,price,vol,ch) in enumerate(micin,1):
            pesan+=f"{i}. <b>{coin}</b> - Rp{price}\n Vol: {vol/1000000:.1f}jt | Naik: {ch:.1f}%\n\n"
        pesan+="⚠️ DYOR! Micin resiko tinggi!"
        kirim(pesan)
except Exception as e:
    kirim(f"✅ BOT HIDUP {JAM}\nError scan: {e}\nTapi bot jalan!")
