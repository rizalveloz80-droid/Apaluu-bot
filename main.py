import requests
import time
import os
from datetime import datetime, timedelta, timezone

MARKETS_URL = "https://indodax.com/api/pairs"
API_URL = "https://indodax.com/api/ticker/{}"

SKIP = {'usdt','usdc','dai','busd','husd','btc','eth','xrp','sol','doge',
    'bnb','ada','dot','ltc','trx','link','avax','mkr','sui','hype',
    'near','ton','apt','sei','inj','ftm','atom','aave','uni','poly',
    'matic','meme','floki','wif','xlm','algo','vet','theta','eos','mana',
    'axs','enj','chz','jup','render','fet','agix','grt','etc','bch','bsv',
    'dash','zec','xmr','btt','win','1inch','gmx','rndr','kas','ordi',
    'portal','tia','ondo','ena','zks','ethfi','pyth','mew','xaut','ern','bome'}

TELE_TOKEN = os.getenv("TELE_TOKEN")
TELE_CHAT_ID = os.getenv("TELE_CHAT_ID")

def send(txt):
    try:
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELE_CHAT_ID, "text": txt, "parse_mode": "Markdown"}, timeout=10)
    except: pass

def get_depth(pair):
    try:
        r = requests.get(f"https://indodax.com/api/{pair}/depth", timeout=4).json()
        buy = sum(float(x[0])*float(x[1]) for x in r.get('buy', [])[:20])
        sell = sum(float(x[0])*float(x[1]) for x in r.get('sell', [])[:20])
        return buy, sell
    except: return 0,0

def get_hijau(pair):
    try:
        trades = requests.get(f"https://indodax.com/api/{pair}/trades", timeout=4).json()[:12]
        hijau = sum(1 for i in range(len(trades)-1) if float(trades[i]['price']) >= float(trades[i+1]['price']))
        return hijau
    except: return 0

def ana(pair):
    try:
        t = requests.get(API_URL.format(pair), timeout=5).json()["ticker"]
        last = float(t["last"]); low = float(t["low"]) or 1; high = float(t["high"]) or last
        vol = float(t.get("vol_idr",0))
        if vol == 0:
            vol = float(t.get("vol_"+pair.split("_")[0],0)) * last
        chg = (last-low)/low*100
        th = (high-last)/high*100 if high else 0
        return chg, th, vol, last
    except: return None

def main():
    now = datetime.now(timezone.utc) + timedelta(hours=7)
    jam_str = now.strftime("%H:%M")
    jam = now.hour

    # ANTI KETINGGALAN UCJL - ENTRY SEJAK DINI
    if 0 <= jam <= 7:
        MIN_VOL = 15000000  # 15Mn aja! biar jam 06:00 ke-detect
        MIN_RATIO = 1.0
        MIN_HIJAU = 3
        S_MIN_CHG, S_MAX_CHG = 0.8, 5  # 0.8% aja udah SEGAR!
        H_MIN_CHG, H_MAX_CHG = 5, 20
        MIN_TH = 5
        mode = "PAGI DINI"
    else:
        MIN_VOL = 30000000  # 30Mn siang
        MIN_RATIO = 1.1
        MIN_HIJAU = 3
        S_MIN_CHG, S_MAX_CHG = 1.0, 4.5
        H_MIN_CHG, H_MAX_CHG = 4.5, 15
        MIN_TH = 8
        mode = "SORE"

    print(f"SCAN {mode} {jam_str} | Vol {MIN_VOL/1e6:.0f}Mn")

    try:
        pairs = requests.get(MARKETS_URL, timeout=8).json()
    except: return

    segar = []
    hunter = []

    for p in pairs:
        pair = p.get("id","")
        if not pair.endswith("_idr") or not p.get("tradable"): continue
        if pair.split("_")[0].lower() in SKIP: continue

        r = ana(pair)
        if not r: 
            time.sleep(0.15)
            continue
        chg, th, vol, last = r
        if vol < MIN_VOL or th < MIN_TH: 
            time.sleep(0.15)
            continue

        buy, sell = get_depth(pair)
        if sell == 0: 
            time.sleep(0.15)
            continue
        ratio = buy / sell
        if ratio < MIN_RATIO or ratio > 7: 
            time.sleep(0.15)
            continue

        hijau = get_hijau(pair)
        if hijau < MIN_HIJAU: 
            time.sleep(0.15)
            continue

        coin = pair.replace("_idr","").upper()
        vstr = f"{vol/1e9:.2f} Bn" if vol>=1e9 else f"{vol/1e6:.0f} Mn"

        if S_MIN_CHG <= chg <= S_MAX_CHG:
            segar.append((vol, f"🌱 SEGAR {coin} | Naik {chg:.1f}% | Sisa {th:.0f}% | Vol {vstr} | B/S {ratio:.1f}x | Ijo {hijau}/12"))
        elif H_MIN_CHG <= chg <= H_MAX_CHG:
            hunter.append((vol, f"🔥 HUNTER {coin} | Naik {chg:.1f}% | Sisa {th:.0f}% | Vol {vstr} | B/S {ratio:.1f}x | Ijo {hijau}/12"))

        time.sleep(0.2)

    segar.sort(key=lambda x: x[0], reverse=True)
    hunter.sort(key=lambda x: x[0], reverse=True)

    if segar or hunter:
        pesan = f"🚨 SCAN {jam_str} WIB | V13 DINI {mode}\n"
        pesan += f"Filter: Vol {MIN_VOL/1e6:.0f}Mn | B/S {MIN_RATIO}x | Ijo {MIN_HIJAU}x\n\n"
        if segar:
            pesan += f"🌱 SEGAR:\n"
            for _, txt in segar[:8]: pesan += f"{txt}\n"
            pesan += "\n"
        if hunter:
            pesan += f"🔥 HUNTER:\n"
            for _, txt in hunter[:8]: pesan += f"{txt}\n"
        send(pesan)
    else:
        # Biar ga spam, kirim KOSONG cuma tiap 1 jam sekali aja
        if now.minute < 5:
            send(f"🚨 SCAN {jam_str} WIB | V13 DINI {mode}\n\nKOSONG - Market sepi\nFilter {MIN_VOL/1e6:.0f}Mn")

if __name__ == "__main__":
    main()
