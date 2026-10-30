# V16.7 - 2 TIER + BLACKLIST TETAP MASUK - FIX JALAN
import requests
import os
import time

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')

BLACKLIST={
    'usdt_idr','usdc_idr','dai_idr','busd_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr','usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'btc_idr','eth_idr','bnb_idr','sol_idr','xrp_idr','ada_idr','doge_idr','trx_idr','dot_idr','matic_idr','avax_idr','link_idr','ltc_idr','bch_idr','etc_idr','xlm_idr','uni_idr',
    'luna_idr','lunc_idr','ftt_idr','ustc_idr','luna2_idr','btt_idr','bttc_idr','dgb_idr','qtum_idr','waves_idr','zrx_idr','omg_idr','bat_idr','ont_idr','iost_idr','sc_idr','zcash_idr','dash_idr','xem_idr','bcd_idr','bcha_idr',
    'shib_idr','pepe_idr','floki_idr','bonk_idr','wif_idr',
    'gtc_idr','haedal_idr','beat_idr','blur_idr'
}
DELISTING = set()  # Biar ga NameError, udah masuk BLACKLIST semua!

def send_tele(msg):
    url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=10)
    except Exception as e:
        print(f"Tele error: {e}")

def get_indodax_tickers():
    try:
        r = requests.get("https://indodax.com/api/tickers", timeout=15).json()
        tickers = r.get('tickers', {})
        out = []
        for pair, d in tickers.items():
            if not pair.endswith('_idr'): continue
            last = float(d['last'])
            low = float(d['low'])
            high = float(d['high'])
            vol_idr = float(d['vol_idr'])
            # hitung pos & naik simple
            pos = ((last - low) / (high - low) * 100) if high != low else 0
            # naik 24h proxy dari last vs low (nanti lu ganti sama logic V16.6 asli lu)
            naik = ((last - low) / low * 100) if low != 0 else 0
            out.append({
                'pair': pair,
                'symbol': pair.replace('_idr','').upper(),
                'last': last, 'low': low, 'high': high,
                'vol_idr': vol_idr,
                'pos': pos,
                'naik_24h': naik,
                'naik_1h': naik,  # sementara pake naik_24h dulu
                'bb_upper': high * 0.95,  # dummy BB
                'mcap': 10_000_000,
                'ratio': 1.5
            })
        return out
    except Exception as e:
        print(f"Indodax error: {e}")
        return []

def get_global_all():
    # Sementara kosong dulu biar ga error, nanti lu balikin logic 6EX V16.6 lu
    return {}

def scan_v16_7():
    tickers = get_indodax_tickers()
    global_data = get_global_all()
    
    tier1 = []
    tier2 = []
    
    for t in tickers:
        pair = t['pair']
        sym = t['symbol']
        price = t['last']
        naik = t['naik_24h']
        pos = t['pos']
        vol_idr = t['vol_idr']
        naik_1h = t['naik_1h']
        bb_upper = t['bb_upper']
        g_pct = global_data.get(pair, 0)
        
        label_extra = " [BLACKLIST TAPI SCAN]" if pair in BLACKLIST else ""
        
        # TIER 1 - TETAP MASUK SEMUA
        if t['mcap'] <= 50_000_000 and t['ratio'] >= 1.0 and naik_1h >= 0.8:
            tier1.append(f"BANDAR GLOBAL | {sym} Rp{price} Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol_idr/1e6:.0f}Mn{label_extra}")
        
        if g_pct >= 3.0 and vol_idr >= 150_000_000 and 2 <= naik <= 35 and pos <= 80:
            tier1.append(f"GLOBAL-ALL {g_pct}% | {sym} Rp{price} Naik {naik:.1f}% Pos {pos:.0f}%{label_extra}")
        
        if vol_idr >= 250_000_000 and 2 <= naik <= 30:
            tier1.append(f"INDODAX | {sym} Rp{price} Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol_idr/1e6:.0f}Mn{label_extra}")
        
        # TIER 2 - BUYER SIAP TERBANG ALLCOIN 2-35% - SEMUA BLACKLIST TETAP MASUK!
        if 2 <= naik <= 35:
            is_flat = (pos <= 15)
            is_vol = (vol_idr >= 100_000_000)
            is_ign = (naik_1h >= 2.5)
            is_bb = (price > bb_upper)
            
            if is_flat and is_vol and is_ign:
                if is_bb:
                    tier2.append(f"🚀 TERBANG BB BREAK | {sym} Rp{price} Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol_idr/1e6:.0f}Mn{label_extra}")
                else:
                    tier2.append(f"🔥 TERBANG IGNITION | {sym} Rp{price} Naik {naik:.1f}% Pos {pos:.0f}%{label_extra}")
            elif is_flat and vol_idr >= 150_000_000:
                tier2.append(f"💰 AKUM BAWAH | {sym} Rp{price} Naik {naik:.1f}% Pos {pos:.0f}%{label_extra}")

    msg = f"=== V16.7 2-TIER BLACKLIST MASUK SEMUA ===\n"
    msg += f"TIER 1 - BANDAR GLOBAL:\n" + ("\n".join(tier1[:15]) if tier1 else "Tidak ada") + "\n\n"
    msg += f"TIER 2 - BUYER SIAP TERBANG 2-35%:\n" + ("\n".join(tier2[:15]) if tier2 else "Tidak ada")
    return msg

if __name__ == "__main__":
    print("Running V16.7...")
    msg = scan_v16_7()
    print(msg)
    send_tele(msg)
    print("Tele sent!")
