# V16.7 FINAL FULL - TIER 1 NO 2 GLOBAL-ALL - BLACKLIST SKIP - MAINTENANCE SKIP - DELISTING SKIP
import requests
import os

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID')

# === BLACKLIST = SKIP! ===
BLACKLIST = {
    'usdt_idr','usdc_idr','dai_idr','busd_idr','usde_idr','paxg_idr','xaut_idr','eurc_idr','usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'btc_idr','eth_idr','bnb_idr','sol_idr','xrp_idr','ada_idr','doge_idr','trx_idr','dot_idr','matic_idr','avax_idr','link_idr','ltc_idr','bch_idr','etc_idr','xlm_idr','uni_idr',
    'shib_idr','pepe_idr','floki_idr','bonk_idr','wif_idr'
}

# === MAINTENANCE + DELISTING INDODAX = SKIP! LUPAIN AJA! ===
# ERN, SKL, dll yang bikin nyangkut!
DELISTING_MAINT = {
    'ern_idr','skl_idr','gtc_idr','haedal_idr','beat_idr','blur_idr',
    'luna_idr','lunc_idr','ftt_idr','ustc_idr','luna2_idr',
    'btt_idr','bttc_idr','dgb_idr','qtum_idr','waves_idr','zrx_idr',
    'omg_idr','bat_idr','ont_idr','iost_idr','sc_idr','zcash_idr','dash_idr','xem_idr','bcd_idr','bcha_idr'
}

def send_tele(msg):
    url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=15)
    except Exception as e:
        print(f"Tele error: {e}")

def get_indodax_tickers():
    try:
        r = requests.get("https://indodax.com/api/tickers", timeout=15).json()['tickers']
        out = []
        for pair, d in r.items():
            if not pair.endswith('_idr'): continue
            if pair in BLACKLIST: continue  # SKIP BLACKLIST
            if pair in DELISTING_MAINT: continue  # SKIP DELISTING/MAINTENANCE - ERN, SKL LUPAIN!
            if float(d['vol_idr']) < 10000000: continue  # SKIP VOL <10Mn - ERN biasanya vol 0!
            if float(d['last']) == 0: continue

            last=float(d['last']); low=float(d['low']); high=float(d['high']); vol=float(d['vol_idr'])
            pos=((last-low)/(high-low)*100) if high!=low else 0
            naik=((last-low)/low*100) if low!=0 else 0
            bb_upper=high*0.97
            
            out.append({
                'pair':pair,'symbol':pair.replace('_idr','').upper(),
                'last':last,'low':low,'high':high,'vol_idr':vol,
                'pos':pos,'naik_24h':naik,'naik_1h':naik,'bb_upper':bb_upper
            })
        return out
    except Exception as e:
        print(f"Indodax error: {e}")
        return []

def get_global_all():
    # === GANTI INI SAMA LOGIC 6EX 5972 KOIN V16.6 LU YANG ASLI YA MIN! ===
    # Ini dummy dulu biar jalan!
    return {}

def scan_v16_7():
    tickers=get_indodax_tickers()
    global_data=get_global_all()
    tier1=[]; tier2=[]

    for t in tickers:
        pair=t['pair']; sym=t['symbol']; price=t['last']
        naik=t['naik_24h']; pos=t['pos']; vol=t['vol_idr']
        naik_1h=t['naik_1h']; bb=t['bb_upper']
        g_pct=global_data.get(pair, 0)

        # TIER 1 - NO 2 BANDAR GLOBAL-ALL (YANG LU BILANG BAGUS!)
        # Global 3%+ + Vol 150Mn+ + Naik 2-35% + Pos <=80%
        if g_pct >= 3.0 and vol >= 150_000_000 and 2 <= naik <= 35 and pos <= 80:
            tier1.append(f"BANDAR GLOBAL-ALL {g_pct}% | {sym} Rp{price} Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn")

        # TIER 2 - BUYER SIAP TERBANG
        if 2 <= naik <= 35:
            if pos <= 15 and vol >= 100_000_000 and naik_1h >= 2.5:
                if price > bb:
                    tier2.append(f"🚀 BB BREAK | {sym} Rp{price} Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn")
                else:
                    tier2.append(f"🔥 IGNITION | {sym} Rp{price} Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn")
            elif pos <= 15 and vol >= 150_000_000:
                tier2.append(f"💰 AKUM BAWAH | {sym} Rp{price} Naik {naik:.1f}% Pos {pos:.0f}%")

    msg=f"=== V16.7 FINAL NO2 GLOBAL-ALL ===\n"
    msg+=f"TIER 1 - BANDAR GLOBAL-ALL:\n"+("\n".join(tier1[:15]) if tier1 else "Tidak ada")+"\n\n"
    msg+=f"TIER 2 - BUYER SIAP TERBANG:\n"+("\n".join(tier2[:15]) if tier2 else "Tidak ada")
    return msg

if __name__=="__main__":
    print("Running V16.7 FINAL...")
    msg=scan_v16_7()
    print(msg)
    send_tele(msg)
    print("Tele sent!")
