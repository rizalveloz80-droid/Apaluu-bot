# V16.8 FINAL FULL - BANDAR GLOBAL + SUPPORT ENTRY + BLACKLIST LENGKAP PUNYA LU!
import requests, os

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')

# BLACKLIST + DELISTING DARI VERSI SEBELUMNYA - MASUKIN SEMUA BIAR AMAN! LENGKAP!
# PAKAI YANG LU KASIH INI AJA MIN! PERSIS!
BLACKLIST={
    # Stablecoin & Wrapped - LENGKAP
    'usdt_idr','usdc_idr','dai_idr','busd_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr','usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr','wbtc_idr',
    # Big Cap - ga usah di scan bandar
    'btc_idr','eth_idr','bnb_idr','sol_idr','xrp_idr','ada_idr','doge_idr','trx_idr','dot_idr','matic_idr','avax_idr','link_idr','ltc_idr','bch_idr','etc_idr','xlm_idr','uni_idr',
    # Delisting / Coin Mati / Luna dkk - LENGKAP!
    'luna_idr','lunc_idr','ftt_idr','ustc_idr','luna2_idr','btt_idr','bttc_idr','dgb_idr','qtum_idr','waves_idr','zrx_idr','omg_idr','bat_idr','ont_idr','iost_idr','sc_idr','zcash_idr','dash_idr','xem_idr','bcd_idr','bcha_idr',
    # Meme berat sampah volume tipis
    'shib_idr','pepe_idr','floki_idr','bonk_idr','wif_idr','ern_idr',
}

def send_tele(msg):
    url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
    try:
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
    tier1=[]; tier2=[]
    for t in tickers:
        sym=t['sym']; price=t['last']; low=t['low']; high=t['high']
        naik=t['naik']; pos=t['pos']; vol=t['vol']; bb=t['bb']
        gp=gdata.get(t['pair'], 0)

        # SUPPORT ENTRY - YANG TEMEN LU PUNYA!
        support1 = low * 1.03
        support2 = bb * 0.98
        entry_zone = f"{support1:.0f}-{support2:.0f}"

        # TIER 1 - BANDAR GLOBAL (VOL 2/3 MCAP LOGIC + GLOBAL ALL)
        # Vol 150Mn = 2/3 Mcap mid tebal BICO/UAI + Global 3%+
        is_mid_tebal = vol>=150_000_000 and 0.8<=naik<=10 and pos<=50
        is_global_all = gp>=3.0 and vol>=150_000_000 and 2<=naik<=35 and pos<=80
        if is_mid_tebal or is_global_all:
            tier1.append(f"BANDAR GLOBAL {gp:.1f}% | {sym} Rp{price} | Support Entry Rp{entry_zone} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn")

        # TIER 2 - POLA ASLI 16.7 YANG PROFIT CVC/SKL/BEAT + SUPPORT
        if 2<=naik<=35 and pos<=15 and vol>=100_000_000 and naik>=2.5:
            label = "🚀 BB BREAK" if price>bb else "🔥 IGNITION"
            tier2.append(f"{label} | {sym} Rp{price} | ENTRY Rp{entry_zone} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn")

    msg=f"=== V16.8 FINAL BANDAR GLOBAL + SUPPORT ===\n"
    msg+=f"TIER 1 - BANDAR GLOBAL VALID:\n"+("\n".join(tier1[:15]) if tier1 else "Tidak ada")+"\n\n"
    msg+=f"TIER 2 - BUYER SIAP TERBANG (POLA CVC/SKL/BEAT):\n"+("\n".join(tier2[:15]) if tier2 else "Tidak ada")
    return msg

if __name__=="__main__":
    msg=scan()
    print(msg)
    send_tele(msg)
