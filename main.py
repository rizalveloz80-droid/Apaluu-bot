import requests, os, json
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

# V8.1 ASLI + CUMA TAMBAH ERN DOANG! 46 KOIN!
BLACKLIST = {
    'usdt_idr','usdc_idr','dai_idr','busd_idr','btc_idr','eth_idr','bnb_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr',
    'usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'bal_idr','collat_idr','dupe_idr','ladys_idr','perp_idr','poly_idr','rfc_idr','dlc_idr','voxel_idr','yfii_idr','moonpig_idr','doge2_idr','mshd_idr','vbg_idr','vra_idr','cht_idr','krd_idr','strm_idr','slp_idr','d_idr','bone_idr','aura_idr','honey_idr','lrc_idr','zeta_idr','shred_idr','h2o_idr',
    'ern_idr'
}

tickers=get_tickers()
wib=timezone(timedelta(hours=7))
now=datetime.now(wib).strftime("%H:%M WIB %d-%m")

result = []

for pair, d in tickers.items():
    if not pair.endswith('_idr'): continue
    if pair in BLACKLIST: continue
    last = fnum(d.get('last')); low = fnum(d.get('low')); high = fnum(d.get('high'))
    vol = fnum(d.get('vol_idr')); chg = fnum(d.get('change'))
    if low <= 0 or last < 1 or vol < 25_000_000: continue
    if abs(chg) < 0.15: continue

    pct_low = (last - low) / low * 100 if low > 0 else 0
    pct_from_high = (high - last) / high * 100 if high > 0 else 0

    # V8.1 EARLY + V10 RUNNING PUMP
    if chg >= 12 and vol >= 40_000_000:
        result.append({'cat': "🔥 RUNNING PUMP", 'pair': pair, 'last': last, 'chg': chg, 'vol': vol, 'pct_low': pct_low, 'pct_from_high': pct_from_high})
    elif 0.15 <= chg < 12 and pct_low >= 0.3:
        result.append({'cat': "👀 AKUM EARLY", 'pair': pair, 'last': last, 'chg': chg, 'vol': vol, 'pct_low': pct_low, 'pct_from_high': pct_from_high})

def fmt_vol(v): return f"{v/1e9:.2f}Bn" if v>=1e9 else f"{v/1e6:.0f}Mn"

result.sort(key=lambda x: (0 if "RUNNING" in x['cat'] else 1, x['pct_low']))
top = result[:10]

if not top:
    # Kalo flat kayak 19:14 tadi, biar ga kosong
    msg = f"<b>💤 SCAN {now}</b>\nMarket flat semua <0.15%"
else:
    msg = f"<b>⚡ EARLY {now}</b>\nV8.1 + ERN + RUNNING PUMP\n──────\n"
    for c in top:
        msg += f"{c['cat']} | {c['pair'].upper()[:-4]} Rp{c['last']:,.0f} ({c['chg']:+.2f}%)\n"
        msg += f"   Naik {c['pct_low']:.1f}% dr low | Jauh {c['pct_from_high']:.0f}% dr high | Vol {fmt_vol(c['vol'])}\n\n"

print(msg)
send_tele(msg)

# AUTO HAPUS STATE BIAR GA 400 KOIN LAGI
if os.path.exists(STATE_FILE):
    try: os.remove(STATE_FILE)
    except: pass
