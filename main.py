# V11 GLOBAL BINANCE -> INDODAX FINAL - SCAN GLOBAL EKSEKUSI LOKAL
# RUMUS TEMEN LU: Scan Binance Global (Vol/MCap 1x/3x/5x + MCap 10M/50M + 1H 2%) -> Entry Indodax
import requests, os, json, time
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')
CMC_API_KEY = os.getenv('CMC_API_KEY')
MEMORY_FILE = "price_memory.json"

# === BLACKLIST V10 MASIH ADA MIN! JANGAN TAKUT! ===
BLACKLIST = {
    'usdt_idr','usdc_idr','dai_idr','busd_idr','btc_idr','eth_idr','bnb_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr',
    'usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'pepe_idr','xrp_idr','sol_idr','hype_idr','dodo_idr','pippin_idr','bome_idr','ada_idr','doge_idr','ena_idr','anoa_idr','ana_idr','sui_idr','ondo_idr','enb_idr','pengu_idr','pump_idr','shib_idr','nom_idr','mpro_idr','amph_idr','uni_idr','unmd_idr','fanch_idr','kdag_idr',
    'bal_idr','collat_idr','dupe_idr','ladys_idr','perp_idr','poly_idr','rfc_idr','dlc_idr','voxel_idr','yfii_idr','moonpig_idr','doge2_idr','mshd_idr','vbg_idr','vra_idr','cht_idr','krd_idr','strm_idr','slp_idr','d_idr','bone_idr','aura_idr','honey_idr','lrc_idr','zeta_idr','shred_idr','h2o_idr','ern_idr'
}
BLACKLIST.update({'luna_idr','lunc_idr','ftt_idr','ustc_idr'})

# ALIAS BUAT COIN YANG BEDA SYMBOL BINANCE vs CMC vs INDODAX
ALIAS_CMC = {'VELODROME':'VELO', 'ORDERLY':'ORDER', 'BIRB':'BIRB', 'TMG':'TMG', 'HAEDAL':'HAEDAL'}

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT_ID: return
    if len(msg) > 4000: msg = msg[:4000] + "\n...(kepotong)"
    try: requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", json={"chat_id": TELE_CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=15)
    except Exception as e: print(f"TELE ERROR: {e}")

def fnum(v,d=0.0):
    try: return float(str(v).replace(',','').strip()) if str(v).strip() else d
    except: return d
def fmt_vol(v): return f"{v/1e9:.2f}Bn" if v>=1e9 else f"{v/1e6:.0f}Mn"
def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f: return json.load(f)
    except: return {}
def save_memory(data):
    with open(MEMORY_FILE, "w") as f: json.dump(data, f)

memory = load_memory()
now_ts = time.time()
wib = timezone(timedelta(hours=7))
now = datetime.now(wib).strftime("%H:%M WIB %d-%m")

# === 1. SCAN GLOBAL BINANCE ===
print("SCAN BINANCE GLOBAL...")
try:
    binance = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=15).json()
    binance_map = {b['symbol'].replace('USDT','').lower(): b for b in binance if b['symbol'].endswith('USDT')}
except Exception as e:
    print(f"BINANCE FAIL {e}"); binance_map = {}

# === 2. SCAN CMC GLOBAL (RUMUS TEMEN LU) ===
cmc_map = {}
if CMC_API_KEY and binance_map:
    try:
        # ambil top symbol dari binance yang naik >5% dulu biar hemat kredit CMC
        top_sym = [k.upper() for k,v in binance_map.items() if fnum(v.get('priceChangePercent'))>=3][:80]
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        headers = {'X-CMC_PRO_API_KEY': CMC_API_KEY}
        for i in range(0, len(top_sym), 40):
            batch = [ALIAS_CMC.get(s, s) for s in top_sym[i:i+40]]
            params = {'symbol': ','.join(batch), 'convert': 'USD'}
            r = requests.get(url, headers=headers, params=params, timeout=15).json()
            data = r.get('data', {})
            for sym, info in data.items():
                q = info.get('quote', {}).get('USD', {})
                # simpen dengan key asli + alias
                key = sym.lower()
                cmc_map[key] = {
                    'mcap': fnum(q.get('market_cap')),
                    'vol24': fnum(q.get('volume_24h')),
                    'chg1h': fnum(q.get('percent_change_1h')),
                    'chg24h': fnum(q.get('percent_change_24h')),
                }
                # balikin alias
                for orig, alias in ALIAS_CMC.items():
                    if alias.lower()==key:
                        cmc_map[orig.lower()] = cmc_map[key]
            time.sleep(1)
        print(f"CMC LOADED {len(cmc_map)} coins")
    except Exception as e:
        print(f"CMC FAIL {e}")

# === 3. CEK INDODAX APA ADA? (EKSEKUSI LOKAL) ===
try: indodax_tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers', {})
except: indodax_tickers = {}

result = []
new_memory = {}

for base, bdata in binance_map.items():
    pair_idr = f"{base}_idr"
    if pair_idr in BLACKLIST: continue  # BLACKLIST TETEP JALAN MIN!
    if pair_idr not in indodax_tickers: continue  # cuma yang ada di Indodax
    
    indodax = indodax_tickers[pair_idr]
    last = fnum(indodax.get('last')); low = fnum(indodax.get('low')); high = fnum(indodax.get('high')); vol_idr = fnum(indodax.get('vol_idr'))
    if last<5 or vol_idr < 80_000_000: continue
    
    cmc = cmc_map.get(base, {})
    mcap = cmc.get('mcap',0); vol24 = cmc.get('vol24',0); chg1h = cmc.get('chg1h',0); chg24h = cmc.get('chg24h',0)
    ratio = (vol24 / mcap) if mcap>0 else 0
    
    # EARLY MEMORY INDODAX
    early_pct = 0
    prev = memory.get(pair_idr)
    if prev and (now_ts - prev["ts"])/60 > 2:
        if prev["last"]>0: early_pct = (last - prev["last"])/prev["last"]*100
    new_memory[pair_idr] = {"last": last, "ts": now_ts}
    
    pct_low = (last - low)/low*100 if low>0 else 0
    pct_high = (high - last)/high*100 if high>0 else 0
    
    # FILTER FINAL SESUAI TEMEN LU: MCap $10M/$50M + Ratio 1x/3x/5x + 1H 2%
    if mcap>0 and mcap<=50_000_000 and ratio>=1.0 and chg1h>=2.0:
        if ratio>=5: cat = f"🔥 GLOBAL 5x {ratio:.1f}x"
        elif ratio>=3: cat = f"🔥 GLOBAL 3x {ratio:.1f}x"
        else: cat = f"💰 GLOBAL 1x {ratio:.1f}x"
        cat += " SPEC" if mcap<=10_000_000 else " MID"
        result.append({'cat':cat,'pair':pair_idr,'last':last,'pct_low':pct_low,'mcap':mcap,'chg1h':chg1h,'chg24h':chg24h,'ratio':ratio,'vol_idr':vol_idr,'bin_vol':fnum(bdata.get('quoteVolume')),'early':early_pct})
    elif early_pct>=2.0:
        result.append({'cat':"⚡ EARLY 2% IDX",'pair':pair_idr,'last':last,'pct_low':pct_low,'mcap':mcap,'chg1h':chg1h,'chg24h':chg24h,'ratio':ratio,'vol_idr':vol_idr,'bin_vol':fnum(bdata.get('quoteVolume')),'early':early_pct})

# RUNNING INDODAX (TETEP)
running = []
for pair, d in indodax_tickers.items():
    if pair in BLACKLIST or not pair.endswith('_idr'): continue
    last = fnum(d.get('last')); low = fnum(d.get('low')); high = fnum(d.get('high')); vol = fnum(d.get('vol_idr'))
    if low<=0 or high<=0 or vol<100_000_000: continue
    pct_low = (last-low)/low*100; pct_high = (high-last)/high*100
    if 0<=pct_high<=8 and pct_low>=4:
        running.append({'symbol': pair[:-4].upper(), 'price': last, 'naik': pct_low, 'jauh': pct_high, 'vol': vol})

result.sort(key=lambda x: (x['ratio'], x['chg1h']), reverse=True)

msg = f"V11 GLOBAL->INDODAX {now}\nSCAN Binance + MCap $10M SPEC / $50M MID | Ratio 1x/3x/5x | 1H>=2% | Eksekusi IDX 80Mn\n------\n"
if result:
    for c in result[:12]:
        mcap_s = f"${c['mcap']/1e6:.1f}M" if c['mcap']>0 else "noCMC"
        msg += f"{c['cat']} | {c['pair'][:-4].upper()} Rp{c['last']:,.0f} Naik {c['pct_low']:.1f}% | MCap {mcap_s} 1H {c['chg1h']:.1f}% 24H {c['chg24h']:.0f}% | Ratio {c['ratio']:.1f}x | VolIDX {fmt_vol(c['vol_idr'])}\n"
else:
    msg += f"Belum ada GLOBAL BANDAR (Binance {len(binance_map)} CMC {len(cmc_map)}). Market flat\n"

if running:
    running = sorted(running, key=lambda x: x['vol'], reverse=True)[:5]
    msg += f"\n----- V11 RUNNING IDX | {len(running)} block -----\n"
    for j,c in enumerate(running,11):
        msg += f"#{j} RUNNING | {c['symbol']} Rp{int(c['price']):,} Naik {c['naik']:.1f}% Jauh {c['jauh']:.0f}% Vol {fmt_vol(c['vol'])}\n"

msg += f"\n---- V11 FINAL {len(new_memory)} block CMC {len(cmc_map)} BIN {len(binance_map)} ----"
print(msg); send_tele(msg); save_memory(new_memory)
