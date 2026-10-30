# V16.8 FIX - TIER 1 GA 0.0% LAGI! PISAH MID TEBAL & GLOBAL!
import requests, os
TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')

BLACKLIST={
    'usdt_idr','usdc_idr','dai_idr','busd_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr','usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr','wbtc_idr',
    'btc_idr','eth_idr','bnb_idr','sol_idr','xrp_idr','ada_idr','doge_idr','trx_idr','dot_idr','matic_idr','avax_idr','link_idr','ltc_idr','bch_idr','etc_idr','xlm_idr','uni_idr',
    'luna_idr','lunc_idr','ftt_idr','ustc_idr','luna2_idr','btt_idr','bttc_idr','dgb_idr','qtum_idr','waves_idr','zrx_idr','omg_idr','bat_idr','ont_idr','iost_idr','sc_idr','zcash_idr','dash_idr','xem_idr','bcd_idr','bcha_idr',
    'shib_idr','pepe_idr','floki_idr','bonk_idr','wif_idr','ern_idr',
}

def send_tele(msg):
    requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", json={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=15)

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
    try:
        r=requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=10).json()
        g={}
        for x in r:
            if x['symbol'].endswith('USDT'):
                g[x['symbol'].replace('USDT','').lower()+'_idr']=float(x['priceChangePercent'])
        return g
    except:
        return {}

def scan():
    tickers=get_tickers()
    gdata=get_global()
    tier1_mid=[]; tier1_global=[]; tier2=[]
    for t in tickers:
        sym=t['sym']; price=t['last']; low=t['low']
        naik=t['naik']; pos=t['pos']; vol=t['vol']; bb=t['bb']
        gp=gdata.get(t['pair'], 0)
        sup = f"{low*1.02:.0f}-{bb*0.98:.0f}"

        # TIER 1A - BANDAR MID TEBAL (POLA UAI, BICO, BEAT KEMARIN!)
        # Pola: Naik 0.8-8%, Pos <=30%, Vol >=150Mn (Vol 2/3 Mcap)
        if vol>=150_000_000 and 0.8<=naik<=8 and pos<=30:
            tier1_mid.append(f"BANDAR MID TEBAL | {sym} Rp{price} | Entry {sup} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn")

        # TIER 1B - BANDAR GLOBAL ALL VALID (GP HARUS >=3.5%! GA 0.0% LAGI!)
        if gp>=3.5 and vol>=150_000_000 and 2<=naik<=35 and pos<=80:
            tier1_global.append(f"BANDAR GLOBAL {gp:.1f}% | {sym} Rp{price} | Entry {sup} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn")

        # TIER 2 - POLA 16.7 (CVC, SKL, BEAT PROFIT!)
        if 2<=naik<=35 and pos<=15 and vol>=100_000_000:
            label = "🚀 BB BREAK" if price>bb else "🔥 IGNITION"
            tier2.append(f"{label} | {sym} Rp{price} | ENTRY {sup} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn")

    msg=f"=== V16.8 FIX NO 0.0% ===\n"
    msg+=f"TIER 1A - MID TEBAL (UAI/BICO/BEAT):\n"+("\n".join(tier1_mid[:10]) if tier1_mid else "Tidak ada")+"\n\n"
    msg+=f"TIER 1B - BANDAR GLOBAL >=3.5%:\n"+("\n".join(tier1_global[:10]) if tier1_global else "Tidak ada (Binance API lg 0%)")+"\n\n"
    msg+=f"TIER 2 - BUYER SIAP TERBANG:\n"+("\n".join(tier2[:10]) if tier2 else "Tidak ada")
    return msg

if __name__=="__main__":
    msg=scan()
    print(msg)
    send_tele(msg)
