# V9.1 FINAL EARLY 3% + BLACKLIST FULL + MEMORY ANTI TELAT UCJL
import requests, os, json, time
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')
MEMORY_FILE = "price_memory.json"

BLACKLIST = {
    'usdt_idr','usdc_idr','dai_idr','busd_idr','btc_idr','eth_idr','bnb_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr',
    'usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'pepe_idr','xrp_idr','sol_idr','hype_idr','dodo_idr','pippin_idr','bome_idr','ada_idr','doge_idr','ena_idr','anoa_idr','ana_idr','sui_idr','ondo_idr','enb_idr','pengu_idr','pump_idr','shib_idr','nom_idr','mpro_idr','amph_idr','uni_idr','unmd_idr','fanch_idr','kdag_idr',
    'bal_idr','collat_idr','dupe_idr','ladys_idr','perp_idr','poly_idr','rfc_idr','dlc_idr','voxel_idr','yfii_idr','moonpig_idr','doge2_idr','mshd_idr','vbg_idr','vra_idr','cht_idr','krd_idr','strm_idr','slp_idr','d_idr','bone_idr','aura_idr','honey_idr','lrc_idr','zeta_idr','shred_idr','h2o_idr','ern_idr'
}

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT_ID: return
    if len(msg) > 4000: msg = msg[:4000] + "\n...(kepotong)"
    try:
        requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",
                      json={"chat_id": TELE_CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=15)
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

# --- LOAD MEMORY ---
memory = load_memory()
now_ts = time.time()
wib = timezone(timedelta(hours=7))
now = datetime.now(wib).strftime("%H:%M WIB %d-%m")

# --- FETCH TICKERS ---
try: tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers', {})
except: tickers = {}

result = []
running = []
new_memory = {}

# --- HITUNG EARLY DARI MEMORY ---
candidates = []
for pair, d in tickers.items():
    if not pair.endswith('_idr') or pair in BLACKLIST: continue
    last = fnum(d.get('last')); low = fnum(d.get('low')); high = fnum(d.get('high')); vol = fnum(d.get('vol_idr'))
    if low <=0 or last <5 or vol < 35_000_000: continue
    pct_low = (last - low) / low * 100
    pct_high = (high - last) / high * 100
    new_memory[pair] = {"last": last, "ts": now_ts}
    
    early_pct = 0
    prev = memory.get(pair)
    if prev:
        dt = (now_ts - prev["ts"]) / 60
        if 5 < dt < 60: # memory 5-60 menit lalu
            if prev["last"] > 0:
                early_pct = (last - prev["last"]) / prev["last"] * 100
    
    candidates.append((pair, d, last, low, high, vol, pct_low, pct_high, early_pct))

candidates.sort(key=lambda x: x[5], reverse=True)

for pair, d, last, low, high, vol, pct_low, pct_high, early_pct in candidates[:40]:
    # PRIORITAS 1: EARLY 3% DARI MEMORY! INI KUNCI UCJL!
    if early_pct >= 3.0 and pct_high >= 1:
        result.append({'cat': "⚡ EARLY 3%", 'pair': pair, 'last': last, 'pct_low': pct_low, 'pct_high': pct_high, 'vol': vol, 'early': early_pct})
    elif 0.8 <= pct_low < 5.8 and pct_high >= 4:
        result.append({'cat': "AKUM EARLY", 'pair': pair, 'last': last, 'pct_low': pct_low, 'pct_high': pct_high, 'vol': vol, 'early': early_pct})
    elif 5.8 <= pct_low <= 150 and pct_high >= 1:
        result.append({'cat': "BARU MAU PUMP", 'pair': pair, 'last': last, 'pct_low': pct_low, 'pct_high': pct_high, 'vol': vol, 'early': early_pct})

# --- V9 RUNNING ---
for pair, d in tickers.items():
    if not pair.endswith('_idr') or pair in BLACKLIST: continue
    last = fnum(d.get('last')); low = fnum(d.get('low')); high = fnum(d.get('high')); vol = fnum(d.get('vol_idr'))
    if low <=0 or high <=0 or vol < 100_000_000: continue
    pct_low = (last - low) / low * 100
    pct_high = (high - last) / high * 100
    if 0 <= pct_high <= 5 and pct_low >= 4:
        running.append({'symbol': pair.upper()[:-4], 'price': last, 'naik': pct_low, 'jauh': pct_high, 'vol': vol})

# --- KIRIM TELE ---
msg = f"EARLY {now}\nV9.1 EARLY 3% + BL + MEMORY\n------\n"
if result:
    result.sort(key=lambda x: (x.get('early',0), x['pct_low']), reverse=True)
    for c in result[:12]:
        early_str = f" Early {c['early']:.1f}%" if c.get('early',0)>=1 else ""
        msg += f"{c['cat']}{early_str} | {c['pair'].upper()[:-4]} Rp{c['last']:,.0f} Naik {c['pct_low']:.1f}% | Jauh {c['pct_high']:.0f}% | Vol {fmt_vol(c['vol'])}\n"
else:
    msg += "Market flat, nunggu memory\n"

if running:
    running = sorted(running, key=lambda x: x['vol'], reverse=True)[:5]
    msg += f"\n----- V9 RUNNING | {len(running)} block -----\n"
    for j,c in enumerate(running,11):
        msg += f"#{j} RUNNING | {c['symbol']} Rp{int(c['price']):,} Naik {c['naik']:.1f}% Jauh {c['jauh']:.0f}% Vol {fmt_vol(c['vol'])}\n"

msg += f"\n---- V9.1 + MEMORY {len(new_memory)} block ----"
print(msg)
send_tele(msg)
save_memory(new_memory)
