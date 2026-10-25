# V8.4 FINAL + GLOBAL LITE - V8.3 TETEP LOCK 46 BLOCK + TAMBAH 5 GLOBAL LEAD COINGECKO!
import requests, os, time
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

def fmt_vol(v): return f"{v/1e9:.2f}Bn" if v>=1e9 else f"{v/1e6:.0f}Mn"

tickers=get_tickers()
wib=timezone(timedelta(hours=7))
now=datetime.now(wib).strftime("%H:%M WIB %d-%m")
result = []

# ========== V8.3 FINAL LOCK - JANGAN DIUBAH! ==========
for pair, d in tickers.items():
    if not pair.endswith('_idr') or pair in BLACKLIST: continue
    last = fnum(d.get('last')); low = fnum(d.get('low')); high = fnum(d.get('high')); vol = fnum(d.get('vol_idr'))
    if low <=0 or last <5 or vol < 35_000_000: continue
    pct_low = (last - low) / low * 100
    pct_high = (high - last) / high * 100
    if 0.8 <= pct_low < 12 and pct_high >= 4:
        result.append({'cat': "AKUM EARLY", 'pair': pair, 'last': last, 'pct_low': pct_low, 'pct_high': pct_high, 'vol': vol})
    elif 12 <= pct_low <= 150 and pct_high >= 1:
        result.append({'cat': "BARU MAU PUMP", 'pair': pair, 'last': last, 'pct_low': pct_low, 'pct_high': pct_high, 'vol': vol})

# ========== GLOBAL LITE COINGECKO - TAMBAHAN 5-10! ==========
global_lead = []
try:
    # Ambil top gainer global 24h dari CoinGecko (akurat & ga ke-block kayak Binance)
    cg = requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=percent_change_24h_desc&per_page=30&page=1&price_change_percentage=24h", timeout=15).json()
    for c in cg:
        sym = c['symbol'].lower()  # ex: mav
        pair_idr = f"{sym}_idr"
        if pair_idr not in tickers or pair_idr in BLACKLIST: continue
        cg_change = c.get('price_change_percentage_24h', 0) or 0
        cg_vol_usd = c.get('total_volume', 0) or 0
        # Cek Indodax masih sepi ga?
        d = tickers[pair_idr]
        indo_last = fnum(d.get('last')); indo_low = fnum(d.get('low'))
        indo_pct_low = (indo_last - indo_low) / indo_low * 100 if indo_low>0 else 0
        
        # LOGIC ALPHA TEMEN LU: Global udah +15% Vol >10M, Indodax masih <5%!
        if cg_change >= 15 and cg_vol_usd >= 10_000_000 and indo_pct_low < 8:
            global_lead.append({
                'sym': sym.upper(),
                'cg_change': cg_change,
                'cg_vol': cg_vol_usd,
                'indo_pct': indo_pct_low,
                'gap': cg_change - indo_pct_low
            })
        if len(global_lead) >= 5: break
    time.sleep(1)
except Exception as e:
    print("CG error", e)

# ========== KIRIM TELE 15-20 COIN! ==========
msg = f"EARLY {now}\nV8.4 FINAL+GLOBAL 46 block\n------\n"
if result:
    result.sort(key=lambda x: x['pct_low'], reverse=True)
    for c in result[:10]:
        msg += f"{c['cat']} | {c['pair'].upper()[:-4]} Rp{c['last']:,.0f} Naik {c['pct_low']:.1f}% | Jauh {c['pct_high']:.0f}% | Vol {fmt_vol(c['vol'])}\n"
else:
    msg += "Market flat V8.3\n"

if global_lead:
    msg += f"\n------ GLOBAL LEAD (CoinGecko Lite) ------\n"
    for g in global_lead:
        msg += f"LEAD | {g['sym']} Global +{g['cg_change']:.1f}% Vol ${g['cg_vol']/1e6:.1f}M | Indo +{g['indo_pct']:.1f}% | GAP {g['gap']:.0f}% -> SIAP PUMP!\n"
else:
    msg += f"\n------ GLOBAL LEAD: Ga ada gap gede, Indodax udah ngikut global ------\n"

print(msg)
send_tele(msg)
