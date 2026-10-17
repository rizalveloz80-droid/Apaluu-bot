# V29.4 FINAL COMBO - ANTI-BLANK LOG & FIX MATCHING - LAST EDIT 18 OKT 2026
import requests, os, json
from datetime import datetime

# Filter koin besar yang sudah Anda DCA + Stablecoin
BLACKLIST = ["usdt_idr","usdc_idr","xaut_idr","paxg_idr","idrt_idr","ouros_idr","btc_idr","eth_idr","xrp_idr","sol_idr","hype_idr","sui_idr"]
CACHE_FILE = "price_cache.json"
TELE_TOKEN = os.getenv("TELE_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
TELE_CHAT_ID = os.getenv("TELE_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID")

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT_ID: 
        print("-> Gagal Kirim Telegram: Token atau Chat ID Kosong!")
        return
    try: 
        requests.post(f"https://telegram.org{TELE_TOKEN}/sendMessage", data={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=15)
        print("-> Berhasil Kirim Telegram!")
    except Exception as e: 
        print(f"-> Gagal Kirim Telegram, Error: {e}")

def smart_combo(chg, chg_vol_1m, dl, dh, vol):
    sq = dl + dh
    
    # FILTER UTAMA LIKUIDITAS: Minimal volume 24 jam 400 Juta IDR agar terhindar koin mati
    if vol < 400000000:
        return "NORMAL", sq

    # ==========================================
    # LOGIKA GABUNGAN 1: DETEKSI CURI START / RUNNING (VOLUME SPIKE)
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
    # PRE - VOL BESAR
    if 0 <= dl <= 2.5 and sq < 9 and -2 <= chg <= 2.5 and vol >= 100000000: return "PRE", sq
    # DALEM BOTTOM PAS
    if -25 <= chg <= -2.2 and 0 <= dl <= 1.5 and sq < 20 and vol >= 20000000: return "DALEM", sq
    
    return "NORMAL", sq

cache = {}
if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE,'r') as f: cache=json.load(f)
    except: pass

try: 
    print("Mengambil data market Indodax...")
    tickers = requests.get("https://indodax.com", timeout=15).json()["tickers"]
    print(f"Berhasil memuat {len(tickers)} pasang aset.")
except Exception as e: 
    print(f"Gagal mengambil API Indodax: {e}")
    exit()

cands=[]
new_cache = {}

for pair, data in tickers.items():
    if not pair.lower().endswith("_idr"): continue
    if pair.lower() in BLACKLIST: continue
    try:
        last=float(data["last"]); low=float(data["low"]); high=float(data["high"]); vol=float(data["vol_idr"])
        if last==0: continue
        
        dl=((last-low)/last)*100; dh=((high-last)/last)*100
        
        prev_data = cache.get(pair, {"price": last, "vol": vol})
        if isinstance(prev_data, dict):
            prev_price = prev_data.get("price", last)
            prev_vol = prev_data.get("vol", vol)
        else:
            prev_price = prev_data
            prev_vol = vol
            
        chg = ((last - prev_price) / prev_price * 100) if prev_price else 0
        chg_vol_1m = ((vol - prev_vol) / prev_vol * 100) if prev_vol else 0
        
        cat, sq = smart_combo(chg, chg_vol_1m, dl, dh, vol)
        if cat != "NORMAL" and cat != "SKIP": 
            cands.append({
                "pair": pair.upper().replace("_IDR", ""),
                "chg": chg,
                "dl": dl,
                "sq": sq,
                "vol": vol,
                "cat": cat,
                "chg_vol": chg_vol_1m
            })
            
        new_cache[pair] = {"price": last, "vol": vol}
    except: continue

with open(CACHE_FILE,'w') as f: json.dump(new_cache, f)

# Urutkan kandidat berdasarkan lonjakan volume menit terbaru (chg_vol)
cands.sort(key=lambda x: x["chg_vol"], reverse=True)

# Memperbaiki pencarian string kategori dari List Objek Dictionary
curi_start = [c for c in cands if c["cat"] == "CURI_START"][:5]
gold = [c for c in cands if c["cat"] == "GOLD"][:3]
silver = [c for c in cands if c["cat"] == "SILVER"][:3]
dalem = [c for c in cands if c["cat"] == "DALEM"][:3]

now = datetime.now().strftime('%H:%M')
msg = f"🛰️ V29.4 COMBO RADAR FLIGHT | {now}\n\n"

ada_sinyal = False

if curi_start:
    ada_sinyal = True
    msg += f"🔥 CURI START FLY ({len(curi_start)}):\n"
    for i, c in enumerate(curi_start, 1): 
        msg += f"{i}. {c['pair']} | +{c['chg']:.2f}% | Vol1m: +{c['chg_vol']:.0f}% | Total: {int(c['vol']/1000000)}jt\n"
    msg += "\n"

if gold:
    ada_sinyal = True
    msg += f"👑 GOLD JACKPOT ({len(gold)}):\n"
    for i, c in enumerate(gold, 1): 
        msg += f"{i}. {c['pair']} | +{c['chg']:.1f}% | Low {int(c['dl'])}% | sq {int(c['sq'])}%\n"
    msg += "\n"

if silver:
    ada_sinyal = True
    msg += f"🥈 SILVER ({len(silver)}):\n"
    for i, c in enumerate(silver, 1): 
        msg += f"{i}. {c['pair']} | +{c['chg']:.1f}% | Low {int(c['dl'])}%\n"
    msg += "\n"

if dalem:
    ada_sinyal = True
    msg += f"🛡️ DALEM / BOTTOM ({len(dalem)}):\n"
    for i, c in enumerate(dalem, 1): 
        msg += f"{i}. {c['pair']} | {c['chg']:.1f}% | BOTTOM MANTUL\n"
    msg += "\n"

msg += f"SCAN {len(tickers)} | DCA CLEAN | RADAR ACTIVE"

# Selalu paksa kirim ke Telegram agar Anda tahu bot tidak mati di server
print(msg)
send_tele(msg)
