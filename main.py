# V8.3 FINAL LOCK - FIX SKYAI 22% + MAV 73% KEDETEK! V8.2 + ANTI PUCUK FILTER
# ERN TETEP KE-BLOCK 46!
import requests, os
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')

def send_tele(msg):
    requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",
    json={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=15)

def get_tickers():
    try: return requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers', {})
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

for pair, d in tickers.items():
    if not pair.endswith('_idr') or pair in BLACKLIST: continue
    last = fnum(d.get('last')); low = fnum(d.get('low')); high = fnum(d.get('high')); vol = fnum(d.get('vol_idr'))
    if low <=0 or last <5 or vol < 35_000_000: continue
    pct_low = (last - low) / low * 100
    pct_high = (high - last) / high * 100
    
    # FIX V8.3: BEDA FILTER BIAR YANG RUNNING MASUK!
    if 0.8 <= pct_low < 12 and pct_high >= 4:
        result.append({'cat': "AKUM EARLY", 'pair': pair, 'last': last, 'pct_low': pct_low, 'pct_high': pct_high, 'vol': vol})
    elif 12 <= pct_low <= 150 and pct_high >= 1:  # YANG PUMP 12-150% BOLEH MEPET HIGH 1% AJA!
        result.append({'cat': "BARU MAU PUMP", 'pair': pair, 'last': last, 'pct_low': pct_low, 'pct_high': pct_high, 'vol': vol})

def fmt_vol(v): return f"{v/1e9:.2f}Bn" if v>=1e9 else f"{v/1e6:.0f}Mn"

if not result:
    msg = f"SCAN {now}\nMarket flat - {len(tickers)} tickers"
else:
    result.sort(key=lambda x: x['pct_low'], reverse=True) # YANG GEDE DI ATAS BIAR KELIATAN!
    msg = f"EARLY {now}\nV8.3 FINAL 46 block\n------\n"
    for c in result[:10]:
        msg += f"{c['cat']} | {c['pair'].upper()[:-4]} Rp{c['last']:,.0f}\n   Naik {c['pct_low']:.1f}% dr low | Jauh {c['pct_high']:.0f}% dr high | Vol {fmt_vol(c['vol'])}\n\n"

print(msg)
send_tele(msg)
