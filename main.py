import requests, os, json

# CUMA INI YANG DI BLOCK! SISANYA ICNT, AIH, STIK, XR, BR, UCJL DLL MASUK!
BLOCKED = {
    'BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','DAI_IDR','PAXG_IDR',
    'XRP_IDR','DOGE_IDR','SOL_IDR','HYPE_IDR','FARTCOIN_IDR',
    'PEPE_IDR','SHIB_IDR','TRX_IDR','AVAX_IDR','ADA_IDR','DOT_IDR','LINK_IDR','LTC_IDR','BCH_IDR','XLM_IDR','UNI_IDR','ETC_IDR','NEAR_IDR','BONK_IDR','FLOKI_IDR','WIF_IDR',
    'HBAR_IDR','XAUT_IDR','PIPPIN_IDR','PENGU_IDR','ANOA_IDR','GID_IDR','WLD_IDR','TIA_IDR','MOODENG_IDR',
    'BOME_IDR','ONDO_IDR',
    'ENA_IDR','ASTER_IDR','MYX_IDR','USDE_IDR','USD1_IDR','SUSDE_IDR','WUSDT_IDR',
    'ATOM_IDR','FIL_IDR','APT_IDR','ARB_IDR','OP_IDR','SUI_IDR','SEI_IDR',
    'MITO_IDR','ERN_IDR','UNMD_IDR','LUNA_IDR','LUNC_IDR','FTM_IDR','BTT_IDR','XEM_IDR','USELESS_IDR','PUMP_IDR','MAVIA_IDR',
}

STATE_FILE = "/tmp/v50_state.json"
def load_state():
    try:
        with open(STATE_FILE,'r') as f: return json.load(f)
    except: return {}
def save_state(s):
    with open(STATE_FILE,'w') as f: json.dump(s,f)

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
                if last < 0.5: continue
                if vol_bn < 0.05: continue # ICNT vol kecil biar masuk!
                if vol_bn > 20: continue
                chg24 = change.get(pair, 0)
                if abs(chg24) < 0.1:
                    chg24 = (last-low)/low*100 if low else 0
                sisa=(high-last)/last*100 if last else 0
                rg=(high-low)/low*100 if low else 0
                chg_low=(last-low)/low*100 if low else 0
                
                if chg24 < 0.5: continue
                if sisa < 0.5: continue
                if sisa > 45: continue
                if rg < 2: continue
                if rg > 200: continue
                if chg_low < 0.5: continue
                if chg24 < -25: continue
                
                out.append({'sym':sym,'chg':chg24,'low':chg_low,'sisa':sisa,'vol':vol_bn,'last':last,'high':high,'rg':rg})
            except: continue
        return out
    except: return []

def scan(data):
    state=load_state()
    new_state={}
    hold=[]; pre=[]; moon=[]
    for k in data:
        sym=k['sym']; sisa=k['sisa']; low=k['low']; chg=k['chg']; rg=k['rg']
        hist=state.get(sym,{})
        prev_sisa=hist.get('sisa',100)
        new_state[sym]={'sisa':sisa,'vol':k['vol'],'high':k['high'],'last':k['last'],'rg':rg}
        is_moon = sisa < prev_sisa and sisa < 5 and prev_sisa!=100
        is_hold = 0.5 <= chg <= 10 and sisa <= 15 and rg >= 2
        is_pre = rg >= 3 and sisa >= 3
        
        if is_moon:
            moon.append(k)
        elif is_hold:
            hold.append(k)
        elif is_pre:
            pre.append(k)
    save_state({**state,**new_state})
    return (
        sorted(hold, key=lambda x: x['chg'], reverse=True)[:6],
        sorted(pre, key=lambda x: x['vol'], reverse=True)[:4],
        sorted(moon, key=lambda x: x['vol'], reverse=True)[:3]
    )

def kirim(msg):
    token=os.getenv('TELE_TOKEN')
    chat=os.getenv('TELE_CHAT_ID')
    if not token or not chat: print(msg); return
    try:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id":chat,"text":msg}, timeout=15)
    except: print(msg)

if __name__=="__main__":
    data=get_data()
    hold, pre, moon = scan(data)
    total=len(hold)+len(pre)+len(moon)
    msg=f"V50 Data {len(data)} | HOLD{len(hold)} PRE{len(pre)} M{len(moon)} = {total}\n\n"
    if hold:
        msg+="💎 HOLD IJO\n"
        for k in hold: msg+=f"{k['sym']} {k['chg']:.1f}% rg {k['rg']:.0f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg+="\n"
    if pre:
        msg+="⚠️ PRE-PUMP\n"
        for k in pre: msg+=f"{k['sym']} {k['chg']:.1f}% rg {k['rg']:.0f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg+="\n"
    if moon:
        msg+="🚀 MOONING\n"
        for k in moon: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    if total==0:
        msg+="MARKET SEPI! SEMUA KOIN MERAH!"
    print(msg)
    kirim(msg)
