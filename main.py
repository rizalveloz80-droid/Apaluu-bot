import requests, os
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')

INDO_MAX = "https://indodax.com/api/tickers"
TARGET_PCT = 10

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
        hasil.append({"name": name, "kategori": kategori, "range": range_pct, "harga": entry, "target": target})
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
        baris.append(f"{emoji} | {k['name']} | Range {k['range']:.2f}% | Entry Rp {k['harga']:,.0f} | Target Rp {k['target']:,.0f}")
    return header + "\n".join(baris)

# JALAN SEKALI AJA! BIAR HIJAU!
hasil = scan_koin()
msg = format_hasil(hasil)
print(msg)
kirim_pesan(msg)
