# V17.4 FINAL - ENTRY OB KETAT 1-3% = DAPAT 7% KAYAK TEMEN LU!
import requests, os

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')

BLACKLIST={
    'usdt_idr','usdc_idr','dai_idr','busd_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr','usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'btc_idr','eth_idr','bnb_idr','sol_idr','xrp_idr','ada_idr','doge_idr','trx_idr','dot_idr','matic_idr','avax_idr','link_idr','ltc_idr','bch_idr','etc_idr','xlm_idr','uni_idr',
    'luna_idr','lunc_idr','ftt_idr','ustc_idr','luna2_idr','btt_idr','bttc_idr','dgb_idr','qtum_idr','waves_idr','zrx_idr','omg_idr','bat_idr','ont_idr','iost_idr','sc_idr','zcash_idr','dash_idr','xem_idr','bcd_idr','bcha_idr',
    'shib_idr','pepe_idr','floki_idr','bonk_idr','wif_idr','ern_idr',
    'ondo_idr','hype_idr','sui_idr','dodo_idr','bome_idr','nom_idr','mpro_idr','amp_idr','unmd_idr','kdag_idr',
}

def send_tele(msg):
    try:
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=15)
    except: pass

def get_tickers():
    r = requests.get("https://indodax.com/api/tickers", timeout=15).json()['tickers']
    out=[]
    for pair,d in r.items():
        if not pair.endswith('_idr'): continue
        if pair in BLACKLIST: continue
        if float(d['vol_idr']) < 10_000_000: continue
        if float(d['last']) == 0: continue
        last=float(d['last']); low=float(d['low']); high=float(d['high']); vol=float(d['vol_idr'])
        pos=((last-low)/(high-low)*100) if high!=low else 0
        naik=((last-low)/low*100) if low!=0 else 0
        out.append({'pair':pair,'sym':pair.replace('_idr','').upper(),'last':last,'low':low,'high':high,'vol':vol,'pos':pos,'naik':naik})
    return out

def get_global():
    g = {}
    try:
        r = requests.get("https://api.bybit.com/v5/market/tickers?category=spot", timeout=6).json()
        for x in r['result']['list']:
            if x['symbol'].endswith('USDT'):
                key = x['symbol'].replace('USDT','').lower()+'_idr'
                g[key] = max(g.get(key, -100), float(x['price24hPcnt'])*100)
    except: pass
    try:
        r = requests.get("https://api.gateio.ws/api/v4/spot/tickers", timeout=6).json()
        for x in r:
            if x['currency_pair'].endswith('_USDT'):
                key = x['currency_pair'].replace('_USDT','').lower()+'_idr'
                g[key] = max(g.get(key, -100), float(x['change_percentage']))
    except: pass
    try:
        r = requests.get("https://api.kucoin.com/api/v1/market/allTickers", timeout=6).json()
        for x in r['data']['ticker']:
            if x['symbol'].endswith('-USDT'):
                key = x['symbol'].replace('-USDT','').lower()+'_idr'
                g[key] = max(g.get(key, -100), float(x['changeRate'])*100)
    except: pass
    try:
        r = requests.get("https://api.bitget.com/api/v2/spot/market/tickers", timeout=6).json()
        for x in r['data']:
            if x['symbol'].endswith('USDT'):
                key = x['symbol'].replace('USDT','').lower()+'_idr'
                g[key] = max(g.get(key, -100), float(x['change24h'])*100)
    except: pass
    try:
        r = requests.get("https://api.mexc.com/api/v3/ticker/24hr", timeout=6).json()
        for x in r:
            if x['symbol'].endswith('USDT'):
                key = x['symbol'].replace('USDT','').lower()+'_idr'
                g[key] = max(g.get(key, -100), float(x['priceChangePercent']))
    except: pass
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=6).json()
        for x in r:
            if x['symbol'].endswith('USDT'):
                key = x['symbol'].replace('USDT','').lower()+'_idr'
                g[key] = max(g.get(key, -100), float(x['priceChangePercent']))
    except: pass
    return g

def detect_ob_and_entry(t):
    low=t['low']; pos=t['pos']; naik=t['naik']; vol=t['vol']
    # OB KETAT: 2-8% di atas low = PRESISI!
    # Ini yang bikin temen lu dapat 7%!
    if pos <= 55 and vol >= 80_000_000 and naik >= 2:
        ob_low = low * 0.995  # 0.5% di bawah low
        ob_high = low * 1.06  # 6% di atas low = OB KETAT!
        # Entry = 1-3% di atas OB = pas di atas tembok bandar!
        entry_low = low * 1.01
        entry_high = low * 1.04
        return ob_low, ob_high, entry_low, entry_high
    return None, None, None, None

def scan():
    tickers=get_tickers()
    gdata=get_global()
    tier0=[]; tier1_mid=[]; tier1_global=[]; tier2=[]
    
    for t in tickers:
        sym=t['sym']; price=t['last']; low=t['low']
        naik=t['naik']; pos=t['pos']; vol=t['vol']
        gp=gdata.get(t['pair'], 0)
        
        ob_low, ob_high, ent_low, ent_high = detect_ob_and_entry(t)
        
        if ob_low is None:
            continue
            
        ob_txt = f"OB {ob_low:.0f}-{ob_high:.0f}"
        entry_txt = f"{ent_low:.0f}-{ent_high:.0f}"

        # TIER 0 - NEW LAUNCH + OB KETAT
        if low < 1000 and vol>=80_000_000 and 20<=naik<=1200 and pos<=80:
            tier0.append(f"💥 NEW {naik:.0f}% + {ob_txt} | {sym} Rp{price} | ENTRY OB {entry_txt} | Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn")

        # TIER 1A - MID TEBAL + OB KETAT
        if vol>=150_000_000 and 0.8<=naik<=8 and pos<=30:
            tier1_mid.append(f"BANDAR MID TEBAL {ob_txt} | {sym} Rp{price} | ENTRY OB {entry_txt} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn")

        # TIER 1B - BANDAR GLOBAL + OB KETAT (INI KUNCI 7%!)
        if gp>=3.5 and vol>=150_000_000 and 2<=naik<=35 and pos<=55:
            tier1_global.append(f"BANDAR GLOBAL {gp:.1f}% {ob_txt} | {sym} Rp{price} | ENTRY OB {entry_txt} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}%")

        # TIER 2 - IGNITION + OB KETAT
        if 2<=naik<=50 and pos<=15 and vol>=100_000_000:
            tier2.append(f"🔥 IGNITION {ob_txt} | {sym} Rp{price} | ENTRY OB {entry_txt} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn")

    msg=f"=== V17.4 ENTRY OB KETAT 7% ===\n"
    msg+=f"TIER 0 - NEW LAUNCH + OB:\n"+("\n".join(tier0[:10]) if tier0 else "Tidak ada")+"\n\n"
    msg+=f"TIER 1A - MID TEBAL + OB:\n"+("\n".join(tier1_mid[:10]) if tier1_mid else "Tidak ada")+"\n\n"
    msg+=f"TIER 1B - BANDAR GLOBAL + OB KETAT (7%):\n"+("\n".join(tier1_global[:10]) if tier1_global else "Tidak ada")+"\n\n"
    msg+=f"TIER 2 - IGNITION + OB:\n"+("\n".join(tier2[:10]) if tier2 else "Tidak ada")
    return msg

if __name__=="__main__":
    msg=scan()
    print(msg)
    send_tele(msg)
