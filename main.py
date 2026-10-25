import requests, os, json, time
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')
STATE_FILE = "state_v78_gabungan.json"
OLD_STATE_FILE = "state_v73_rotation.json"
STABLE_FILE = "stable_66.json"

def send_tele(msg):
    try: requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",json={"chat_id": TELE_CHAT_ID, "text": msg},timeout=15)
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
BLACKLIST = STABLE_66
state=load_state()
now_ts=time.time()
tickers=get_tickers()
wib=timezone(timedelta(hours=7))
now=datetime.now(wib).strftime("%H:%M")

result_safe=[]
result_all=[]

for pair,d in tickers.items():
    if not pair.endswith('_idr'): continue
    if pair in BLACKLIST: continue
    if state.get(pair,{}).get('blocked_permanent'): continue
    s=state.get(pair,{})
    if s.get('count',0)>=3 and now_ts - s.get('time',0) < 7200: continue
    last=fnum(d.get('last')); low=fnum(d.get('low')); high=fnum(d.get('high'))
    vol=fnum(d.get('vol_idr')); chg=fnum(d.get('change'))
    if low<=0 or last<30: continue
    if vol<80_000_000 or vol>10_000_000_000: continue
    pct_low=(last-low)/low*100 if low>0 else 0
    range_pct=(high-low)/low*100 if low>0 else 0
    pct_from_high=(high-last)/high*100 if high>0 else 0
    # s punya lu = pct_from_high, c punya lu = chg
    result_all.append({'pair':pair,'last':last,'low':low,'high':high,'vol':vol,'chg':chg,'pct_low':pct_low,'range_pct':range_pct,'pct_from_high':pct_from_high, 'c':chg, 's':pct_from_high})
    if chg < -2: continue
    if range_pct > 12 and pct_low < 3: continue
    if pct_from_high > 8 and pct_low < 3: continue
    if last >= high*0.97: continue
    result_safe.append({'pair':pair,'last':last,'low':low,'high':high,'vol':vol,'chg':chg,'pct_low':pct_low,'range_pct':range_pct,'pct_from_high':pct_from_high})

def fmt_vol(v): return f"{v/1e9:.2f} Bn" if v>=1e9 else f"{v/1e6:.0f} Mn"
def boleh(pair, cd): s=state.get(pair,{}); return now_ts - s.get('time',0) >= cd*60
def vol_growth(pair, curr_vol): s=state.get(pair,{}); prev=s.get('vol',curr_vol); return curr_vol/prev if prev>0 else 1.0

akum=[]; pemula=[]; akan=[]; lagi=[]; trending=[]; bottom=[]

for x in result_safe:
    if not (-1.5 <= x['chg'] <= 1.5 and 0.2 <= x['pct_low'] <= 1.8 and x['pct_from_high'] <= 2.5 and x['range_pct'] <= 5): continue
    if not boleh(x['pair'],15): continue
    akum.append(x)

for x in result_safe:
    if x['pair'] in {y['pair'] for y in akum}: continue
    if not (1.8 <= x['pct_low'] <= 8 and x['range_pct']<=60 and x['chg']>=0.5 and x['pct_from_high']<=6): continue
    if not boleh(x['pair'],15): continue
    pemula.append(x)

for x in result_safe:
    if x['pair'] in {y['pair'] for y in akum+pemula}: continue
    growth=vol_growth(x['pair'], x['vol'])
    if growth >= 2.0:
        if not (5 < x['pct_low'] <= 20 and x['pct_from_high']<=8): continue
    else:
        if not (8 < x['pct_low'] <= 20 and x['chg']>=1 and x['pct_from_high']<=8): continue
    if not boleh(x['pair'],15): continue
    akan.append(x)

for x in result_safe:
    if x['pair'] in {y['pair'] for y in akum+pemula+akan}: continue
    if not (20 < x['pct_low'] <= 40 and x['vol']>=200_000_000 and x['chg']>=3 and x['pct_from_high']<=8): continue
    if not boleh(x['pair'],15): continue
    lagi.append(x)

for x in result_safe:
    if x['pair'] in {y['pair'] for y in akum+pemula+akan+lagi}: continue
    if not ((x['chg']>=10 and x['vol']>=200_000_000 and x['pct_from_high']<=7) or (x['pct_low']>=35 and x['chg']>=5 and x['pct_from_high']<=7)): continue
    if not boleh(x['pair'],10): continue
    trending.append(x)

# === BOUNCE MERAH GABUNGAN - PUNYA LU c<0 s>20 + SAFETY GUA! ===
for x in result_all:
    if x['pair'] in {y['pair'] for y in akum+pemula+akan+lagi+trending}: continue
    c = x['c'] # chg punya lu
    s = x['s'] # pct_from_high punya lu
    
    # LOGIKA LU: c < 0 and s >20 and 5 <= s <=70 -> GUA BENERIN JADI 5-20 AJA! 70 KEGEDEAN!
    if not (c < 0): continue
    if not (5 <= s <= 20): continue # s 5-20% doang! Kalo 70% = crash UCJL!
    if not (-15 <= c <= -2): continue # c -15 sampai -2! Jangan -30%!
    
    # SAFETY GUA TAMBAHAN:
    if not (0.2 <= x['pct_low'] <= 4): continue # harus di lantai!
    if x['vol'] < 100_000_000: continue # harus ada buyer!
    if not (x['range_pct'] >= 7): continue
    if x['pct_from_high'] > 20 and x['range_pct'] > 35: continue
    if not boleh(x['pair'],30): continue
    bottom.append(x)

bottom=sorted(bottom,key=lambda x:x['vol'],reverse=True)[:4]
akum=sorted(akum,key=lambda x:x['vol'],reverse=True)[:2]
pemula=sorted(pemula,key=lambda x:x['pct_low'],reverse=True)[:3]
akan=sorted(akan,key=lambda x:x['vol'],reverse=True)[:3]
lagi=sorted(lagi,key=lambda x:x['pct_low'],reverse=True)[:2]
trending=sorted(trending,key=lambda x:x['chg'],reverse=True)[:3]

for x in akum+pemula+akan+lagi+trending+bottom:
    prev=state.get(x['pair'],{})
    state[x['pair']]={'last':x['last'],'vol':x['vol'],'time':now_ts,'count':prev.get('count',0)+1,'blocked_permanent':prev.get('blocked_permanent',False)}
save_state(state)

msg=f"SCAN V7.8 {now} WIB | SAFE {len(result_safe)} BOUNCE {len(result_all)} | BLOCK {len(BLACKLIST)} stable\n\n"
if trending: msg+="🔥 TRENDING:\n"+ "".join([f"-> {c['pair'].upper()[:-4]} CHG {c['chg']:.1f}% vol {fmt_vol(c['vol'])}\n" for c in trending])+"\n"
if lagi: msg+="🚀 LAGI:\n"+ "".join([f"-> {c['pair'].upper()[:-4]} naik {c['pct_low']:.0f}% vol {fmt_vol(c['vol'])}\n" for c in lagi])+"\n"
if akan: msg+="🎯 AKAN:\n"+ "".join([f"-> {c['pair'].upper()[:-4]} naik {c['pct_low']:.0f}% vol {fmt_vol(c['vol'])}\n" for c in akan])+"\n"
if pemula: msg+="🌱 PEMULA:\n"+ "".join([f"-> {c['pair'].upper()[:-4]} naik {c['pct_low']:.1f}% vol {fmt_vol(c['vol'])}\n" for c in pemula])+"\n"
if akum: msg+="💎 AKUM:\n"+ "".join([f"-> {c['pair'].upper()[:-4]} naik {c['pct_low']:.1f}% vol {fmt_vol(c['vol'])}\n" for c in akum])+"\n"
if bottom: msg+="💥 BOUNCE MERAH (c<0 s 5-20% + SAFETY):\n"+ "".join([f"-> {c['pair'].upper()[:-4]} CHG {c['c']:.1f}% s {c['s']:.0f}% low {c['pct_low']:.1f}% vol {fmt_vol(c['vol'])}\n" for c in bottom])+"\n"

if not (trending or lagi or akan or pemula or akum or bottom):
    print(f"V7.8 {now} | SAFE {len(result_safe)} BOUNCE {len(result_all)} | BLOCK {len(BLACKLIST)} | Sepi"); exit()

print(msg)
send_tele(msg)
