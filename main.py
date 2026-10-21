import requests
import time
import os

API_URL = "https://indodax.com/api/ticker/{}"
MARKETS_URL = "https://indodax.com/api/pairs"

SKIP = {'usdt','usdc','dai','busd','husd','btc','eth','xrp','sol','doge',
    'bnb','ada','dot','ltc','trx','link','avax','mkr','sui','hype',
    'near','ton','apt','sei','inj','ftm',
    'atom','aave','uni','poly','matic','meme','floki',
    'wif','xlm','algo','vet','theta','eos','mana',
    'axs','enj','chz','jup','render','fet','agix','grt',
    'etc','bch','bsv','dash','zec','xmr','btt','win','1inch',
    'gmx','rndr','kas','ordi','portal',
    'tia','ondo','ena','zks','ethfi','pyth','mew','xaut'}

MIN_CHANGE = 5
MAX_CHANGE = 25
MIN_TO_HIGH = 25
MIN_VOL = 100000

S_MIN_CHANGE = 3
S_MAX_CHANGE = 10
S_MIN_TO_HIGH = 20
S_MIN_VOL = 200000

TELE_TOKEN = os.getenv("TELE_TOKEN")
TELE_CHAT_ID = os.getenv("TELE_CHAT_ID")

def send(txt):
    try:
        requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",
            json={"chat_id": TELE_CHAT_ID, "text": txt, "parse_mode": "HTML"})
    except:
        pass

def ana(pair):
    try:
        t = requests.get(API_URL.format(pair)).json()["ticker"]
        last = float(t["last"]); low = float(t["low"]) or 1
        high = float(t["high"]) or last
        b = pair.split("_")[0]
        vol = float(t["vol_"+b]) * last
        chg = (last-low)/low*100
        th = (high-last)/last*100 if last else 0
        return chg, th, vol
    except:
        return None

def main():
    try:
        pairs = requests.get(MARKETS_URL).json()
    except:
        return
    for p in pairs:
        if not p.get("tradable", False):
            continue
        pair = p["id"]
        base = pair.split("_")[0].lower()
        if base in SKIP:
            continue
        r = ana(pair)
        if not r:
            continue
        chg, th, vol = r
        if vol >= MIN_VOL and MIN_CHANGE <= chg <= MAX_CHANGE and th >= MIN_TO_HIGH:
            send(f"🔥 HUNTER {pair}\nnaik {chg:.1f}% dr low\n⚡ sisa ke high {th:.1f}%\nvol {vol/1e6:.2f}M")
        elif vol >= S_MIN_VOL and S_MIN_CHANGE <= chg <= S_MAX_CHANGE and th >= S_MIN_TO_HIGH:
            send(f"🌱 SEGAR {pair}\nnaik {chg:.1f}% dr low\n⚡ sisa ke high {th:.1f}%\nvol {vol/1e6:.2f}M")
        time.sleep(0.3)

if __name__ == "__main__":
    main()
