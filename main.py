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
            if last < 50 or last > 8000: continue # BUANG RP1-50
            if vol < 500000000: continue
            naik=(last-low)/low*100; posisi=(last-low)/(high-low)*100
            if posisi>80: continue # UDAH PUCUK SKIP
            if 4 <= naik <= 35 and 25 <= posisi <= 80:
                early.append((k.upper().replace("_IDR",""),last,vol,naik,posisi))
        except: pass
    if early:
        txt=f"✅ <b>BARU MULAI - NO RECEH - {JAM}</b>\nFilter: >Rp50, Vol >500jt, Belum Pucuk\n\n"
        for c,p,vo,na,po in sorted(early,key=lambda x:x[3],reverse=True)[:7]:
            txt+=f"🟢 <b>{c}</b> Rp{p} | +{na:.1f}% | Pos {po:.0f}% | {vo/1e9:.1f}M\n\n"
        kirim(txt)
    else:
        kirim(f"⏸️ {JAM} - Ga ada yang baru mulai. Semua yang naik udah pucuk / receh Rp1-2 di skip.")
except Exception as e:
    kirim(f"Error {JAM}: {e}")
