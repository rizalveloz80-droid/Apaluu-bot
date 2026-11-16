# === V37.1 RECOVERY - BALIK KE YANG BENER! ===
# V37.1 = V37 - summaries! - CoinGecko! BALIK KE Global 6EX + Bandar Indodax!
# Naik24h = Global 6EX (BYBIT+GATE+KUCOIN+BITGET+MEXC+BINANCE)! BUKAN summaries! BUKAN dari Low!
# Kalo Global [-] = UNKNOWN! Bukan 0.0%! Jangan dilolosin ke AKUMULASI Global!
# TIER 1 AKUMULASI = Bandar lagi kumpul, mau running! TIER 2 PANTAU = Udah pump, jangan kejar!
import requests, os, json, time
from datetime import datetime
import pytz

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID') or os.getenv('CHAT_ID')
WIB = pytz.timezone('Asia/Jakarta')

BLACKLIST={
    'usdt_idr','usdc_idr','dai_idr','busd_idr','usde_idr','paxg_idr','xaut_idr','xaus_idr','eurc_idr','usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'btc_idr','eth_idr','bnb_idr','sol_idr','xrp_idr','ada_idr','doge_idr','trx_idr','dot_idr','matic_idr','avax_idr','link_idr','ltc_idr','bch_idr','etc_idr','xlm_idr','uni_idr',
    'luna_idr','lunc_idr','ftt_idr','ustc_idr','luna2_idr','btt_idr','bttc_idr','dgb_idr','qtum_idr','waves_idr','zrx_idr','omg_idr','bat_idr','ont_idr','iost_idr','sc_idr','zcash_idr','dash_idr','xem_idr','bcd_idr','bcha_idr',
    'shib_idr','pepe_idr','floki_idr','bonk_idr','wif_idr','ern_idr',
    'ondo_idr','sui_idr','dodo_idr','bome_idr','nom_idr','mpro_idr','amp_idr','unmd_idr','kdag_idr',
    'bsv_idr','vet_idr','fil_idr','eos_idr','xtz_idr','neo_idr','aave_idr','comp_idr','mkr_idr','snx_idr','yfi_idr','mana_idr','axs_idr','slp_idr','chz_idr','enj_idr',
    'flow_idr','icp_idr','near_idr','egld_idr','hbar_idr','algo_idr','ftm_idr','one_idr','klay_idr','celo_idr',
    'ena_idr','hype_idr','pippin_idr','pengu_idr','fanc_idr','mog_idr','edena_idr',
}

VOL_FILE = "vol_history.json"
def load_json(f):
    if os.path.exists(f):
        try:
            d = json.load(open(f))
            if isinstance(d, dict): return d
            return {}
        except: return {}
    return {}
def save_json(f,d):
    try: json.dump(d, open(f,"w"))
    except: pass

def get_vol_3h(hist_list, now_ts):
    best=None; best_diff=999999
    for e in hist_list:
        if not isinstance(e, dict): continue
        age=now_ts-e.get("ts",0)
        if 2.5*3600<=age<=3.5*3600:
            diff=abs(age-3*3600)
            if diff<best_diff:
                best_diff=diff; best=e.get("vol",0)
    return best

def send_tele(msg):
    print(msg)
    msg=msg[:3800]
    try:
        requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", json={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=20)
    except: pass

def get_tickers():
    # CUMA PAKE tickers! GAK PAKE summaries LAGI!
    # tickers cuma buat: last, low, high, vol_idr -> Pantulan + Pos + Vol!
    # Naik24h JANGAN dari sini! Naik24h dari Global 6EX!
    try:
        r=requests.get("https://indodax.com/api/tickers", timeout=15).json()['tickers']
    except: return []
    out=[]
    for pair,d in r.items():
        if not pair.endswith('_idr'): continue
        if pair in BLACKLIST: continue
        try:
            if float(d['vol_idr'])<15_000_000: continue
            last=float(d['last']); low=float(d['low']); high=float(d['high']); vol=float(d['vol_idr'])
        except: continue
        if last==0 or low==0 or high==low: continue
        pos=((last-low)/(high-low)*100) if high!=low else 0
        pantulan=((last-low)/low*100) if low!=0 else 0
        out.append({'pair':pair,'sym':pair.replace('_idr','').upper(),'last':last,'low':low,'high':high,'vol':vol,'pos':pos,'pantulan':pantulan})
    return out

def get_global():
    # Global 6EX = Naik24h yang bener!
    # Kalo gak ada di 6EX, gp = None = UNKNOWN! Bukan 0.0%!
    g={}; src={}
    def upd(sym, val, name):
        try: val=float(val)
        except: return
        key=sym.lower()+'_idr'
        if key not in g or val>g[key]: g[key]=val; src[key]=name
    h={"User-Agent":"Mozilla/5.0"}
    try:
        r=requests.get("https://api.bybit.com/v5/market/tickers?category=spot",timeout=6).json()
        for x in r['result']['list']:
            if x['symbol'].endswith('USDT'): upd(x['symbol'].replace('USDT',''), float(x['price24hPcnt'])*100, "BYBIT")
    except: pass
    try:
        r=requests.get("https://api.gateio.ws/api/v4/spot/tickers",timeout=6).json()
        for x in r:
            if x['currency_pair'].endswith('_USDT'): upd(x['currency_pair'].replace('_USDT',''), float(x['change_percentage']), "GATE")
    except: pass
    try:
        r=requests.get("https://api.kucoin.com/api/v1/market/allTickers",timeout=6).json()
        for x in r['data']['ticker']:
            if x['symbol'].endswith('-USDT'): upd(x['symbol'].replace('-USDT',''), float(x['changeRate'])*100, "KUCOIN")
    except: pass
    try:
        r=requests.get("https://api.bitget.com/api/v2/spot/market/tickers",timeout=6).json()
        for x in r['data']:
            if x['symbol'].endswith('USDT'): upd(x['symbol'].replace('USDT',''), float(x['change24h']), "BITGET")
    except: pass
    try:
        r=requests.get("https://api.mexc.com/api/v3/ticker/24hr",timeout=6,headers=h).json()
        for x in r:
            if x['symbol'].endswith('USDT'): upd(x['symbol'].replace('USDT',''), float(x['priceChangePercent']), "MEXC")
    except: pass
    try:
        r=requests.get("https://data-api.binance.vision/api/v3/ticker/24hr",timeout=6,headers=h).json()
        for x in r:
            if x['symbol'].endswith('USDT'): upd(x['symbol'].replace('USDT',''), float(x['priceChangePercent']), "BINANCE")
    except:
        try:
            r=requests.get("https://api.binance.com/api/v3/ticker/24hr",timeout=6,headers=h).json()
            for x in r:
                if x['symbol'].endswith('USDT'): upd(x['symbol'].replace('USDT',''), float(x['priceChangePercent']), "BINANCE")
        except: pass
    return g, src

def scan():
    now=datetime.now(WIB).strftime("%H:%M WIB")
    now_ts=int(time.time())
    vol_hist=load_json(VOL_FILE)
    new_vol={}
    tickers=get_tickers()
    gdata, gsrc=get_global()
    tier_akumulasi=[]; tier_pantau=[]
    hist_kosong=True
    for t in tickers:
        sym=t['sym']; price=t['last']; low=t['low']; pantulan=t['pantulan']; pos=t['pos']; vol=t['vol']
        # Global 6EX = Naik24h! Kalo gak ada = None = UNKNOWN!
        gp=gdata.get(t['pair'])  # None kalo gak ada! Bukan 0!
        gname=gsrc.get(t['pair'],"-")
        gp_txt=f"{gp:.1f}% [{gname}]" if gp is not None else "UNKNOWN [-]"
        # Vol history 3 jam - anti crash!
        hist=vol_hist.get(t['pair'],[])
        if not isinstance(hist, list): hist=[]
        hist=[e for e in hist if isinstance(e, dict) and now_ts-e.get("ts",0)<4*3600]
        vol_3h=get_vol_3h(hist, now_ts)
        if vol_3h: hist_kosong=False
        vol_ratio=(vol/vol_3h) if vol_3h and vol_3h>0 else 0
        hist.append({"ts": now_ts, "vol": vol}); new_vol[t['pair']]=hist
        # === TIER 2 PANTAU DULU! ===
        # Udah pump = Global >=40% ATAU Pantulan >=10% + Pos >=60%
        # HUMA Global 34.8% + Pantulan 41% + Pos 65% -> PANTAU! Bukan 0.0% lagi!
        if (gp is not None and gp>=40) or (pantulan>=10 and pos>=60):
            retest_low=price*0.70; retest_high=price*0.80
            tier_pantau.append((gp if gp is not None else pantulan, f"👀 PANTAU [UDAH PUMP - JANGAN KEJAR]! | {sym} Rp{price:.0f} | Global {gp_txt} Pantulan {pantulan:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | TUNGGU RETEST {retest_low:.0f}-{retest_high:.0f} | Kalo beli sekarang = jadi ONL -72%!"))
            continue
        # === TIER 1 AKUMULASI - 2 JALUR! ===
        # Jalur A: BANDAR INDODAX 3J! Vol 3J naik >=2.5x + Pantulan 0-3% + Pos 15-45% + Vol >=30Mn
        # Kalo Global ada, harus <5%! Kalo Global UNKNOWN, boleh, tapi tulis UNKNOWN!
        # Jalur B: BANDAR GLOBAL VIA INDO! Vol >=100Mn + Pantulan 0-3% + Pos <=45% + Global HARUS ADA dan 0-5%!
        # Kalo Global UNKNOWN, JANGAN lolos Jalur B! Itu yang bikin PM/SHOW kemarin lolos!
        entry_low=low*1.01; entry_high=low*1.03
        target=entry_high*1.10; cut=low*0.995
        if 0<=pantulan<=3.0 and 15<=pos<=45 and vol>=30_000_000 and vol_ratio>=2.5:
            # Global kalo ada harus belum terbang (<5%)! Kalo Global udah >5%, bukan akumulasi!
            if gp is None or gp<5:
                tier_akumulasi.append(f"🔥 AKUMULASI [BANDAR INDO 3J]! | {sym} Rp{price:.0f} | Global {gp_txt} Pantulan {pantulan:.1f}% Pos {pos:.0f}% | Vol 3J Naik {vol_ratio:.1f}x ({vol/1e6:.0f}Mn vs {vol_3h/1e6:.0f}Mn) | ENTRY {entry_low:.0f}-{entry_high:.0f} | TARGET {target:.0f} | CUT {cut:.0f} | BANDAR LAGI KUMPUL!")
                continue
        if 0<=pantulan<=3.0 and pos<=45 and vol>=100_000_000 and gp is not None and -2<=gp<=5:
            tier_akumulasi.append(f"🌍 AKUMULASI [BANDAR GLOBAL VIA INDO]! | {sym} Rp{price:.0f} | Global {gp_txt} Pantulan {pantulan:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn GEDE! | ENTRY {entry_low:.0f}-{entry_high:.0f} | TARGET {target:.0f} | CUT {cut:.0f} | INDO VOL GEDE, GLOBAL BELUM TERBANG!")
            continue
    save_json(VOL_FILE, new_vol)
    tier_pantau_sorted=[x[1] for x in sorted(tier_pantau, key=lambda x: x[0], reverse=True)]
    msg=f"=== V37.1 RECOVERY [Global 6EX + Bandar Indo] {now} - {len(tickers)} KOINS ===\n"
    if hist_kosong:
        msg+=f"⚠️ History baru! Vol 3J belum valid! Tunggu 3 jam! AKUMULASI 3J mungkin kosong dulu, wajar!\n\n"
    msg+=f"🔥 AKUMULASI [BANDAR LAGI KUMPUL - MAU TERBANG - INI YANG DIBELI]:\n"+("\n".join(tier_akumulasi[:8]) if tier_akumulasi else "Belum ada akumulasi - Bandar belum kumpul / Market kalem")+"\n\n"
    msg+=f"👀 PANTAU [UDAH PUMP - JANGAN KEJAR - CUMA DIPANTAU]:\n"+("\n".join(tier_pantau_sorted[:8]) if tier_pantau_sorted else "Belum ada yang pump - Market kalem")+"\n\n"
    msg+=f"📌 Cara baca: Global = Naik24h dari 6EX! Pantulan = dari Low Indodax! Kalo Global UNKNOWN, berarti gak ada di 6EX, koin lokal!\n"
    return msg

if __name__=="__main__":
    send_tele(scan())
