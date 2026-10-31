# V16.9 FINAL - 6 EXCHANGE BANDAR GLOBAL ALL + SUPPORT ENTRY + BLACKLIST LENGKAP!
import requests, os

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')

# BLACKLIST PUNYA LU - LENGKAP PERSIS!
BLACKLIST={
    'usdt_idr','usdc_idr','dai_idr','busd_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr','usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'btc_idr','eth_idr','bnb_idr','sol_idr','xrp_idr','ada_idr','doge_idr','trx_idr','dot_idr','matic_idr','avax_idr','link_idr','ltc_idr','bch_idr','etc_idr','xlm_idr','uni_idr',
    'luna_idr','lunc_idr','ftt_idr','ustc_idr','luna2_idr','btt_idr','bttc_idr','dgb_idr','qtum_idr','waves_idr','zrx_idr','omg_idr','bat_idr','ont_idr','iost_idr','sc_idr','zcash_idr','dash_idr','xem_idr','bcd_idr','bcha_idr',
    'shib_idr','pepe_idr','floki_idr','bonk_idr','wif_idr','ern_idr','ondo'
    _idr','Hype_idr','sui_idr','pepe_idr','dodo_idr','bome_','nom_idr',mpro_idr',amp_idr','unmd_idr','kdag_idr',
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
        out.append({'pair':pair,'sym':pair.replace('_idr','').upper(),'last':last,'low':low,'high':high,'vol':vol,'pos':pos,'naik':naik,'bb':high*0.97})
    return out

def get_global():
    g = {}
    # 1. BYBIT - Bandar pump tercepat
    try:
        r = requests.get("https://api.bybit.com/v5/market/tickers?category=spot", timeout=6).json()
        for x in r['result']['list']:
            if x['symbol'].endswith('USDT'):
                key = x['symbol'].replace('USDT','').lower()+'_idr'
                val = float(x['price24hPcnt'])*100
                g[key] = max(g.get(key, -100), val)
    except: pass
    # 2. GATE.IO - Paling banyak altcoin baru (CVC, UAI, BICO)
    try:
        r = requests.get("https://api.gateio.ws/api/v4/spot/tickers", timeout=6).json()
        for x in r:
            if x['currency_pair'].endswith('_USDT'):
                key = x['currency_pair'].replace('_USDT','').lower()+'_idr'
                val = float(x['change_percentage'])
                g[key] = max(g.get(key, -100), val)
    except: pass
    # 3. KUCOIN - Micro cap
    try:
        r = requests.get("https://api.kucoin.com/api/v1/market/allTickers", timeout=6).json()
        for x in r['data']['ticker']:
            if x['symbol'].endswith('-USDT'):
                key = x['symbol'].replace('-USDT','').lower()+'_idr'
                val = float(x['changeRate'])*100
                g[key] = max(g.get(key, -100), val)
    except: pass
    # 4. BITGET - Sering duluan 10 menit
    try:
        r = requests.get("https://api.bitget.com/api/v2/spot/market/tickers", timeout=6).json()
        for x in r['data']:
            if x['symbol'].endswith('USDT'):
                key = x['symbol'].replace('USDT','').lower()+'_idr'
                val = float(x['change24h'])*100
                g[key] = max(g.get(key, -100), val)
    except: pass
    # 5. MEXC - KUNCI! Banyak koin Indodax MYX, MARSCOIN!
    try:
        r = requests.get("https://api.mexc.com/api/v3/ticker/24hr", timeout=6).json()
        for x in r:
            if x['symbol'].endswith('USDT'):
                key = x['symbol'].replace('USDT','').lower()+'_idr'
                val = float(x['priceChangePercent'])
                g[key] = max(g.get(key, -100), val)
    except: pass
    # 6. BINANCE - Backup (lagi hack, tapi biarin)
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=6).json()
        for x in r:
            if x['symbol'].endswith('USDT'):
                key = x['symbol'].replace('USDT','').lower()+'_idr'
                val = float(x['priceChangePercent'])
                g[key] = max(g.get(key, -100), val)
    except: pass
    return g

def scan():
    tickers=get_tickers()
    gdata=get_global()
    tier1_mid=[]; tier1_global=[]; tier2=[]
    for t in tickers:
        sym=t['sym']; price=t['last']; low=t['low']
        naik=t['naik']; pos=t['pos']; vol=t['vol']; bb=t['bb']
        gp=gdata.get(t['pair'], 0)
        sup = f"{low*1.02:.0f}-{bb*0.98:.0f}"

        # TIER 1A - BANDAR MID TEBAL (POLA UAI, BICO, BEAT!)
        if vol>=150_000_000 and 0.8<=naik<=8 and pos<=30:
            tier1_mid.append(f"BANDAR MID TEBAL | {sym} Rp{price} | Entry {sup} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn")

        # TIER 1B - BANDAR GLOBAL ALL EXCHANGE 6x (GP >=3.5%!)
        if gp>=3.5 and vol>=150_000_000 and 2<=naik<=35 and pos<=80:
            tier1_global.append(f"BANDAR GLOBAL {gp:.1f}% | {sym} Rp{price} | Entry {sup} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn")

        # TIER 2 - POLA 16.7 (CVC, SKL, BEAT, AAPLX PROFIT!)
        if 2<=naik<=35 and pos<=15 and vol>=100_000_000:
            label = "🚀 BB BREAK" if price>bb else "🔥 IGNITION"
            tier2.append(f"{label} | {sym} Rp{price} | ENTRY {sup} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn")

    msg=f"=== V16.9 FINAL 6 EXCHANGE GLOBAL ===\n"
    msg+=f"TIER 1A - MID TEBAL (UAI/BICO/BEAT):\n"+("\n".join(tier1_mid[:10]) if tier1_mid else "Tidak ada")+"\n\n"
    msg+=f"TIER 1B - BANDAR GLOBAL 6 EXCH >=3.5%:\n"+("\n".join(tier1_global[:10]) if tier1_global else "Tidak ada (Market sepi global)")+"\n\n"
    msg+=f"TIER 2 - BUYER SIAP TERBANG (CVC/SKL/BEAT):\n"+("\n".join(tier2[:10]) if tier2 else "Tidak ada")
    return msg

if __name__=="__main__":
    msg=scan()
    print(msg)
    send_tele(msg)
