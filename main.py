# V10 FINAL BANDAR CMC - SESUAI RUMUS TEMEN LU - 28 OKT 2026
# RUMUS: V24H/MCap 1x/3x/5x + MCap $10M/$50M + 1H +2% + Vol IDR
import requests, os, json, time
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')
CMC_API_KEY = os.getenv('CMC_API_KEY')
MEMORY_FILE = "price_memory.json"

# BLACKLIST + DELISTING LU TETEP AMAN!
BLACKLIST = {
    'usdt_idr','usdc_idr','dai_idr','busd_idr','btc_idr','eth_idr','bnb_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr',
    'usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'pepe_idr','xrp_idr','sol_idr','hype_idr','dodo_idr','pippin_idr','bome_idr','ada_idr','doge_idr','ena_idr','anoa_idr','ana_idr','sui_idr','ondo_idr','enb_idr','pengu_idr','pump_idr','shib_idr','nom_idr','mpro_idr','amph_idr','uni_idr','unmd_idr','fanch_idr','kdag_idr',
    'bal_idr','collat_idr','dupe_idr','ladys_idr','perp_idr','poly_idr','rfc_idr','dlc_idr','voxel_idr','yfii_idr','moonpig_idr','doge2_idr','mshd_idr','vbg_idr','vra_idr','cht_idr','krd_idr','strm_idr','slp_idr','d_idr','bone_idr','aura_idr','honey_idr','lrc_idr','zeta_idr','shred_idr','h2o_idr','ern_idr'
}
BLACKLIST.update({'luna_idr','lunc_idr','ftt_idr','ustc_idr'})

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

# === AMBIL CMC DULU (RUMUS TEMEN LU) ===
cmc_map = {}
if CMC_API_KEY:
    try:
        # Ambil tickers Indodax dulu buat list symbol
        tickers_raw = requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers', {})
        symbols = []
        for pair in tickers_raw:
            if not pair.endswith('_idr') or pair in BLACKLIST: continue
            base = pair[:-4].upper()
            if len(base)>=2: symbols.append(base)
        symbols = list(set(symbols))[:80] # CMC max 120 per call, kita 80 biar aman
        
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        headers = {'X-CMC_PRO_API_KEY': CMC_API_KEY}
        # batch 40-40 biar ga limit
        for i in range(0, len(symbols), 40):
            batch = symbols[i:i+40]
            params = {'symbol': ','.join(batch), 'convert': 'USD'}
            r = requests.get(url, headers=headers, params=params, timeout=15).json()
            data = r.get('data', {})
            for sym, info in data.items():
                q = info.get('quote', {}).get('USD', {})
                cmc_map[sym.lower()] = {
                    'mcap': fnum(q.get('market_cap')),
                    'vol24': fnum(q.get('volume_24h')),
                    'chg1h': fnum(q.get('percent_change_1h')),
                    'chg24h': fnum(q.get('percent_change_24h')),
                    'price': fnum(q.get('price'))
                }
            time.sleep(1)
        print(f"CMC LOADED {len(cmc_map)} coins")
    except Exception as e:
        print(f"CMC FAIL: {e}")
else:
    print("CMC KEY KOSONG!")

# === INDODAX TICKER ===
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
    
    early_pct = 0
    prev = memory.get(pair)
    if prev:
        dt = (now_ts - prev["ts"]) / 60
        if 5 < dt < 120:
            if prev["last"] > 0:
                early_pct = (last - prev["last"]) / prev["last"] * 100
    
    base = pair[:-4]
    cmc = cmc_map.get(base, {})
    mcap = cmc.get('mcap',0)
    vol24_usd = cmc.get('vol24',0)
    chg1h = cmc.get('chg1h',0)
    chg24h = cmc.get('chg24h',0)
    ratio = (vol24_usd / mcap) if mcap>0 else 0
    
    candidates.append((pair, last, low, high, vol, pct_low, pct_high, early_pct, mcap, vol24_usd, ratio, chg1h, chg24h))

candidates.sort(key=lambda x: (x[10], x[11], x[5]), reverse=True)

for pair, last, low, high, vol, pct_low, pct_high, early_pct, mcap, vol24, ratio, chg1h, chg24h in candidates[:50]:
    # FILTER SESUAI TEMEN LU: 1H +2% + MCap
    is_spec = mcap <= 10_000_000
    is_mid = mcap <= 50_000_000
    
    # BANDAR DETECTOR
    if mcap>0 and ratio>=1.0 and chg1h>=2.0 and vol>=80_000_000:
        if ratio>=5: cat = f"🔥 BANDAR 5x {ratio:.1f}x"
        elif ratio>=3: cat = f"🔥 BANDAR 3x {ratio:.1f}x"
        else: cat = f"💰 BANDAR 1x {ratio:.1f}x"
        cat += " SPEC" if is_spec else " MID"
        result.append({'cat': cat, 'pair': pair, 'last': last, 'pct_low': pct_low, 'pct_high': pct_high, 'vol': vol, 'early': early_pct, 'mcap': mcap, 'vol24': vol24, 'ratio': ratio, 'chg1h': chg1h, 'chg24h': chg24h})
    elif early_pct >=2.0 and pct_high>=1:
        result.append({'cat': "⚡ EARLY 2%", 'pair': pair, 'last': last, 'pct_low': pct_low, 'pct_high': pct_high, 'vol': vol, 'early': early_pct, 'mcap': mcap, 'vol24': vol24, 'ratio': ratio, 'chg1h': chg1h, 'chg24h': chg24h})

for pair, d in tickers.items():
    if not pair.endswith('_idr') or pair in BLACKLIST: continue
    last = fnum(d.get('last')); low = fnum(d.get('low')); high = fnum(d.get('high')); vol = fnum(d.get('vol_idr'))
    if low <=0 or high <=0 or vol < 100_000_000: continue
    pct_low = (last - low) / low * 100
    pct_high = (high - last) / high * 100
    if 0 <= pct_high <= 8 and pct_low >= 4:
        running.append({'symbol': pair.upper()[:-4], 'price': last, 'naik': pct_low, 'jauh': pct_high, 'vol': vol})

msg = f"V10 BANDAR CMC {now}\nMCap $10M SPEC / $50M MID | Ratio 1x/3x/5x | 1H>=2% | VolIDR 80Mn\n------\n"
if result:
    result.sort(key=lambda x: (x['ratio'], x['chg1h']), reverse=True)
    for c in result[:12]:
        mcap_s = f"${c['mcap']/1e6:.1f}M" if c['mcap']>0 else "noCMC"
        chg_s = f"1H {c['chg1h']:.1f}% 24H {c['chg24h']:.0f}%" if c['mcap']>0 else ""
        msg += f"{c['cat']} | {c['pair'].upper()[:-4]} Rp{c['last']:,.0f} Naik {c['pct_low']:.1f}% | MCap {mcap_s} {chg_s} | Ratio {c['ratio']:.1f}x | Vol {fmt_vol(c['vol'])}\n"
else:
    msg += f"Belum ada BANDAR 1x+1H2% (CMC {len(cmc_map)} coin). Market flat\n"

if running:
    running = sorted(running, key=lambda x: x['vol'], reverse=True)[:5]
    msg += f"\n----- V10 RUNNING | {len(running)} block -----\n"
    for j,c in enumerate(running,11):
        msg += f"#{j} RUNNING | {c['symbol']} Rp{int(c['price']):,} Naik {c['naik']:.1f}% Jauh {c['jauh']:.0f}% Vol {fmt_vol(c['vol'])}\n"

msg += f"\n---- V10 FINAL {len(new_memory)} block CMC {len(cmc_map)} ----"
print(msg)
send_tele(msg)
save_memory(new_memory)
