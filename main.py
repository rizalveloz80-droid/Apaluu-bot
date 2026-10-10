import requests, os, pytz, datetime, time

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

GAIN_MIN, GAIN_MAX = 0.5, 6.0
HL_MIN, HL_MAX = 2.0, 8.0
VOL_MIN = 100000000
HARGA_MAX = 15000
BLACKLIST = ["BTC","ETH","USDT","USDC"]

def cek_borongan_safe(sym):
    try:
        r = requests.get(f"https://indodax.com/api/trades/{sym.lower()}_idr", timeout=4)
        trades = r.json().get("trades", [])[:80]
        if len(trades) < 20: return False, 0, 0
        buys = sum(1 for t in trades if t['type']=='buy')
        buy_ratio = buys/len(trades)*100
        now = int(time.time())
        v15 = sum(float(t['price'])*float(t['amount']) for t in trades if now-int(t['date'])<=900)
        v60 = sum(float(t['price'])*float(t['amount']) for t in trades if now-int(t['date'])<=3600)
        spike = (v15*4/v60) if v60>0 else 0
        return (buy_ratio>=65 and spike>=1.8), buy_ratio, spike
    except:
        return False, 0, 0 # Kalau error API, anggap ga borongan biar ga crash

# 1. SCAN AWAL CEPAT (tanpa cek trades dulu biar ga berat)
tickers = requests.get("https://indodax.com/api/tickers", timeout=10).json()["tickers"]
kandidat = []
for koin, t in tickers.items():
    try:
        sym = koin.upper().replace("_IDR","")
        if sym in BLACKLIST: continue
        last, low, high, vol = float(t["last"]), float(t["low"]), float(t["high"]), float(t["vol_idr"])
        if low==0 or last<10 or last>HARGA_MAX or vol<VOL_MIN: continue
        naik = (last-low)/low*100
        total = (high-low)/low*100
        if not (GAIN_MIN<=naik<=GAIN_MAX and HL_MIN<=total<=HL_MAX): continue
        kandidat.append((sym, naik, total, vol))
    except: continue

# Urut H-L terkecil dulu (paling fresh)
kandidat = sorted(kandidat, key=lambda x: x[2])[:15] # Ambil 15 teratas aja biar ga spam API

# 2. CEK BORONGAN HANYA 15 KOIN ITU (jadi ga eror / ga kena ban Indodax)
hasil = []
for sym, naik, hl, vol in kandidat:
    is_borong, br, sp = cek_borongan_safe(sym)
    # Jika buy_ratio 0 (API gagal) tetep masukin, kalau ada buy_ratio harus lolos borongan
    if br==0 or is_borong:
        hasil.append((sym, naik, hl, vol, br, sp))
    time.sleep(0.2) # Jeda 0.2 detik biar ga spam

# ANTI-SPAM
koin_str = ",".join([x[0] for x in hasil])
try:
    with open("last.txt","r") as f: last = f.read()
except: last = ""
if koin_str==last and hasil:
    print("SKIP spam"); exit()
with open("last.txt","w") as f: f.write(koin_str)

wib = datetime.datetime.now(pytz.timezone('Asia/Jakarta')).strftime('%H:%M')
if not hasil:
    pesan = f"⏳ HUNTER ALL COIN {wib} WIB\nScan {len(tickers)} | 0 signal (Gain {GAIN_MIN}-{GAIN_MAX}% H-L<{HL_MAX}% Vol>{VOL_MIN//1000000}jt)"
else:
    pesan = f"🚨 BORONGAN ALL COIN {wib} WIB\nScan {len(tickers)} | {len(hasil)} signal | TOP:\n\n"
    for sym, naik, hl, vol, br, sp in hasil:
        vol_jt = int(vol/1000000)
        vstr = f"{vol_jt/1000:.1f}M" if vol_jt>=1000 else f"{vol_jt}jt"
        if br>0:
            pesan += f"🔥 {sym} +{naik:.1f}% H-L{hl:.1f}% V{vstr} BUY{br:.0f}% Sp{sp:.1f}x\n"
        else:
            pesan += f"👀 {sym} +{naik:.1f}% H-L{hl:.1f}% V{vstr}\n"
    pesan += f"\nFilter: Gain {GAIN_MIN}-{GAIN_MAX}% H-L {HL_MIN}-{HL_MAX}% Vol>{VOL_MIN//1000000}jt | All Coin Hunter"

# KIRIM ANTI-ERROR 23:25 (potong 3500 karakter)
def kirim(txt):
    try:
        for i in range(0, len(txt), 3500):
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id":CHAT_ID,"text":txt[i:i+3500]}, timeout=10)
    except Exception as e:
        print(f"Gagal kirim tele: {e}")

kirim(pesan)
print(f"OK kirim {len(hasil)}")
