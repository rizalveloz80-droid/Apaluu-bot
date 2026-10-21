import requests
import time
import os
from datetime import datetime, timedelta

API_URL = "https://indodax.com/api/ticker/{}"
MARKETS_URL = "https://indodax.com/api/pairs"

# SKIP coin gede biar fokus koin kecil kayak SHOW, ZEREBRO, ICNT
SKIP = {'usdt','usdc','dai','busd','husd','btc','eth','xrp','sol','doge',
    'bnb','ada','dot','ltc','trx','link','avax','mkr','sui','hype',
    'near','ton','apt','sei','inj','ftm',
    'atom','aave','uni','poly','matic','meme','floki',
    'wif','xlm','algo','vet','theta','eos','mana',
    'axs','enj','chz','jup','render','fet','agix','grt',
    'etc','bch','bsv','dash','zec','xmr','btt','win','1inch',
    'gmx','rndr','kas','ordi','portal',
    'tia','ondo','ena','zks','ethfi','pyth','mew','xaut','ern'} # ERN mimin masukin SKIP biar ilang permanen

# HUNTER = RUN kayak SHOW pas jam 4 sore (6.7%)
MIN_CHANGE = 4
MAX_CHANGE = 15
MIN_TO_HIGH = 12
MIN_VOL = 80000000 # 80jt IDR - vol kecil mimin naikin biar ga spam koin gorengan 100rb

# SEGAR = DINI kayak VELVET, UNI, POL pas baru bangun
S_MIN_CHANGE = 1.5
S_MAX_CHANGE = 6
S_MIN_TO_HIGH = 12
S_MIN_VOL = 80000000

# PAKE YANG LAMA MIN, GA USAH GANTI
TELE_TOKEN = os.getenv("TELE_TOKEN")
TELE_CHAT_ID = os.getenv("TELE_CHAT_ID")

def send(txt):
    try:
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELE_CHAT_ID, "text": txt, "parse_mode": "Markdown"}, timeout=10)
    except:
        pass

def get_depth(pair):
    try:
        r = requests.get(f"https://indodax.com/api/{pair}/depth", timeout=4).json()
        buy = sum(float(x[0])*float(x[1]) for x in r.get('buy', [])[:20])
        sell = sum(float(x[0])*float(x[1]) for x in r.get('sell', [])[:20])
        return buy, sell
    except: return 0,0

def ana(pair):
    try:
        t = requests.get(API_URL.format(pair), timeout=5).json()["ticker"]
        last = float(t["last"]); low = float(t["low"]) or 1
        high = float(t["high"]) or last
        # vol IDR yang bener
        vol_idr = float(t.get("vol_idr", 0))
        if vol_idr == 0:
            b = pair.split("_")[0]
            vol_idr = float(t.get("vol_"+b, 0)) * last
        
        chg = (last-low)/low*100
        th = (high-last)/high*100 if high else 0 # pake high biar akurat kayak SHOW tadi
        return chg, th, vol_idr, last, high, low
    except:
        return None

def main():
    print("SCAN HUNTER + SEGAR ANTI ERN...")
    try:
        pairs = requests.get(MARKETS_URL, timeout=10).json()
    except:
        return
    
    now_wib = datetime.utcnow() + timedelta(hours=7)
    jam_str = now_wib.strftime("%H:%M")
    
    hunter_list = []
    segar_list = []

    for p in pairs:
        if not p.get("id"): continue
        pair = p["id"]
        if not pair.endswith("_idr"): continue
        if not p.get("tradable", False): continue
        base = pair.split("_")[0].lower()
        if base in SKIP: continue

        r = ana(pair)
        if not r: 
            time.sleep(0.2)
            continue
        chg, th, vol, last, high, low = r

        # FILTER ANTI DUMP kayak SHOW
        buy, sell = get_depth(pair)
        if sell > 0:
            ratio = buy / sell
            if ratio < 1.25 or ratio > 7: # buy tipis = skip
                time.sleep(0.2)
                continue
        else:
            time.sleep(0.2)
            continue

        coin = pair.replace("_idr","").upper()
        vstr = f"{vol/1e9:.2f} Bn" if vol>=1e9 else f"{vol/1e6:.0f} Mn"

        # HUNTER = kayak SHOW 6.7%, ZEREBRO 6.9%, ICNT 5%
        if vol >= MIN_VOL and MIN_CHANGE <= chg <= MAX_CHANGE and th >= MIN_TO_HIGH:
            hunter_list.append((vol, f"🔥 HUNTER {coin} | Naik {chg:.1f}% | Sisa {th:.0f}% | Vol {vstr} | B/S {ratio:.1f}x"))

        # SEGAR = kayak VELVET, UNI, POL baru bangun
        elif vol >= S_MIN_VOL and S_MIN_CHANGE <= chg <= S_MAX_CHANGE and th >= S_MIN_TO_HIGH:
            segar_list.append((vol, f"🌱 SEGAR {coin} | Naik {chg:.1f}% | Sisa {th:.0f}% | Vol {vstr} | B/S {ratio:.1f}x"))

        time.sleep(0.3)

    hunter_list.sort(key=lambda x: x[0], reverse=True)
    segar_list.sort(key=lambda x: x[0], reverse=True)

    if hunter_list or segar_list:
        pesan = f"🚨 SCAN {jam_str} WIB | {len(pairs)} koin\n"
        pesan += f"HUNTER (RUN DINI) + SEGAR (DINI) - ANTI ERN ON\n\n"
        if segar_list:
            pesan += "🌱 SEGAR - Baru Bangun ( kayak SHOW jam 16:00 ):\n"
            for vol, txt in segar_list[:6]:
                pesan += f"{txt}\n"
            pesan += "\n"
        if hunter_list:
            pesan += "🔥 HUNTER - Udah RUN tapi masih dini ( kayak ZEREBRO/ICNT/SHOW ):\n"
            for vol, txt in hunter_list[:6]:
                pesan += f"{txt}\n"
        send(pesan)
    else:
        send(f"🚨 SCAN {jam_str} WIB\n\nKOSONG - ERN ke-filter, market sepi kayak jam 22:35 tadi")

if __name__ == "__main__":
    main()
