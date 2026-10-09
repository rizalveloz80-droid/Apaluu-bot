import requests, os, pytz, datetime

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
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

        if low==0 or vol_idr < 10000000: continue
        if last < 10: continue

        naik = ((last - low) / low) * 100
        total = ((high - low) / low) * 100

        if total > 20.0: continue # H-L max 20%
        if 3.0 <= naik <= 12.0:
            hasil.append((koin.upper(), naik, total, vol_idr))
    except:
        continue

hasil = sorted(hasil, key=lambda x: x[1], reverse=True)
total_koin = len(hasil)
top15 = hasil[:15]

# ANTI-SPAM
koin_saat_ini = ",".join([x[0] for x in top15])
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
pesan = f"⏳ BARU MAU PUMP {wib} WIB\nScan {len(data)} | {total_koin} koin BARU MAU (H-L<20%) | TOP 15:\n\n"
for koin, naik, hl, vol in top15:
    vol_jt = int(vol/1000000)
    pesan += f"👀 {koin} +{naik:.1f}% (H-L {hl:.1f}%) Vol {vol_jt}jt\n"
pesan += f"\nTotal {total_koin} koin fase awal"

requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": pesan})
print(f"KIRIM {total_koin} koin")
