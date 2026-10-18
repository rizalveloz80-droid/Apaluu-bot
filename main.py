import requests, os
from datetime import datetime

FORCE_BLACKLIST = set(["usdt_idr","usdc_idr","idrt_idr","usde_idr","xaut_idr","paxg_idr","ouros_idr","btc_idr","eth_idr","xrp_idr","sol_idr","bnb_idr","gid_idr","col_idr","okusd_idr","lyfel_idr","dfg_idr","inr_idr","eur_idr","indr_idr","neorpnew_idr","ern_idr"])

TELE_TOKEN = os.getenv("TELE_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
TELE_CHAT_ID = os.getenv("TELE_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID")

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT_ID:
        print(f"DEBUG ENV ADA: {list(os.environ.keys())[:10]}")
        print("TELE_TOKEN / CHAT_ID kosong! Cek run.yml & Secrets!")
        return
    try:
        r = requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", data={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=20)
        print(f"Telegram status: {r.status_code} {r.text[:200]}")
    except Exception as e:
        print(f"Gagal tele: {e}")

tickers = requests.get("https://indodax.com/api/tickers", timeout=20).json()["tickers"]
cands=[]
for pair,data in tickers.items():
    pl=pair.lower()
    if not pl.endswith("_idr") or pl in FORCE_BLACKLIST: continue
    try:
        last=float(data["last"]); low=float(data["low"]); vol=float(data["vol_idr"])
        if vol<100000 or last==0 or low==0: continue
        dl=(last-low)/last*100
        if dl>80: continue
        cands.append((pair.upper(), dl, vol))
    except: continue
cands.sort(key=lambda x: -x[2])
super_t=[c for c in cands if c[2]>=3000000000][:3]
trend=[c for c in cands if c[1]>=15][:5]
gold=[c for c in cands if 0<=c[1]<=2.5][:5]

now=datetime.now().strftime('%H:%M')
msg=f"V37 SCAN {now} | {len(tickers)}->{len(cands)} coin\n\n"
if super_t: msg+=f"🚨 SUPER >3Bn:\n" + "\n".join([f"-> {c[0]} {int(c[1])}% low Vol {round(c[2]/1e9,2)}Bn" for c in super_t]) + "\n\n"
if trend: msg+=f"🔥 TRENDING >=15%:\n" + "\n".join([f"-> {c[0]} {int(c[1])}% low Vol {int(c[2]/1e6)}jt" for c in trend]) + "\n\n"
if gold: msg+=f"⭐ GOLD deket low:\n" + "\n".join([f"-> {c[0]} {int(c[1])}% low Vol {int(c[2]/1e6)}jt" for c in gold])

print(msg)
send_tele(msg)
