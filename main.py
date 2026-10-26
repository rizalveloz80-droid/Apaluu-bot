import requests
from datetime import datetime

# PAKAI TOKE LAMA LU YANG V8.5 - JANGAN GANTI!
TELE_TOKEN = "PAKAI_TOKE_LAMA_LU"
TELE_CHAT_ID = "PAKAI_CHAT_ID_LAMA_LU"

def get_tickers():
    r = requests.get("https://indodax.com/api/tickers", timeout=15).json()['tickers']
    coins = []
    for pair, d in tickers.items():
        if not pair.endswith('_idr'): continue
        last = float(d['last'])
        high = float(d['high'])
        low = float(d['low'])
        vol = float(d['vol_idr'])
        mid = (high + low) / 2
        naik = abs((last - mid) / mid * 100) if mid>0 else 0
        jauh = ((high - last) / high * 100) if high>0 else 0
        score = naik + (jauh * 0.5)
        coins.append({'symbol': pair.replace('_idr','').upper(), 'price': last, 'naik': naik, 'jauh': jauh, 'vol': vol, 'score': score})
    return coins

# ========== V8.5 ASLI LU - JANGAN DIUBAH! ==========
def v85_ranking_kebalik_46_block(coins):
    filtered = [c for c in coins if c['vol'] > 10_000_000 and c['jauh'] < 20 and c['naik'] < 10]
    sorted_all = sorted(filtered, key=lambda x: x['score'])
    return sorted_all[:10], len(sorted_all), sorted_all
# ===================================================

# ========== TAMBAHAN BARU V9 - CUMA INI! #11-15 ==========
def v9_running_5_block(coins):
    running = [c for c in coins if 0 <= c['jauh'] <= 2.5 and c['naik'] >= 6 and c['vol'] >= 200_000_000]
    return sorted(running, key=lambda x: x['vol'], reverse=True)[:5]
# ========================================================

def kirim_tele(pesan):
    url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELE_CHAT_ID, "text": pesan})

def main():
    coins = get_tickers()
    
    # V8.5 LAMA - TETEP!
    top10, total_46, all_46 = v85_ranking_kebalik_46_block(coins)
    
    # V9 BARU - TAMBAHAN #11-15
    running5 = v9_running_5_block(coins)

    jam = datetime.now().strftime("%H:%M WIB %d-%m")
    
    # PESAN TELE V8.5 ASLI + TAMBAHAN V9
    msg = f"EARLY {jam}\nV9.0 RANKING KEBALIK {total_46} block + 5 RUNNING\n-----\n"
    for i,c in enumerate(top10,1):
        label = "ENTRY NOW" if i<=3 else "WATCH" if i<=6 else "SKIP TINGGI"
        vol = f"{c['vol']/1_000_000:.0f}Mn"
        msg += f"#{i} {label} | {c['symbol']} Rp{int(c['price']):,} Naik {c['naik']:.1f}% Jauh {c['jauh']:.0f}% Vol {vol} Score {c['score']:.1f}\n"
    
    # BLOK BARU - INI YANG LU MAU #11-15
    msg += f"\n----- V9 RUNNING | {len(running5)} block -----\n"
    if not running5:
        msg += "Tidak ada RUNNING\n"
    else:
        for j,c in enumerate(running5,11):
            vol = f"{c['vol']/1_000_000_000:.2f}Bn" if c['vol']>=1e9 else f"{c['vol']/1_000_000:.0f}Mn"
            msg += f"#{j} RUNNING | {c['symbol']} Rp{int(c['price']):,} Naik {c['naik']:.1f}% Jauh {c['jauh']:.0f}% Vol {vol} Score {c['score']:.1f}\n"
    
    msg += "\n----- GLOBAL LEAD: Sinkron -----"
    print(msg)
    kirim_tele(msg)

if __name__ == "__main__":
    main()
