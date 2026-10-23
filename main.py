import requests, os, json

BLOCKED = {
    'BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','DAI_IDR','PAXG_IDR',
    'XRP_IDR','DOGE_IDR','SOL_IDR','HYPE_IDR','FARTCOIN_IDR',
    'PEPE_IDR','SHIB_IDR','TRX_IDR','AVAX_IDR','ADA_IDR','DOT_IDR','LINK_IDR','LTC_IDR','BCH_IDR','XLM_IDR','UNI_IDR','ETC_IDR','NEAR_IDR','BONK_IDR','FLOKI_IDR','WIF_IDR',
    'HBAR_IDR','XAUT_IDR','PIPPIN_IDR','PENGU_IDR','ANOA_IDR','GID_IDR','WLD_IDR','TIA_IDR',
    'BEAT_IDR','MARSCOIN_IDR','MOODENG_IDR','NOVA_IDR','SHOW_IDR','MRS_IDR','CST_IDR',
    'BOME_IDR','ONDO_IDR',
    'MITO_IDR','ERN_IDR','UNMD_IDR','LUNA_IDR','LUNC_IDR','FTM_IDR','BTT_IDR','XEM_IDR','USELESS_IDR','PUMP_IDR','MAVIA_IDR','SKYAI_IDR','ARC_IDR'
}

STATE_FILE = "/tmp/trailing_state.json"

def load_state():
    try:
        with open(STATE_FILE,'r') as f: return json.load(f)
    except: return {}

def save_state(state):
    try:
        with open(STATE_FILE,'w') as f: json.dump(state,f)
    except: pass

def get_data():
    try:
        tickers = requests.get("https://indodax.com/api/tickers", timeout=15).json().get('tickers',{})
        summ = requests.get("https://indodax.com/api/summaries", timeout=15).json()
        change={}
        for k,v in summ.get('tickers',{}).items():
            try: change[k]=float(v.get('percent_change',0))
            except: pass
        out=[]
        for pair,d in tickers.items():
            if not pair.endswith('_idr'): continue
            sym=pair.upper()
            if sym in BLOCKED: continue
            try:
                last=float(d['last']); low=float(d['low']); high=float(d['high']); vol=float(d['vol_idr'])
                if last < 15: continue
                vol_bn=vol/1e9
                if vol_bn < 0.15: continue
                if vol_bn > 10: continue
                chg24 = change.get(pair, 0)
                if abs(chg24) < 0.1:
                    chg24 = (last-low)/low*100 if low else 0
                if chg24 < -25: continue
                if chg24 > 100: continue
                sisa=(high-last)/last*100 if last else 0
                rg=(high-low)/low*100 if low else 0
                chg_low=(last-low)/low*100 if low else 0
                if sisa < 1: continue
                if sisa > 25: continue # Longgarin dikit biar bounce masuk
                if rg < 2: continue
                if rg > 100: continue
                out.append({'sym':sym,'chg':chg24,'low':chg_low,'sisa':sisa,'vol':vol_bn,'last':last,'high':high,'rg':rg})
            except: continue
        return out
    except: return []

def scan(data):
    state = load_state()
    new_state = {}
    mooning=[]; running=[]; early=[]; bounce=[]
    
    for k in data:
        sym=k['sym']; last=k['last']; high=k['high']; sisa=k['sisa']; low=k['low']; chg=k['chg']
        
        prev_high = state.get(sym, {}).get('high', high)
        if high > prev_high: prev_high = high
        new_state[sym] = {'high': prev_high, 'last': last, 'sisa': sisa}
        
        prev_sisa = state.get(sym, {}).get('sisa', 100)
        is_mooning = sisa < prev_sisa and sisa < 8 and prev_sisa != 100
        
        # BOUNCE LOGIC BALIK!
        # Bounce = dari low naik 3-25% + chg masih minus / kecil
        is_bounce = 3 <= low <= 30 and 5 <= sisa <= 25 and chg < 5
        
        k['is_mooning'] = is_mooning
        k['is_bounce'] = is_bounce
        
        if is_mooning and sisa <= 6:
            mooning.append(k)
        elif is_bounce:
            bounce.append(k)
        elif 1 <= sisa <= 6:
            running.append(k)
        elif 7 <= sisa <= 25:
            early.append(k)

    save_state({**state, **new_state})

    return (
        sorted(mooning, key=lambda x: x['vol'], reverse=True)[:3],
        sorted(bounce, key=lambda x: x['vol'], reverse=True)[:3],
        sorted(running, key=lambda x: x['vol'], reverse=True)[:3],
        sorted(early, key=lambda x: x['vol'], reverse=True)[:3]
    )

def kirim(msg):
    token=os.getenv('TELE_TOKEN')
    chat=os.getenv('TELE_CHAT_ID')
    if not token or not chat: print(msg); return
    try:
        url = "https://api.telegram.org/bot" + token + "/sendMessage"
        requests.post(url, json={"chat_id": chat, "text": msg}, timeout=15)
    except: print(msg)

if __name__=="__main__":
    data=get_data()
    moon, bnc, run, erl = scan(data)
    total = len(moon)+len(bnc)+len(run)+len(erl)
    msg=f"V44 TRAIL+BOUNCE Data {len(data)} | M{len(moon)} B{len(bnc)} R{len(run)} E{len(erl)} = {total}\n\n"
    if moon:
        msg+="🚀 MOONING (sisa mengecil!)\n"
        for k in moon: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% bnc {k['low']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg+="\n"
    if bnc:
        msg+="📈 BOUNCE (pantulan dari low!)\n"
        for k in bnc: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% bnc {k['low']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg+="\n"
    if run:
        msg+="RUNNING 1-6%\n"
        for k in run: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% bnc {k['low']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg+="\n"
    if erl:
        msg+="EARLY 7-25% (ALTLAYER!)\n"
        for k in erl: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% bnc {k['low']:.0f}% Vol {k['vol']:.2f}Bn\n"
    print(msg)
    kirim(msg)
