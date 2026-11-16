# === V37 RECOVERY - CUMA 2 TIER! ===
# V37 = V28.4 FIX + BENERIN NAIK 24H PAKE summaries/prices24h (BUKAN DARI LOW!)
# TIER 1 AKUMULASI = Koin baru, bandar lagi kumpul, mau running, mau terbang! INI YANG DIBELI!
# TIER 2 PANTAU = Udah pump, jangan kejar, cukup dipantau! TUNGGU RETEST!
# GAK ADA HOLDING! GAK ADA TIER 0! GAK ADA BULLISH! GAK ADA PUMP CEPET!
# FIX: Naik 24h dari summaries, Pantulan dari Low dipisah! ONL -26% gak akan ketipu jadi +9% lagi!
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

def get_coingecko_chg():
    # Buat cadangan Naik 24h kalo summaries gagal
    out={}
    try:
        for page in [1,2]:
            r=requests.get(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page={page}&sparkline=false", timeout=12).json()
            for x in r:
                sym=x['symbol'].upper()
                chg=x.get('price_change_percentage_24h')
                if chg is not None: out[sym]=float(chg)
    except: pass
    return out

def get_tickers():
    # PAKAI summaries! Karena summaries punya prices24h = harga 24 jam lalu!
    # tickers doang gak punya Open, makanya dulu ketipu ONL!
    prices24h={}
    tickers_data=None
    try:
        s=requests.get("https://indodax.com/api/summaries", timeout=15).json()
        # summaries bisa format: {"tickers": {...}, "prices_24h": {...}} atau {"tickers":..., "prices24h":...}
        tickers_data=s.get('tickers') or s.get('ticker') or {}
        prices24h=s.get('prices24h') or s.get('prices_24h') or s.get('prices24') or {}
        # prices24h format bisa: {"btc_idr": 123} atau {"btc": 123}
    except: pass
    if not tickers_data:
        try:
            tickers_data=requests.get("https://indodax.com/api/tickers", timeout=15).json()['tickers']
        except: return []
    cg_chg=get_coingecko_chg()
    out=[]
    for pair,d in tickers_data.items():
        if not pair.endswith('_idr'): continue
        if pair in BLACKLIST: continue
        try:
            if float(d['vol_idr'])<15_000_000: continue
            last=float(d['last']); low=float(d['low']); high=float(d['high']); vol=float(d['vol_idr'])
        except: continue
        if last==0 or low==0 or high==low: continue
        pos=((last-low)/(high-low)*100) if high!=low else 0
        # PANTULAN = dari Low! Bukan Naik!
        pantulan=((last-low)/low*100) if low!=0 else 0
        # NAIK 24H YANG BENER = dari harga 24 jam lalu!
        sym=pair.replace('_idr','').upper()
        p24=None
        if pair in prices24h:
            try: p24=float(prices24h[pair])
            except: p24=None
        if p24 is None and sym.lower() in prices24h:
            try: p24=float(prices24h[sym.lower()])
            except: p24=None
        if p24 and p24>0:
            naik24h=(last-p24)/p24*100
        else:
            # Fallback ke CoinGecko kalo summaries gak kasih prices24h
            naik24h=cg_chg.get(sym, 0)
        out.append({'pair':pair,'sym':sym,'last':last,'low':low,'high':high,'vol':vol,'pos':pos,'pantulan':pantulan,'naik24h':naik24h})
    return out

def get_global():
    g={}; src={}
    def upd(sym, val, name):
        try: val=float(val)
        except: return
        key=sym.lower()+'_idr'
        if val>g.get(key,-100): g[key]=val; src[key]=name
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
        sym=t['sym']; price=t['last']; low=t['low']; pantulan=t['pantulan']; naik24h=t['naik24h']; pos=t['pos']; vol=t['vol']
        gp=gdata.get(t['pair'],0); gname=gsrc.get(t['pair'],"-")
        # Vol history 3 jam - anti crash!
        hist=vol_hist.get(t['pair'],[])
        if not isinstance(hist, list): hist=[]
        hist=[e for e in hist if isinstance(e, dict) and now_ts-e.get("ts",0)<4*3600]
        vol_3h=get_vol_3h(hist, now_ts)
        if vol_3h: hist_kosong=False
        vol_ratio=(vol/vol_3h) if vol_3h and vol_3h>0 else 0
        hist.append({"ts": now_ts, "vol": vol}); new_vol[t['pair']]=hist
        # === TIER 2 PANTAU DULU! Biar yang udah terbang gak masuk AKUMULASI! ===
        # Udah terbang = Naik24h >=40% ATAU Pantulan >=10% + Pos >=60%
        if naik24h>=40 or (pantulan>=10 and pos>=60):
            retest_low=price*0.70; retest_high=price*0.80
            tier_pantau.append((naik24h, f"👀 PANTAU [UDAH PUMP - JANGAN KEJAR]! | {sym} Rp{price:.0f} | Naik24h {naik24h:.1f}% Pantulan {pantulan:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}% [{gname}] | TUNGGU RETEST {retest_low:.0f}-{retest_high:.0f} | Kalo beli sekarang = jadi ONL -72%!"))
            continue
        # === TIER 1 AKUMULASI - BANDAR LAGI KUMPUL, MAU RUNNING! ===
        # Syarat ketat! Biar ONL yang -26% gak lolos!
        # 1. Naik24h harus di -5% sampai +5%! Kalo -26% berarti lagi jatuh! BUKAN akumulasi!
        # 2. Pantulan 0-3%! Masih nempel Low!
        # 3. Pos 15-45%! Masih di bawah!
        # 4. Vol 3J naik >=2.5x ATAU Vol Indo >=100Mn (bandar global via Indo langsung)!
        # 5. Global belum terbang (<5%)!
        if -5<=naik24h<=5 and 0<=pantulan<=3.0 and 15<=pos<=45 and gp<5:
            entry_low=low*1.01; entry_high=low*1.03
            target=entry_high*1.10; cut=low*0.995
            if vol_ratio>=2.5 and vol>=30_000_000:
                tier_akumulasi.append(f"🔥 AKUMULASI [BANDAR INDO 3J]! | {sym} Rp{price:.0f} | Naik24h {naik24h:.1f}% Pantulan {pantulan:.1f}% Pos {pos:.0f}% | Vol 3J Naik {vol_ratio:.1f}x ({vol/1e6:.0f}Mn vs {vol_3h/1e6:.0f}Mn) | Global {gp:.1f}% [{gname}] | ENTRY {entry_low:.0f}-{entry_high:.0f} | TARGET {target:.0f} | CUT {cut:.0f} | BANDAR LAGI KUMPUL!")
                continue
            if vol>=100_000_000:
                tier_akumulasi.append(f"🌍 AKUMULASI [BANDAR GLOBAL VIA INDO]! | {sym} Rp{price:.0f} | Naik24h {naik24h:.1f}% Pantulan {pantulan:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn GEDE! | Global {gp:.1f}% [{gname}] | ENTRY {entry_low:.0f}-{entry_high:.0f} | TARGET {target:.0f} | CUT {cut:.0f} | INDO VOL GEDE, BELUM TERBANG!")
                continue
    save_json(VOL_FILE, new_vol)
    # Urutin PANTAU dari Naik24h paling gede!
    tier_pantau_sorted=[x[1] for x in sorted(tier_pantau, key=lambda x: x[0], reverse=True)]
    msg=f"=== V37 RECOVERY {now} - {len(tickers)} KOINS ===\n"
    if hist_kosong:
        msg+=f"⚠️ History baru! Vol 3J belum valid! Tunggu 3 jam biar Vol 3J keisi! AKUMULASI 3J mungkin kosong dulu, wajar!\n\n"
    msg+=f"🔥 AKUMULASI [BANDAR LAGI KUMPUL - MAU TERBANG - INI YANG DIBELI]:\n"+("\n".join(tier_akumulasi[:8]) if tier_akumulasi else "Belum ada akumulasi - Bandar belum kumpul / Market kalem")+"\n\n"
    msg+=f"👀 PANTAU [UDAH PUMP - JANGAN KEJAR - CUMA DIPANTAU]:\n"+("\n".join(tier_pantau_sorted[:8]) if tier_pantau_sorted else "Belum ada yang pump - Market kalem")+"\n\n"
    msg+=f"📌 Cara baca: Naik24h = dari harga 24 jam lalu (summaries)! Pantulan = dari Low hari ini! Kalo Naik24h -26% tapi Pantulan +9%, itu lagi JATUH, bukan naik!\n"
    return msg

if __name__=="__main__":
    send_tele(scan())
