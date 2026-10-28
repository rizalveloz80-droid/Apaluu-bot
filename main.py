# V10 BINANCE LEAD + V9.2 LITE - 28 OKT 2026 - BANDAR DETECTOR
import requests, os, json, time
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')
MEMORY_FILE = "price_memory.json"

# BLACKLIST + DELISTING LU GUA AMANIN! JANGAN DIHAPUS!
BLACKLIST = {
    'usdt_idr','usdc_idr','dai_idr','busd_idr','btc_idr','eth_idr','bnb_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr',
    'usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'pepe_idr','xrp_idr','sol_idr','hype_idr','dodo_idr','pippin_idr','bome_idr','ada_idr','doge_idr','ena_idr','anoa_idr','ana_idr','sui_idr','ondo_idr','enb_idr','pengu_idr','pump_idr','shib_idr','nom_idr','mpro_idr','amph_idr','uni_idr','unmd_idr','fanch_idr','kdag_idr',
    'bal_idr','collat_idr','dupe_idr','ladys_idr','perp_idr','poly_idr','rfc_idr','dlc_idr','voxel_idr','yfii_idr','moonpig_idr','doge2_idr','mshd_idr','vbg_idr','vra_idr','cht_idr','krd_idr','strm_idr','slp_idr','d_idr','bone_idr','aura_idr','honey_idr','lrc_idr','zeta_idr','shred_idr','h2o_idr','ern_idr'
}

# TAMBAHAN DELISTING INDODAX 2024-2026 (BIAR GA NYANGKUT)
DELISTING = {'luna_idr','lunc_idr','ftt_idr','ustc_idr'} # tambah kalo ada info baru
BLACKLIST = BLACKLIST.union(DELISTING)

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT_ID: return
    if len(msg) > 4000: msg = msg[:4000] + "\n...(kepotong)"
    try: requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", json={"chat_id": TELE_CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=15)
    except Exception as e: print(f"TELE ERROR: {e}")

def fnum(v,d=0.0):
    try: v=str(v).replace(',','').strip(); return float(v) if v else d
    except: return d

def fmt_vol(v): return f"{v/1e9:.2f}Bn" if v>=1e9 else f"{v/1e6:.0f}Mn"

def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f: return json.load(f)
    except: return {}

def save_memory(data):
    with open(MEMORY_FILE, "w") as f: json.dump(data, f)

# === 1. AMBIL BINANCE DULU (KUNCI TEMEN LU!) ===
binance_map = {}
try:
    b_data = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=10).json()
    for b in b_data:
        sym = b.get('symbol','')
        if sym.endswith('USDT'):
            base = sym[:-4].lower() # BTCUSDT -> btc
            binance_map[base] = {
                'chg': fnum(b.get('priceChangePercent')),
                'vol_usd': fnum(b.get('quoteVolume')), # Vol 24H USD = V24H proxy
                'last': fnum(b.get('lastPrice'))
            }
    print(f"BINANCE LOADED {len(binance_map)} coins")
except Exception as e:
    print(f"BINANCE FAIL: {e}")

memory = load_memory()
now_ts = time.time()
wib = timezone(timedelta(hours=7))
now = datetime.now(wib).strftime("%H:%M WIB %d-%m")

try: tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers', {})
except: tickers = {}

result = []
running = []
new_memory = {}
candidates = []

for pair, d in tickers.items():
    if not pair.endswith('_idr') or pair in BLACKLIST: continue
    last = fnum(d.get('last')); low = fnum(d.get('low')); high = fnum(d.get('high')); vol = fnum(d.get('vol_idr'))
    if low <=0 or last <5 or vol < 80_000_000: continue
    pct_low = (last - low) / low * 100
    pct_high = (high - last) / high * 100
    new_memory[pair] = {"last": last, "ts": now_ts}
    
    # MEMORY 120m V9.2
    early_pct = 0
    prev = memory.get(pair)
    if prev:
        dt = (now_ts - prev["ts"]) / 60
        if 5 < dt < 120:
            if prev["last"] > 0:
                early_pct = (last - prev["last"]) / prev["last"] * 100
    
    # BINANCE LEAD DATA
    base = pair[:-4] # birb_idr -> birb
    b_info = binance_map.get(base, {})
    b_chg = b_info.get('chg', 0)
    b_vol = b_info.get('vol_usd', 0)
    
    # RUMUS BANDAR V24H/MCAP PROXY: Binance Vol gede + Binance Chg gede = Bandar Masuk!
    # Kalo Binance Vol > 5M USD (kira2 80M IDR * 1000) dan MCap kecil (<50M) -> proxy V24H/MCap >=1x
    bandar_score = 0
    if b_vol > 5_000_000 and b_chg >= 2: bandar_score = 3
    elif b_vol > 1_000_000 and b_chg >= 1: bandar_score = 1
    
    candidates.append((pair, d, last, low, high, vol, pct_low, pct_high, early_pct, b_chg, b_vol, bandar_score))

candidates.sort(key=lambda x: (x[11], x[8], x[5]), reverse=True) # sort by bandar_score, early, vol

for pair, d, last, low, high, vol, pct_low, pct_high, early_pct, b_chg, b_vol, bandar_score in candidates[:40]:
    # PRIORITAS 1: BINANCE LEAD (SEBELUM INDODAX PUMP!)
    if bandar_score >= 3 and pct_low < 15:
        result.append({'cat': f"🔥 BINANCE LEAD {b_chg:.0f}%", 'pair': pair, 'last': last, 'pct_low': pct_low, 'pct_high': pct_high, 'vol': vol, 'early': early_pct, 'b_vol': b_vol})
    elif early_pct >= 2.0 and pct_high >= 1:
        result.append({'cat': "⚡ EARLY 3%", 'pair': pair, 'last': last, 'pct_low': pct_low, 'pct_high': pct_high, 'vol': vol, 'early': early_pct, 'b_vol': b_vol})
    elif 0.8 <= pct_low < 5.8 and pct_high >= 4:
        result.append({'cat': "AKUM EARLY", 'pair': pair, 'last': last, 'pct_low': pct_low, 'pct_high': pct_high, 'vol': vol, 'early': early_pct, 'b_vol': b_vol})
    elif 5.8 <= pct_low <= 150 and pct_high >= 1:
        result.append({'cat': "BARU MAU PUMP", 'pair': pair, 'last': last, 'pct_low': pct_low, 'pct_high': pct_high, 'vol': vol, 'early': early_pct, 'b_vol': b_vol})

for pair, d in tickers.items():
    if not pair.endswith('_idr') or pair in BLACKLIST: continue
    last = fnum(d.get('last')); low = fnum(d.get('low')); high = fnum(d.get('high')); vol = fnum(d.get('vol_idr'))
    if low <=0 or high <=0 or vol < 100_000_000: continue
    pct_low = (last - low) / low * 100
    pct_high = (high - last) / high * 100
    if 0 <= pct_high <= 8 and pct_low >= 4:
        running.append({'symbol': pair.upper()[:-4], 'price': last, 'naik': pct_low, 'jauh': pct_high, 'vol': vol})

msg = f"EARLY {now}\nV10 BINANCE LEAD + V9.2 LITE 2% + BL {len(BLACKLIST)}\n------\n"
if result:
    result.sort(key=lambda x: (x.get('b_vol',0) if 'BINANCE' in x['cat'] else x.get('early',0), x['pct_low']), reverse=True)
    for c in result[:12]:
        early_str = f" Early {c['early']:.1f}%" if c.get('early',0)>=1 else ""
        b_str = f" BVol ${c['b_vol']/1e6:.1f}M" if c.get('b_vol',0)>1e6 else ""
        msg += f"{c['cat']}{early_str} | {c['pair'].upper()[:-4]} Rp{c['last']:,.0f} Naik {c['pct_low']:.1f}% | Jauh {c['pct_high']:.0f}% | Vol {fmt_vol(c['vol'])}{b_str}\n"
else:
    msg += "Market flat, nunggu memory + binance\n"

if running:
    running = sorted(running, key=lambda x: x['vol'], reverse=True)[:5]
    msg += f"\n----- V10 RUNNING | {len(running)} block -----\n"
    for j,c in enumerate(running,11):
        msg += f"#{j} RUNNING | {c['symbol']} Rp{int(c['price']):,} Naik {c['naik']:.1f}% Jauh {c['jauh']:.0f}% Vol {fmt_vol(c['vol'])}\n"

msg += f"\n---- V10 BINANCE LEAD {len(new_memory)} block ----"
print(msg)
send_tele(msg)
save_memory(new_memory)
