import requests, os, json, time
BLOCKED = {
    'BTC_IDR','ETH_IDR','USDT_IDR','USDC_IDR','DAI_IDR','PAXG_IDR',
    'XRP_IDR','DOGE_IDR','SOL_IDR','HYPE_IDR','FARTCOIN_IDR',
    'PEPE_IDR','SHIB_IDR','TRX_IDR','AVAX_IDR','ADA_IDR','DOT_IDR','LINK_IDR','LTC_IDR','BCH_IDR','XLM_IDR','UNI_IDR','ETC_IDR','NEAR_IDR','BONK_IDR','FLOKI_IDR','WIF_IDR',
    'HBAR_IDR','XAUT_IDR','PIPPIN_IDR','PENGU_IDR','ANOA_IDR','GID_IDR','WLD_IDR','TIA_IDR','MOODENG_IDR',
    'BOME_IDR','ONDO_IDR',
    'ENA_IDR','ASTER_IDR','MYX_IDR','USDE_IDR','USD1_IDR','SUSDE_IDR','WUSDT_IDR',
    'ATOM_IDR','FIL_IDR','APT_IDR','ARB_IDR','OP_IDR','SUI_IDR','SEI_IDR',
    'MITO_IDR','ERN_IDR','UNMD_IDR','LUNA_IDR','LUNC_IDR','FTM_IDR','BTT_IDR','XEM_IDR','USELESS_IDR','PUMP_IDR','MAVIA_IDR',
    'AMP_IDR','IOST_IDR','KISHU_IDR',
}
STATE_FILE = "/tmp/v57_state.json"

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
                if last < 5: continue
                if vol_bn < 0.08: continue
                if vol_bn > 30: continue
                chg24 = change.get(pair, 0)
                if abs(chg24) < 0.1: chg24 = (last-low)/low*100 if low else 0
                sisa=(high-last)/last*100 if last else 0
                rg=(high-low)/low*100 if low else 0
                if chg24 < -25 or chg24 > 300 or sisa < 0.2 or sisa > 70 or rg < 2 or rg > 300: continue
                out.append({'sym':sym,'chg':chg24,'sisa':sisa,'vol':vol_bn,'last':last,'high':high,'low':low,'rg':rg})
            except: continue
        return out
    except: return []

def scan(data):
    state=load_state()
    new_state={}
    hold=[]; pre=[]; moon=[]; early=[]; koreksi=[]
    now = time.time()
    
    for k in data:
        sym=k['sym']; sisa=k['sisa']; chg=k['chg']; rg=k['rg']; vol=k['vol']
        hist=state.get(sym,{})
        prev_sisa=hist.get('sisa',100)
        prev_vol=hist.get('vol',0)
        prev_high=hist.get('high',0)
        prev_last=hist.get('last',0)
        prev_chg=hist.get('chg',0)
        last_early_time=hist.get('last_early',0) # Kapan terakhir alert early?
        last_hold_time=hist.get('last_hold',0)
        
        new_state[sym]={'sisa':sisa,'vol':vol,'high':k['high'],'last':k['last'],'rg':rg,'low':k['low'],'chg':chg,
                        'last_early':last_early_time,'last_hold':last_hold_time}
        
        sisa_naik = sisa > prev_sisa + 4 and prev_sisa != 100
        last_turun = prev_last > 0 and (prev_last - k['last'])/prev_last*100 > 5 and k['high'] == prev_high
        chg_drop = prev_chg > 0 and prev_chg - chg > 6
        
        if sisa_naik or last_turun or chg_drop:
            koreksi.append(k)
            continue
        
        vol_spike = vol > prev_vol * 1.8 and prev_vol > 0.05 and vol >= 0.30
        is_moon = sisa < prev_sisa and sisa < 3.5 and prev_sisa!=100 and sisa <= 5
        
        is_early_t1 = vol >= 1.0 and 2.5 <= chg <= 30 and 8 <= rg <= 90 and 3 <= sisa <= 35
        is_early_t2 = vol >= 0.40 and 4 <= chg <= 35 and 10 <= rg <= 100 and 5 <= sisa <= 40
        is_early_raw = is_early_t1 or is_early_t2 or vol_spike
        
        is_hold_t1 = vol >= 0.08 and 8 <= chg <= 25 and sisa <= 15 and rg >= 5
        is_hold_t2 = vol >= 0.25 and 3 <= chg <= 20 and sisa <= 15 and rg >= 8
        is_hold_raw = is_hold_t1 or is_hold_t2
        is_pre = vol >= 0.35 and 2.5 <= chg <= 25 and rg >= 10 and sisa >= 8
        
        # V57 FIX ANTI ITU-ITU TERUS!
        # Early cuma alert kalo:
        # 1. Belum pernah alert early dalam 3 jam terakhir, ATAU
        # 2. Vol spike baru (vol naik 1.8x), ATAU
        # 3. Chg naik 2%+ dari sebelumnya (progress!)
        if is_early_raw:
            cooldown = 3*3600 # 3 jam jangan alert lagi!
            if now - last_early_time > cooldown or vol_spike or (chg - prev_chg > 2):
                early.append(k)
                new_state[sym]['last_early'] = now
            else:
                # Udah pernah alert, skip! Biar ga itu-itu terus!
                continue
        
        if is_hold_raw:
            cooldown_hold = 2*3600 # Hold cooldown 2 jam
            if now - last_hold_time > cooldown_hold or chg - prev_chg > 1.5:
                hold.append(k)
                new_state[sym]['last_hold'] = now
        
        if is_moon: moon.append(k)
        elif is_pre and not is_early_raw and not is_hold_raw: pre.append(k)
    
    save_state({**state,**new_state})
    return (
        sorted(early, key=lambda x: x['vol'], reverse=True)[:5],
        sorted(hold, key=lambda x: x['chg'], reverse=True)[:5],
        sorted(pre, key=lambda x: x['vol'], reverse=True)[:3],
        sorted(moon, key=lambda x: x['vol'], reverse=True)[:2],
        sorted(koreksi, key=lambda x: x['vol'], reverse=True)[:4]
    )

def kirim(msg):
    token=os.getenv('TELE_TOKEN'); chat=os.getenv('TELE_CHAT_ID')
    if not token or not chat: print(msg); return
    try: requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id":chat,"text":msg}, timeout=15)
    except: print(msg)

if __name__=="__main__":
    data=get_data()
    early, hold, pre, moon, koreksi = scan(data)
    total=len(early)+len(hold)+len(pre)+len(moon)
    msg=f"V57 ANTI-SPAM Data {len(data)} BLOCKED 66 | EARLY{len(early)} HOLD{len(hold)} PRE{len(pre)} M{len(moon)} = {total}\n\n"
    if early:
        msg+="🔥 EARLY RUNNER - BARU!\n"
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
    if koreksi:
        msg+="📉 KOREKSI - SKIP!\n"
        for k in koreksi: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
        msg+="\n"
    if moon:
        msg+="🚀 MOONING\n"
        for k in moon: msg+=f"{k['sym']} {k['chg']:.1f}% sisa {k['sisa']:.0f}% Vol {k['vol']:.2f}Bn\n"
    if total==0:
        msg+="MARKET SEPI - Ga ada koin baru! Yang tadi udah di-alert 3 jam yang lalu, ga diulang lagi biar ga bosan!"
    print(msg)
    kirim(msg)
