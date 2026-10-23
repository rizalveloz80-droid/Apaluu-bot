import requests, os, json

BLOCKED = {
    'BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','DAI_IDR','PAXG_IDR',
    'XRP_IDR','DOGE_IDR','SOL_IDR','HYPE_IDR','FARTCOIN_IDR',
    'PEPE_IDR','SHIB_IDR','TRX_IDR','AVAX_IDR','ADA_IDR','DOT_IDR','LINK_IDR','LTC_IDR','BCH_IDR','XLM_IDR','UNI_IDR','ETC_IDR','NEAR_IDR','BONK_IDR','FLOKI_IDR','WIF_IDR',
    'HBAR_IDR','XAUT_IDR','PIPPIN_IDR','PENGU_IDR','ANOA_IDR','GID_IDR','WLD_IDR','TIA_IDR',
    'BEAT_IDR','MARSCOIN_IDR','MOODENG_IDR','NOVA_IDR','SHOW_IDR','MRS_IDR','CST_IDR',
    'BOME_IDR','ONDO_IDR',
    'MITO_IDR','ERN_IDR','UNMD_IDR','LUNA_IDR','LUNC_IDR','FTM_IDR','BTT_IDR','XEM_IDR','USELESS_IDR','PUMP_IDR','MAVIA_IDR','SUI_IDR','ARC_IDR'
}

STATE_FILE = "/tmp/v46_state.json"
def load_state():
    try:
        with open(STATE_FILE,'r') as f: return json.load(f)
    except: return {}
def save_state(s):
    try:
        with open(STATE_FILE,'w') as f: json.dump(s,f)
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
                vol_bn=vol/1e9
                if last < 0.5: continue # <0.5 baru block total
                if vol_bn < 0.08: continue # Turunin jadi 0.08Bn = 80Mn biar BIRB 18:00 masuk!
                if vol_bn > 20: continue
                chg24 = change.get(pair, 0)
                if abs(chg24) < 0.1:
                    chg24 = (last-low)/low*100 if low else 0
                if chg24 < -40: continue
                if chg24 > 200: continue
                sisa=(high-last)/last*100 if last else 0
                rg=(high-low)/low*100 if low else 0
                chg_low=(last-low)/low*100 if low else 0
                
                # GA FILTER SISA KETAT DULU, BIAR PRE-PUMP MASUK!
                out.append({'sym':sym,'chg':chg24,'low':chg_low,'sisa':sisa,'vol':vol_bn,'last':last,'high':high,'rg':rg,'low_price':low})
            except: continue
        return out
    except: return []

def scan(data):
    state=load_state()
    new_state={}
    pre_pump=[]; moon=[]; bounce=[]; early=[]
    
    for k in data:
        sym=k['sym']; last=k['last']; high=k['high']; sisa=k['sisa']; low=k['low']; chg=k['chg']; rg=k['rg']; vol=k['vol']
        
        # Track history buat detek vol spike
        hist = state.get(sym, {})
        prev_vol = hist.get('vol', vol)
        prev_rg = hist.get('rg', rg)
        prev_sisa = hist.get('sisa', 100)
        
        vol_spike = vol / prev_vol if prev_vol>0 else 1
        rg_grow = rg - prev_rg
        
        new_state[sym] = {'vol':vol,'rg':rg,'sisa':sisa,'high':high,'last':last}
        
        # 1. PRE-PUMP DETECTOR (PELAJARAN DARI BIRB!)
        # Ciri BIRB jam 18:00-21:00:
        # - rg kecil 10-30% (sideways)
        # - sisa gede 20-40% (jauh dari high)
        # - low naik dikit 1-5% (akumulasi)
        # - vol mulai naik dikit (17K -> 20K)
        is_pre_pump = (
            5 <= rg <= 40 and  # Sideways belum meledak
            10 <= sisa <= 50 and # Masih jauh dari pucuk
            0.5 <= low <= 15 and # Udah naik dikit dari low
            vol >= 0.08 and # Vol mulai ada
            chg < 15 # Belum pump
        )
        
        # 2. MOONING TRAIL
        is_mooning = sisa < prev_sisa and sisa < 10 and prev_sisa != 100
        
        # 3. BOUNCE
        is_bounce = 3 <= low <= 50 and chg < 8
        
        if is_mooning and sisa <= 8:
            moon.append(k)
        elif is_pre_pump:
            # Kasih score: vol spike + rg grow = lebih bagus
            k['score'] = vol_spike + rg_grow
            pre_pump.append(k)
        elif is_bounce:
            bounce.append(k)
        elif 7 <= sisa <= 30:
            early.append(k)
    
    save_state({**state, **new_state})
    
    return (
        sorted(pre_pump, key=lambda x: (x['vol'], x.get('score',0)), reverse=True)[:4],
        sorted(moon, key=lambda x: x['vol'], reverse=True)[:3],
        sorted(bounce, key=lambda x: x['vol'], reverse=True)[:3],
        sorted(early, key=lambda x: x['vol'], reverse=True)[:3]
    )

def kirim(msg):
    token=os.getenv('TELE_TOKEN')
    chat=os.getenv('TELE_CHAT_ID')
    if not token or not chat: print(msg); return
    try:
        url="https://api.telegram.org/bot"+token+"/sendMessage"
        requests.post(url, json={"chat_id":chat,"text":msg}, timeout=15)
    except: print(msg)

if __name__=="__main__":
    data=get_data()
    pre, moon, bnc, erl = scan(data)
    total=len(pre)+len(moon)+len(bnc)+len(erl)
    msg=f"V46 ANTI KETINGGALAN Data {len(data)} | PRE{len(pre)} M{len(moon)} B{len(bnc)} E{len(erl)} = {total}\n\n"
    if pre:
        msg+="⚠️ PRE-PUMP (tangkap sebelum meledak!)\n"
        for k in pre: msg+=f"{k['sym']} {k['chg']:.1f}% rg {k['rg']:.0f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg+="\n"
    if moon:
        msg+="🚀 MOONING TRAIL\n"
        for k in moon: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg+="\n"
    if bnc:
        msg+="📈 BOUNCE\n"
        for k in bnc: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% bnc {k['low']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg+="\n"
    if erl:
        msg+="EARLY\n"
        for k in erl: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    print(msg)
    kirim(msg)
