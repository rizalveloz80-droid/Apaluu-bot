import requests, os, json
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
STATE_FILE = "/tmp/v52_state.json"
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
                if last < 20: continue # BIRB 3 IDR, AMP 15, IOST 15 HILANG!
                if vol_bn < 0.08: continue
                if vol_bn > 25: continue
                chg24 = change.get(pair, 0)
                if abs(chg24) < 0.1: chg24 = (last-low)/low*100 if low else 0
                sisa=(high-last)/last*100 if last else 0
                rg=(high-low)/low*100 if low else 0
                chg_low=(last-low)/low*100 if low else 0
                if chg24 < -30: continue
                if chg24 > 250: continue
                if sisa < 0.3: continue
                if sisa > 60: continue
                if rg < 3 and vol_bn < 0.5: continue
                if rg > 250: continue
                is_early = vol_bn >= 0.5 and 3 <= chg24 <= 45 and 10 <= rg <= 130 and 3 <= sisa <= 50
                out.append({'sym':sym,'chg':chg24,'low':chg_low,'sisa':sisa,'vol':vol_bn,'last':last,'high':high,'rg':rg,'early':is_early})
            except: continue
        return out
    except: return []
def scan(data):
    state=load_state()
    new_state={}
    hold=[]; pre=[]; moon=[]; early=[]
    for k in data:
        sym=k['sym']; sisa=k['sisa']; low=k['low']; chg=k['chg']; rg=k['rg']; vol=k['vol']
        hist=state.get(sym,{})
        prev_sisa=hist.get('sisa',100)
        prev_vol=hist.get('vol',0)
        new_state[sym]={'sisa':sisa,'vol':vol,'high':k['high'],'last':k['last'],'rg':rg}
        vol_spike = vol > prev_vol * 2 and prev_vol > 0 and vol >= 0.5
        is_moon = sisa < prev_sisa and sisa < 5 and prev_sisa!=100
        is_early = k.get('early', False) or vol_spike
        is_hold = 1 <= chg <= 20 and sisa <= 20 and rg >= 5
        is_pre = rg >= 8 and sisa >= 5 and chg >= 1
        if is_moon: moon.append(k)
        elif is_early: early.append(k)
        elif is_hold: hold.append(k)
        elif is_pre: pre.append(k)
    save_state({**state,**new_state})
    return (
        sorted(early, key=lambda x: x['vol'], reverse=True)[:4],
        sorted(hold, key=lambda x: x['chg'], reverse=True)[:5],
        sorted(pre, key=lambda x: x['vol'], reverse=True)[:4],
        sorted(moon, key=lambda x: x['vol'], reverse=True)[:3]
    )
def kirim(msg):
    token=os.getenv('TELE_TOKEN'); chat=os.getenv('TELE_CHAT_ID')
    if not token or not chat: print(msg); return
    try: requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id":chat,"text":msg}, timeout=15)
    except: print(msg)
if __name__=="__main__":
    data=get_data()
    early, hold, pre, moon = scan(data)
    total=len(early)+len(hold)+len(pre)+len(moon)
    msg=f"V52 FINAL Data {len(data)} | EARLY{len(early)} HOLD{len(hold)} PRE{len(pre)} M{len(moon)} = {total}\n\n"
    if early:
        msg+="🔥 EARLY RUNNER\n"
        for k in early: msg+=f"{k['sym']} {k['chg']:.1f}% rg {k['rg']:.0f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn Hrg {k['last']:.0f}\n"
        msg+="\n"
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
    if total==0: msg+="MARKET SEPI!"
    print(msg)
    kirim(msg)
