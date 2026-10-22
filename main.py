# ============================================
# SCAN V18.5 10 KOINS - FINAL LOCK 22 OKT 2026
# EARLY ketatin 3, HUNTER label 3, SEGAR longgar 4
# BLOCK LIST LAMA TETAP AMAN!
# ============================================

BLOCKED = [
    'BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','DAI_IDR',
    'SHIB_IDR','DOGE_IDR','PEPE_IDR','BONK_IDR','FLOKI_IDR'
    # GANTI INI SAMA BLOCK LIST LAMA LU YANG ASLI DI V18.4!
]

def scan_v18_5(data):
    early, hunter, segar = [], [], []
    
    for koin in data:
        symbol = koin.get('symbol', koin.get('pair',''))
        chg = float(koin.get('chg', 0))
        th = float(koin.get('th', 0))
        vol = float(koin.get('vol', 0))  # dalam Bn
        last = float(koin.get('last', 0))
        low = float(koin.get('low', 1))
        
        # 1. BLOCK LIST LAMA - TETAP DI BLOCK!
        if symbol in BLOCKED:
            continue
        # 2. VOL MINIMAL 25JT - AUTO BLOCK MICIN
        if vol < 0.025:
            continue
            
        # 3. EARLY = DETEKSI DINI - 3 BIJI - HOLD BESOK
        if 1.0 <= chg <= 4.0 and th <= 5.0 and vol >= 0.08 and last > low:
            early.append(koin)
        # 4. HUNTER = SCALP - 3 BIJI - LABEL TH 0%
        elif chg > 4.0 and th <= 10.0 and vol >= 0.07:
            koin['label'] = "SCALP ONLY! JANGAN HOLD!" if th <= 1.0 else "SCALP"
            hunter.append(koin)
        # 5. SEGAR = SWING VOL RAME - 4 BIJI
        elif chg <= 4.0 and th <= 12.0 and vol >= 0.15:
            segar.append(koin)
    
    early = sorted(early, key=lambda x: float(x['chg']))[:3]
    hunter = sorted(hunter, key=lambda x: float(x['th']))[:3]
    segar = sorted(segar, key=lambda x: float(x['vol']), reverse=True)[:4]
    
    return early, hunter, segar

def format_tele(early, hunter,
