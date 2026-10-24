import requests, os, json, time, datetime
BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID") or os.getenv("TELE_CHAT_ID")

SKIP_66 = {'btc','eth','usdt','usdc','dai','paxg','bnb','xrp','doge','sol','hype','fartcoin','pepe','shib','trx','avax','ada','dot','link','ltc','bch','xlm','uni','etc','near','bonk','floki','wif','hbar','xaut','pippin','pengu','anoa','gid','wld','tia','moodeng','bome','ondo','ena','aster','myx','usde','usd1','susde','wusdt','atom','fil','apt','arb','op','sui','sei','matic','mito','ern','unmd','luna','lunc','ftm','btt','xem','useless','pump','mavia','amp','iost','kishu'}

STATE_FILE = "/tmp/v65_state.json"
VOL_MIN_TRACK = 15000000  # 15Mn! Biar ORDER 606 ke-track!
VOL_MIN_ALERT = 35000000  # 35Mn alert!
COOLDOWN_AKUM = 25*60
COOLDOWN_PRE = 45*60
COOLDOWN_EARLY = 90*60
COOLDOWN_BOTTOM = 4*3600

def load_state():
    try:
        with open(STATE_FILE,'r') as f: return json.load(f)
    except: return {}
def save_state(s):
    try: 
        with open(STATE_FILE,'w') as f: json.dump(s,f)
    except: pass
def send_tele(m):
    try:
        if not BOT_TOKEN or not CHAT_ID: print(m); return
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": m}, timeout=10)
    except: print(m)

tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers',{})
now = time.time()
now_str = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).strftime("%H:%M WIB")
state = load_state()
new_state = {}

akum=[]; pre=[]; bottom=[]; early=[]; moon=[]; trending=[]; hunter=[]; segar=[]; emrg=[]

for pair,d in tickers.items():
    if not pair.endswith("_idr"): continue
    symbol = pair.split('_')[0].lower()
    if symbol in SKIP_66: continue
    try:
        last=float(d["last"]); low=float(d["low"]); high=float(d["high"]); vol=float(d["vol_idr"])
        if low==0 or last<1 or last>10000000: continue
        if vol < VOL_MIN_TRACK: continue
        rg = ((high-low)/low*100) if low else 0
        if rg < 1.5 or rg > 350: continue
        chg = ((last-low)/low*100) if low else 0
        th = ((high-last)/last*100) if last else 0
        dl = ((last-low)/last*100) if last else 0
        sq = dl+th
        vol_bn = vol/1e9
        
        hist = state.get(symbol,{})
        prev_vol=hist.get('vol',0); prev_chg=hist.get('chg',0); prev_last=hist.get('last',0)
        last_akum=hist.get('last_akum',0); last_pre=hist.get('last_pre',0)
        last_early=hist.get('last_early',0); last_bottom=hist.get('last_bottom',0); last_moon=hist.get('last_moon',0)
        new_state[symbol]={'vol':vol_bn,'chg':chg,'last':last,'last_akum':last_akum,'last_pre':last_pre,'last_early':last_early,'last_bottom':last_bottom,'last_moon':last_moon}

        price_jump = ((last-prev_last)/prev_last*100) if prev_last>0 else 0
        chg_jump = chg - prev_chg
        vol_growth = vol_bn / (prev_vol + 0.005) if prev_vol>=0 else 5.0

        # === EMERGENCY - ORDER 794->1311 +55% 15m BYPASS! ===
        if (price_jump >= 18 or chg_jump >= 18) and vol_bn >= 0.08:
            emrg.append((pair,chg,vol_bn,th,dl,last,price_jump,vol_growth))
            new_state[symbol]['last_pre']=now; new_state[symbol]['last_moon']=now
            continue

        # === 1. AKUMULASI 25M - BUYER DI BAWAH! ORDER 606! ENTRY 40%! ===
        # Ciri: chg 2-16% + TH <=20% + DL <=12% + Vol 0.015-0.15Bn + RG <=12% + harga <3000 + Vol growth >=2x
        is_akum = 2 <= chg <= 16 and th <= 20 and dl <= 12 and sq < 32 and 0.015 <= vol_bn <= 0.15 and rg <= 12 and last < 3000 and last > low*1.02
        if is_akum:
            if (now - last_akum > COOLDOWN_AKUM or vol_growth >= 3.0) and (vol_growth >= 1.8 or vol_bn >= 0.025):
                akum.append((pair,chg,vol_bn,th,dl,last,vol_growth))
                new_state[symbol]['last_akum']=now
            continue

        # === 2. PRE-TRENDING 45M - Calon BIRB/ORDER sebelum +200% ===
        is_pre = 0.5 <= chg <= 18 and 1 <= th <= 25 and dl <= 30 and sq < 45 and 0.03 <= vol_bn <= 1.5 and last < 5000 and rg >= 3
        if is_pre and vol >= VOL_MIN_ALERT:
            if vol_growth >= 2.5 or vol_bn >= 0.18 or (vol_bn > prev_vol*2.5 and prev_vol>0.015):
                if now - last_pre > COOLDOWN_PRE or vol_growth >= 3.0:
                    pre.append((pair,chg,vol_bn,th,dl,last,vol_growth))
                    new_state[symbol]['last_pre']=now
                continue

        # TRENDING - udah +20% ke atas!
        if chg >= 20 and vol >= VOL_MIN_ALERT:
            if (th <= 25 and vol_bn >= 0.08) or vol_bn >= 1.0:
                if now - last_moon > 20*60:
                    trending.append((pair,chg,vol_bn,th,dl,last))
                    new_state[symbol]['last_moon']=now
                continue

        # BOTTOM - kayak BSV 0.3% sisa25% DL1%
        is_bottom = 0 <= chg <= 2.5 and 18 <= th <= 42 and 0.03 <= vol_bn <= 0.50 and dl <= 6 and 3 <= rg <= 80
        if is_bottom and vol >= VOL_MIN_ALERT:
            if now - last_bottom > COOLDOWN_BOTTOM:
                bottom.append((pair,chg,vol_bn,th,dl,last))
                new_state[symbol]['last_bottom']=now
            continue

        # EARLY - kayak ICNT 3.1% Vol4.72Bn TH10 DL3 SQ13
        vol_spike_big = vol_bn > prev_vol*2.5 and prev_vol>0.03 and vol_bn>=0.20
        is_early = (vol_bn >= 0.70 and 2 <= chg <= 20 and th <= 12 and dl <= 15) or (vol_spike_big and 2 <= chg <= 15)
        if is_early and vol >= VOL_MIN_ALERT:
            if now - last_early > COOLDOWN_EARLY or vol_spike_big:
                early.append((pair,chg,vol_bn,th,dl,last))
                new_state[symbol]['last_early']=now
            continue

        if chg < 0.8 or th > 50: continue
        if vol < VOL_MIN_ALERT: continue

        if chg <= 4:
            if 1 <= chg <= 4 and th <= 16 and dl <= 15 and sq <= 28:
                segar.append((pair,chg,vol_bn,th,dl,last))
        else:
            if 4 < chg <= 20 and th <= 12 and dl <= 20 and sq <= 30:
                hunter.append((pair,chg,vol_bn,th,dl,last))
    except: continue

save_state({**state,**new_state})

# TELE MAX 15 KOIN! Prioritas: EMRG > AKUM > PRE > BOTTOM > EARLY
total_limit = 15
msg=f"V65 BUYER+15 {now_str} D{len(tickers)}\nAK{len(akum)} PR{len(pre)} B{len(bottom)} E{len(early)} T{len(trending)} H{len(hunter)} S{len(segar)} EM{len(emrg)}\n\n"
count=0

if emrg and count < total_limit:
    msg+="🚨 EMRG 0M - +18% 15m BYPASS!\n"
    for p,c,v,th,dl,last,pjump,growth in sorted(emrg,key=lambda x:x[6],reverse=True)[:2]:
        if count>=total_limit: break
        msg+=f"{p.upper()} {c:.0f}% {last:.0f} Vol {v:.2f}Bn +{pjump:.0f}% x{growth:.1f}\n"
        count+=1
    msg+="\n"

if akum and count < total_limit:
    msg+="🔵 AKUM 25M - Buyer bawah! Entry 40% enak!\n"
    for p,c,v,th,dl,last,growth in sorted(akum,key=lambda x:x[6],reverse=True)[:3]:
        if count>=total_limit: break
        msg+=f"{p.upper()} {c:.1f}% Vol {v:.2f}Bn TH {th:.0f}% DL {dl:.0f}% {last:.0f} x{growth:.1f}\n"
        count+=1
    msg+="\n"

if pre and count < total_limit:
    msg+="⚡ PRE 45M - Calon BIRB +200%!\n"
    for p,c,v,th,dl,last,growth in sorted(pre,key=lambda x:x[6],reverse=True)[:4]:
        if count>=total_limit: break
        msg+=f"{p.upper()} {c:.1f}% Vol {v:.2f}Bn TH {th:.0f}% DL {dl:.0f}% {last:.0f} x{growth:.1f}\n"
        count+=1
    msg+="\n"

if bottom and count < total_limit:
    msg+="💎 BOTTOM 4H - Kayak BSV 0.3%->22%!\n"
    for p,c,v,th,dl,last in sorted(bottom,key=lambda x:x[3],reverse=True)[:3]:
        if count>=total_limit: break
        msg+=f"{p.upper()} {c:.1f}% sisa {th:.0f}% Vol {v:.2f}Bn DL {dl:.0f}% {last:.0f}\n"
        count+=1
    msg+="\n"

if early and count < total_limit:
    msg+="🔥 EARLY 90M - Kayak ICNT 3.1%->15%!\n"
    for p,c,v,th,dl,last in sorted(early,key=lambda x:x[2],reverse=True)[:3]:
        if count>=total_limit: break
        msg+=f"{p.upper()} {c:.1f}% Vol {v:.2f}Bn TH {th:.0f}% DL {dl:.0f}% {last:.0f}\n"
        count+=1
    msg+="\n"

if count==0: msg+="SEPI - Cooldown!"

send_tele(msg); print(msg)
