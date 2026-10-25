import requests, os
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')

def send_tele(msg):
    try:
        # HAPUS parse_mode HTML BIAR GA ERROR 400 KARENA TANDA <
        r = requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",
        json={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=15)
        print(f"TELE {r.status_code} - {r.text[:150]}")
        if r.status_code == 400:
            # Coba tanpa format apapun
            requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",
            json={"chat_id": TELE_CHAT_ID, "text": msg.replace('<','').replace('>','')}, timeout=15)
    except Exception as e:
        print(f"TELE ERR {e}")

def get_tickers():
    try: return requests.get("https://indodax.com/api/tickers", timeout=20).json().get('tickers', {})
    except: return {}

def fnum(v,d=0.0):
    try: v=str(v).replace(',','').strip(); return float(v) if v else d
    except: return d

# V8.1 + CUMA ERN! 46 KOIN!
BLACKLIST = {
    'usdt_idr','usdc_idr','dai_idr','busd_idr','btc_idr','eth_idr','bnb_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr',
    'usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'bal_idr','collat_idr','dupe_idr','ladys_idr','perp_idr','poly_idr','rfc_idr','dlc_idr','voxel_idr','yfii_idr','moonpig_idr','doge2_idr','mshd_idr','vbg_idr','vra_idr','cht_idr','krd_idr','strm_idr','slp_idr','d_idr','bone_idr','aura_idr','honey_idr','lrc_idr','zeta_idr','shred_idr','h2o_idr',
    'ern_idr'
}

tickers=get_tickers()
print(f"TICKERS {len(tickers)}")
wib=timezone(timedelta(hours=7))
now=datetime.now(wib).strftime("%H:%M WIB %d-%m")

candidates = []
all_list = []

for pair, d in tickers.items():
    if not pair.endswith('_idr'): continue
    if pair in BLACKLIST: continue
    last = fnum(d.get('last')); low = fnum(d.get('low')); high = fnum(d.get('high'))
    vol = fnum(d.get('vol_idr')); chg = fnum(d.get('change'))
    if low <= 0 or last < 1 or vol < 10_000_000: continue
    pct_low = (last - low) / low * 100 if low > 0 else 0
    all_list.append((pair, chg, vol, pct_low))
    if abs(chg) < 0.1: continue
    pct_from_high = (high - last) / high * 100 if high > 0 else 0
    if chg >= 5:
        candidates.append({'cat': "RUNNING PUMP", 'pair': pair, 'last': last, 'chg': chg, 'vol': vol, 'pct_low': pct_low, 'pct_from_high': pct_from_high})
    elif 0.1 <= chg < 5:
        candidates.append({'cat': "AKUM EARLY", 'pair': pair, 'last': last, 'chg': chg, 'vol': vol, 'pct_low': pct_low, 'pct_from_high': pct_from_high})

# DEBUG: LIAT 5 KOIN CHG TERBESAR BIAR TAU CTSI MASUK GA
all_list.sort(key=lambda x: -x[1])
print(f"TOP CHG: {all_list[:5]}")

def fmt_vol(v): return f"{v/1e9:.2f}Bn" if v>=1e9 else f"{v/1e6:.0f}Mn"

if not candidates:
    # FIX: GA PAKE TANDA < BIAR GA TELE 400 LAGI!
    msg = f"SCAN {now}\nMarket flat di bawah 0.1%\nTickers {len(tickers)}\nTop chg: {all_list[0][0]} {all_list[0][1]}% - {all_list[1][0]} {all_list[1][1]}%"
else:
    candidates.sort(key=lambda x: (-x['chg'], x['pct_low']))
    top = candidates[:10]
    msg = f"SCAN {now}\nV8.1 + ERN | Vol 10Mn | Chg 5pct\n------\n"
    for c in top:
        msg += f"{c['cat']} | {c['pair'].upper()[:-4]} Rp{c['last']:,.0f} ({c['chg']:+.2f}%)\n"
        msg += f"   Naik {c['pct_low']:.1f}% dr low | Vol {fmt_vol(c['vol'])}\n\n"

print(msg)
send_tele(msg)
