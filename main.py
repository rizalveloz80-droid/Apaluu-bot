import os, requests
from datetime import datetime, timezone, timedelta
TOKEN=os.getenv("TELEGRAM_TOKEN"); CHAT=os.getenv("CHAT_ID")
WIB=datetime.now(timezone.utc)+timedelta(hours=7); JAM=WIB.strftime("%H:%M WIB")
def kirim(t):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",json={"chat_id":CHAT,"text":t,"parse_mode":"HTML"},timeout=20)
try:
    data=requests.get("https://indodax.com/api/tickers", timeout=20).json()["tickers"]
    early=[]
    for k,v in data.items():
        if "_idr" not in k: continue
        try:
            last=float(v["last"]); low=float(v["low"]); high=float(v["high"]); vol=float(v["vol_idr"])
            if high==low or low==0: continue
            if last < 80 or last > 8000: continue
            if vol < 1000000000: continue # Vol naikin jadi 1 Miliar!

            # ANTI BANTING: Harga harus masih nempel di HIGH minimal 98%
            if last < high * 0.985: continue # Kalo udah turun 1.5% dari high = SKIP! (MARSCOIN 1705/1780=95% bakal ke skip!)

            naik=(last-low)/low*100; posisi=(last-low)/(high-low)*100

            if posisi > 65: continue # Pos harus masih di bawah 65% - SUPER EARLY!
            if 8 <= naik <= 30:
                early.append((k.upper().replace("_IDR",""),last,vol,naik,posisi,high))
        except: pass

    if early:
        txt=f"✅ <b>SUPER EARLY - ANTI PUCUK - {JAM}</b>\nFilter: >Rp80, Vol >1M, Nempel High 98.5%, Pos <65%\n\n"
        for c,p,vo,na,po,hi in sorted(early,key=lambda x:x[3],reverse=True)[:5]:
            txt+=f"🟢 <b>{c}</b> Rp{p} (High {hi})\n +{na:.1f}% | Pos {po:.0f}% | {vo/1e9:.1f}M | MASIH NAIK!\n\n"
        kirim(txt)
    else:
        kirim(f"⏸️ <b>{JAM}</b> - Ga ada yang super early. Semua udah lewat high / udah dibanting kayak MARSCOIN. Jangan FOMO, tunggu yang baru!")
except Exception as e:
    kirim(f"Error {JAM}: {e}")
