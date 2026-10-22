import requests, os, datetime

# === V15.3 UNIVERSAL - FINAL ===
VOL_MIN = 10_000_000
RATIO_MIN = 0.6
S_MIN_CHG = 0.8
H_MIN_CHG = 4.0
MAX_CHG = 30.0
GREEN_MIN = 2
TH_MIN = 2.0
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_tele(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except: pass

def get_ticker():
    try:
        r = requests.get("https://indodax.com/api/tickers", timeout=15).json()
        return r.get("tickers", {})
    except: return {}

def get_trades(pair, limit=10):
    try:
        # ambil 10 trade terakhir buat hitung ijo
        url = f"https://indodax.com/api/trades/{pair}"
        r = requests.get(url, timeout=10).json()
        trades = r.get("trades", [])[:limit]
        green = 0
        for t in trades:
            # di indodax type buy = ijo (buyer take)
            if t.get("type") == "buy":
                green += 1
        return green
    except: return 0

def get_depth_ratio(pair):
    try:
        # ambil orderbook buat B/S ratio
        url = f"https://indodax.com/api/depth/{pair}"
        r = requests.get(url, timeout=10).json()
        # indodax depth format beda2, coba handle
        buy_vol = sum([float(x[1]) * float(x[0]) for x in r.get("buy", [])[:10]])
        sell_vol = sum([float(x[1]) * float(x[0]) for x in r.get("sell", [])[:10]])
        if sell_vol == 0: return 999
        return buy_vol / sell_vol
    except: return 0

tickers = get_ticker()
now = datetime.datetime.now().strftime("%H:%M WIB")
hasil_segar = []
hasil_hunter = []

for pair, data in tickers.items():
    if not pair.endswith("_idr"): continue
    try:
        last = float(data.get("last", 0))
        low = float(data.get("low", 0))
        high = float(data.get("high", 0))
        vol_idr = float(data.get("vol_idr", 0))
        
        if low == 0 or last == 0: continue
        if vol_idr < VOL_MIN: continue
        
        chg = ((last - low) / low) * 100
        if chg < S_MIN_CHG: continue
        if chg > MAX_CHG: continue
        
        # TH = jarak ke high
        th = ((high - last) / last) * 100 if last>0 else 0
        if th < TH_MIN and chg > 10: # kalo udah tinggi, harus masih ada ruang 2% ke high
            continue
        if th < 0: continue # udah break high ga usah
        
        # B/S Ratio
        ratio = get_depth_ratio(pair)
        if ratio < RATIO_MIN: continue
        
        # Green count
        green = get_trades(pair, 10)
        
        # LOGIKA ANTI PUCUK V15.3
        need_green = GREEN_MIN
        if chg > 15: # kalo udah naik 15%+ dari low 24jam, wajib ijo 3x (bandar masih jaga)
            need_green = 3
        
        if green < need_green: continue
        
        # Masuk kategori
        if chg <= H_MIN_CHG:
            hasil_segar.append(f"🌱 {pair.upper()} {chg:.2f}% Vol {vol_idr/1e9:.1f}Bn B/S {ratio:.2f}x Ijo {green}x TH {th:.1f}%")
        else:
            hasil_hunter.append(f"🔥 {pair.upper()} {chg:.2f}% Vol {vol_idr/1e9:.1f}Bn B/S {ratio:.2f}x Ijo {green}x TH {th:.1f}%")
            
    except: continue

# Kirim hasil
if not hasil_segar and not hasil_hunter:
    send_tele(f"KOSONG - Market sepi bener\nSCAN {now} | V15.3 UNIVERSAL 10Mn\nFilter Vol 10Mn B/S 0.6x Ijo 2x(3x jika >15%) TH
