import requests, os, time
from datetime import datetime, timedelta, timezone

TELE_TOKEN = os.getenv('TELE_TOKEN') or os.getenv('TELEGRAM_BOT_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID') or os.getenv('TELEGRAM_CHAT_ID')

def kirim(teks):
    try:
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        r = requests.post(url, data={"chat_id": TELE_CHAT_ID, "text": teks, "parse_mode": "Markdown"}, timeout=10)
        print(f"TELE {r.status_code}: {teks[:50]}")
    except Exception as e:
        print(f"TELE GAGAL: {e}")

def get_depth(pair):
    try:
        r = requests.get(f"https://indodax.com/api/{pair}/depth", timeout=4).json()
        buy = sum(float(x[0])*float(x[1]) for x in r.get('buy',[])[:15])
        sell = sum(float(x[0])*float(x[1]) for x in r.get('sell',[])[:15])
        return buy, sell, buy/sell if sell else 0
    except: return 0,0,0

def get_hijau(pair):
    try:
        trades = requests.get(f"https://indodax.com/api/{pair}/trades", timeout=3).json()[:10]
        hijau = sum(1 for i in range(len(trades)-1) if float(trades[i]['price']) >= float(trades[i+1]['price']))
        return hijau
    except: return 0

def scan():
    wib = timezone(timedelta(hours=7))
    now_str = datetime.now(wib).strftime("%H:%M WIB")
    try:
        tickers = requests.get("https://indodax.com/api/tickers", timeout=10).json().get("tickers",{})
    except Exception as e:
        print(f"Gagal ambil ticker: {e}")
        return

    segar = []
    hunter = []
    
    for pair, t in tickers.items():
        if not pair.endswith("_idr"): continue
        try:
            last = float(t.get("last",0)); low = float(t.get("low",0)); high = float(t.get("high",0))
            vol = float(t.get("vol_idr",0))
            if low<=0 or last<10 or vol<10_000_000: continue  # 10Mn biar ga KOSONG
            
            chg = (last-low)/low*
