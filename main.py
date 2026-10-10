import os, requests
from datetime import datetime, timezone, timedelta

TOKEN=os.getenv("TELEGRAM_TOKEN")
CHAT=os.getenv("CHAT_ID")
WIB=datetime.now(timezone.utc)+timedelta(hours=7)
JAM=WIB.strftime("%H:%M WIB - %d %b %Y")

def kirim(t):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    json={"chat_id":CHAT,"text":t,"parse_mode":"HTML","disable_web_page_preview":True}, timeout=20)

try:
    r=requests.get("https://indodax.com/api/tickers", timeout=20).json()["tickers"]
    micin=[]; fresh=[]; willpump=[]; alert=[]

    for k,v in r.items():
        if "_idr" not in k: continue
        try:
            last=float(v["last"]); low=float(v["low"]); vol=float(v["vol_idr"])
            naik = (last-low)/low*100 if low>0 else 0
            coin=k.upper().replace("_IDR","")

            if vol < 50000000: continue

            # KUMPUL DATA
            if last < 5000: micin.append((coin,last,vol,naik))
            if last < 100 and naik > 40 and vol > 800000000: fresh.append((coin,last,vol,naik))
            if 10 < naik < 600 and vol > 1000000000: willpump.append((coin,last,vol,naik))
            # ALERT >50%
            if naik >= 50 and vol > 500000000 and last < 5000:
                alert.append((coin,last,vol,naik))
        except: pass

    # 1. KIRIM ALERT DULU KALO ADA YANG PUMP >50%
    if alert:
        txt_alert=f"🚨🚨 <b>PUMP ALERT {JAM} - NAIK >50%!</b> 🚨🚨\n\n"
        for c,p,vo,na in sorted(alert,key=lambda x:x[3],reverse=True)[:5]:
            txt_alert+=f"🔥 <b>{c}</b> - Rp{p}\n NAIK: <b>{na:.1f}%</b> | Vol: {vo/1e9:.2f} Miliar\n ⚡ SIAP TERBANG! CEK SEKARANG!\n\n"
        kirim(txt_alert)

    # 2. LAPORAN RUTIN TOP 7
    txt=f"🚀 <b>TOP MICIN HUNTER - {JAM}</b>\n\n"

    if willpump:
        txt+=f"🔥 <b>WILL PUMP:</b>\n"
        for i,(c,p,vo,na) in enumerate(sorted(willpump,key=lambda x:x[3],reverse=True)[:3],1):
            txt+=f"{i}. {c} Rp{p} | +{na:.0f}% | {vo/1e9:.1f}M\n"
        txt+="\n"

    if fresh:
        txt+=f"✨ <b>FRESH:</b>\n"
        for i,(c,p,vo,na) in enumerate(sorted(fresh,key=lambda x:x[3],reverse=True)[:3],1):
            txt+=f"{i}. {c} Rp{p} | +{na:.0f}% | {vo/1e9:.1f}M\n"
        txt+="\n"

    txt+=f"📊 <b>TOP 7 TRENDING:</b>\n"
    for i,(c,p,vo,na) in enumerate(sorted(micin,key=lambda x:x[2],reverse=True)[:7],1):
        txt+=f"{i}. {c} - Rp{p} ({na:.0f}%)\n"

    txt+=f"\n⏰ Auto scan 5 menit | {JAM}"
    kirim(txt)

except Exception as e:
    kirim(f"⚠️ Error scan {JAM}: {e}\nBot tetap jalan!")
