import requests, os
from datetime import datetime

FORCE_BLACKLIST = set([
    "usdt_idr","usdc_idr","idrt_idr","usde_idr","xaut_idr","paxg_idr","ouros_idr",
    "btc_idr","eth_idr","xrp_idr","sol_idr","bnb_idr","gid_idr","col_idr",
    "okusd_idr","lyfel_idr","dfg_idr","inr_idr","eur_idr","indr_idr","neorpnew_idr"
])

TELE_TOKEN=os.getenv("TELE_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
TELE_CHAT_ID=os.getenv("TELE_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID")

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT_ID: return
    try: requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", data={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=20)
    except: pass

def get_active_pairs():
    try:
        r=requests.get("https://indodax.com/api/pairs", timeout=15).json()
        if isinstance(r, list): return set([str(p).lower() for p in r])
        if isinstance(r, dict): return set([k.lower() for k in r.keys()])
        return None
    except: return None

active_pairs=get_active_pairs()
try:
    tickers=requests.get("https://indodax.com/api/tickers", timeout=20).json()["tickers"]
except Exception as e:
    print(f"GAGAL API: {e}")
    exit()

cands=[]
for pair,data in tickers.items():
    pl=pair.lower()
    if not pl.endswith("_idr"): continue
    if pl in FORCE_BLACKLIST: continue
    if active_pairs and pl not in active_pairs: continue
    try:
        last=float(data["last"]); low=float(data["low"]); high=float(data["high"]); vol=float(data["vol_idr"])
        # GA ADA FILTER LAST <1 LAGI! PEPE 0.0002 MASUK!
        if vol < 100000: continue # cuma filter vol <100rb
        dl=((last-low)/last*100) if last>0 else 0
        cands.append((pair.upper(),dl,vol,last,low,high))
    except Exception as e:
        continue

print(f"DEBUG: DAPET {len(cands)} COIN DARI {len(tickers)}")
if len(cands)==0:
    # KALO MASIH 0, PRINT 3 CONTOH TICKER BIAR KETAUAN ERROR NYA!
    print("CONTOH TICKER:")
    for k,v in list(tickers.items())[:3]:
        print(k, v)

cands.sort(key=lambda x: -x[2]) # sort vol terbesar

top=cands[:15]

now=datetime.now().strftime('%H:%M')
msg=f"V32 NO FILTER FIX PEPE | {now}\nSCAN {len(tickers)} WL {len(active_pairs) if active_pairs else 0} CANDS {len(cands)}\n\n"

msg+=f"🚨 TOP VOL HARI INI ({len(top)}):\n"
for c in top:
    # c = pair, dl, vol, last, low, high
    msg+=f"-> {c[0]} {int(c[1])}% low Vol {int(c[2]/1000000)}jt Last {c[3]}\n"

print(msg)
send_tele(msg)
