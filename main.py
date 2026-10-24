import requests, os, json, time, datetime, sys
BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID") or os.getenv("TELE_CHAT_ID")

# === BLOCKED 66 TETAP! Pake cara lu split lower biar aman! ===
SKIP_66 = {
    'btc','eth','usdt','usdc','dai','paxg',
    'xrp','doge','sol','hype','fartcoin',
    'pepe','shib','trx','avax','ada','dot','link','ltc','bch','xlm','uni','etc','near','bonk','floki','wif',
    'hbar','xaut','pippin','pengu','anoa','gid','wld','tia','moodeng',
    'bome','ondo',
    'ena','aster','myx','usde','usd1','susde','wusdt',
    'atom','fil','apt','arb','op','sui','sei',
    'mito','ern','unmd','luna','lunc','ftm','btt','xem','useless','pump','mavia',
    'amp','iost','kishu',
}

STATE_FILE = "/tmp/v58_state.json"
VOL_MIN = 80000000  # 0.08Bn
COOLDOWN_EARLY = 3*3600
COOLDOWN_HOLD = 2*3600

def load_state():
    try:
        with open(STATE_FILE,'r') as f: return json.load(f)
    except: return {}

def save_state(s):
    with open(STATE_FILE,'w') as f: json.dump(s,f)

def send_tele(m):
    try:
        if not BOT_TOKEN or not CHAT_ID:
            print(m); return
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": m}, timeout=10)
    except:
        print(m)

def get_data():
    try:
        tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers',{})
        summ = requests.get("https://indodax.com/api/summaries", timeout=15).json()
        change={}
        for k,v in summ.get('tickers',{}).items():
            try: change[k]=float(v.get('percent_change',0))
            except: pass
        return tickers, change
    except:
        return {}, {}

tickers, change = get_data()
state = load_state()
new_state = {}
now = time.time()
now_str = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).strftime("%H:%M WIB")

early=[]; hunter=[]; segar=[]; dalem=[]; koreksi=[]; moon=[]

for pair,d in tickers.items():
    if not pair.endswith("_idr"): continue
    symbol = pair.split('_')[0].lower()
    if symbol in SKIP_66: continue

    try:
        last=float(d["last"]); low=float(d["low"]); high=float(d["high"]); vol=float(d["vol_idr"])
        if low==0 or last<5 or vol<VOL_MIN: continue
        
        rg = ((high-low)/low*100) if low else 0
        if rg < 2 or rg > 300: continue
        
        chg = ((last-low)/low*100) if low else 0  # bounce dari low - punya lu
        th = ((high-last)/last*100) if last else 0  # sisa ke pucuk - punya lu
        dl = ((last-low)/last*100) if last else 0  # dalam dari low - punya lu
        sq = dl + th  # total range - punya lu
        vol_bn = vol/1e9
        chg24 = change.get(pair, chg)
        
        hist = state.get(symbol, {})
        prev_sisa = hist.get('sisa',100)
        prev_vol = hist.get('vol',0)
        prev_high = hist.get('high',0)
        prev_last = hist.get('last',0)
        prev_chg = hist.get('chg',0)
        last_early = hist.get('last_early',0)
        last_hold = hist.get('last_hold',0)
        
        new_state[symbol] = {'sisa':th,'vol':vol_bn,'high':high,'last':last,'rg':rg,'chg':chg,'chg24':chg24,
                             'last_early':last_early,'last_hold':last_hold}
        
        # === FIX KOREKSI ONT - dari V57 ===
        sisa_naik = th > prev_sisa + 4 and prev_sisa != 100
        last_turun = prev_last>0 and (prev_last-last)/prev_last*100 > 5 and high==prev_high
        chg_drop = prev_chg>0 and prev_chg - chg > 6
        if sisa_naik or last_turun or chg_drop:
            koreksi.append((pair,chg,vol_bn,th,dl,sq))
            continue
        
        # === MOON ===
        is_moon = th < prev_sisa and th < 3.5 and prev_sisa!=100
        if is_moon:
            moon.append((pair,chg,vol_bn,th))
            continue
        
        # === VOL SPIKE 1.8x - dari V57 ===
        vol_spike = vol_bn > (prev_vol*1.8) and prev_vol>0.05 and vol_bn>=0.30
        
        # === EARLY GABUNGAN - tier vol + dl/th/sq punya lu ===
        # Tier 1: Vol gede >=1.0Bn = chg 2.5% aja early (BR 2.6% Vol 4.55Bn)
        # Tier 2: Vol sedang + dl/th/sq ketat punya lu
        is_early_t1 = vol_bn >= 1.0 and 2.5 <= chg <= 30 and 3 <= th <= 35 and rg <= 90
        is_early_t2 = vol_bn >= 0.40 and 1.2 <= chg <= 20 and th <= 15 and dl <= 15 and sq < 30
        is_early_raw = is_early_t1 or is_early_t2 or vol_spike
        
        # === ANTI-SPAM 3 JAM - dari V57 - biar ga itu-itu terus ===
        if is_early_raw:
            if now - last_early > COOLDOWN_EARLY or vol_spike or (chg - prev_chg > 2):
                early.append((pair,chg,vol_bn,th,dl,sq,last))
                new_state[symbol]['last_early'] = now
            continue
        
        # === DALEM - FIX BUG V18.4 ===
        if -30 <= chg <= -1.5 and dl <= 8 and sq < 30 and th < 30:
            dalem.append((pair,chg,vol_bn,th,dl))
            continue
        
        if chg < 0.3 or chg > 100 or th < 0 or th > 50: continue
        
        # === SEGAR vs HUNTER - punya lu ===
        if chg <= 4:
            if th <= 15 and sq < 30:
                if now - last_hold > COOLDOWN_HOLD or chg - prev_chg > 1.5:
                    segar.append((pair,chg,vol_bn,th,dl,sq))
                    new_state[symbol]['last_hold'] = now
        else:
            if th <= 12 and sq < 30:
                if now - last_hold > COOLDOWN_HOLD or chg - prev_chg > 1.5:
                    hunter.append((pair,chg,vol_bn,th,dl,sq))
                    new_state[symbol]['last_hold'] = now
                    
    except: continue

save_state({**state, **new_state})

msg=f"V58 GABUNGAN {now_str} Data {len(tickers)} BLOCKED 66\n"
msg+=f"EARLY{len(early)} HUNTER{len(hunter)} SEGAR{len(segar)} DALEM{len(dalem)} KOREKSI{len(koreksi)} MOON{len(moon)}\n\n"

if early:
    msg+="🔥 EARLY RUNNER - BARU! Vol gede + dl/th/sq rapet!\n"
    for p,c,v,th,dl,sq,last in sorted(early,key=lambda x:x[2],reverse=True)[:5]:
        msg+=f"{p.upper()} {c:.1f}% Vol {v:.2f}Bn TH {th:.0f}% DL {dl:.0f}% SQ {sq:.0f}% Hrg {last:.0f}\n"
    msg+="\n"
if hunter:
    msg+="🚀 HUNTER - Udah lari!\n"
    for p,c,v,th,dl,sq in sorted(hunter,key=lambda x:x[1],reverse=True)[:5]:
        msg+=f"{p.upper()} {c:.1f}% Vol {v:.2f}Bn TH {th:.0f}% DL {dl:.0f}%\n"
    msg+="\n"
if segar:
    msg+="🌱 SEGAR - Baru seger!\n"
    for p,c,v,th,dl,sq in sorted(segar,key=lambda x:x[2],reverse=True)[:5]:
        msg+=f"{p.upper()} {c:.1f}% Vol {v:.2f}Bn TH {th:.0f}% DL {dl:.0f}% SQ {sq:.0f}%\n"
    msg+="\n"
if dalem:
    msg+="💎 DALEM - Di bawah!\n"
    for p,c,v,th,dl in sorted(dalem,key=lambda x:x[4])[:4]:
        msg+=f"{p.upper()} {c:.1f}% DL {dl:.0f}% TH {th:.0f}% Vol {v:.2f}Bn\n"
    msg+="\n"
if koreksi:
    msg+="📉 KOREKSI - SKIP! Kaya ONT!\n"
    for p,c,v,th,dl,sq in sorted(koreksi,key=lambda x:x[2],reverse=True)[:4]:
        msg+=f"{p.upper()} {c:.1f}% TH {th:.0f}% Vol {v:.2f}Bn\n"
    msg+="\n"
if moon:
    msg+="🚀 MOONING\n"
    for p,c,v,th in moon[:2]:
        msg+=f"{p.upper()} {c:.1f}% TH {th:.0f}% Vol {v:.2f}Bn\n"

if not (early or hunter or segar or dalem or koreksi or moon):
    msg+="MARKET SEPI - Ga ada koin baru! Cooldown 3 jam aktif biar ga itu-itu terus!"

send_tele(msg); print(msg); sys.exit(0)
