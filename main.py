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
        if len(trades) < 20: return 0, 0
        buys = sum(1 for t in trades if t['type']=='buy')
        buy_ratio = buys/len(trades)*100
        now = int(time.time())
        v15 = sum(float(t['price'])*float(t['amount']) for t in trades if now-int(t['date'])<=900)
        v60 = sum(float(t['price'])*float(t['amount']) for t in trades if now-int(t['date'])<=3600)
        spike = (v15*4/v60) if v60>0 else 0
        return buy_ratio, spike
    except:
        return 0, 0

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

# URUT: Vol gede + H-L kecil = paling potensial pump
kandidat = sorted(kandidat, key=lambda x: (-x[3], x[2]))[:12]

hasil = []
for sym, naik, hl, vol in kandidat:
    br, sp = cek_borongan_safe(sym)
    # Hitung Skor Potensi Pump (mirip STIK/MAGIC)
    # Gain kecil + H-L kecil + Vol gede = skor tinggi
    skor = (vol/100000000) / (hl+1) / (naik+1)
    hasil.append((sym, naik, hl, vol, br, sp, skor))
    time.sleep(0.15)

# AMBIL TOP 7 PALING BRUTAL
hasil = sorted(hasil, key=lambda x: -x[6])[:7]

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
    pesan = f"⏳ HUNTER TOP7 {wib} WIB\nScan {len(tickers)} | Belum ada yang fresh"
else:
    pesan = f"🚨 TOP 7 BORONGAN {wib} WIB\nScan {len(tickers)} | {len(hasil)} koin paling fresh siap pump:\n\n"
    for i, (sym, naik, hl, vol, br, sp, skor) in enumerate(hasil, 1):
        vol_jt = int(vol/1000000)
        vstr = f"{vol_jt/1000:.1f}M" if vol_jt>=1000 else f"{vol_jt}jt"
        # Kasih label potensi
        if i<=3:
            label = "🔥🔥 POTENSI 68%"
        elif i<=5:
            label = "🔥 POTENSI 40%"
        else:
            label = "👀 WATCH"

        if br>=65:
            pesan += f"{i}. {label} {sym} +{naik:.1f}% H-L{hl:.1f}% V{vstr} BUY{br:.0f}%\n"
        else:
            pesan += f"{i}. {label} {sym} +{naik:.1f}% H-L{hl:.1f}% V{vstr}\n"

    pesan += f"\nFilter: Gain {GAIN_MIN}-{GAIN_MAX}% H-L {HL_MIN}-{HL_MAX}% | All Coin Hunter 24JAM"
    pesan += f"\nFokus No 1-3 aja min!"

def kirim(txt):
    for i in range(0, len(txt), 3500):
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id":CHAT_ID,"text":txt[i:i+3500]}, timeout=10)

kirim(pesan)
print(f"OK TOP7 kirim {len(hasil)}")
