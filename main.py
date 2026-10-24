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
STATE_FILE = "/tmp/v54_state.json"
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
                # V54 FIX 1: Harga receh <5 aja! Biarin 15 IDR masuk kalo vol gede! AMP 15 IDR vol 0.06Bn kecil = nanti ke-filter vol!
                if last < 5: continue
                # V54 FIX 2: Vol min 0.08Bn! Longgar! ICNT 0.12Bn masuk! ATH 0.10Bn masuk!
                if vol_bn < 0.08: continue
                if vol_bn > 30: continue
                chg24 = change.get(pair, 0)
                if abs(chg24) < 0.1: chg24 = (last-low)/low*100 if low else 0
                sisa=(high-last)/last*100 if last else 0
                rg=(high-low)/low*100 if low else 0
                # V54 FIX 3: Filter super longgar di get_data! Biarin semua masuk dulu! Nanti di-scan yang ketat!
                if chg24 < -25: continue
                if chg24 > 300: continue
                if sisa < 0.2: continue
                if sisa > 70: continue
                if rg < 2: continue
                if rg > 300: continue
                out.append({'sym':sym,'chg':chg24,'sisa':sisa,'vol':vol_bn,'last':last,'high':high,'rg':rg})
            except: continue
        return out
    except: return []

def scan(data):
    state=load_state()
    new_state={}
    hold=[]; pre=[]; moon=[]; early=[]
    for k in data:
        sym=k['sym']; sisa=k['sisa']; chg=k['chg']; rg=k['rg']; vol=k['vol']
        hist=state.get(sym,{})
        prev_sisa=hist.get('sisa',100)
        prev_vol=hist.get('vol',0)
        new_state[sym]={'sisa':sisa,'vol':vol,'high':k['high'],'last':k['last'],'rg':rg}
        
        # V54 FIX 4: VOL MOMENTUM! INI KUNCI AWAL RAME!
        # Kalo vol naik 1.8x dari kemarin + vol >=0.30Bn = buyer masuk!
        vol_spike = vol > prev_vol * 1.8 and prev_vol > 0.05 and vol >= 0.30
        
        is_moon = sisa < prev_sisa and sisa < 3.5 and prev_sisa!=100
        
        # V54 FIX 5: EARLY RUNNER TIER VOL! INI YANG BIKIN KEDETEKSI AWAL!
        # Tier 1: Vol gede >=1.0Bn = chg 2.5% aja udah rame! BR 3% Vol 4.68Bn = MASUK! ZEREBRO 4.4% Vol 5.16Bn = MASUK!
        # Tier 2: Vol sedang >=0.40Bn = chg 4% baru rame!
        # Tier 3: Vol kecil >=0.15Bn = chg 7% baru rame! (ATH 10.3% Vol 0.10Bn = ga masuk early, tapi masuk hold!)
        is_early_tier1 = vol >= 1.0 and 2.5 <= chg <= 30 and 8 <= rg <= 90 and 3 <= sisa <= 40
        is_early_tier2 = vol >= 0.40 and 4 <= chg <= 35 and 10 <= rg <= 100 and 5 <= sisa <= 45
        is_early = is_early_tier1 or is_early_tier2 or vol_spike
        
        # V54 FIX 6: HOLD TIER VOL! ATH 10.3% Vol 0.10Bn MASUK!
        is_hold_tier1 = vol >= 0.08 and chg >= 8 and chg <= 25 and sisa <= 18 and rg >= 5 # ATH 10.3% Vol 0.10Bn MASUK! Entry lu aman!
        is_hold_tier2 = vol >= 0.25 and 3 <= chg <= 20 and sisa <= 18 and rg >= 8 # BR 3% Vol 4.68Bn MASUK kalo sisa kecil!
        is_hold = is_hold_tier1 or is_hold_tier2
        
        # V54 FIX 7: PRE TIER VOL! PM 1.2% HILANG!
        is_pre = vol >= 0.35 and 2.5 <= chg <= 25 and rg >= 10 and sisa >= 8 # PM 1.2% HILANG! STIK 1.5% HILANG!
        
        if is_moon: moon.append(k)
        elif is_early: early.append(k)
        elif is_hold: hold.append(k)
        elif is_pre: pre.append(k)
    save_state({**state,**new_state})
    return (
        sorted(early, key=lambda x: x['vol'], reverse=True)[:5],
        sorted(hold, key=lambda x: x['chg'], reverse=True)[:5],
        sorted(pre, key=lambda x: x['vol'], reverse=True)[:3],
        sorted(moon, key=lambda x: x['vol'], reverse=True)[:2]
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
    msg=f"V54 EARLY-DETECT Data {len(data)} | EARLY{len(early)} HOLD{len(hold)} PRE{len(pre)} M{len(moon)} = {total}\n\n"
    if early:
        msg+="🔥 EARLY RUNNER (DETEKSI AWAL RAME!)\n"
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
