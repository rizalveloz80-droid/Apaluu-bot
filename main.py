# V29.1 COMBO - ALTCOIN MURNI & EARLY RADAR - LAST EDIT 18 OKT 2026
import requests, os, json
from datetime import datetime

# Filter koin besar yang sudah Anda DCA + Stablecoin
BLACKLIST = ["usdt_idr","usdc_idr","xaut_idr","paxg_idr","idrt_idr","ouros_idr","btc_idr","eth_idr","xrp_idr","sol_idr","hype_idr","sui_idr"]
CACHE_FILE = "price_cache.json"
TELE_TOKEN = os.getenv("TELE_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
TELE_CHAT_ID = os.getenv("TELE_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID")

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT_ID: return
    try: requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", data={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=15)
    except: pass

def smart_combo(chg, chg_vol_1m, dl, dh, vol):
    sq = dl + dh
    
    # FILTER UTAMA LIKUIDITAS: Minimal volume 24 jam 400 Juta IDR agar terhindar koin mati
    if vol < 400000000:
        return "NORMAL", sq

    # ==========================================
    # LOGIKA GABUNGAN 1: DETEKSI CURI START / RUNNING (VOLUME SPIKE)
    # Harga menit ini mulai merangkak naik (0.3% - 1.8%), volume menit ini melonjak > 45% dari menit lalu,
    # dan ruang ke atas masih longgar (dh >= 1.0%), artinya belum mentok pucuk.
    # ==========================================
    if 0.3 <= chg <= 1.8 and chg_vol_1m >= 45.0 and dh >= 1.0:
        return "CURI_START", sq

    # ==========================================
    # LOGIKA GABUNGAN 2: PARAMETER DATA HISTORIS LAMA (V28.4)
    # ==========================================
    # SKIP OGN JEBOL
    if chg <= -1.5 and dl <= 2.0 and vol >= 30000000: return "SKIP", sq
    # GOLD VALID
    if 0 <= dl <= 8 and sq < 12 and -1.5 <= chg <= 4 and vol >= 15000000: return "GOLD", sq
    # SILVER
    if 0 <= dl <= 10 and sq < 16 and -1.5 <= chg <= 6 and vol >= 15000000: return "SILVER", sq
    # PRE - DIUBAH MENGIKUTI STRATEGI CURI START VOLUME TEBAL
    if 0 <= dl <= 2.5 and sq < 9 and -2 <= chg <= 2.5 and vol >= 100000000: return "PRE", sq
    # DALEM BOTTOM PAS (Ditingkatkan dengan pantulan volume awal)
    if -25 <= chg <= -2.2 and 0 <= dl <= 1.5 and sq < 20 and vol >= 20000000: return "DALEM", sq
    
    return "NORMAL", sq

cache = {}
if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE,'r') as f: cache=json.load(f)
    except: pass

try: tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json()["tickers"]
except: exit()

cands=[]
new_cache = {}

for pair, data in tickers.items():
    if not pair.lower().endswith("_idr"): continue
    if pair.lower() in BLACKLIST: continue
    try:
        last=float(data["last"]); low=float(data["low"]); high=float(data["high"]); vol=float(data["vol_idr"])
        if last==0: continue
        
        dl=((last-low)/last)*100; dh=((high-last)/last)*100
        
        # Ambil data terstruktur dari cache menit lalu
        prev_data = cache.get(pair, {"price": last, "vol": vol})
        # Handle jika cache lama masih bertipe float harga saja
        if isinstance(prev_data, dict):
            prev_price = prev_data.get("price", last)
            prev_vol = prev_data.get("vol", vol)
        else:
            prev_price = prev_data
            prev_vol = vol
            
        # Hitung perubahan harga & volume per 1 menit
        chg = ((last - prev_price) / prev_price * 100) if prev_price else 0
        chg_vol_1m = ((vol - prev_vol) / prev_vol * 100) if prev_vol else 0
        
        cat, sq = smart_combo(chg, chg_vol_1m, dl, dh, vol)
        if cat != "NORMAL" and cat != "SKIP": 
            cands.append((pair.upper().replace("_IDR", ""), chg, dl, sq, vol, cat, chg_vol_1m))
            
        # Simpan struktur baru ke cache harian
        new_cache[pair] = {"price": last, "vol": vol}
    except: continue

with open(CACHE_FILE,'w') as f: json.dump(new_cache, f)

# Urutkan kandidat berdasarkan lonjakan volume menit terbaru
cands.sort(key=lambda x: x[6], reverse=True)

top = cands[:500]
curi_start = [c for c in top if c[5]=="CURI_START"][:5]
gold = [c for c in top if c[5]=="GOLD"][:3]
silver = [c for c in top if c[5]=="SILVER"][:3]
pre = [c for c in top if c[5]=="PRE"][:2]
dalem = [c for c in top if c[5]=="DALEM"][:3]

now = datetime.now().strftime('%H:%M')
msg = f"🛰️ V29.1 COMBO EARLY RADAR | {now}\n\n"

if curi_start:
    msg += f"🔥 CURI START FLY ({len(curi_start)}):\n"
    for i, c in enumerate(curi_start, 1): 
        msg += f"{i}. {c[0]} | +{c[1]:.2f}% | Vol1m: +{c[6]:.0f}% | Total:{int(c[4]/1000000)}jt\n"
    msg += "\n"

if gold:
    msg += f"👑 GOLD JACKPOT ({len(gold)}):\n"
    for i, c in enumerate(gold, 1): 
        msg += f"{i}. {c[0]} {c[1]:.1f}% | Low {int(c[2])}% | sq{int(c[3])}%\n"
    msg += "\n"

if silver:
    msg += f"🥈 SILVER ({len(silver)}):\n"
    for i, c in enumerate(silver, 1): 
        msg += f"{i}. {c[0]} {c[1]:.1f}% | Low {int(c[2])}%\n"
    msg += "\n"

if dalem:
    msg += f"🛡️ DALEM / BOTTOM ({len(dalem)}):\n"
    for i, c in enumerate(dalem, 1): 
        msg += f"{i}. {c[0]} {c[1]:.1f}% | BOTTOM MANTUL\n"
    msg += "\n"

total_valid = len(curi_start + gold + silver + dalem)
if total_valid > 0:
    msg += f"SCAN {len(tickers)} | DCA CLEAN | HYPE ALERT!"
    print(msg)
    send_tele(msg)
else:
    print(f"[{now}] Hasil scan bersih, tidak ada sinyal akumulasi kilat harian.")
