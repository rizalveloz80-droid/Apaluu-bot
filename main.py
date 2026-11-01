# === V17.11 CMC FINAL - BLACKLIST BENER V17.4-V17.7 + SEPI HUNTER ===
# by Min - 1 Nov 2026 - FIX BLACKLIST SALAH!

import os
import requests
import json
import time
from datetime import datetime
import pytz

# === CONFIG ===
TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')
CMC_API_KEY = os.getenv('CMC_API_KEY')
WIB = pytz.timezone('Asia/Jakarta')

# === 1. BLACKLIST BENER DARI V17.4 - V17.7 LU! ===
BLACKLIST = {
    'usdt_idr','usdc_idr','dai_idr','busd_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr','usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'btc_idr','eth_idr','bnb_idr','sol_idr','xrp_idr','ada_idr','doge_idr','trx_idr','dot_idr','matic_idr','avax_idr','link_idr','ltc_idr','bch_idr','etc_idr','xlm_idr','uni_idr',
    'luna_idr','lunc_idr','ftt_idr','ustc_idr','luna2_idr','btt_idr','bttc_idr','dgb_idr','qtum_idr','waves_idr','zrx_idr','omg_idr','bat_idr','ont_idr','iost_idr','sc_idr','zcash_idr','dash_idr','xem_idr','bcd_idr','bcha_idr',
    'shib_idr','pepe_idr','floki_idr','bonk_idr','wif_idr','ern_idr',
    'ondo_idr','hype_idr','sui_idr','dodo_idr','bome_idr','nom_idr','mpro_idr','amp_idr','unmd_idr','kdag_idr',
}

VOL_SEPI_MIN = 10_000_000
VOL_SEPI_MAX = 250_000_000
VOL_NEW_MIN = 100_000_000

def send_tele(msg):
    try:
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        data = {"chat_id": TELE_CHAT_ID, "text": msg}
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"Tele error: {e}")

def get_indodax_data():
    try:
        r = requests.get("https://indodax.com/api/tickers", timeout=15)
        data = r.json()['tickers']
        coins = []
        for pair, ticker in data.items():
            if pair in BLACKLIST:  # <-- LANGSUNG SKIP BLACKLIST!
                continue
            if not pair.endswith('_idr'):
                continue
            symbol = pair.replace('_idr','').upper()
            price = float(ticker['last'])
            vol_idr = float(ticker['vol_idr'])
            high = float(ticker['high'])
            low = float(ticker['low'])
            if low > 0:
                pos = ((price - low) / (high - low) * 100) if high != low else 50
                naik_24h = ((price - low) / low * 100) if low>0 else 0
            else:
                pos = 50
                naik_24h = 0
            ob_low = int(low + (high-low)*0.2)
            ob_high = int(low + (high-low)*0.35)
            coins.append({
                'symbol': symbol,
                'pair': pair,
                'price': price,
                'vol_idr': vol_idr,
                'pos': round(pos,1),
                'naik_24h': round(naik_24h,1),
                'ob_low': ob_low,
                'ob_high': ob_high,
            })
        return coins
    except Exception as e:
        print(f"Indodax error: {e}")
        return []

def get_global_pump_cmc(symbol):
    if not CMC_API_KEY:
        return 0
    try:
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        headers = {'X-CMC_PRO_API_KEY': CMC_API_KEY}
        params = {'symbol': symbol, 'convert': 'USD'}
        r = requests.get(url, headers=headers, params=params, timeout=10)
        data = r.json()
        if 'data' in data and symbol in data['data']:
            change = data['data'][symbol]['quote']['USD']['percent_change_24h']
            return float(change) if change else 0
        return 0
    except:
        return 0

def scan():
    now = datetime.now(WIB).strftime("%H:%M:%S")
    print(f"Scan {now}...")
    indodax_coins = get_indodax_data()
    print(f"Dapat {len(indodax_coins)} koin (setelah blacklist {len(BLACKLIST)} koin dihapus)")
    
    results = {'SEPI': [], 'NEW': [], 'BANDAR_INDO': [], 'BANDAR_GLOBAL': [], 'IGNITION': []}
    
    for coin in indodax_coins:
        symbol = coin['symbol']
        if coin['vol_idr'] < VOL_SEPI_MIN:
            continue
        
        global_pct = get_global_pump_cmc(symbol)
        time.sleep(0.3)
        
        price = coin['price']
        vol = coin['vol_idr']
        pos = coin['pos']
        naik = coin['naik_24h']
        ob_low = coin['ob_low']
        ob_high = coin['ob_high']
        
        # 🤫 SEPI
        if (global_pct >= 5.0 and naik < 2.0 and pos <= 5 and VOL_SEPI_MIN <= vol <= VOL_SEPI_MAX):
            results['SEPI'].append(f"🤫 SEPI! GLOBAL {global_pct:.1f}% | {symbol} Rp{int(price)} | ENTRY {ob_low}-{ob_high} OB | Indo Naik {naik}% Pos {pos}% Vol {int(vol//1_000_000)}Mn | Global {global_pct:.1f}% | BURU!")
        
        # 💥 NEW
        is_new = pos < 20 and vol >= VOL_NEW_MIN and naik < 30
        if (is_new and global_pct > 3.0 and pos < 20 and naik < 30):
            entry_type = "OB" if pos < 10 else "RETEST"
            entry = f"{ob_low}-{ob_high} {entry_type}" if entry_type=="OB" else f"{int(ob_low*0.95)}-{int(ob_high*0.95)} {entry_type}"
            results['NEW'].append(f"💥 NEW {naik}% + OB {ob_low}-{ob_high} | {symbol} Rp{int(price)} | ENTRY {entry} | Pos {pos}% Vol {int(vol//1_000_000)}Mn | Global {global_pct:.1f}%")
        
        # 🏦 BANDAR INDO
        if (naik >= 5.0 and global_pct < 3.0 and vol > 200_000_000 and pos < 30):
            results['BANDAR_INDO'].append(f"🏦 BANDAR INDO! Indo {naik}% Global {global_pct:.1f}% | {symbol} Rp{int(price)} | ENTRY {ob_low}-{ob_high} OB | Pos {pos}% Vol {int(vol//1_000_000)}Mn | WASPADA PUCUK!")
        
        # 🚀 BANDAR GLOBAL
        if (global_pct >= 4.0 and vol > 100_000_000):
            entry_type = "OB" if pos < 15 else "RETEST"
            entry = f"{ob_low}-{ob_high} {entry_type}" if entry_type=="OB" else f"{int(ob_low*0.95)}-{int(ob_high*0.95)} {entry_type}"
            results['BANDAR_GLOBAL'].append(f"🚀 GLOBAL {global_pct:.1f}% OB {ob_low}-{ob_high} | {symbol} Rp{int(price)} | ENTRY {entry} | Pos {pos}% Vol {int(vol//1_000_000)}Mn | Global {global_pct:.1f}%")
        
        # 🔥 IGNITION
        if (2 <= naik < 5 and pos < 15 and vol > 100_000_000 and global_pct < 5):
            results['IGNITION'].append(f"🔥 IGNITION OB {ob_low}-{ob_high} | {symbol} Rp{int(price)} | ENTRY {ob_low}-{ob_high} OB | Naik {naik}% Pos {pos}% Vol {int(vol//1_000_000)}Mn | Global {global_pct:.1f}%")
    
    final_msg = f"=== V17.11 CMC FINAL {now} WIB - BLACKLIST {len(BLACKLIST)} KOINS ===\n"
    if results['SEPI']:
        final_msg += "\n🤫 TIER SEPI - BURU!:\n" + "\n".join(results['SEPI'][:5]) + "\n"
    else:
        final_msg += "\n🤫 TIER SEPI: Belum ada\n"
    if results['NEW']:
        final_msg += "\n💥 TIER 0 NEW:\n" + "\n".join(results['NEW'][:5]) + "\n"
    if results['BANDAR_INDO']:
        final_msg += "\n🏦 TIER 1A BANDAR INDO:\n" + "\n".join(results['BANDAR_INDO'][:5]) + "\n"
    if results['BANDAR_GLOBAL']:
        final_msg += "\n🚀 TIER 1B BANDAR GLOBAL:\n" + "\n".join(results['BANDAR_GLOBAL'][:8]) + "\n"
    if results['IGNITION']:
        final_msg += "\n🔥 TIER 2 IGNITION:\n" + "\n".join(results['IGNITION'][:5]) + "\n"
    final_msg += f"\nNOTE: Blacklist bener {len(BLACKLIST)} | Vol Sepi 10-250Mn | CMC 1 API!"
    
    print(final_msg)
    if results['SEPI'] or results['BANDAR_INDO'] or results['BANDAR_GLOBAL']:
        send_tele(final_msg)
    
    with open('price_memory.json','w') as f:
        json.dump({"last_scan": now}, f)

if __name__ == "__main__":
    scan()
