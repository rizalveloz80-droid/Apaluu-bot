import requests, os, json, time
from datetime import datetime, timezone, timedelta

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')
STATE_FILE = "state_v66_4.json"

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

BLACKLIST = {'usdt_idr','usdc_idr','dai_idr','busd_idr','usde_idr','paxg_idr'}
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

# CEK APAKAH SUDAH DIKIRIM + HARUS NAIK DULU!
def boleh_kirim(pair, last_now, cooldown_min):
    s = state.get(pair, {})
    last_time = s.get('time', 0)
    last_price = s.get('last', 0)
    # harus lewat cooldown + harga naik >=0.5% baru boleh kirim lagi!
    if now_ts - last_time < cooldown_min*60: return False
    if last_price>0 and (last_now-last_price)/last_price*100 < 0.5 and last_time!=0:
        return False
    return True

akum=[]; pemula=[]; akan=[]; lagi=[]; emrg=[]

for x in result:
    pair=x['pair']; last=x['last']
    s=state.get(pair, {})
    prev_vol=s.get('vol', x['vol'])
    vol_growth=x['vol']/prev_vol if prev_vol>0 else 1

    # AKUM 0.3-1.5% - 1 koin - cooldown 90m - harus vol naik x1.3!
    if 0.3 <= x['pct_low'] <= 1.5 and x['range_pct'] <= 35 and 30 <= x['pct_high'] <= 80 and x['vol']>=150_000_000 and vol_growth>=1.3:
        if boleh_kirim(pair,last,90): akum.append(x)

# urut vol gede
akum = sorted(akum, key=lambda x:x['vol'], reverse=True)[:1]
akum_pairs={x['pair'] for x in akum}
for x in akum: state[x['pair']]={'last':x['last'],'vol':x['vol'],'time':now_ts}

for x in result:
    if x['pair'] in akum_pairs: continue
    pair=x['pair']; last=x['last']
    if not (1.5 <= x['pct_low'] <= 5 and x['range_pct']<=45 and 25<=x['pct_high']<=70 and x['vol']>=100_000_000): continue
    if not boleh_kirim(pair,last,60): continue
    pemula.append(x)

pemula=sorted(pemula,key=lambda x:x['pct_low'],reverse=True)[:3]
pemula_pairs=akum_pairs|{x['pair'] for x in pemula}
for x in pemula: state[x['pair']]={'last':x['last'],'vol':x['vol'],'time':now_ts}

for x in result:
    if x['pair'] in pemula_pairs: continue
    pair=x['pair']; last=x['last']
    if not (5 < x['pct_low'] <= 12 and x['range_pct']<=55 and 15<=x['pct_high']<=60 and x['vol']>=200_000_000): continue
    if not boleh_kirim(pair,last,45): continue
    akan.append(x)

akan=sorted(akan,key=lambda x:x['pct_high'],reverse=True)[:3]
akan_pairs=pemula_pairs|{x['pair'] for x in akan}
for x in akan: state[x['pair']]={'last':x['last'],'vol':x['vol'],'time':now_ts}

for x in result:
    if x['pair'] in akan_pairs: continue
    pair=x['pair']; last=x['last']
    if not (12 < x['pct_low'] <= 25 and x['range_pct']<=60 and 10<=x['pct_high']<=50 and x['vol']>=250_000_000): continue
    if not boleh_kirim(pair,last,45): continue
    lagi.append(x)

lagi=sorted(lagi,key=lambda x:x['vol'],reverse=True)[:2]
lagi_pairs=akan_pairs|{x['pair'] for x in lagi}
for x in lagi: state[x['pair']]={'last':x['last'],'vol':x['vol'],'time':now_ts}

# EMRG GANTI UDAH - ERN 26% sisa 17% chg 0% = GA MASUK KARENA BUTUH chg>=4%!
for x in result:
    if x['pair'] in lagi_pairs: continue
    pair=x['pair']; last=x['last']
    if not ((x['pct_low']>=35 and x['chg']>=4 and x['vol']>=800_000_000) or (x['range_pct']>=60 and x['pct_high']<=15 and x['vol']>=1_000_000_000)): continue
    if not boleh_kirim(pair,last,30): continue
    emrg.append(x)

emrg=sorted(emrg,key=lambda x:x['vol'],reverse=True)[:1]
for x in emrg: state[x['pair']]={'last':x['last'],'vol':x['vol'],'time':now_ts}

# SIMPAN STATE BIAR GA SPAM LAGI!
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
    msg+="🚨 EMRG 35%+ (bukan ERN):\n"
    for c in emrg: msg+=f"-> {c['pair'].upper()[:-4]} naik {c['pct_low']:.0f}% sisa {c['pct_high']:.0f}% vol {fmt_vol(c['vol'])} chg {c['chg']:.1f}%\n"

if not (akum or pemula or akan or lagi or emrg):
    print("Sepi - semua koin tidur / masih cooldown, ga spam tele")
    exit()

print(msg)
send_tele(msg)
