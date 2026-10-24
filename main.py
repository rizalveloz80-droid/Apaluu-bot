import requests, os, json, time
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')
STATE_FILE = "state_v66_5.json"

def send_tele(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",
                      json={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=15)
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

# FIX: ERN DELISTING + STABLE + KOIN MATI DI BLOCK!
BLACKLIST = {
    'usdt_idr','usdc_idr','dai_idr','busd_idr','usde_idr','paxg_idr',
    'ern_idr',  # <-- ERN DELISTING! BLOCK!
    'xvs_idr','bsv_idr','bcha_idr','bch_idr','btg_idr', # koin tua delisting
    'luna_idr','lunc_idr','ftt_idr'
}

state = load_state()
now_ts = time.time()
tickers = get_tickers()
wib = timezone(timedelta(hours=7))
now = datetime.now(wib).strftime("%H:%M")
result = []

for pair,d in tickers.items():
    if not pair.endswith('_idr') or pair in BLACKLIST: continue
    last=fnum(d.get('last')); low=fnum(d.get('low')); high=fnum(d.get('high'))
    vol=fnum(d.get('vol_idr')); chg=fnum(d.get('change'))
    if low<=0 or last<20: continue
    if vol<30_000_000 or vol>10_000_000_000: continue
    pct_low=(last-low)/low*100
    pct_high=(high-last)/last*100
    range_pct=(high-low)/low*100
    mid=(high+low)/2
    if last >= high*0.92: continue
    if last < mid*0.85: continue
    result.append({'pair':pair,'vol':vol,'pct_low':pct_low,'pct_high':pct_high,'chg':chg,'range_pct':range_pct,'last':last})

def fmt_vol(v): return f"{v/1e9:.2f} Bn" if v>=1e9 else f"{v/1e6:.0f} Mn"

def boleh_kirim(pair, last_now, cooldown_min):
    s=state.get(pair,{})
    if now_ts - s.get('time',0) < cooldown_min*60: return False
    if s.get('last',0)>0 and (last_now-s['last'])/s['last']*100 < 0.5 and s.get('time',0)!=0:
        return False
    return True

akum=[]; pemula=[]; akan=[]; lagi=[]; emrg=[]

# AKUM 0.3-1.5% 1 koin
for x in result:
    if not (0.3 <= x['pct_low'] <= 1.5 and x['range_pct']<=35 and 30<=x['pct_high']<=80 and x['vol']>=150_000_000): continue
    if not boleh_kirim(x['pair'],x['last'],90): continue
    akum.append(x)
akum=sorted(akum,key=lambda x:x['vol'],reverse=True)[:1]
for x in akum: state[x['pair']]={'last':x['last'],'vol':x['vol'],'time':now_ts}
akum_pairs={x['pair'] for x in akum}

# PEMULA 1.5-5% 3 koin - BUTUH chg >0 atau vol growth biar ga chg 0.0% terus!
for x in result:
    if x['pair'] in akum_pairs: continue
    if not (1.5 <= x['pct_low'] <= 5 and x['range_pct']<=45 and 25<=x['pct_high']<=70 and x['vol']>=100_000_000 and x['chg']>-1): continue
    if x['chg']==0.0 and x['vol']<300_000_000: continue # chg 0.0% vol kecil = skip kayak BSV 344Mn!
    if not boleh_kirim(x['pair'],x['last'],60): continue
    pemula.append(x)
pemula=sorted(pemula,key=lambda x:x['pct_low'],reverse=True)[:3]
for x in pemula: state[x['pair']]={'last':x['last'],'vol':x['vol'],'time':now_ts}
pemula_pairs=akum_pairs|{x['pair'] for x in pemula}

# AKAN 5-12% 3 koin
for x in result:
    if x['pair'] in pemula_pairs: continue
    if not (5 < x['pct_low'] <= 12 and x['range_pct']<=55 and 15<=x['pct_high']<=60 and x['vol']>=200_000_000): continue
    if x['chg']==0.0 and x['pct_low']>10: continue # ZORA 12% chg 0.0% = pucuk!
    if not boleh_kirim(x['pair'],x['last'],45): continue
    akan.append(x)
akan=sorted(akan,key=lambda x:x['pct_high'],reverse=True)[:3]
for x in akan: state[x['pair']]={'last':x['last'],'vol':x['vol'],'time':now_ts}
akan_pairs=pemula_pairs|{x['pair'] for x in akan}

# LAGI 12-25% 2 koin - KETATIN! ERN 19% sisa 24% chg 0.0% = SKIP KARENA chg 0.0% + BLACKLIST!
for x in result:
    if x['pair'] in akan_pairs: continue
    if not (12 < x['pct_low'] <= 25 and x['range_pct']<=60 and 10<=x['pct_high']<=50 and x['vol']>=250_000_000): continue
    if x['chg']<=0.0: continue # FIX ERN! chg 0.0% = ga ada buyer! SKIP!
    if not boleh_kirim(x['pair'],x['last'],45): continue
    lagi.append(x)
lagi=sorted(lagi,key=lambda x:x['vol'],reverse=True)[:2]
for x in lagi: state[x['pair']]={'last':x['last'],'vol':x['vol'],'time':now_ts}
lagi_pairs=akan_pairs|{x['pair'] for x in lagi}

# EMRG 35%+ 1 koin - HARUS chg HIJAU!
for x in result:
    if x['pair'] in lagi_pairs: continue
    if not ((x['pct_low']>=35 and x['chg']>=4 and x['vol']>=800_000_000)): continue
    if not boleh_kirim(x['pair'],x['last'],30): continue
    emrg.append(x)
emrg=sorted(emrg,key=lambda x:x['vol'],reverse=True)[:1]
for x in emrg: state[x['pair']]={'last':x['last'],'vol':x['vol'],'time':now_ts}

save_state(state)

msg=f"SCAN DINI {now} WIB | {len(result)} koin\n\n"
if akum:
    msg+="💎 AKUM 0.3-1.5%:\n"
    for c in akum: msg+=f"-> {c['pair'].upper()[:-4]} naik {c['pct_low']:.1f}% sisa {c['pct_high']:.0f}% vol {fmt_vol(c['vol'])} chg {c['chg']:.1f}%\n"
    msg+="\n"
if pemula:
    msg+="🌱 PEMULA 1.5-5%:\n"
    for c in pemula: msg+=f"-> {c['pair'].upper()[:-4]} naik {c['pct_low']:.1f}% sisa {c['pct_high']:.0f}% vol {fmt_vol(c['vol'])} chg {c['chg']:.1f}%\n"
    msg+="\n"
if akan:
    msg+="🎯 AKAN 5-12%:\n"
    for c in akan: msg+=f"-> {c['pair'].upper()[:-4]} naik {c['pct_low']:.0f}% sisa {c['pct_high']:.0f}% vol {fmt_vol(c['vol'])} chg {c['chg']:.1f}%\n"
    msg+="\n"
if lagi:
    msg+="🚀 LAGI 12-25%:\n"
    for c in lagi: msg+=f"-> {c['pair'].upper()[:-4]} naik {c['pct_low']:.0f}% sisa {c['pct_high']:.0f}% vol {fmt_vol(c['vol'])} chg {c['chg']:.1f}%\n"
    msg+="\n"
if emrg:
    msg+="🚨 EMRG 35%+:\n"
    for c in emrg: msg+=f"-> {c['pair'].upper()[:-4]} naik {c['pct_low']:.0f}% sisa {c['pct_high']:.0f}% vol {fmt_vol(c['vol'])} chg {c['chg']:.1f}%\n"

if not (akum or pemula or akan or lagi or emrg):
    print("Sepi - ERN diblock, koin sama cooldown")
    exit()

print(msg)
send_tele(msg)
