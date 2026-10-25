import requests, os, json, time
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')
STATE_FILE = "state_v7.json"

def send_tele(msg):
    try: requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",json={"chat_id": TELE_CHAT_ID, "text": msg},timeout=15)
    except: pass
def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE,'r') as f: return json.load(f)
        except: return {}
    return {}
def save_state(s):
    with open(STATE_FILE,'w') as f: json.dump(s,f)
def get_tickers():
    try: return requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers', {})
    except: return {}
def fnum(v,d=0.0):
    try:
        v=str(v).replace(',','').strip()
        return float(v) if v else d
    except: return d

BLACKLIST = {'usdt_idr','usdc_idr','dai_idr','busd_idr','usde_idr','paxg_idr','ern_idr','luna_idr','lunc_idr','ftt_idr'}

state=load_state()
now_ts=time.time()
tickers=get_tickers()
wib=timezone(timedelta(hours=7))
now=datetime.now(wib).strftime("%H:%M")
result=[]

for pair,d in tickers.items():
    if not pair.endswith('_idr') or pair in BLACKLIST: continue
    last=fnum(d.get('last')); low=fnum(d.get('low')); high=fnum(d.get('high'))
    vol=fnum(d.get('vol_idr')); chg=fnum(d.get('change'))
    if low<=0 or last<20: continue
    if vol<20_000_000 or vol>20_000_000_000: continue
    pct_low=(last-low)/low*100 if low>0 else 0
    pct_high=(high-last)/last*100 if last>0 else 100
    range_pct=(high-low)/low*100 if low>0 else 0
    # JANGAN BLOCK RESISTANCE BUAT TRENDING! BREAKOUT BOLEH!
    # if last >= high*0.92: continue  # HAPUS! INI YANG BIKIN MAV KE BLOCK!
    result.append({'pair':pair,'last':last,'low':low,'high':high,'vol':vol,'chg':chg,'pct_low':pct_low,'pct_high':pct_high,'range_pct':range_pct})

def fmt_vol(v): return f"{v/1e9:.2f} Bn" if v>=1e9 else f"{v/1e6:.0f} Mn"
def boleh(pair, cd):
    s=state.get(pair,{}); return now_ts - s.get('time',0) >= cd*60

akum=[]; pemula=[]; akan=[]; lagi=[]; trending=[]

# AKUM 0.3-1.5% vol gede
for x in result:
    if not (0.3 <= x['pct_low'] <= 1.5 and x['chg']>-1 and x['vol']>=80_000_000): continue
    if not boleh(x['pair'],30): continue
    akum.append(x)
akum=sorted(akum,key=lambda x:x['vol'],reverse=True)[:2]

# PEMULA 1.5-8% - LONGGARIN DARI 5% KE 8%!
for x in result:
    if x['pair'] in {y['pair'] for y in akum}: continue
    if not (1.5 <= x['pct_low'] <= 8 and x['range_pct']<=60 and x['vol']>=80_000_000): continue
    if not boleh(x['pair'],25): continue
    pemula.append(x)
pemula=sorted(pemula,key=lambda x:x['pct_low'],reverse=True)[:3]

# AKAN 8-20% - LONGGARIN DARI 5-12% KE 8-20%! BIAR EPIC 32% KETANGKEP DI SINI ATAU LAGI!
for x in result:
    if x['pair'] in {y['pair'] for y in akum+pemula}: continue
    if not (8 < x['pct_low'] <= 20 and x['vol']>=100_000_000): continue
    if not boleh(x['pair'],20): continue
    akan.append(x)
akan=sorted(akan,key=lambda x:x['vol'],reverse=True)[:3]

# LAGI 20-40% - INI YANG KEMAREN LOBANG! SEKARANG 20-40% BIAR EPIC 32% MASUK!
for x in result:
    if x['pair'] in {y['pair'] for y in akum+pemula+akan}: continue
    if not (20 < x['pct_low'] <= 40 and x['vol']>=100_000_000): continue
    if not boleh(x['pair'],20): continue
    lagi.append(x)
lagi=sorted(lagi,key=lambda x:x['pct_low'],reverse=True)[:3]

# TRENDING - BACA CHG ASLI INDODAX! INI KUNCI! T +48%, MAV +52%, ORDER +58% LANGSUNG MASUK!
for x in result:
    if x['pair'] in {y['pair'] for y in akum+pemula+akan+lagi}: continue
    # chg asli indodax >=20% ATAU pct_low >=40% = TRENDING!
    if not ((x['chg']>=20 and x['vol']>=100_000_000) or (x['pct_low']>=40 and x['chg']>=15)): continue
    if not boleh(x['pair'],15): continue
    trending.append(x)
trending=sorted(trending,key=lambda x:x['chg'],reverse=True)[:4]

# SIMPAN STATE
for x in akum+pemula+akan+lagi+trending:
    state[x['pair']]={'last':x['last'],'vol':x['vol'],'time':now_ts}
save_state(state)

msg=f"SCAN V7 {now} WIB | {len(result)} koin\n\n"
if trending:
    msg+="🔥 TRENDING (baca trending Indodax!):\n"
    for c in trending: msg+=f"-> {c['pair'].upper()[:-4]} CHG {c['chg']:.0f}% naik {c['pct_low']:.0f}% vol {fmt_vol(c['vol'])} sisa {c['pct_high']:.0f}%\n"
    msg+="\n"
if lagi:
    msg+="🚀 LAGI 20-40% (EPIC disini!):\n"
    for c in lagi: msg+=f"-> {c['pair'].upper()[:-4]} naik {c['pct_low']:.0f}% chg {c['chg']:.0f}% vol {fmt_vol(c['vol'])}\n"
    msg+="\n"
if akan:
    msg+="🎯 AKAN 8-20%:\n"
    for c in akan: msg+=f"-> {c['pair'].upper()[:-4]} naik {c['pct_low']:.0f}% chg {c['chg']:.0f}% vol {fmt_vol(c['vol'])}\n"
    msg+="\n"
if pemula:
    msg+="🌱 PEMULA 1.5-8%:\n"
    for c in pemula: msg+=f"-> {c['pair'].upper()[:-4]} naik {c['pct_low']:.1f}% chg {c['chg']:.1f}% vol {fmt_vol(c['vol'])}\n"
    msg+="\n"
if akum:
    msg+="💎 AKUM:\n"
    for c in akum: msg+=f"-> {c['pair'].upper()[:-4]} naik {c['pct_low']:.1f}% vol {fmt_vol(c['vol'])}\n"

if not (trending or lagi or akan or pemula or akum):
    print("Sepi"); exit()

print(msg)
send_tele(msg)
