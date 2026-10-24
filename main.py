import requests, os, json, time, datetime
BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID") or os.getenv("TELE_CHAT_ID")

# BLOCKED 67 - BNB udah block!
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

# HOLDING - Koin lu hold +15% biar cooldown 20M bukan 90M!
HOLDING = {'nmd','pha','zerebro','skyai'}

STATE_FILE = "/tmp/v62_state.json"
VOL_MIN = 80000000
COOLDOWN_EARLY = 90*60
COOLDOWN_HOLD = 60*60
COOLDOWN_BOTTOM = 4*3600
COOLDOWN_MOON_NORMAL = 45*60
COOLDOWN_MOON_HOLD = 20*60

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
    except Exception as e: print(e); print(m)

tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers',{})
now = time.time()
now_str = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).strftime("%H:%M WIB")
state = load_state()
new_state = {}

early=[]; hunter=[]; segar=[]; bottom=[]; dalem=[]; koreksi=[]; moon=[]

for pair,d in tickers.items():
    if not pair.endswith("_idr"): continue
    symbol = pair.split('_')[0].lower()
    if symbol in SKIP_66: continue
    try:
        last=float(d["last"]); low=float(d["low"]); high=float(d["high"]); vol=float(d["vol_idr"])
        if low==0 or last<5 or last>2000000 or vol<VOL_MIN: continue
        rg = ((high-low)/low*100) if low else 0
        if rg < 2 or rg > 200: continue
        chg = ((last-low)/low*100) if low else 0
        th = ((high-last)/last*100) if last else 0
        dl = ((last-low)/last*100) if last else 0
        sq = dl+th
        vol_bn = vol/1e9
        
        hist = state.get(symbol,{})
        prev_sisa=hist.get('sisa',100); prev_vol=hist.get('vol',0); prev_high=hist.get('high',0)
        prev_last=hist.get('last',0); prev_chg=hist.get('chg',0)
        last_early=hist.get('last_early',0); last_hold=hist.get('last_hold',0)
        last_bottom=hist.get('last_bottom',0); last_moon=hist.get('last_moon',0)
        new_state[symbol]={'sisa':th,'vol':vol_bn,'high':high,'last':last,'rg':rg,'chg':chg,
                           'last_early':last_early,'last_hold':last_hold,'last_bottom':last_bottom,'last_moon':last_moon}
        
        is_holding = symbol in HOLDING
        cd_moon = COOLDOWN_MOON_HOLD if is_holding else COOLDOWN_MOON_NORMAL
        
        # KOREKSI - turun dari pucuk
        if (th > prev_sisa + 5 and prev_sisa!=100) or (prev_last>0 and (prev_last-last)/prev_last*100>5 and high==prev_high):
            koreksi.append((pair,chg,vol_bn,th,last)); continue
        
        # MOON - ICNT TH0% + BSV TH0% - HOLDING 20M!
        is_moon = th < prev_sisa and th < 2.5 and prev_sisa!=100 and chg>5 and vol_bn>=0.10
        if is_moon:
            if now - last_moon > cd_moon or chg - prev_chg > 2:
                moon.append((pair,chg,vol_bn,th,dl,last))
                new_state[symbol]['last_moon']=now
            continue
        
        vol_spike = vol_bn > prev_vol*2.0 and prev_vol>0.05 and vol_bn>=0.30
        
        # === BOTTOM LESSON BSV 0.3% sisa25% Vol0.09Bn DL1% ===
        # chg kecil 0-2.5% sisa 20-40% DL<=6% Vol 0.05-0.40Bn RG 5-60%
        is_bottom_raw = 0 <= chg <= 2.5 and 20 <= th <= 40 and 0.05 <= vol_bn <= 0.45 and dl <= 6 and 5 <= rg <= 70
        if is_bottom_raw:
            if now - last_bottom > COOLDOWN_BOTTOM:
                bottom.append((pair,chg,vol_bn,th,dl,sq,last))
                new_state[symbol]['last_bottom']=now
            continue
        
        # === EARLY LESSON ICNT 3.1% Vol4.72Bn TH10 DL3 SQ13 ===
        # Vol gede >=1.2Bn + TH 3-12 + DL<=10 + SQ<20 + chg 2.5-20
        # atau Vol>=0.50 + TH<=10 DL<=8 SQ<18 + chg 3-15
        # atau Vol Spike 2x + TH<=10
        is_early_t1 = vol_bn >= 1.2 and 2.5 <= chg <= 20 and 3 <= th <= 12 and dl <= 10 and sq < 20
        is_early_t2 = vol_bn >= 0.50 and 3.0 <= chg <= 15 and th <= 10 and dl <= 8 and sq < 18
        is_early_raw = is_early_t1 or is_early_t2 or (vol_spike and 3 <= chg <= 15 and th <= 10 and sq < 20)
        
        if is_early_raw:
            if now - last_early > COOLDOWN_EARLY or vol_spike or chg - prev_chg > 2.5:
                early.append((pair,chg,vol_bn,th,dl,sq,last))
                new_state[symbol]['last_early']=now
            continue
        
        # DALEM - koin nyungsep
        if -25 <= chg <= -1.5 and dl <= 6 and th < 30 and sq < 30:
            dalem.append((pair,chg,vol_bn,th,dl,last)); continue
        
        if chg < 1.2 or chg > 80 or th > 45: continue
        
        # SEGAR vs HUNTER - ADA HARGA SEKARANG!
        if chg <= 4:
            if 1.2 <= chg <= 4 and 3 <= th <= 15 and 1 <= dl <= 8 and 5 <= sq <= 22 and vol_bn>=0.12:
                if now - last_hold > COOLDOWN_HOLD or chg-prev_chg>1.5:
                    segar.append((pair,chg,vol_bn,th,dl,sq,last))
                    new_state[symbol]['last_hold']=now
        else:
            if 4 < chg <= 20 and th <= 10 and 3 <= dl <= 12 and 8 <= sq <= 25 and vol_bn>=0.10:
                if now - last_hold > COOLDOWN_HOLD or chg-prev_chg>1.5:
                    hunter.append((pair,chg,vol_bn,th,dl,sq,last))
                    new_state[symbol]['last_hold']=now
    except: continue

save_state({**state,**new_state})
msg=f"V62 BSV+ICNT {now_str} Data {len(tickers)} B67\nE{len(early)} H{len(hunter)} S{len(segar)} B{len(bottom)} M{len(moon)} K{len(koreksi)} D{len(dalem)}\n\n"
if bottom:
    msg+="💎 BOTTOM - Entry semalam! Kayak BSV 0.3%->22%!\n"
    for p,c,v,th,dl,sq,last in sorted(bottom,key=lambda x:x[3],reverse=True)[:4]:
        msg+=f"{p.upper()} {c:.1f}% sisa {th:.0f}% Vol {v:.2f}Bn DL {dl:.0f}% {last:.0f}\n"
    msg+="\n"
if early:
    msg+="🔥 EARLY 90M - Vol gede rapet! Kayak ICNT 3.1%->15%!\n"
    for p,c,v,th,dl,sq,last in sorted(early,key=lambda x:x[2],reverse=True)[:4]:
        msg+=f"{p.upper()} {c:.1f}% Vol {v:.2f}Bn TH {th:.0f}% DL {dl:.0f}% SQ {sq:.0f}% {last:.0f}\n"
    msg+="\n"
if moon:
    msg+="🚀 MOONING - TH<2.5% Hold 20M!\n"
    for p,c,v,th,dl,last in sorted(moon,key=lambda x:x[1],reverse=True)[:5]:
        hold_tag = " [HOLD]" if p.split('_')[0].lower() in HOLDING else ""
        msg+=f"{p.upper()} {c:.1f}% TH {th:.1f}% DL {dl:.0f}% Vol {v:.2f}Bn {last:.0f}{hold_tag}\n"
    msg+="\n"
if hunter:
    msg+="🚀 HUNTER 60M\n"
    for p,c,v,th,dl,sq,last in sorted(hunter,key=lambda x:x[1],reverse=True)[:4]:
        msg+=f"{p.upper()} {c:.1f}% Vol {v:.2f}Bn TH {th:.0f}% DL {dl:.0f}% {last:.0f}\n"
    msg+="\n"
if segar:
    msg+="🌱 SEGAR 60M\n"
    for p,c,v,th,dl,sq,last in sorted(segar,key=lambda x:x[2],reverse=True)[:5]:
        msg+=f"{p.upper()} {c:.1f}% Vol {v:.2f}Bn TH {th:.0f}% DL {dl:.0f}% {last:.0f}\n"
    msg+="\n"
if koreksi:
    msg+="📉 KOREKSI - Sisa naik!\n"
    for p,c,v,th,last in koreksi[:3]:
        msg+=f"{p.upper()} {c:.1f}% TH {th:.0f}% Vol {v:.2f}Bn {last:.0f}\n"
    msg+="\n"
if not (early or hunter or segar or bottom or moon): msg+="SEPI - Cooldown 20-90M aktif!"

send_tele(msg); print(msg)
