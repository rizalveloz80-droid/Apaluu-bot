import requests, os, time
from datetime import datetime, timezone, timedelta

# TETEP PUNYA LU YANG LAMA! GA GUE RUBAH!
TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')

INDO_MAX = "https://indodax.com/api/tickers"
TARGET_PCT = 10
CHECK_INTERVAL = 300  # 5 menit

def fnum(v, default=0.0):
    try:
        v = str(v).replace(',', '').strip()
        if not v:
            return default
        return float(v)
    except Exception:
        return default

def kirim_pesan(teks):
    try:
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        data = {"chat_id": TELE_CHAT_ID, "text": teks}
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"Gagal kirim: {e}")

def scan_koin():
    try:
        data = requests.get(INDO_MAX, timeout=15).json().get("tickers", {})
    except Exception as e:
        print(f"Gagal ambil data: {e}")
        return []
    hasil = []
    for pair, info in data.items():
        if not pair.endswith("_idr"):
            continue
        name = pair.replace("_idr", "").upper()
        last = fnum(info.get("last"))
        tinggi = fnum(info.get("high"))
        rendah = fnum(info.get("low"))

        if rendah <= 0 or last < 20:
            continue

        range_pct = ((tinggi - rendah) / rendah) * 100
        
        if range_pct < 1.5:
            kategori = "SINYAL"
        elif range_pct <= 5.0:
            kategori = "PEMULA"
        else:
            continue
            
        entry = last
        target = entry * (1 + TARGET_PCT / 100)
        hasil.append({"name": name, "kategori": kategori,
                      "range": range_pct, "harga": entry,
                      "target": target})
                      
    hasil.sort(key=lambda x: (x["kategori"] != "SINYAL", x["range"]))
    return hasil

def format_hasil(koin_list):
    wib = timezone(timedelta(hours=7))
    now = datetime.now(wib).strftime("%H:%M")
    if not koin_list:
        return f"SCAN SINYAL {now} WIB\nTidak ada koin spot dalam range 1.5-5% saat ini."
    
    header = f"SCAN SINYAL {now} WIB | {len(koin_list)} koin\n\n"
    baris = []
    for k in koin_list:
        emoji = "🔔 SINYAL" if k["kategori"] == "SINYAL" else "🌱 PEMULA"
        baris.append(f"{emoji} | {k['name']} | Range {k['range']:.2f}% | "
                     f"Entry Rp {k['harga']:,.0f} | Target Rp {k['target']:,.0f}")
    return header + "\n".join(baris)

harga_sebelumnya = {}

def cek_breakout(hasil):
    global harga_sebelumnya
    alert = []
    for k in hasil:
        name = k["name"]
        harga = k["harga"]
        if name in harga_sebelumnya:
            perubahan = ((harga - harga_sebelumnya[name]) / harga_sebelumnya[name]) * 100
            if perubahan > 3.0:
                alert.append(f"🚀 BREAKOUT! {name} naik {perubahan:.2f}% dalam 5 menit! Rp {harga:,.0f}")
        harga_sebelumnya[name] = harga
    return alert

def main():
    print("Bot scan spot Indodax dimulai...")
    kirim_pesan("Bot Scan SPOT Indodax aktif! Cek tiap 5 menit. Target +10%.")
    while True:
        try:
            hasil = scan_koin()
            kirim_pesan(format_hasil(hasil))
            for alert in cek_breakout(hasil):
                kirim_pesan(alert)
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("Bot dihentikan.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
