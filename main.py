# V29.8 FINAL COMBO - BYPASS APIS SUMMARIES ULTRA SAFE - LAST EDIT 18 OKT 2026
import requests, os, json, time
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
    if chg <= -1.5 and dl <= 2.0 and vol >= 30000000: return "SKIP", sq
    if 0 <= dl <= 8 and sq < 12 and -1.5 <= chg <= 4 and vol >= 15000000: return "GOLD", sq
    if 0 <= dl <= 10 and sq < 16 and -1.5 <= chg <= 6 and vol >= 15000000: return "SILVER", sq
    if 0 <= dl <= 2.5 and sq < 9 and -2 <= chg <= 2.5 and vol >= 100000000: return "PRE", sq
    if -25 <= chg <= -2.2 and 0 <= dl <= 1.5 and sq < 20 and vol >= 20000000: return "DALEM", sq
    
    return "NORMAL", sq

cache = {}
if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE,'r') as f: cache=json.load(f)
    except: pass

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

# JALUR ALTERNATIF UTAMA: Menggunakan data rangkuman pasar yang keamanannya lebih longgar
url_summaries = "https://indodax.com"
data_market = None

print(f"Menembus pasar Indodax via jalur summaries {url_summaries}...")

for attempt in range(1, 4):
    try:
        res = requests.get(url_summaries, headers=headers, timeout=15)
        data_market = res.json()
        print(f"Jalur summaries tembus! Berhasil memuat data market pada percobaan ke-{attempt}.")
        break
    except Exception as e:
        print(f"Percobaan jalur summaries ke-{attempt} gagal. Error: {e}")
        if attempt < 3:
            time.sleep(2)
        else:
            print("Seluruh jalur akses Indodax diblokir oleh Cloudflare.")
            exit()

cands = []
new_cache = {}

# Parsing data berdasarkan struktur JSON ticker summaries indodax
tickers = data_market.get("tickers", {})

for pair, data in tickers.items():
    if not pair.lower().endswith("_idr"): continue
    if pair.lower() in BLACKLIST: continue
    try:
        last = float(data.get("last", 0))
        low = float(data.get("low", 0))
        high = float(data.get("high", 0))
        # summaries menggunakan string/float vol_idr langsung
        vol = float(data.get("vol_idr", 0))
        if last == 0: continue
        
        dl = ((last - low) / last) * 100
        dh = ((high - last) / last) * 100
        
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

cands.sort(key=lambda x: x["chg_vol"], reverse=True)

curi_start = [c for c in cands if c["cat"] == "CURI_START"][:5]
gold = [c for c in cands if c["cat"] == "GOLD"][:3]
silver = [c for c in cands if c["cat"] == "SILVER"][:3]
dalem = [c for c in cands if c["cat"] == "DALEM"][:3]

now = datetime.now().strftime('%H:%M')
msg = f"🛰️ V29.8 SUMMARIES RADAR | {now}\n\n"

if curi_start:
    msg += f"🔥 CURI START FLY ({len(curi_start)}):\n"
    for i, c in enumerate(curi_start, 1): 
        msg += f"{i}. {c['pair']} | +{c['chg']:.2f}% | Vol1m: +{c['chg_vol']:.0f}% | Total: {int(c['vol']/1000000)}jt\n"
    msg += "\n"

if gold:
    msg += f"👑 GOLD JACKPOT ({len(gold)}):\n"
    for i, c in enumerate(gold, 1): 
        msg += f"{i}. {c['pair']} | +{c['chg']:.1f}% | Low {int(c['dl'])}% | sq {int(c['sq'])}%\n"
    msg += "\n"

if silver:
    msg += f"🥈 SILVER ({len(silver)}):\n"
    for i, c in enumerate(silver, 1): 
        msg += f"{i}. {c['pair']} | +{c['chg']:.1f}% | Low {int(c['dl'])}%\n"
    msg += "\n"

if dalem:
    msg += f"🛡️ DALEM / BOTTOM ({len(dalem)}):\n"
    for i, c in enumerate(dalem, 1): 
        msg += f"{i}. {c['pair']} | {c['chg']:.1f}% | BOTTOM MANTUL\n"
    msg += "\n"

msg += f"SCAN {len(tickers)} | DCA CLEAN | RADAR ACTIVE"

print(msg)
send_tele(msg)
