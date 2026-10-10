import requests, os, pytz, datetime

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

url = "https://indodax.com/api/tickers"
data = requests.get(url).json()["tickers"]

hasil = []
for koin, t in data.items():
    try:
        last = float(t["last"])
        low = float(t["low"])
        high = float(t["high"])
        vol_idr = float(t["vol_idr"])

        if low==0: continue
        # --- SETTING BARU PERKETAT ---
        if vol_idr < 200000000: continue # Vol <200jt skip (dulu 10jt)
        if last < 10: continue

        naik = ((last - low) / low) * 100
        total = ((high - low) / low) * 100

        if total > 13.0: continue # H-L max 13% (dulu 20% kelonggaran)
        if 7.0 <= naik <= 13.0: # Gain 7-13% (dulu 3-12% kebanyakan)
            hasil.append((koin.upper(), naik, total, vol_idr))
    except:
        continue

# Urut paling fresh H-L terkecil + Vol gede (dulu urut gain doang)
hasil = sorted(hasil, key=lambda x: (x[2], -x[3]))
total_koin = len(hasil)
top30 = hasil[:30] # Kirim max 30 (dulu top 15 tapi total_koin 124)

# ANTI-SPAM (tetep pake punya kamu)
koin_saat_ini = ",".join([x[0] for x in top30])
try:
    with open("last.txt","r") as f:
        last_data = f.read()
except:
    last_data = ""

if koin_saat_ini == last_data and total_koin!= 0:
    print(f"SKIP spam - {total_koin} koin sama")
    exit()

with open("last.txt","w") as f:
    f.write(koin_saat_ini)

wib = datetime.datetime.now(pytz.timezone('Asia/Jakarta')).strftime('%H:%M')

if total_koin == 0:
    pesan = f"⏳ BARU MAU PUMP {wib} WIB\nScan {len(data)} | Ga ada yang fresh (H-L<13% Vol>200jt)"
else:
    pesan = f"⏳ BARU MAU PUMP {wib} WIB\nScan {len(data)} | {total_koin} koin FRESH (H-L<13% Vol>200jt) | TOP {len(top30)}:\n\n"
    for koin, naik, hl, vol in top30:
        vol_jt = int(vol/1000000)
        # Format Vol biar cakep kayak VELVET 244jt
        if vol_jt >= 1000:
            vol_str = f"{vol_jt/1000:.1f}M"
        else:
            vol_str = f"{vol_jt}jt"
        pesan += f"👀 {koin} +{naik:.1f}% (H-L {hl:.1f}%) Vol {vol_str}\n"
    pesan += f"\nFilter: Gain 7-13% | H-L <13% | Vol >200jt"

# ANTI GAGAL 23:25 - Potong pesan kalau kepanjangan
def kirim(pesan_kirim):
    for i in range(0, len(pesan_kirim), 3500):
        chunk = pesan_kirim[i:i+3500]
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": chunk})

kirim(pesan)
print(f"KIRIM {total_koin} koin fresh (dari {len(data)} scan)")
