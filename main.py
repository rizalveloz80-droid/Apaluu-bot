import requests, json, os, time
from datetime import datetime

# === V66.2 FINAL 10 KOIN - RANGKUMAN V47-V65 ===
BOT_TOKEN = "ISI_TOKEN_BOT_LU"
CHAT_ID = "ISI_CHAT_ID_LU"
STATE_FILE = "state_v66_2_final.json"

# FIX ACTSOL -> ACT
ALIAS = {'actsol': 'act'}
# SKIP 15 KOIN GEDE + STABLE - GA AKAN 100%!
SKIP = {'usdt','usdc','dai','paxg','bttc','btc','eth','bnb','xrp','doge','usde','eur','myr','sgd','actsol'}

def load_state():
    if os.path.exists(STATE_FILE):
        try: return json.load(open(STATE_FILE))
        except: return {}
    return {}
def save_state(s):
    with open(STATE_FILE,'w') as f: json.dump(f,s)

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

    # === FILTER V47-V65 FIX ===
    # 1. VOL <0.09Bn = HART HOME NOM HILANG! (V55 RUSAK 0.015)
    if vol_bn < 0.09: 
        state[pair]={'last':last,'vol':vol_bn,'th':th,'chg':chg,'time':state.get(pair,{}).get('time',0)}
        continue
    # 2. CHG MERAH = PM -17% GTC -10% HILANG! (V65 RUSAK MERAH MASUK)
    if chg < 0:
        state[pair]={'last':last,'vol':vol_bn,'th':th,'chg':chg,'time':state.get(pair,{}).get('time',0)}
        continue

    s=state.get(pair,{})
    prev_last=s.get('last',last); prev_vol=s.get('vol',vol_bn); prev_th=s.get('th',th); prev_time=s.get('time',0)
    if prev_vol==0: prev_vol=vol_bn
    vol_growth=vol_bn/prev_vol if prev_vol>0 else 1
    price_25m=(last-prev_last)/prev_last*100 if prev_last>0 else 0
    chg_jump=chg-s.get('chg',chg)

    # === EMRG INFO - 1 KOIN - BUKAN BUAT ENTRY! (V60 RUSAK BYPASS) ===
    if (price_25m>=18 or chg_jump>=18) and vol_bn>=0.15 and vol_growth>=4:
        emrg.append((pair.upper().replace('ACTSOL','ACT'),chg,vol_bn,price_25m,vol_growth))
        state[pair]={'last':last,'vol':vol_bn,'th':th,'chg':chg,'time':now}
        continue

    # === AKUM 25M - 3 KOIN - BUYER BAWAH! (V47 ENAK 3-12% RG<=10% TH<=12%) ===
    # FIX: Vol 0.09-0.40 + chg 4-18 + RG 12-35 + TH<=12 DL<=10 TH+DL<=12 + price>=1% + x2.2
    # HART RG2% HOME RG5% SKIP! NOM -3.3% SKIP! BIRB RG30% ORDER RG20% MASUK!
    if 0.09 <= vol_bn <= 0.40 and 4 <= chg <= 18 and 12 <= rg <= 35 and th <= 12 and dl <= 10 and (th+dl) <= 12:
        if vol_growth>=2.2 and price_25m>=1.0:
            if now-prev_time>=25*60:
                score=vol_growth*10+price_25m
                akum.append((pair.upper().replace('ACTSOL','ACT'),chg,vol_bn,th,dl,last,price_25m,vol_growth,score))

    # === PRE 45M - 3 KOIN - MAU RUNNING! (V47 ENAK 0.1-0.8Bn) ===
    # FIX: Vol 0.15-1.0 + chg 2-14 + TH<=12 DL<=10 RG>=10 + price>=1% + x2.8 + hijau!
    # PM TH23% -17% SKIP! GTC -10% SKIP!
    if 0.15 <= vol_bn <= 1.0 and 2 <= chg <= 14 and th <= 12 and dl <= 10 and rg>=10:
        if vol_growth>=2.8 and price_25m>=1.0:
            if now-prev_time>=45*60:
                pre.append((pair.upper().replace('ACTSOL','ACT'),chg,vol_bn,th,dl,last,price_25m,vol_growth,price_25m+vol_growth))

    # === BOTTOM BOUNCE - 2 KOIN - NEWT 764 -> 842 +11% ENAK! (V52) ===
    # FIX: sisa 25-40% DL<=2.5% + price bounce >=0.8% + chg>0 + vol>=0.08
    # BSV -2.8% BANANA -3.88% SKIP! NEWT +1.2% MASUK!
    sisa=th
    if 25 <= sisa <= 40 and dl <= 2.5 and vol_bn>=0.08 and chg>0:
        if price_25m>=0.8:
            if now-prev_time>=4*3600:
                bottom.append((pair.upper().replace('ACTSOL','ACT'),chg,vol_bn,sisa,dl,last,price_25m))

    # === EARLY 90M - 1 KOIN - VOL GEDE! ===
    if vol_bn>=1.0 and 2 <= chg <= 14 and th <= 12 and dl <= 10:
        if now-prev_time>=90*60:
            early.append((pair.upper().replace('ACTSOL','ACT'),chg,vol_bn,th,dl,last))

    if pair not in state: state[pair]={'last':last,'vol':vol_bn,'th':th,'chg':chg,'time':0}
    else: state[pair].update({'last':last,'vol':vol_bn,'th':th,'chg':chg})

# MAX 10 KOIN! AK3 PRE3 BOT2 EARLY1 EMRG1 (V47 MAX 8 + V65 RUSAK 15)
akum=sorted(akum,key=lambda x:x[8],reverse=True)[:3]
pre=sorted(pre,key=lambda x:x[8],reverse=True)[:3]
bottom=bottom[:2]; early=early[:1]; emrg=sorted(emrg,key=lambda x:x[4],reverse=True)[:1]
total=len(akum)+len(pre)+len(bottom)+len(early)+len(emrg)
if total==0:
    print("Sepi - 66 koin tidur, ga ada buyer running early")
    save_state(state); exit()

msg=f"V66.2 DINI-10 {datetime.now().strftime('%H:%M')} AK{len(akum)} PR{len(pre)} B{len(bottom)} E{len(early)} M{len(emrg)} T{total}\n\n"
if emrg:
    msg+="🚨 EMRG INFO - Langit 7, jangan entry! TP temen lu!\n"
    for p,c,v,pc,g in emrg: msg+=f"{p} {c:.0f}% Vol {v:.2f}Bn +{pc:.0f}% x{g:.1f}\n"
    msg+="\n"
if akum:
    msg+="🔵 AKUM 25M - Koin lain early! Entry 40%! (V47 BEST)\n"
    for p,c,v,th,dl,last,pc,g,sc in akum: msg+=f"{p} {c:.1f}% Vol {v:.2f}Bn TH{th:.0f}% DL{dl:.0f}% {last:.0f} x{g:.1f} +{pc:.1f}%\n"
    msg+="\n"
if pre:
    msg+="⚡ PRE 45M - Mulai naik!\n"
    for p,c,v,th,dl,last,pc,g,sc in pre: msg+=f"{p} {c:.1f}% Vol {v:.2f}Bn TH{th:.0f}% {last:.0f} x{g:.1f}\n"
    msg+="\n"
if bottom:
    msg+="💎 BOTTOM 4H - Bounce! (NEWT 764->842)\n"
    for p,c,v,sisa,dl,last,pc in bottom: msg+=f"{p} {c:.1f}% sisa{sisa:.0f}% DL{dl:.0f}% {last:.0f} +{pc:.1f}%\n"
    msg+="\n"
if early:
    msg+="🔥 EARLY 90M\n"
    for p,c,v,th,dl,last in early: msg+=f"{p} {c:.1f}% Vol {v:.2f}Bn TH{th:.0f}% {last:.0f}\n"

print(msg)
save_state(state)
# requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={urllib.parse.quote(msg)}")
