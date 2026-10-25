import requests, os
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')

def send_tele(msg):
    try:
        r = requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",
        json={"chat_id": TELE_CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=15)
        print(f"TELE {r.status_code}")
    except Exception as e:
        print(f"TELE ERR {e}")

def get_tickers():
    # Retry 2x biar ga flat kayak 19:25 tadi!
    for _ in range(3):
        try:
            data = requests.get("https://indodax.com/api/tickers", timeout=20).json().get('tickers', {})
            if data: return data
        except: pass
    return {}

def fnum(v,d=0.0):
    try: v=str(v).replace(',','').strip(); return float(v) if v else d
    except: return d

# V8.1 ASLI + ERN DOANG! 46 KOIN!
BLACKLIST = {
    'usdt_idr','usdc_idr','dai_idr','busd_idr','btc_idr','eth_idr','bnb_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr',
    'usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'bal_idr','collat_idr','dupe_idr','ladys_idr','perp_idr','poly_idr','rfc_idr','dlc_idr','voxel_idr','yfii_idr','moonpig_idr','doge2_idr','mshd_idr','vbg_idr','vra_idr','cht_idr','krd_idr','strm_idr','slp_idr','d_idr','bone_idr','aura_idr','honey_idr','lrc_idr','zeta_idr','shred_idr','h2o_idr',
    'ern_idr'
}

tickers=get_tickers()
print(f"TICKERS COUNT {len(tickers)}") # Biar ketauan kalo API ngelag kayak 19:25!
wib=timezone(timedelta(hours=7))
now=datetime.now(wib).strftime("%H:%M WIB %d-%m")

candidates = []

for pair, d in tickers.items():
    if not pair.endswith('_idr'): continue
    if pair in BLACKLIST: continue
    last = fnum(d.get('last')); low = fnum(d.get('low')); high = fnum(d.get('high'))
    vol = fnum(d.get('vol_idr')); chg = fnum(d.get('change'))
    if low <= 0 or last < 1 or vol < 15_000_000: continue # BALIK KE 15Mn KAYA V8.1! BIAR CTSI 132Mn KEMAREN MASUK!
    
    pct_low = (last - low) / low * 100 if low > 0 else 0
    pct_from_high = (high - last) / high * 100 if high > 0 else 0

    # CTSI +21.62% VOL 148Mn INI BAKAL MASUK SINI!
    # MAV +113% & T +23% JUGA MASUK SINI!
    if chg >= 8 and vol >= 20_000_000: # DULU 12%, SEKARANG 8% BIAR CTSI +20% KEDETEK!
        candidates.append({'cat': "🔥 RUNNING PUMP", 'pair': pair, 'last': last, 'chg': chg, 'vol': vol, 'pct_low': pct_low, 'pct_from_high': pct_from_high})
    elif 0.1 <= chg < 8 and pct_low >= 0.2:
        candidates.append({'cat': "👀 AKUM EARLY", 'pair': pair, 'last': last, 'chg': chg, 'vol': vol, 'pct_low': pct_low, 'pct_from_high': pct_from_high})

def fmt_vol(v): return f"{v/1e9:.2f}Bn" if v>=1e9 else f"{v/1e6:.0f}Mn"

if not candidates:
    msg = f"<b>💤 SCAN {now}</b>\nMarket flat semua <0.15%\nTickers {len(tickers)}"
else:
    candidates.sort(key=lambda x: (-x['chg'], x['pct_low']))
    top = candidates[:12]
    msg = f"<b>⚡ SCAN {now}</b>\nV8.1 + ERN | Vol >=15Mn | Chg >=8%\n──────\n"
    for c in top:
        msg += f"{c['cat']} | {c['pair'].upper()[:-4]} Rp{c['last']:,.0f} ({c['chg']:+.2f}%)\n"
        msg += f"   Naik {c['pct_low']:.1f}% dr low | Jauh {c['pct_from_high']:.0f}% dr high | Vol {fmt_vol(c['vol'])}\n\n"

print(msg)
send_tele(msg)
