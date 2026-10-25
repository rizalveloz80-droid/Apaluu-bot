import requests, os, json, time
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')
STATE_FILE = "state_v8_early.json"

def send_tele(msg):
    try: requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",json={"chat_id": TELE_CHAT_ID, "text": msg, "parse_mode": "HTML"},timeout=15)
    except: pass

def get_tickers():
    try: return requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers', {})
    except: return {}

def fnum(v,d=0.0):
    try: v=str(v).replace(',','').strip(); return float(v) if v else d
    except: return d

# CUMA ERN + 27 DELISTING + STABLE = 46! SAMA KAYAK 18:02 YANG LU SUKA!
BLACKLIST = {
    'usdt_idr','usdc_idr','dai_idr','busd_idr','btc_idr','eth_idr','bnb_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr',
    'usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'bal_idr','collat_idr','dupe_idr','ladys_idr','perp_idr','poly_idr','rfc_idr','dlc_idr','voxel_idr','yfii_idr','moonpig_idr','doge2_idr','mshd_idr','vbg_idr','vra_idr','cht_idr','krd_idr','strm_idr','slp_idr','d_idr','bone_idr','aura_idr','honey_idr','lrc_idr','zeta_idr','shred_idr','h2o_idr',
    'ern_idr'
}

tickers=get_tickers()
wib=timezone(timedelta(hours=7))
now=datetime.now(wib).strftime("%H:%M WIB %d-%m")

early = []
running = []

for pair, d in tickers.items():
    if not pair.endswith('_idr'): continue
    if pair in BLACKLIST: continue
    
    last = fnum(d.get('last')); low = fnum(d.get('low')); high = fnum(d.get('high'))
    vol = fnum(d.get('vol_idr')); chg = fnum(d.get('change'))
    
    if low <= 0 or last < 1: continue
    if vol < 25_000_000: continue
    if abs(chg) < 0.2: continue

    pct_low = (last - low) / low * 100 if low > 0 else 0
    pct_from_high = (high - last) / high * 100 if high > 0 else 0

    # TANPA GROWTH SAMA SEKALI! INI YANG BIKIN 18:54-19:08 TIDUR TADI!
    
    # RUNNING PUMP - BSV +33% KEMARIN BAKAL MASUK SINI!
    if chg >= 12 and vol >= 40_000_000:
        running.append({'pair': pair, 'last': last, 'chg': chg, 'vol': vol, 'pct_low': pct_low, 'pct_from_high': pct_from_high, 'category': "🔥 RUNNING PUMP"})
    # EARLY - NMD Naik 0.9% dr low KEMARIN MASUK SINI!
    elif 0.2 <= chg < 12 and pct_low >= 0.3:
        early.append({'pair': pair, 'last': last, 'chg': chg, 'vol': vol, 'pct_low': pct_low, 'pct_from_high': pct_from_high, 'category': "👀 AKUM EARLY"})

def fmt_vol(v): return f"{v/1e9:.2f}Bn" if v>=1e9 else f"{v/1e6:.0f}Mn"

all_candidates = running + early
# Running pump di atas, urut chg paling gede
all_candidates.sort(key=lambda x: (-x['chg'] if "RUNNING" in x['category'] else 999, x['pct_low']))

if not all_candidates:
    msg = f"<b>💤 SCAN {now}</b>\nMarket flat - Ga ada yg >=0.2%\n"
    print(msg); send_tele(msg); exit()

top_10 = all_candidates[:12]
msg = f"<b>⚡ SCAN {now}</b>\n"
msg += f"BLOCK {len(BLACKLIST)} (ERN only) | NO GROWTH FILTER\n──────\n"
for c in top_10:
    msg += f"{c['category']} | {c['pair'].upper()[:-4]} Rp{c['last']:,.0f} ({c['chg']:+.2f}%)\n"
    msg += f"   Naik {c['pct_low']:.1f}% dr low | Jauh {c['pct_from_high']:.0f}% dr high | Vol {fmt_vol(c['vol'])}\n\n"

print(msg)
send_tele(msg)

# HAPUS STATE FILE BIAR GA 400 KOIN TERUS!
if os.path.exists(STATE_FILE):
    try: os.remove(STATE_FILE); print("State 400 koin dihapus biar fresh!")
    except: pass
