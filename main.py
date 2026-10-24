import requests, os, json, time, datetime, sys
BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID") or os.getenv("TELE_CHAT_ID")

# BLOCKED 67 - 66 + BNB! Biar BNB 0.5% ga bocor lagi!
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

STATE_FILE = "/tmp/v59_state.json"
VOL_MIN = 80000000

def load_state():
    try:
        with open(STATE_FILE,'r') as f: return json.load(f)
    except: return {}
def save_state(s):
    with open(STATE_FILE,'w') as f: json.dump(s,f)
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

early=[]; hunter=[]; segar=[]; dalem=[]; koreksi=[]; moon=[]

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
        new_state[symbol]={'sisa':th,'vol':vol_bn,'high':high,'last':last,'rg':rg,'chg':chg,'last_early':last_early,'last_hold':last_hold}
        
        # KOREKSI - ONT style
        if (th > prev_sisa + 5 and prev_sisa!=100) or (prev_last>0 and (prev_last-last)/prev_last*100>5 and high==prev_high):
            koreksi.append((pair,chg,vol_bn,th)); continue
        # MOON - ICNT TH 0.56% bakal masuk sini!
        if th < prev_sisa and th < 2.5 and prev_sisa!=100 and chg>5:
            moon.append((pair,chg,vol_bn,th,dl))
            continue
        
        vol_spike = vol_bn > prev_vol*2.0 and prev_vol>0.05 and vol_bn>=0.35
        
        # EARLY - KETAT! th 3-12 dl<=10 sq<20 chg min 2.5% vol>=1.2Bn
        is_early_t1 = vol_bn >= 1.2 and 2.5 <= chg <= 20 and 3 <= th <= 12 and dl <= 10 and sq < 20
        is_early_t2 = vol_bn >= 0.50 and 3.0 <= chg <= 15 and th <= 10 and dl <= 8 and sq < 18
        is_early_raw = is_early_t1 or is_early_t2 or (vol_spike and 3 <= chg <= 15 and th <= 10 and sq < 20)
        
        if is_early_raw:
            if now - last_early > 3*3600 or vol_spike or chg - prev_chg > 2.5:
                early.append((pair,chg,vol_bn,th,dl,sq,last))
                new_state[symbol]['last_early']=now
            continue
        
        # DALEM
        if -25 <= chg <= -1.5 and dl <= 6 and th < 25 and sq < 25:
            dalem.append((pair,chg,vol_bn,th,dl)); continue
        
        if chg < 1.2 or chg > 80 or th > 40: continue
        
        # SEGAR vs HUNTER
        if chg <= 4:
            if 1.2 <= chg <= 4 and 3 <= th <= 15 and 1 <= dl <= 8 and 5 <= sq <= 22 and vol_bn>=0.15:
                if now - last_hold > 2*3600 or chg-prev_chg>1.5:
                    segar.append((pair,chg,vol_bn,th,dl,sq))
                    new_state[symbol]['last_hold']=now
        else:
            if 4 < chg <= 20 and th <= 10 and 3 <= dl <= 12 and 8 <= sq <= 25 and vol_bn>=0.12:
                if now - last_hold > 2*3600 or chg-prev_chg>1.5:
                    hunter.append((pair,chg,vol_bn,th,dl,sq))
                    new_state[symbol]['last_hold']=now
    except: continue

save_state({**state,**new_state})
msg=f"V59 FIX {now_str} Data {len(tickers)} BLOCKED 67\nEARLY{len(early)} HUNTER{len(hunter)} SEGAR{len(segar)} DALEM{len(dalem)} KOREKSI{len(koreksi)} MOON{len(moon)}\n\n"
if early:
    msg+="🔥 EARLY - RAPET!\n"
    for p,c,v,th,dl,sq,last in sorted(early,key=lambda x:x[2],reverse=True)[:5]:
        msg+=f"{p.upper()} {c:.1f}% Vol {v:.2f}Bn TH {th:.0f}% DL {dl:.0f}% SQ {sq:.0f}% {last:.0f}\n"
    msg+="\n"
if moon:
    msg+="🚀 MOONING - TH <2.5%! ICNT masuk sini!\n"
    for p,c,v,th,dl in moon[:4]:
        msg+=f"{p.upper()} {c:.1f}% TH {th:.1f}% DL {dl:.0f}% Vol {v:.2f}Bn\n"
    msg+="\n"
if hunter:
    msg+="🚀 HUNTER\n"
    for p,c,v,th,dl,sq in sorted(hunter,key=lambda x:x[1],reverse=True)[:4]:
        msg+=f"{p.upper()} {c:.1f}% Vol {v:.2f}Bn TH {th:.0f}% DL {dl:.0f}%\n"
    msg+="\n"
if segar:
    msg+="🌱 SEGAR\n"
    for p,c,v,th,dl,sq in sorted(segar,key=lambda x:x[2],reverse=True)[:4]:
        msg+=f"{p.upper()} {c:.1f}% Vol {v:.2f}Bn TH {th:.0f}% DL {dl:.0f}%\n"
    msg+="\n"
if dalem:
    msg+="💎 DALEM\n"
    for p,c,v,th,dl in sorted(dalem,key=lambda x:x[4])[:3]:
        msg+=f"{p.upper()} {c:.1f}% DL {dl:.0f}% Vol {v:.2f}Bn\n"
    msg+="\n"
if koreksi:
    msg+="📉 KOREKSI\n"
    for p,c,v,th in koreksi[:3]:
        msg+=f"{p.upper()} {c:.1f}% TH {th:.0f}% Vol {v:.2f}Bn\n"
    msg+="\n"
if not (early or hunter or segar or moon): msg+="SEPI - Cooldown aktif!"

send_tele(msg); print(msg)
