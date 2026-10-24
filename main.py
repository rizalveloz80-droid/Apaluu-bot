import requests, json, os, time
from datetime import datetime

BOT_TOKEN = "ISI_TOKEN_BOT_LU"
CHAT_ID = "ISI_CHAT_ID_LU"
STATE_FILE = "state_v66_2_final.json"
ALIAS = {'actsol': 'act'}
SKIP = {'usdt','usdc','dai','paxg','bttc','btc','eth','bnb','xrp','doge','usde','eur','myr','sgd','actsol'}

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE,'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_state(s):
    # FIX MERAH: json.dump(s,f) BUKAN json.dump(f,s)!
    with open(STATE_FILE,'w') as f:
        json.dump(s, f)

state = load_state()
now = time.time()

try:
    tickers = requests.get("https://indodax.com/api/tickers", timeout=10).json()['tickers']
except:
    print("Gagal ambil tickers"); exit()

akum=[]; pre=[]; bottom=[]; early=[]; emrg=[]

for pair,d in tickers.items():
    if not pair.endswith("_idr"): continue
    raw = pair.split("_")[0].lower()
    sym = ALIAS.get(raw, raw)
    if sym in SKIP: continue
    try:
        last=float(d['last']); high=float(d['high']); low=float(d['low'])
        vol_bn=float(d['vol_idr'])/1e9
        if low==0: continue
        chg=(last-low)/low*100
        th=(high-last)/last*100 if last>0 else 100
        dl=(last-low)/last*100 if last>0 else 100
        rg=(high-low)/low*100 if low>0 else 100
    except: continue

    if vol_bn < 0.09: 
        state[pair]={'last':last,'vol':vol_bn,'th':th,'chg':chg,'time':state.get(pair,{}).get('time',0)}
        continue
    if chg < 0:
        state[pair]={'last':last,'vol':vol_bn,'th':th,'chg':chg,'time':state.get(pair,{}).get('time',0)}
        continue

    s=state.get(pair,{})
    prev_last=s.get('last',last); prev_vol=s.get('vol',vol_bn); prev_th=s.get('th',th); prev_time=s.get('time',0)
    if prev_vol==0: prev_vol=vol_bn
    vol_growth=vol_bn/prev_vol if prev_vol>0 else 1
    price_25m=(last-prev_last)/prev_last*100 if prev_last>0 else 0
    chg_jump=chg-s.get('chg',chg)

    if (price_25m>=18 or chg_jump>=18) and vol_bn>=0.15 and vol_growth>=4:
        emrg.append((pair.upper().replace('ACTSOL','ACT'),chg,vol_bn,price_25m,vol_growth))
        state[pair]={'last':last,'vol':vol_bn,'th':th,'chg':chg,'time':now}
        continue

    if 0.09 <= vol_bn <= 0.40 and 4 <= chg <= 18 and 12 <= rg <= 35 and th <= 12 and dl <= 10 and (th+dl) <= 12:
        if vol_growth>=2.2 and price_25m>=1.0:
            if now-prev_time>=25*60:
                score=vol_growth*10+price_25m
                akum.append((pair.upper().replace('ACTSOL','ACT'),chg,vol_bn,th,dl,last,price_25m,vol_growth,score))

    if 0.15 <= vol_bn <= 1.0 and 2 <= chg <= 14 and th <= 12 and dl <= 10 and rg>=10:
        if vol_growth>=2.8 and price_25m>=1.0:
            if now-prev_time>=45*60:
                pre.append((pair.upper().replace('ACTSOL','ACT'),chg,vol_bn,th,dl,last,price_25m,vol_growth,price_25m+vol_growth))

    sisa=th
    if 25 <= sisa <= 40 and dl <= 2.5 and vol_bn>=0.08 and chg>0:
        if price_25m>=0.8:
            if now-prev_time>=4*3600:
                bottom.append((pair.upper().replace('ACTSOL','ACT'),chg,vol_bn,sisa,dl,last,price_25m))

    if vol_bn>=1.0 and 2 <= chg <= 14 and th <= 12 and dl <= 10:
        if now-prev_time>=90*60:
            early.append((pair.upper().replace('ACTSOL','ACT'),chg,vol_bn,th,dl,last))

    if pair not in state: state[pair]={'last':last,'vol':vol_bn,'th':th,'chg':chg,'time':0}
    else: state[pair].update({'last':last,'vol':vol_bn,'th':th,'chg':chg})

akum=sorted(akum,key=lambda x:x[8],reverse=True)[:3]
pre=sorted(pre,key=lambda x:x[8],reverse=True)[:3]
bottom=bottom[:2]; early=early[:1]; emrg=sorted(emrg,key=lambda x:x[4],reverse=True)[:1]
total=len(akum)+len(pre)+len(bottom)+len(early)+len(emrg)
if total==0:
    print("Sepi - 66 koin tidur, ga ada buyer running early")
    save_state(state); exit()

msg=f"V66.2 DINI-10 {datetime.now().strftime('%H:%M')} AK{len(akum)} PR{len(pre)} B{len(bottom)} E{len(early)} M{len(emrg)} T{total}\n\n"
if emrg:
    msg+="🚨 EMRG INFO - Langit 7, jangan entry!\n"
    for p,c,v,pc,g in emrg: msg+=f"{p} {c:.0f}% Vol {v:.2f}Bn +{pc:.0f}% x{g:.1f}\n"
    msg+="\n"
if akum:
    msg+="🔵 AKUM 25M - Entry 40%!\n"
    for p,c,v,th,dl,last,pc,g,sc in akum: msg+=f"{p} {c:.1f}% Vol {v:.2f}Bn TH{th:.0f}% DL{dl:.0f}% {last:.0f} x{g:.1f} +{pc:.1f}%\n"
    msg+="\n"
if pre:
    msg+="⚡ PRE 45M\n"
    for p,c,v,th,dl,last,pc,g,sc in pre: msg+=f"{p} {c:.1f}% Vol {v:.2f}Bn TH{th:.0f}% {last:.0f} x{g:.1f}\n"
    msg+="\n"
if bottom:
    msg+="💎 BOTTOM 4H\n"
    for p,c,v,sisa,dl,last,pc in bottom: msg+=f"{p} {c:.1f}% sisa{sisa:.0f}% DL{dl:.0f}% {last:.0f} +{pc:.1f}%\n"
    msg+="\n"
if early:
    msg+="🔥 EARLY 90M\n"
    for p,c,v,th,dl,last in early: msg+=f"{p} {c:.1f}% Vol {v:.2f}Bn TH{th:.0f}% {last:.0f}\n"

print(msg)
save_state(state)
