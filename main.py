import requests, os, datetime, sys
BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID") or os.getenv("TELE_CHAT_ID")

# === SKIP PUNYA LU - 74 KOIN ===
SKIP = {'usdt','usdc','dai','busd','husd','btc','eth','xrp','sol','doge',
    'bnb','ada','dot','ltc','trx','link','avax','mkr','sui','hype',
    'near','ton','apt','sei','inj','ftm','atom','aave','uni','poly',
    'matic','meme','floki','wif','xlm','algo','vet','theta','eos','mana',
    'axs','enj','chz','jup','render','fet','agix','grt','etc','bch','bsv',
    'dash','zec','xmr','btt','win','1inch','gmx','rndr','kas','ordi',
    'portal','tia','ondo','ena','zks','ethfi','pyth','mew','xaut','pengu','pump'}

VOL_MIN = 5000000
MAX_CHG = 100.0

def send_tele(m):
 try: requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": m}, timeout=10)
 except: pass

tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json().get("tickers", {})
now = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).strftime("%H:%M WIB")
early=[]; hunter=[]; segar=[]; dalem=[]

for pair,d in tickers.items():
 if not pair.endswith("_idr"): continue
 symbol = pair.split('_')[0].lower()
 if symbol in SKIP: continue
 try:
  last=float(d["last"]); low=float(d["low"]); high=float(d["high"]); vol=float(d["vol_idr"])
  if low==0 or last<10 or vol<VOL_MIN: continue
  if ((high-low)/low*100) < 0.5: continue
  chg=(last-low)/low*100; th=(high-last)/last*100; dl=(last-low)/last*100; sq=dl+th
  if -30 <= chg <= -1.5 and dl<=5 and sq<22 and th<25 and chg>=0.3: dalem.append((pair,chg,vol,th,dl))
  if 1.2 <= chg <=10 and th<=6 and dl<=6 and sq<13 and vol>=5000000: early.append((pair,chg,vol,th))
  if chg<1.2 or chg>MAX_CHG or th<0 or th>50 or chg<0.3: continue
  if chg<=4:
   if th<=15: segar.append((pair,chg,vol,th))
  else:
   if th<=12: hunter.append((pair,chg,vol,th))
 except: continue

msg=f"SCAN {now} V18.4 SKIP FIX\n"
if early: msg+="\n⚡ EARLY\n"+"".join([f"{p.upper()} {c:.1f}% Vol {v/1e9:.2f}Bn\n" for p,c,v,th in early[:3]])
if hunter: msg+="\n🚀 HUNTER\n"+"".join([f"{p.upper()} {c:.1f}% Vol {v/1e9:.2f}Bn TH {th:.1f}%\n" for p,c,v,th in sorted(hunter,key=lambda x:x[1],reverse=True)[:5]])
if segar: msg+="\n🌱 SEGAR\n"+"".join([f"{p.upper()} {c:.1f}% Vol {v/1e9:.2f}Bn\n" for p,c,v,th in sorted(segar,key=lambda x:x[2],reverse=True)[:5]])
if dalem: msg+="\n💎 DALEM\n"+"".join([f"{p.upper()} {c:.1f}% DL {dl:.1f}%\n" for p,c,v,th,dl in sorted(dalem,key=lambda x:x[4])[:5]])
if not (early or hunter or segar or dalem): msg+="KOSONG"

send_tele(msg); print(msg); sys.exit(0)
