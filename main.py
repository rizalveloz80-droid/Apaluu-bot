# V8.6 FINAL + EARLY 5M - V8.5 6% + BLACKLIST FULL + 5M BREAKOUT FIX BEAT TELAT!
import requests, os
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')

def send_tele(msg):
    if not TELE_TOKEN or not TELE_CHAT_ID: return
    if len(msg) > 4000: msg = msg[:4000] + "\n...(kepotong)"
    try:
        requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",
                      json={"chat_id": TELE_CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=15)
    except Exception as e: print(f"TELE ERROR: {e}")

def get_tickers():
    try: return requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers', {})
    except: return {}

def fnum(v,d=0.0):
    try: v=str(v).replace(',','').strip(); return float(v) if v else d
    except: return d

BLACKLIST = {
    'usdt_idr','usdc_idr','dai_idr','busd_idr','btc_idr','eth_idr','bnb_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr',
    'usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'pepe_idr','xrp_idr','sol_idr','hype_idr','dodo_idr','pippin_idr','bome_idr','ada_idr','doge_idr','ena_idr','anoa_idr','ana_idr','sui_idr','ondo_idr','enb_idr','pengu_idr','pump_idr','shib_idr','nom_idr','mpro_idr','amph_idr','uni_idr','unmd_idr','fanch_idr','kdag_idr',
    'bal_idr','collat_idr','dupe_idr','ladys_idr','perp_idr','poly_idr','rfc_idr','dlc_idr','voxel_idr','yfii_idr','moonpig_idr','doge2_idr','mshd_idr','vbg_idr','vra_idr','cht_idr','krd_idr','strm_idr','slp_idr','d_idr','bone_idr','aura_idr','honey_idr','lrc_idr','zeta_idr','shred_idr','h2o_idr','ern_idr'
}

def fmt_vol(v): return f"{v/1e9:.2f}Bn" if v>=1e9 else f"{v/1e6:.0f}Mn"

# FUNGSI BARU V8.6 - CEK KENAIKAN 5 MENIT
def get_5m_change(pair):
    try:
        # ambil trade terakhir pair itu
        r = requests.get(f"https://indodax.com/api/trades/{pair}", timeout=6).json()
        trades = r.get('trades', []) if isinstance(r, dict) else r
        if not trades or len(trades) < 5: return 0.0
        # trade terbaru = paling atas, trade 5 menit lalu = cari yang beda waktu > 300 detik
        last_price = fnum(trades[0].get('price'))
        last_time = int(trades[0].get('date', 0))
        old_price = None
        for t in trades[1:]:
            if last_time - int(t.get('date',0)) >= 300: # 5 menit
                old_price = fnum(t.get('price'))
                break
        if not old_price: old_price = fnum(trades[-1].get('price'))
        if old_price <=0: return 0.0
        return (last_price - old_price) / old_price * 100
    except: return 0.0

tickers=get_tickers()
wib=timezone(timedelta(hours=7))
now=datetime.now(wib).strftime("%H:%M WIB %d-%m")
result = []
running = []

# ========== V8.6 LOCK 46 BLOCK + EARLY 5M ==========
candidates = []
for pair, d in tickers.items():
    if not pair.endswith('_idr') or pair in BLACKLIST: continue
    last = fnum(d.get('last')); low = fnum(d.get('low')); high = fnum(d.get('high')); vol = fnum(d.get('vol_idr'))
    if low <=0 or last <5 or vol < 35_000_000: continue
    pct_low = (last - low) / low * 100
    pct_high = (high - last) / high * 100
    candidates.append((pair, d, last, low, high, vol, pct_low, pct_high))

# sort by vol biar cek 5m yang rame dulu (hemat API)
candidates.sort(key=lambda x: x[5], reverse=True)

for pair, d, last, low, high, vol, pct_low, pct_high in candidates[:30]: # cek 30 coin ter-ramai aja biar cepet
    change_5m = get_5m_change(pair)
    # PRIORITAS 1: EARLY 5M - NAIK 3% DALAM 5 MENIT! INI YANG BIKIN GA KETINGGALAN BEAT!
    if change_5m >= 3.0 and pct_high >= 2 and pct_low < 25:
        result.append({'cat': "⚡ EARLY 5M", 'pair': pair, 'last': last, 'pct_low': pct_low, 'pct_high': pct_high, 'vol': vol, 'chg5m': change_5m})
    # PRIORITAS 2 & 3: FILTER 6% LAMA
    elif 0.8 <= pct_low < 5.8 and pct_high >= 4:
        result.append({'cat': "AKUM EARLY", 'pair': pair, 'last': last, 'pct_low': pct_low, 'pct_high': pct_high, 'vol': vol, 'chg5m': change_5m})
    elif 5.8 <= pct_low <= 150 and pct_high >= 1:
        result.append({'cat': "BARU MAU PUMP", 'pair': pair, 'last': last, 'pct_low': pct_low, 'pct_high': pct_high, 'vol': vol, 'chg5m': change_5m})

# Sisa coin yang sepi ga usah cek 5m
for pair, d, last, low, high, vol, pct_low, pct_high in candidates[30:]:
    if 0.8 <= pct_low < 5.8 and pct_high >= 4:
        result.append({'cat': "AKUM EARLY", 'pair': pair, 'last': last, 'pct_low': pct_low, 'pct_high': pct_high, 'vol': vol, 'chg5m': 0})
    elif 5.8 <= pct_low <= 150 and pct_high >= 1:
        result.append({'cat': "BARU MAU PUMP", 'pair': pair, 'last': last, 'pct_low': pct_low, 'pct_high': pct_high, 'vol': vol, 'chg5m': 0})

# ========== V9 RUNNING ==========
for pair, d in tickers.items():
    if not pair.endswith('_idr') or pair in BLACKLIST: continue
    last = fnum(d.get('last')); low = fnum(d.get('low')); high = fnum(d.get('high')); vol = fnum(d.get('vol_idr'))
    if low <=0 or high <=0 or vol < 100_000_000: continue
    pct_low = (last - low) / low * 100
    pct_high = (high - last) / high * 100
    if 0 <= pct_high <= 5 and pct_low >= 4:
        running.append({'symbol': pair.upper()[:-4], 'price': last, 'naik': pct_low, 'jauh': pct_high, 'vol': vol})

# GLOBAL LITE
global_lead = []
try:
    cg = requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=percent_change_24h_desc&per_page=30&page=1&price_change_percentage=24h", timeout=15).json()
    for c in cg:
        sym = c['symbol'].lower()
        pair_idr = f"{sym}_idr"
        if pair_idr not in tickers or pair_idr in BLACKLIST: continue
        cg_change = c.get('price_change_percentage_24h', 0) or 0
        if cg_change >= 15:
            indo_last = fnum(tickers[pair_idr].get('last')); indo_low = fnum(tickers[pair_idr].get('low'))
            indo_pct_low = (indo_last - indo_low) / indo_low * 100 if indo_low>0 else 0
            if indo_pct_low < 8:
                global_lead.append({'sym': sym.upper(), 'cg_change': cg_change, 'gap': cg_change - indo_pct_low, 'indo_pct': indo_pct_low})
        if len(global_lead) >= 5: break
except: pass

# KIRIM TELE
msg = f"EARLY {now}\nV8.6 EARLY 5M + 6% + 46 block\n------\n"
if result:
    result.sort(key=lambda x: (x.get('chg5m',0), x['pct_low']), reverse=True)
    for c in result[:12]:
        chg = f" 5m+{c['chg5m']:.1f}%" if c.get('chg5m',0)>=3 else ""
        msg += f"{c['cat']}{chg} | {c['pair'].upper()[:-4]} Rp{c['last']:,.0f} Naik {c['pct_low']:.1f}% | Jauh {c['pct_high']:.0f}% | Vol {fmt_vol(c['vol'])}\n"
else:
    msg += "Market flat\n"

if running:
    running = sorted(running, key=lambda x: x['vol'], reverse=True)[:5]
    msg += f"\n----- V9 RUNNING | {len(running)} block -----\n"
    for j,c in enumerate(running,11):
        msg += f"#{j} RUNNING | {c['symbol']} Rp{int(c['price']):,} Naik {c['naik']:.1f}% Jauh {c['jauh']:.0f}% Vol {fmt_vol(c['vol'])}\n"

if global_lead:
    msg += f"\n----- GLOBAL LEAD -----\n"
    for g in global_lead: msg += f"LEAD | {g['sym']} Global +{g['cg_change']:.1f}% Gap {g['gap']:.1f}%\n"
else:
    msg += f"\n----- GLOBAL LEAD: Ga ada gap -----\n"

print(msg)
send_tele(msg)
