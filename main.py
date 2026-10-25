import requests, os, json, time
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')
STATE_FILE = "state_v75_final.json"
OLD_STATE_FILE = "state_v73_rotation.json"
STABLE_FILE = "stable_66.json"

def send_tele(msg):
    try: requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",json={"chat_id": TELE_CHAT_ID, "text": msg, "parse_mode": "HTML"},timeout=15)
    except: pass

def load_state():
    old={}
    if os.path.exists(OLD_STATE_FILE):
        try:
            with open(OLD_STATE_FILE,'r') as f: old=json.load(f)
        except: pass
    new={}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE,'r') as f: new=json.load(f)
        except: pass
    for k,v in old.items():
        if k not in new: new[k]=v
    return new

def load_stable_66():
    if os.path.exists(STABLE_FILE):
        try:
            with open(STABLE_FILE,'r') as f: return set([x.lower() for x in json.load(f)])
        except: pass
    return {
        'usdt_idr','usdc_idr','dai_idr','busd_idr','usde_idr','paxg_idr','xaut_idr','xaus_idr',
        'btc_idr','eth_idr','bnb_idr','sol_idr','xrp_idr','doge_idr','ada_idr','trx_idr',
        'wbtc_idr','weth_idr','weur_idr','eurc_idr','usdp_idr','tusd_idr','gusd_idr','usdd_idr',
        'ern_idr','luna_idr','lunc_idr','ftt_idr','bsv_idr','bcha_idr','bch_idr','ltc_idr',
        'etc_idr','btt_idr','vet_idr','fil_idr','eos_idr','xtz_idr','neo_idr','waves_idr',
        'link_idr','dot_idr','uni_idr','aave_idr','comp_idr','mkr_idr','snx_idr','yfi_idr',
        'bat_idr','zrx_idr','mana_idr','sand_idr','axs_idr','slp_idr','chz_idr','enj_idr',
        'flow_idr','icp_idr','near_idr','egld_idr','hbar_idr','algo_idr','ftm_idr','one_idr',
        'klay_idr','celo_idr','rvn_idr'
    }

def save_state(s):
    with open(STATE_FILE,'w') as f: json.dump(s,f)
def get_tickers():
    try: return requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers', {})
    except: return {}
def fnum(v,d=0.0):
    try: v=str(v).replace(',','').strip(); return float(v) if v else d
    except: return d

STABLE_66 = load_stable_66()
BLACKLIST = STABLE_66 | {'pengu_idr','pepe_idr','shib_idr','floki_idr','bonk_idr'}
state=load_state()
now_ts=time.time()
tickers=get_tickers()
wib=timezone(timedelta(hours=7))
now=datetime.now(wib).strftime("%H:%M")

result_safe=[]
result_all=[]
result_bottom=[]
result_trending=[]
result_akum=[]

# === BLOK 1: FIX TYPO e2 + MICIN UNMD + MAV EARLY ===
for pair, d in tickers.items():
    if not pair.endswith('_idr'): continue
    if pair in BLACKLIST: continue
    if state.get(pair, {}).get('blocked_permanent'): continue

    s = state.get(pair, {})
    if s.get('count', 0) >= 3 and now_ts - s.get('time', 0) < 7200: continue

    last = fnum(d.get('last')); low = fnum(d.get('low')); high = fnum(d.get('high'))
    vol = fnum(d.get('vol_idr')); chg = fnum(d.get('change'))

    if low <= 0 or last < 1: continue
    if vol < 50_000_000 or vol > 10_000_000_000: continue

    pct_low = (last - low) / low * 100 if low > 0 else 0
    range_pct = (high - low) / low * 100 if low > 0 else 0
    pct_from_high = (high - last) / high * 100 if high > 0 else 0

    data_item = {
        'pair': pair, 'last': last, 'low': low, 'high': high, 'vol': vol, 'chg': chg,
        'pct_low': pct_low, 'range_pct': range_pct, 'pct_from_high': pct_from_high, 
        'c': chg, 's': pct_from_high
    }

    # === BLOK 2: KATEGORI ANTI BANJIR + ANTI NYANGKUT + MAV LEG 2 ===
    if (0.2 <= pct_low <= 4 and -15 <= chg <= -2 and 5 <= pct_from_high <= 20 
        and vol >= 100_000_000 and range_pct >= 7 
        and not (pct_from_high > 20 and range_pct > 35)):
        result_bottom.append(data_item)

    is_trending_normal = (chg >= 5 and pct_from_high < 15 and vol >= 200_000_000)
    is_trending_leg2 = (chg >= 50 and pct_low >= 100 and pct_from_high <= 35 and vol >= 500_000_000)
    is_super_pump = (chg >= 100 and pct_low >= 150)
    if (is_trending_normal or is_trending_leg2 or is_super_pump):
        result_trending.append(data_item)

    if (0.5 <= chg <= 20 and 5 <= range_pct <= 60 and 0.2 <= pct_low <= 20 
        and pct_from_high <= 8 and vol >= 50_000_000):
        result_akum.append(data_item)

    result_all.append(data_item)
    if chg < -2: continue
    if range_pct > 12 and pct_low < 3: continue
    if pct_from_high > 8 and pct_low < 3: continue
    if last >= high*0.97: continue
    result_safe.append(data_item)

def fmt_vol(v): return f"{v/1e9:.2f} Bn" if v>=1e9 else f"{v/1e6:.0f} Mn"
def boleh(pair, cd): s=state.get(pair,{}); return now_ts - s.get('time',0) >= cd*60
def vol_growth(pair, curr_vol): s=state.get(pair,{}); prev=s.get('vol',curr_vol); return curr_vol/prev if prev>0 else 1.0

# === BLOK 3: FIX SEPI 14:57 - FILTER ADAPTIF + TOP 10 ===
all_candidates = []
for cat, items in [("🔥 TRENDING", result_trending),
                   ("🚀 AKUMULASI", result_akum),
                   ("📉 BOTTOM", result_bottom)]:
    for i in items:
        i['category'] = cat
        all_candidates.append(i)

# [FIX ADAPTIF BIAR GA SEPI] - Jam 14:57 tadi SAFE 58 BOUNCE 113 tapi last >20 kosong!
# Coba >20 dulu, kalo kosong turunin ke >10, >5, terakhir >1 biar tele tetap masuk!
filtered_by_price = [c for c in all_candidates if c['last'] > 20]
if not filtered_by_price:
    filtered_by_price = [c for c in all_candidates if c['last'] > 10]
if not filtered_by_price:
    filtered_by_price = [c for c in all_candidates if c['last'] > 5]
if not filtered_by_price:
    filtered_by_price = [c for c in all_candidates if c['last'] > 1]
    
all_candidates = filtered_by_price

# Cooldown filter
filtered = []
for c in all_candidates:
    cd = 3 if "TRENDING" in c['category'] else 15
    if boleh(c['pair'], cd):
        filtered.append(c)
all_candidates = filtered

all_candidates.sort(key=lambda x: x['chg'], reverse=True)
top_10_coins = all_candidates[:10]

if not top_10_coins:
    print(f"SCAN V7.5 FINAL {now} | SAFE {len(result_safe)} BOUNCE {len(result_all)} | BLOCK {len(BLACKLIST)} | Sepi")
    exit()

for x in top_10_coins:
    prev=state.get(x['pair'],{})
    state[x['pair']]={'last':x['last'],'vol':x['vol'],'time':now_ts,'count':prev.get('count',0)+1,'blocked_permanent':prev.get('blocked_permanent',False)}
save_state(state)

msg = f"<b>💎 TOP 10 COIN BERBOBOT {now} WIB</b>\n"
msg += f"SAFE {len(result_safe)} BOUNCE {len(result_all)} | BLOCK {len(BLACKLIST)}\n"
msg += "──────\n"
for idx, coin in enumerate(top_10_coins, 1):
    msg += f"{idx}. {coin['category']} | {coin['pair'].upper()[:-4]}\n"
    msg += f"   Price: Rp{coin['last']:,.0f} ({coin['chg']:+.2f}%)\n"
    msg += f"   Vol: {fmt_vol(coin['vol'])} | naik {coin['pct_low']:.1f}% s {coin['pct_from_high']:.0f}%\n\n"

print(msg)
send_tele(msg)
