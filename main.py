# V12 HYBRID GLOBAL LOCAL FINAL - ANTI BIN 0 + SUPPORT ANIME & ALL COIN
import requests, os, json, time
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')
CMC_API_KEY = os.getenv('CMC_API_KEY')
MEMORY_FILE = "price_memory.json"

BLACKLIST = {
    'usdt_idr','usdc_idr','dai_idr','busd_idr','btc_idr','eth_idr','bnb_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr',
    'usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'pepe_idr','xrp_idr','sol_idr','hype_idr','dodo_idr','pippin_idr','bome_idr','ada_idr','doge_idr','ena_idr','anoa_idr','ana_idr','sui_idr','ondo_idr','enb_idr','pengu_idr','pump_idr','shib_idr','nom_idr','mpro_idr','amph_idr','uni_idr','unmd_idr','fanch_idr','kdag_idr',
    'bal_idr','collat_idr','dupe_idr','ladys_idr','perp_idr','poly_idr','rfc_idr','dlc_idr','voxel_idr','yfii_idr','moonpig_idr','doge2_idr','mshd_idr','vbg_idr','vra_idr','cht_idr','krd_idr','strm_idr','slp_idr','d_idr','bone_idr','aura_idr','honey_idr','lrc_idr','zeta_idr','shred_idr','h2o_idr','ern_idr',
    'luna_idr','lunc_idr','ftt_idr','ustc_idr'
}

ALIAS = {'velodrome_idr':'velo', 'orderly_idr':'order', 'anime_idr':'anime', 'haedal_idr':'haedal', 'rez_idr':'rez', 'tag_idr':'tag'}

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

# 1. INDODAX TICKER (EKSEKUSI LOKAL)
try:
    tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers', {})
except:
    tickers = {}

# 2. BINANCE GLOBAL (Coba dulu, kalo gagal fallback)
binance_map = {}
try:
    headers = {'User-Agent': 'Mozilla/5.0'}
    binance = requests.get("https://api.binance.com/api/v3/ticker/24hr", headers=headers, timeout=15).json()
    if isinstance(binance, list):
        binance_map = {b['symbol'].replace('USDT','').lower(): b for b in binance if b['symbol'].endswith('USDT')}
    print(f"BINANCE LOADED {len(binance_map)}")
except Exception as e:
    print(f"BINANCE FAIL {e} -> fallback ke INDODAX only")

# 3. CMC GLOBAL (Market Cap + Vol 24H Global + 1H + 24H)
cmc_map = {}
if CMC_API_KEY:
    try:
        # KUMPUL SYMBOL DARI INDODAX + BINANCE YANG NAIK
        candidates = []
        for pair, d in tickers.items():
            if pair in BLACKLIST: continue
            if fnum(d.get('vol_idr')) < 5_000_000: continue  # 5Mn EARLY kaya ANIME udah masuk!
            # ambil semua yang naik >1%
            low = fnum(d.get('low')); last = fnum(d.get('last'))
            if low>0 and ((last-low)/low*100) >= 1:
                base = pair[:-4]
                cmc_sym = ALIAS.get(pair, base).upper()
                candidates.append(cmc_sym)
        # tambah dari binance top gainer
        if binance_map:
            for k,v in binance_map.items():
                if fnum(v.get('priceChangePercent')) >= 2:
                    candidates.append(k.upper())
        
        # unique + limit 80
        candidates = list(dict.fromkeys(candidates))[:80]
        print(f"CANDIDATES {len(candidates)}: {candidates[:10]}")
        
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        headers = {'X-CMC_PRO_API_KEY': CMC_API_KEY}
        for i in range(0, len(candidates), 40):
            batch = candidates[i:i+40]
            if not batch: continue
            params = {'symbol': ','.join(batch), 'convert': 'USD'}
            r = requests.get(url, headers=headers, params=params, timeout=20).json()
            data = r.get('data', {})
            for sym, info in data.items():
                q = info.get('quote', {}).get('USD', {})
                cmc_map[sym.lower()] = {
                    'mcap': fnum(q.get('market_cap')),
                    'vol24': fnum(q.get('volume_24h')),
                    'chg1h': fnum(q.get('percent_change_1h')),
                    'chg24h': fnum(q.get('percent_change_24h')),
                }
                # alias balik
                for orig_pair, alias in ALIAS.items():
                    if alias.lower() == sym.lower():
                        cmc_map[orig_pair[:-4]] = cmc_map[sym.lower()]
            time.sleep(1)
        print(f"CMC LOADED {len(cmc_map)} coins")
    except Exception as e:
        print(f"CMC FAIL {e}")

result = []
new_memory = {}
for pair, d in tickers.items():
    if pair in BLACKLIST or not pair.endswith('_idr'): continue
    last = fnum(d.get('last')); low = fnum(d.get('low')); high = fnum(d.get('high')); vol_idr = fnum(d.get('vol_idr'))
    if last < 1 or vol_idr < 5_000_000: continue  # 5Mn biar ANIME masuk!
    
    base = pair[:-4]
    cmc = cmc_map.get(base, {}) or cmc_map.get(ALIAS.get(pair, base).lower(), {})
    mcap = cmc.get('mcap',0); vol24 = cmc.get('vol24',0); chg1h = cmc.get('chg1h',0); chg24h = cmc.get('chg24h',0)
    ratio = (vol24 / mcap) if mcap>0 else 0
    
    # EARLY MEMORY 2%
    early_pct = 0
    prev = memory.get(pair)
    if prev and (now_ts - prev["ts"])/60 > 2:
        if prev["last"]>0: early_pct = (last - prev["last"])/prev["last"]*100
    new_memory[pair] = {"last": last, "ts": now_ts}
    
    pct_low = (last - low)/low*100 if low>0 else 0
    pct_high = (high - last)/high*100 if high>0 else 0
    
    # === FILTER SESUAI MAU LU MIN: MCap 10M/50M + Ratio 1x/3x/5x + 1H 2% ===
    if mcap>0 and mcap<=50_000_000 and ratio>=1.0 and chg1h>=2.0:
        cat_ratio = "5x" if ratio>=5 else "3x" if ratio>=3 else "1x"
        cat_mcap = "SPEC" if mcap<=10_000_000 else "MID"
        # Vol IDX bedain EARLY vs CONFIRM
        vol_tag = "TIPIS" if vol_idr < 80_000_000 else "TEBAL"
        cat = f"🔥 BANDAR {cat_ratio} {cat_mcap} {vol_tag}"
        result.append({'cat':cat,'pair':pair,'last':last,'pct_low':pct_low,'mcap':mcap,'chg1h':chg1h,'chg24h':chg24h,'ratio':ratio,'vol_idr':vol_idr,'early':early_pct})
    elif early_pct>=2.0 and vol_idr>=5_000_000:
        result.append({'cat':"⚡ EARLY 2% ALL",'pair':pair,'last':last,'pct_low':pct_low,'mcap':mcap,'chg1h':chg1h,'chg24h':chg24h,'ratio':ratio,'vol_idr':vol_idr,'early':early_pct})

# RUNNING
running = []
for pair, d in tickers.items():
    if pair in BLACKLIST or not pair.endswith('_idr'): continue
    last = fnum(d.get('last')); low = fnum(d.get('low')); high = fnum(d.get('high')); vol = fnum(d.get('vol_idr'))
    if low<=0 or high<=0 or vol<100_000_000: continue
    pct_low = (last-low)/low*100; pct_high = (high-last)/high*100
    if 0<=pct_high<=8 and pct_low>=4:
        running.append({'symbol': pair[:-4].upper(), 'price': last, 'naik': pct_low, 'jauh': pct_high, 'vol': vol})

result.sort(key=lambda x: (x['ratio'], x['chg1h']), reverse=True)
msg = f"V12 HYBRID {now}\nSCAN CMC Vol/MCap {len(cmc_map)} | MCap $10M SPEC / $50M MID | Ratio 1x/3x/5x | 1H>=2% | Vol IDX 5Mn EARLY / 80Mn SAFE\n------\n"
if result:
    for c in result[:15]:
        mcap_s = f"${c['mcap']/1e6:.1f}M" if c['mcap']>0 else "noCMC"
        msg += f"{c['cat']} | {c['pair'][:-4].upper()} Rp{c['last']:,.0f} Naik {c['pct_low']:.1f}% | MCap {mcap_s} 1H {c['chg1h']:.1f}% 24H {c['chg24h']:.0f}% | Ratio {c['ratio']:.1f}x | VolIDX {fmt_vol(c['vol_idr'])}\n"
else:
    msg += f"Belum ada BANDAR (CMC {len(cmc_map)} BIN {len(binance_map)}). Market flat\n"

if running:
    running = sorted(running, key=lambda x: x['vol'], reverse=True)[:5]
    msg += f"\n----- RUNNING IDX | {len(running)} -----\n"
    for j,c in enumerate(running,11):
        msg += f"#{j} RUNNING | {c['symbol']} Rp{int(c['price']):,} Naik {c['naik']:.1f}% Jauh {c['jauh']:.0f}% Vol {fmt_vol(c['vol'])}\n"

msg += f"\n---- V12 FINAL {len(new_memory)} block CMC {len(cmc_map)} BIN {len(binance_map)} ----"
print(msg); send_tele(msg); save_memory(new_memory)
