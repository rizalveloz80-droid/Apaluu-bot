import requests, os, json, time, datetime
BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID") or os.getenv("TELE_CHAT_ID")

SKIP_66 = {
    'btc','eth','usdt','usdc','dai','paxg','bnb',
    'xrp','doge','sol','hype','fartcoin',
    'pepe','shib','trx','avax','ada','dot','link','ltc','bch','xlm','uni','etc','near','bonk','floki','wif',
    'hbar','xaut','pippin','pengu','anoa','gid','wld','tia','moodeng',
    'bome','ondo',
    'ena','aster','myx','usde','usd1','susde','wusdt',
    'atom','fil','apt','arb','op','sui','sei','matic',
    'mito','ern','unmd','luna','lunc','ftm','btt','xem','useless','pump','mavia',
    'amp','iost','kishu',
}

HOLDING = {'icnt','bsv','nmd','order','birb','bmt'}

STATE_FILE = "/tmp/v64_state.json"
VOL_MIN_TRACK = 30000000  # 30Mn tracking biar ORDER 15Mn -> 80Mn ke-track!
VOL_MIN_ALERT = 50000000  # 50Mn alert biar ORDER 103Mn masuk!
COOLDOWN_PRE = 45*60
COOLDOWN_EARLY = 90*60
COOLDOWN_HOLD = 60*60
COOLDOWN_BOTTOM = 4*3600
COOLDOWN_MOON = 20*60

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

pre=[]; bottom=[]; early=[]; hunter=[]; segar=[]; moon=[]; trending=[]; koreksi=[]

for pair,d in tickers.items():
    if not pair.endswith("_idr"): continue
    symbol = pair.split('_')[0].lower()
    if symbol in SKIP_66: continue
    try:
        last=float(d["last"]); low=float(d["low"]); high=float(d["high"]); vol=float(d["vol_idr"])
        if low==0 or last<1 or last>10000000: continue
        if vol < VOL_MIN_TRACK: continue  # 30Mn tracking!
        rg = ((high-low)/low*100) if low else 0
        if rg < 2 or rg > 350: continue
        chg = ((last-low)/low*100) if low else 0
        th = ((high-last)/last*100) if last else 0
        dl = ((last-low)/last*100) if last else 0
        sq = dl+th
        vol_bn = vol/1e9
        
        hist = state.get(symbol,{})
        prev_sisa=hist.get('sisa',100); prev_vol=hist.get('vol',0); prev_chg=hist.get('chg',0)
        last_early=hist.get('last_early',0); last_hold=hist.get('last_hold',0)
        last_bottom=hist.get('last_bottom',0); last_moon=hist.get('last_moon',0)
        last_pre=hist.get('last_pre',0)
        new_state[symbol]={'sisa':th,'vol':vol_bn,'high':high,'last':last,'rg':rg,'chg':chg,
                           'last_early':last_early,'last_hold':last_hold,'last_bottom':last_bottom,'last_moon':last_moon,'last_pre':last_pre}
        
        is_holding = symbol in HOLDING
        cd_moon = 20*60 if is_holding else 45*60
        
        # KOREKSI
        if th > prev_sisa + 6 and prev_sisa!=100:
            if vol >= VOL_MIN_ALERT:
                koreksi.append((pair,chg,vol_bn,th,last)); continue
        
        # === PRE-TRENDING SCAN DINI - Calon BIRB/ORDER/BMT sebelum +200% ===
        # ORDER pas 580: chg 6.6% TH 3% DL 6% Vol 0.08Bn x5 growth!
        # BIRB pas 1.2: chg 8% TH 6% DL 10% Vol 0.2Bn x8 growth!
        # Syarat: chg 0.5-18% + TH 1-25% + DL <=30% + Vol 0.03-1.5Bn + harga <5000 + RG>=4
        is_pre_raw = 0.5 <= chg <= 18 and 1 <= th <= 25 and dl <= 30 and sq < 45 and 0.03 <= vol_bn <= 1.5 and last < 5000 and rg >= 3.5
        
        if is_pre_raw and vol >= VOL_MIN_ALERT:
            vol_growth = vol_bn / (prev_vol + 0.01) if prev_vol>0 else 5.0
            vol_spike = vol_bn > prev_vol*2.5 and prev_vol>0.015
            # Growth >=2.5x atau Vol >=0.18Bn atau spike = pre-trending!
            if vol_growth >= 2.5 or vol_spike or vol_bn >= 0.18:
                if now - last_pre > COOLDOWN_PRE:
                    pre.append((pair,chg,vol_bn,th,dl,sq,last,vol_growth))
                    new_state[symbol]['last_pre']=now
                continue
        
        # === TRENDING - Udah jadi BIRB +223% - jangan dikejar tapi alert! ===
        if chg >= 20 and vol >= VOL_MIN_ALERT:
            is_trending = (th <= 25 and vol_bn >= 0.08) or (vol_bn >= 1.5 and th <= 65)
            if is_trending:
                if now - last_moon > cd_moon:
                    trending.append((pair,chg,vol_bn,th,dl,sq,last))
                    new_state[symbol]['last_moon']=now
                continue
        
        # === MOON - TH<2.5% ===
        is_moon = th < prev_sisa and th < 2.5 and prev_sisa!=100 and chg>5 and vol_bn>=0.08
        if is_moon and vol >= VOL_MIN_ALERT:
            if now - last_moon > cd_moon or chg - prev_chg > 2:
                moon.append((pair,chg,vol_bn,th,dl,last))
                new_state[symbol]['last_moon']=now
            continue
        
        vol_spike_big = vol_bn > prev_vol*2.5 and prev_vol>0.03 and vol_bn>=0.20
        
        # === BOTTOM - BSV 0.3% sisa25% Vol0.09Bn DL1% ===
        is_bottom_raw = 0 <= chg <= 2.5 and 20 <= th <= 42 and 0.03 <= vol_bn <= 0.50 and dl <= 6 and 4 <= rg <= 80
        if is_bottom_raw and vol >= VOL_MIN_ALERT:
            if now - last_bottom > COOLDOWN_BOTTOM:
                bottom.append((pair,chg,vol_bn,th,dl,sq,last))
                new_state[symbol]['last_bottom']=now
            continue
        
        # === EARLY - ICNT 3.1% Vol4.72Bn TH10 DL3 SQ13 ===
        is_early_t1 = vol_bn >= 0.80 and 2.0 <= chg <= 20 and 2 <= th <= 12 and dl <= 15 and sq < 22
        is_early_t2 = vol_bn >= 0.40 and 2.5 <= chg <= 15 and th <= 10 and dl <= 12 and sq < 20
        is_early_raw = is_early_t1 or is_early_t2 or (vol_spike_big and 2 <= chg <= 15 and th <= 12 and sq < 22)
        
        if is_early_raw and vol >= VOL_MIN_ALERT:
            if now - last_early > COOLDOWN_EARLY or vol_spike_big or chg - prev_chg > 2.5:
                early.append((pair,chg,vol_bn,th,dl,sq,last))
                new_state[symbol]['last_early']=now
            continue
        
        if chg < 1.0 or th > 50: continue
        if vol < VOL_MIN_ALERT: continue
        
        # SEGAR vs HUNTER - ada harga!
        if chg <= 4:
            if 1.0 <= chg <= 4 and 2 <= th <= 16 and dl <= 15 and sq <= 28 and vol_bn>=0.08:
                if now - last_hold > COOLDOWN_HOLD or chg-prev_chg>1.2:
                    segar.append((pair,chg,vol_bn,th,dl,sq,last))
                    new_state[symbol]['last_hold']=now
        else:
            if 4 < chg <= 20 and th <= 12 and dl <= 20 and sq <= 30 and vol_bn>=0.08:
                if now - last_hold > COOLDOWN_HOLD or chg-prev_chg>1.2:
                    hunter.append((pair,chg,vol_bn,th,dl,sq,last))
                    new_state[symbol]['last_hold']=now
    except: continue

save_state({**state,**new_state})

# BATAS 15 TOTAL! Prioritas: PRE > BOTTOM > EARLY > MOON > TRENDING > HUNTER > SEGAR
total_limit = 15
msg=f"V64 PRE+15 {now_str} D{len(tickers)} B67\nPR{len(pre)} B{len(bottom)} E{len(early)} M{len(moon)} T{len(trending)} H{len(hunter)} S{len(segar)}\n\n"
count=0

if pre and count<total_limit:
    msg+="⚡ PRE-TRENDING 45M - Calon BIRB! Entry dini!\n"
    for p,c,v,th,dl,sq,last,growth in sorted(pre,key=lambda x:x[7],reverse=True)[:5]:
        if count>=total_limit: break
        msg+=f"{p.upper()} {c:.1f}% Vol {v:.2f}Bn TH {th:.0f}% DL {dl:.0f}% {last:.0f} x{growth:.1f}\n"
        count+=1
    msg+="\n"

if bottom and count<total_limit:
    msg+="💎 BOTTOM - Kayak BSV 0.3%->22%!\n"
    for p,c,v,th,dl,sq,last in sorted(bottom,key=lambda x:x[3],reverse=True)[:4]:
        if count>=total_limit: break
        msg+=f"{p.upper()} {c:.1f}% sisa {th:.0f}% Vol {v:.2f}Bn DL {dl:.0f}% {last:.0f}\n"
        count+=1
    msg+="\n"

if early and count<total_limit:
    msg+="🔥 EARLY 90M - Kayak ICNT 3.1%->15%!\n"
    for p,c,v,th,dl,sq,last in sorted(early,key=lambda x:x[2],reverse=True)[:3]:
        if count>=total_limit: break
        msg+=f"{p.upper()} {c:.1f}% Vol {v:.2f}Bn TH {th:.0f}% DL {dl:.0f}% SQ {sq:.0f}% {last:.0f}\n"
        count+=1
    msg+="\n"

if moon and count<total_limit:
    msg+="🚀 MOONING 20M\n"
    for p,c,v,th,dl,last in sorted(moon,key=lambda x:x[1],reverse=True)[:3]:
        if count>=total_limit: break
        msg+=f"{p.upper()} {c:.1f}% TH {th:.1f}% Vol {v:.2f}Bn {last:.0f}\n"
        count+=1
    msg+="\n"

if trending and count<total_limit:
    msg+="🔥 TRENDING - Udah naik! Jangan kejar!\n"
    for p,c,v,th,dl,sq,last in sorted(trending,key=lambda x:x[1],reverse=True)[:3]:
        if count>=total_limit: break
        msg+=f"{p.upper()} {c:.0f}% Vol {v:.2f}Bn TH {th:.0f}% {last:.0f}\n"
        count+=1
    msg+="\n"

if hunter and count<total_limit:
    msg+="🚀 HUNTER 60M\n"
    for p,c,v,th,dl,sq,last in sorted(hunter,key=lambda x:x[1],reverse=True)[:2]:
        if count>=total_limit: break
        msg+=f"{p.upper()} {c:.1f}% Vol {v:.2f}Bn TH {th:.0f}% {last:.0f}\n"
        count+=1
    msg+="\n"

if segar and count<total_limit:
    msg+="🌱 SEGAR 60M\n"
    for p,c,v,th,dl,sq,last in sorted(segar,key=lambda x:x[2],reverse=True)[:2]:
        if count>=total_limit: break
        msg+=f"{p.upper()} {c:.1f}% Vol {v:.2f}Bn TH {th:.0f}% {last:.0f}\n"
        count+=1
    msg+="\n"

if count==0: msg+="SEPI - Cooldown aktif!"

send_tele(msg); print(msg)
