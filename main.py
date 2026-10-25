import requests, os, json, time
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')
STATE_FILE = "state_v8_early.json"

def send_tele(msg):
    try: requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",json={"chat_id": TELE_CHAT_ID, "text": msg, "parse_mode": "HTML"},timeout=15)
    except: pass

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE,'r') as f: return json.load(f)
        except: pass
    return {}

def save_state(s):
    with open(STATE_FILE,'w') as f: json.dump(s,f)

def get_tickers():
    try: return requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers', {})
    except: return {}

def fnum(v,d=0.0):
    try: v=str(v).replace(',','').strip(); return float(v) if v else d
    except: return d

# === INI YANG LU MAU MIN! CUMA ERN DOANG + DELISTING RESMI + STABLE! ===
# Total 46 - Sama kayak V8.4 yang enak, bukan 66!
BLACKLIST = {
    'usdt_idr','usdc_idr','dai_idr','busd_idr','btc_idr','eth_idr','bnb_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr',
    'usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'bal_idr','collat_idr','dupe_idr','ladys_idr','perp_idr','poly_idr','rfc_idr','dlc_idr','voxel_idr','yfii_idr','moonpig_idr','doge2_idr','mshd_idr','vbg_idr','vra_idr','cht_idr','krd_idr','strm_idr','slp_idr','d_idr','bone_idr','aura_idr','honey_idr','lrc_idr','zeta_idr','shred_idr','h2o_idr',
    'ern_idr' # <-- CUMA INI TAMBAHANNYA!
}

state=load_state()
now_ts=time.time()
tickers=get_tickers()
wib=timezone(timedelta(hours=7))
now=datetime.now(wib).strftime("%H:%M WIB %d-%m")

result_early = []
result_running = []
all_vol_state = {}

for pair, d in tickers.items():
    if not pair.endswith('_idr'): continue
    if pair in BLACKLIST: continue
    
    last = fnum(d.get('last')); low = fnum(d.get('low')); high = fnum(d.get('high'))
    vol = fnum(d.get('vol_idr')); chg = fnum(d.get('change'))
    
    if vol > 0:
        all_vol_state[pair] = {'last': last, 'vol': vol, 'time': now_ts}

    if low <= 0 or last < 1: continue
    if vol < 25_000_000: continue
    if abs(chg) < 0.2: continue # Anti +0.0% kayak 18:31 kemarin

    pct_low = (last - low) / low * 100 if low > 0 else 0
    pct_from_high = (high - last) / high * 100 if high > 0 else 0

    prev = state.get(pair, {})
    prev_vol = prev.get('vol', 0)
    is_first_run = prev_vol == 0
    vol_growth = 1.0 if is_first_run else (vol / prev_vol if prev_vol > 0 else 1.0)
    # Growth cukup 1% aja biar run ke-2 ga tidur kayak 18:54!
    ok_growth = True if is_first_run else vol_growth >= 1.01

    # 1. EARLY - Kayak NMD jam 18:31 Naik 0.9% dr low
    if (0.2 <= chg <= 15 and pct_low >= 0.3 and ok_growth):
        data = {'pair': pair, 'last': last, 'chg': chg, 'vol': vol, 'pct_low': pct_low, 'pct_from_high': pct_from_high, 'growth': vol_growth, 'first': is_first_run}
        data['category'] = "👀 AKUM EARLY"
        result_early.append(data)
    
    # 2. RUNNING PUMP - Buat BSV kayak screenshot lu +33.43% jam 19:00!
    # Ini ga pake syarat jauh dr high, soalnya emang lagi di high!
    if (chg >= 15 and vol >= 50_000_000 and pct_low >= 10):
        data = {'pair': pair, 'last': last, 'chg': chg, 'vol': vol, 'pct_low': pct_low, 'pct_from_high': pct_from_high, 'growth': vol_growth, 'first': is_first_run}
        data['category'] = "🔥 RUNNING PUMP"
        result_running.append(data)

# Save semua
for k,v in state.items():
    if k not in all_vol_state: all_vol_state[k] = v
if len(all_vol_state) > 400: all_vol_state = dict(list(all_vol_state.items())[-400:])
save_state(all_vol_state)

def fmt_vol(v): return f"{v/1e9:.2f}Bn" if v>=1e9 else f"{v/1e6:.0f}Mn"

# Gabung: Running pump di atas, Early di bawah
all_candidates = result_running + result_early
all_candidates.sort(key=lambda x: (0 if "RUNNING" in x['category'] else 1, -x['chg']))

if not all_candidates:
    msg = f"<b>💤 SCAN {now}</b>\nGa ada early/running\nState {len(all_vol_state)}"
    print(msg); send_tele(msg); exit()

top_10 = all_candidates[:10]
msg = f"<b>⚡ SCAN {now}</b>\n"
msg += f"BLOCK {len(BLACKLIST)} (ERN+27 delist) | Growth 1.01x\n──────\n"
for c in top_10:
    tag = " NEW" if c['first'] else f" G{c['growth']:.2f}x"
    msg += f"{c['category']} | {c['pair'].upper()[:-4]} Rp{c['last']:,.0f} ({c['chg']:+.2f}%){tag}\n"
    msg += f"   Naik {c['pct_low']:.1f}% dr low | Jauh {c['pct_from_high']:.0f}% dr high | Vol {fmt_vol(c['vol'])}\n\n"

print(msg)
send_tele(msg)
