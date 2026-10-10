import os, requests
from datetime import datetime, timezone, timedelta
TOKEN=os.getenv("TELEGRAM_TOKEN"); CHAT=os.getenv("CHAT_ID")
WIB=datetime.now(timezone.utc)+timedelta(hours=7); JAM=WIB.strftime("%H:%M WIB")
def kirim(t):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",json={"chat_id":CHAT,"text":t,"parse_mode":"HTML"},timeout=20)
try:
    r=requests.get("https://indodax.com/api/tickers", timeout=20).json()["tickers"]
    early=[]
    for k,v in r.items():
        if "_idr" not in k: continue
        try:
            last=float(v["last"]); low=float(v["low"]); high=float(v["high"]); vol=float(v["vol_idr"])
            if high==low or low==0: continue
            # FILTER HARGA: BUANG RP1 - RP50
            if last < 50: continue
            if last > 8000: continue
            if vol < 500000000: continue # vol minimal 500jt

            naik = (last-low)/low*100
            posisi = (last-low)/(high-low)*100

            # ANTI PUCUK
            if posisi > 80: continue
            # BARU MULAI NAIK: 4-30%, posisi 25-80%
            if 4 <= naik <= 35 and 25 <= posisi <= 80:
                coin=k.upper().replace("_IDR","")
                early.append((coin,last,vol,naik,posisi))
        except: pass

    if early:
        txt=f"✅ <b>FRESH PUMP - BUKAN RECEH - {JAM}</b>\n\n"
        txt+=f"Filter: Harga >Rp50, Vol >500jt, Belum Pucuk\n\n"
        for c,p,vo,na,po in sorted(early,key=lambda x:(x[3]),reverse=True)[:7]:
            txt+=f"🟢 <b>{c}</b> - Rp{p}\n +{na:.1f}% | Pos {po:.0f}% | Vol {vo/1e9:.1f}M\n\n"
        txt+="⚡ Ini baru mulai, bukan yang Rp1-Rp2!"
        kirim(txt)
    else:
        kirim(f"⏸️ <b>{JAM}</b> - Ga ada setup bagus (Rp>50). Yang naik udah pucuk / receh Rp1-2 di skip. Tunggu entry bagus!")
except Exception as e:
    kirim(f"Error {JAM}: {e}")
