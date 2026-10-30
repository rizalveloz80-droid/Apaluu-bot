# V16.7 - 2 TIER + BLACKLIST DELISTING TETAP MASUK
# TIER 1 BANDAR GLOBAL TETAP + TIER 2 BUYER SIAP TERBANG ALLCOIN 2-35%

import requests

# BLACKLIST + DELISTING DARI VERSI SEBELUMNYA - MASUKIN SEMUA BIAR AMAN! LENGKAP!
BLACKLIST={
    # Stablecoin & Wrapped - LENGKAP
    'usdt_idr','usdc_idr','dai_idr','busd_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr','usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr','wbtc_idr',
    # Big Cap - ga usah di scan bandar
    'btc_idr','eth_idr','bnb_idr','sol_idr','xrp_idr','ada_idr','doge_idr','trx_idr','dot_idr','matic_idr','avax_idr','link_idr','ltc_idr','bch_idr','etc_idr','xlm_idr','uni_idr',
    # Delisting / Coin Mati / Luna dkk - LENGKAP!
    'luna_idr','lunc_idr','ftt_idr','ustc_idr','luna2_idr','btt_idr','bttc_idr','dgb_idr','qtum_idr','waves_idr','zrx_idr','omg_idr','bat_idr','ont_idr','iost_idr','sc_idr','zcash_idr','dash_idr','xem_idr','bcd_idr','bcha_idr',
    # Meme berat sampah volume tipis
    'shib_idr','pepe_idr','floki_idr','bonk_idr','wif_idr'
}

def get_global_all():
    # Scan 6EX 5972 koin kayak V16.6
    # Binance, Bybit, Gate, Mexc, Bingx, Bitget
    # Return dict {symbol: g_pct}
    pass

def get_indodax_tickers():
    # Return all tickers IDR
    pass

def scan_v16_7():
    tickers = get_indodax_tickers()
    global_data = get_global_all()
    
    tier1 = []
    tier2 = []
    
    for t in tickers:
        sym = t['symbol']  # BICO, SNT, LSK, UAI
        price = t['last']
        naik = t['naik_24h']
        pos = t['pos']  # (price-low)/(high-low)*100
        vol_idr = t['vol_idr']
        naik_1h = t['naik_1h']
        bb_upper = t['bb_upper']
        g_pct = global_data.get(sym, 0)
        
        # === LABEL BLACKLIST DELISTING TETAP MASUK ===
        label_extra = ""
        if sym in BLACKLIST:
            label_extra = " [BLACKLIST TAPI SCAN]"
        if sym in DELISTING:
            label_extra = " [DELISTING/MAINTENANCE]"
        
        # ================= TIER 1 - BANDAR GLOBAL (TETAP KAYA V16.6) =================
        # 1. BANDAR GLOBAL
        if t['mcap'] <= 50_000_000 and t['ratio'] >= 1.0 and naik_1h >= 0.8:
            tier1.append(f"BANDAR GLOBAL MID TEBAL | {sym} Rp{price} Naik {naik}% Pos {pos}% Ratio {t['ratio']}x Vol {vol_idr}Mn{label_extra}")
        
        # 2. BANDAR GLOBAL-ALL
        if g_pct >= 3.0 and vol_idr >= 150_000_000 and 2 <= naik <= 35 and pos <= 80:
            tier1.append(f"BANDAR GLOBAL-ALL {g_pct}% | {sym} Rp{price} Naik {naik}% Pos {pos}% Vol {vol_idr}Mn Bin {g_pct}%{label_extra}")
        
        # 3. BANDAR INDODAX
        if vol_idr >= 250_000_000 and 2 <= naik <= 30:
            tier1.append(f"BANDAR INDODAX MID TEBAL | {sym} Rp{price} Naik {naik}% Pos {pos}% Vol {vol_idr}Mn GLOBAL {g_pct}%{label_extra}")
        
        # ================= TIER 2 - BUYER SIAP TERBANG (ALLCOIN 2-35% - POLA SNT) =================
        # Filter utama: ALLCOIN naik 2-35% aja!
        if 2 <= naik <= 35:
            is_flat_bottom = (pos <= 15)  # SNT Pos 2% Low 125 datar
            is_vol_spike = (vol_idr >= 100_000_000)  # SNT Vol 565Mn
            is_ignition = (naik_1h >= 2.5)  # SNT 1H naik cepet
            is_bb_break = (price > bb_upper)  # SNT Close 245 > UPPER 184
            
            # Kategori TERBANG
            if is_flat_bottom and is_vol_spike and is_ignition:
                if is_bb_break:
                    tier2.append(f"🚀 TERBANG BB BREAK | {sym} Rp{price} Naik {naik}% Pos {pos}% Vol {vol_idr}Mn 1H {naik_1h}% BB {bb_upper} LOW {t['low']}{label_extra} - KAYAK SNT 137->245!")
                else:
                    tier2.append(f"🔥 TERBANG IGNITION | {sym} Rp{price} Naik {naik}% Pos {pos}% Vol {vol_idr}Mn 1H {naik_1h}%{label_extra} - SIAP TERBANG!")
            
            elif is_flat_bottom and vol_idr >= 150_000_000:
                tier2.append(f"💰 AKUMULASI BAWAH | {sym} Rp{price} Naik {naik}% Pos {pos}% Vol {vol_idr}Mn GLOBAL {g_pct}%{label_extra} - BUYER SIAP!")
    
    # OUTPUT 2 TIER TERPISAH
    msg = f"=== V16.7 GLOBAL-ALL+TERBANG ===\n"
    msg += f"GLOBAL 6EX: {len(global_data)} koin\n"
    msg += f"---\nTIER 1 - BANDAR GLOBAL (TETAP)\n---\n"
    msg += "\n".join(tier1[:15]) if tier1 else "Tidak ada"
    msg += f"\n---\nTIER 2 - BUYER SIAP TERBANG ALLCOIN 2-35% (POLA SNT)\n---\n"
    msg += "\n".join(tier2[:15]) if tier2 else "Tidak ada"
    
    return msg

# Jalankan tiap 5 menit
# print(scan_v16_7())
