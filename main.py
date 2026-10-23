import requests, os, json

# V48 - BLOCK SEMUA KOIN PERSENAN KECIL!
BLOCKED = {
    'BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','DAI_IDR','PAXG_IDR',
    'XRP_IDR','DOGE_IDR','SOL_IDR','HYPE_IDR','FARTCOIN_IDR',
    'PEPE_IDR','SHIB_IDR','TRX_IDR','AVAX_IDR','ADA_IDR','DOT_IDR','LINK_IDR','LTC_IDR','BCH_IDR','XLM_IDR','UNI_IDR','ETC_IDR','NEAR_IDR','BONK_IDR','FLOKI_IDR','WIF_IDR',
    'HBAR_IDR','XAUT_IDR','PIPPIN_IDR','PENGU_IDR','ANOA_IDR','GID_IDR','WLD_IDR','TIA_IDR','MOODENG_IDR',
    'BOME_IDR','ONDO_IDR',
    # BLOCK KOIN LEMOT / PERSENAN KECIL!
    'ENA_IDR','ASTER_IDR','MYX_IDR','USDE_IDR','USD1_IDR','SUSDE_IDR','WUSDT_IDR',
    'XLM_IDR','XRP_IDR','ADA_IDR','DOT_IDR','LINK_IDR','LTC_IDR','ETC_IDR','TRX_IDR','ATOM_IDR','FIL_IDR','APT_IDR','ARB_IDR','OP_IDR','SUI_IDR','SEI_IDR',
    'MITO_IDR','ERN_IDR','UNMD_IDR','LUNA_IDR','LUNC_IDR','FTM_IDR','BTT_IDR','XEM_IDR','USELESS_IDR','PUMP_IDR','MAVIA_IDR',
}

STATE_FILE = "/tmp/v48_state.json"
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
                if last < 0.5: continue
                if vol_bn < 0.2: continue # Naikin vol min jadi 0.2Bn = 200Mn!
                if vol_bn > 20: continue
                chg24 = change.get(pair, 0)
                if abs(chg24) < 0.1:
                    chg24 = (last-low)/low*100 if low else 0
                
                sisa=(high-last)/last*100 if last else 0
                rg=(high-low)/low*100 if low else 0
                chg_low=(last-low)/low*100 if low else 0
                
                # BLOCK PERSENAN KECIL - ATURAN BARU KETAT!
                if chg24 < 4: continue # Chg <4% LANGSUNG BLOCK! ASTER 3.1% KE BLOCK!
                if rg < 8: continue # RG <8% = coin diem, BLOCK!
                if sisa < 5: continue # Sisa <5% = udah pucuk, BLOCK! ENA sisa 0% KE BLOCK!
                if sisa > 35: continue
                if chg_low < 4: continue # Bounce <4% = lemot, BLOCK!
                if chg_low > 60: continue
                if rg > 120: continue
                
                out.append({'sym':sym,'chg':chg24,'low':chg_low,'sisa':sisa,'vol':vol_bn,'last':last,'high':high,'rg':rg})
            except: continue
        return out
    except: return []

def scan(data):
    state=load_state()
    new_state={}
    pre=[]; moon=[]; bounce=[]
    for k in data:
        sym=k['sym']; sisa=k['sisa']; low=k['low']; chg=k['chg']; rg=k['rg']; vol=k['vol']
        hist=state.get(sym,{})
        prev_sisa=hist.get('sisa',100)
        new_state[sym]={'sisa':sisa,'vol':vol,'high':k['high'],'last':k['last'],'rg':rg}
        is_moon = sisa < prev_sisa and sisa < 10 and prev_sisa!=100
        is_pre = 8 <= rg <= 40 and 8 <= sisa <= 35 and 4 <= low <= 25 and chg >= 4
        is_bounce = 5 <= low <= 40 and 5 <= sisa <= 30 and chg >= 4
        
        if is_moon and sisa <= 8:
            moon.append(k)
        elif is_pre:
            pre.append(k)
        elif is_bounce:
            bounce.append(k)
            
    save_state({**state,**new_state})
    return (
        sorted(pre, key=lambda x: x['vol'], reverse=True)[:4],
        sorted(moon, key=lambda x: x['vol'], reverse=True)[:3],
        sorted(bounce, key=lambda x: x['vol'], reverse=True)[:3]
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
    pre, moon, bnc = scan(data)
    total=len(pre)+len(moon)+len(bnc)
    msg=f"V48 NO KOIN LEMOT Data {len(data)} | PRE{len(pre)} M{len(moon)} B{len(bnc)} = {total}\n\n"
    if pre:
        msg+="⚠️ PRE-PUMP CUAN GEDE\n"
        for k in pre: msg+=f"{k['sym']} {k['chg']:.1f}% rg {k['rg']:.0f}% sisa {k['sisa']:.0f}% bnc {k['low']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg+="\n"
    if moon:
        msg+="🚀 MOONING TRAIL\n"
        for k in moon: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% bnc {k['low']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg+="\n"
    if bnc:
        msg+="📈 BOUNCE CUAN\n"
        for k in bnc: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% bnc {k['low']:.0f}% Vol {k['vol']:.2f}Bn\n"
    if total==0:
        msg+="SEMUA KOIN LEMOT KE BLOCK! MARKET SEPI!"
    print(msg)
    kirim(msg)
