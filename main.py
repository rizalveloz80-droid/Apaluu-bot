import requests, os
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')

def send_tele(msg):
    try:
        # NO HTML - BIAR GA TELE 400
        r = requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",
        json={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=15)
        print(f"TELE {r.status_code}")
    except Exception as e:
        print(f"TELE ERR {e}")

def get_tickers():
    try: return requests.get("https://indodax.com/api/tickers", timeout=20).json().get('tickers', {})
    except: return {}

def fnum(v,d=0.0):
    try: v=str(v).replace(',','').strip(); return float(v) if v else d
    except: return d

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
debug = []

for pair, d in tickers.items():
    if not pair.endswith('_idr'): continue
    if pair in BLACKLIST: continue
    last = fnum(d.get('last')); low = fnum(d.get('low')); high = fnum(d.get('high'))
    vol = fnum(d.get('vol_idr')); chg_api = fnum(d.get('change'))
    if low <=0 or last <1 or vol < 25_000_000: continue

    pct_low = (last - low) / low * 100 if low>0 else 0
    pct_high = (high - last) / high * 100 if high>0 else 0
    # PAKE PCT_LOW JANGAN PAKE CHG API! SOALNYA CHG API 0.0% KAYA JAM 19:49 TADI!
    debug.append((pair, pct_low, chg_api))

    if pct_low >= 0.3 and pct_high >= 2 and pct_low <= 80:
        cat = "RUNNING PUMP" if pct_low >= 15 else "AKUM EARLY"
        result.append({'cat': cat, 'pair': pair, 'last': last, 'chg_api': chg_api, 'pct_low': pct_low, 'pct_high': pct_high, 'vol': vol})

debug.sort(key=lambda x: -x[1])
print(f"TOP PCT_LOW: {debug[:5]}")
print(f"TOTAL CANDIDATE {len(result)}")

def fmt_vol(v): return f"{v/1e9:.2f}Bn" if v>=1e9 else f"{v/1e6:.0f}Mn"

if not result:
    msg = f"SCAN {now}\nMarket flat - {len(tickers)} tickers\nTop naik dr low: {debug[0][0]} {debug[0][1]:.1f}% - {debug[1][0]} {debug[1][1]:.1f}%"
else:
    result.sort(key=lambda x: x['pct_low'])
    top = result[:10]
    msg = f"EARLY {now}\nV8.1 FIX no change - {len(BLACKLIST)} block\n------\n"
    for c in top:
        msg += f"{c['cat']} | {c['pair'].upper()[:-4]} Rp{c['last']:,.0f} API {c['chg_api']:+.1f}%\n"
        msg += f"   Naik {c['pct_low']:.1f}% dr low | Jauh {c['pct_high']:.0f}% dr high | Vol {fmt_vol(c['vol'])}\n\n"

print(msg)
send_tele(msg)
