import requests, json, os
from datetime import datetime

# === TELEGRAM ===
TELE_TOKEN = os.getenv("TELE_TOKEN") or "8675452184:AAHlWcaNYQg62ioe3p3yI1wUO5zXMyFBkVw"
TELE_CHAT_ID = os.getenv("TELE_CHAT_ID") or os.getenv("CHAT_ID")

def send_tele(text):
    if not TELE_TOKEN or not TELE_CHAT_ID:
        print("TELE_SKIP: TELE_CHAT_ID belum di set")
        return
    url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
    try:
        # Potong kalo kepanjangan (limit tele 4096)
        if len(text) > 3500:
            text = text[:3500] + "\n...potong"
        r = requests.post(url, json={"chat_id": TELE_CHAT_ID, "text": text}, timeout=15)
        print(f"TELE_SENT {r.status_code} {r.text[:200]}")
    except Exception as e:
        print(f"TELE_ERR {e}")

# === BOT V27.1 LOOSE ===
print("=== BOT V27.1 LOOSE START ===")

# Load cache chg15m
cache = {}
if os.path.exists("price_cache.json"):
    try:
        cache = json.loads(open("price_cache.json").read())
        print(f"Cache loaded {len(cache)} coin")
    except:
        cache = {}

try:
    data = requests.get("https://indodax.com/api/tickers", timeout=20).json()
    tickers = data.get("tickers", {})
except Exception as e:
    print(f"Fetch error {e}")
    tickers = {}

GOLD = []
PRE = []
DALEM = []

for k,v in tickers.items():
    try:
        last = float(v.get("last",0))
        low = float(v.get("low",0))
        high = float(v.get("high",0))
        vol = float(v.get("vol_idr",0))
        if last==0 or low==0: continue
        
        dl = (last-low)/low*100 if low else 0
        sq = (high-low)/low*100 if low else 0
        
        vol_jt = vol/1_000_000_000
        # chg15m
        prev = cache.get(k)
        chg15m = ((last-prev)/prev*100) if prev else 0.0
        
        item = f"- {k.upper()} dl {dl:.2f}% sq {sq:.1f}% vol {vol_jt:.0f}jt chg15m {chg15m:+.1f}%"
        item_short = f"{k.upper()} {chg15m:+.1f}% vol {vol_jt:.0f}jt"
        
        # LOOSE LOGIC (kayak di SS lu)
        if vol_jt >= 50 and dl < 1.5 and sq < 6:
            GOLD.append((item, item_short, vol_jt))
        elif 10 <= vol_jt < 50 and sq < 5:
            PRE.append((item, item_short, vol_jt))
        elif dl < 0.8 and vol_jt >= 30:
            DALEM.append((f"- {k.upper()} dl {dl:.2f}% vol {vol_jt:.0f}jt", item_short, vol_jt))
    except:
        continue

# Sort by vol
GOLD = sorted(GOLD, key=lambda x: x[2], reverse=True)[:5]
PRE = sorted(PRE, key=lambda x: x[2], reverse=True)[:7]
DALEM = sorted(DALEM, key=lambda x: x[2], reverse=True)[:7]

print(f"\nGOLD ({len(GOLD)}):")
for x in GOLD: print(x[0])
print(f"\nPRE_TRENDING ({len(PRE)}):")
for x in PRE: print(x[0])
print(f"\nSEROK_DALEM ({len(DALEM)}):")
for x in DALEM: print(x[0])

# Save new cache
new_cache = {}
for k,v in tickers.items():
    try:
        new_cache[k] = float(v.get("last",0))
    except: pass
open("price_cache.json","w").write(json.dumps(new_cache))
print("\n=== DONE - cache saved ===")

# === KIRIM TELE ===
if GOLD or PRE or DALEM:
    tele_msg = f"⚡️ *APALUU V27.1 LOOSE* {datetime.now().strftime('%H:%M')}\nSCAN {len(tickers)} COIN\n\n"
    if GOLD:
        tele_msg += f"🥇 GOLD ({len(GOLD)}):\n" + "\n".join([f"{i+1}. {x[1]}" for i,x in enumerate(GOLD)]) + "\n\n"
    if PRE:
        tele_msg += f"🔥 PRE_TRENDING ({len(PRE)}):\n" + "\n".join([f"{i+1}. {x[1]}" for i,x in enumerate(PRE)]) + "\n\n"
    if DALEM:
        tele_msg += f"💎 SEROK_DALEM ({len(DALEM)}):\n" + "\n".join([f"{i+1}. {x[1]}" for i,x in enumerate(DALEM)]) + "\n\n"
    tele_msg += f"Total {len(GOLD)+len(PRE)+len(DALEM)} RANK | Vol min 10jt | LOOSE MODE"
    
    # Kirim tanpa markdown biar aman
    send_tele(tele_msg.replace("*",""))
else:
    send_tele(f"V27.1 LOOSE {datetime.now().strftime('%H:%M')} - No signal, scan {len(tickers)}")
