# === V28.3 SIMPEL - INDODAX + COINGECKO + COINGLASS (BINANCE OI) + 6EX ===
# V28.3 = V28.2 + TIER 0 LONGGAR + BANDAR INDO 3 JAM
# TIER 0 LONGGAR = Mcap <=50Mn + Turnover >=70% + OI >=10% + Vol Indo >=30Mn + Naik 0-5%
# BANDAR INDO 3JAM = Vol 3J Naik >=2.5x (CEPPET! GAK USAH NUNGGU 6 JAM!)
import requests, os, json, time
from datetime import datetime
import pytz

TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID') or os.getenv('CHAT_ID')
WIB = pytz.timezone('Asia/Jakarta')

# === BLACKLIST - TOTAL 102 - JANGAN DIUBAH! ===
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
def load_vol():
    if os.path.exists(VOL_FILE):
        try: return json.load(open(VOL_FILE))
        except: return {}
    return {}
def save_vol(d):
    try: json.dump(d, open(VOL_FILE, "w"))
    except: pass
def get_vol_3h(hist_list, now_ts):
    best=None; best_diff=999999
    for e in hist_list:
        age=now_ts-e.get("ts",0)
        # V28.3: Cari data 2.5 - 3.5 jam lalu, target 3 jam!
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
    r=requests.get("https://indodax.com/api/tickers", timeout=15).json()['tickers']
    out=[]
    for pair,d in r.items():
        if not pair.endswith('_idr'): continue
        if pair in BLACKLIST: continue
        if float(d['vol_idr'])<15_000_000: continue
        last=float(d['last']); low=float(d['low']); high=float(d['high']); vol=float(d['vol_idr'])
        if last==0 or low==0 or high==low: continue
        pos=((last-low)/(high-low)*100) if high!=low else 0
        naik=((last-low)/low*100) if low!=0 else 0
        out.append({'pair':pair,'sym':pair.replace('_idr','').upper(),'last':last,'low':low,'high':high,'vol':vol,'pos':pos,'naik':naik})
    return out

# === COINGECKO - MCAP + V24H GLOBAL ===
def get_coingecko():
    out={}
    try:
        r=requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=1&sparkline=false", timeout=12).json()
        for x in r:
            sym=x['symbol'].upper()
            mcap=x.get('market_cap') or 0
            vol24=x.get('total_volume') or 0
            if mcap>0:
                out[sym]={'mcap':mcap,'vol24':vol24,'turnover':vol24/mcap}
        r2=requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=2&sparkline=false", timeout=12).json()
        for x in r2:
            sym=x['symbol'].upper()
            mcap=x.get('market_cap') or 0
            vol24=x.get('total_volume') or 0
            if mcap>0 and sym not in out:
                out[sym]={'mcap':mcap,'vol24':vol24,'turnover':vol24/mcap}
    except: pass
    return out

# === COINGLASS VIA BINANCE FUTURES OI ===
def get_oi_change(sym):
    try:
        r=requests.get(f"https://fapi.binance.com/futures/data/openInterestHist?symbol={sym}USDT&period=1h&limit=25", timeout=6).json()
        if isinstance(r, list) and len(r)>=2:
            first=float(r[0]['sumOpenInterest'])
            last=float(r[-1]['sumOpenInterest'])
            if first>0:
                return (last-first)/first*100
    except: pass
    return None

# === GLOBAL 6EX ===
def get_global():
    g={}; src={}
    def upd(sym, val, name):
        try: val=float(val)
        except: return
        key=sym.lower()+'_idr'
        if val>g.get(key,-100):
            g[key]=val; src[key]=name
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

def detect_ob(t):
    low=t['low']; last=t['last']; pos=t['pos']
    if pos>25:
        ent_low=last*0.93; ent_high=last*0.97; ent_type="RETEST"
    else:
        ent_low=low*1.01; ent_high=low*1.03; ent_type="OB REAL"
    return low*0.995, low*1.03, ent_low, ent_high, ent_type

def scan():
    now=datetime.now(WIB).strftime("%H:%M WIB")
    now_ts=int(time.time())
    vol_hist=load_vol()
    new_hist={}
    tickers=get_tickers()
    gdata, gsrc=get_global()
    cg=get_coingecko()
    tier_0=[]; tier_bandar3=[]; tier_bandar_v20=[]; tier_global6=[]; tier_bullish=[]
    seen=set()
    oi_cache={}
    for t in tickers:
        sym=t['sym']; price=t['last']; low=t['low']; naik=t['naik']; pos=t['pos']; vol=t['vol']
        gp=gdata.get(t['pair'],0); gname=gsrc.get(t['pair'],"-")
        hist=vol_hist.get(t['pair'],[])
        # V28.3: Simpan cuma 4 jam terakhir aja, biar file gak gede!
        hist=[e for e in hist if now_ts-e.get("ts",0)<4*3600]
        vol_3h=get_vol_3h(hist, now_ts)
        vol_ratio=(vol/vol_3h) if vol_3h and vol_3h>0 else 0
        hist.append({"ts": now_ts, "vol": vol})
        new_hist[t['pair']]=hist
        if naik<0.3: continue
        ob_low,ob_high,ent_low,ent_high,ent_type=detect_ob(t)
        ob_txt=f"OB {ob_low:.0f}-{ob_high:.0f}"; entry_txt=f"{ent_low:.0f}-{ent_high:.0f} {ent_type}"; global_txt=f"Global {gp:.1f}% [{gname}]"
        # === 0. TIER 0 LONGGAR - POLA TEMEN LU VERSI LONGGAR! ===
        cg_data=cg.get(sym)
        if cg_data and vol>=30_000_000 and 0<=naik<=5.0 and 15<=pos<=50:
            mcap=cg_data['mcap']; turnover=cg_data['turnover']; vol24=cg_data['vol24']
            if mcap<=50_000_000 and turnover>=0.7:  # LONGGAR! Mcap 50Mn + Turnover 70%!
                if sym not in oi_cache:
                    oi_cache[sym]=get_oi_change(sym)
                oi_chg=oi_cache[sym]
                if oi_chg is not None and oi_chg>=10.0:  # LONGGAR! OI 10%!
                    if t['pair'] not in seen:
                        tier_0.append(f"🔥 TIER 0 [OI IGNITION]! | {sym} Rp{price:.0f} | Mcap ${mcap/1e6:.1f}Mn Vol24 ${vol24/1e6:.1f}Mn Turnover {turnover*100:.0f}% | OI +{oi_chg:.1f}% | Indo Vol {vol/1e6:.0f}Mn Harga {naik:.1f}% Pos {pos:.0f}% | {global_txt} | {ob_txt} | GILA! BANDAR UDAH MASUK!")
                        seen.add(t['pair'])
                    continue
        # === 1. BANDAR INDODAX 3JAM - BARU MASUK! ===
        if vol_ratio>=2.5 and 0<=naik<=3.0 and 15<=pos<=45 and vol>=30_000_000:
            if t['pair'] not in seen:
                tier_bandar3.append(f"👑 BANDAR INDO 3JAM! | {sym} Rp{price:.0f} | Vol 3J Naik {vol_ratio:.1f}x ({vol/1e6:.0f}Mn vs {vol_3h/1e6:.0f}Mn) | Harga {naik:.1f}% Pos {pos:.0f}% | {global_txt} | OB {ob_low:.0f}-{ob_high:.0f} | MASUK SEBELUM TERBANG!")
                seen.add(t['pair'])
            continue
        # === 2. BANDAR INDODAX V20 - UDAH JALAN! ===
        if vol_ratio>=2.5 and 3.0<naik<=15.0 and 15<=pos<=65 and vol>=30_000_000:
            if t['pair'] not in seen:
                tier_bandar_v20.append(f"👀 BANDAR INDO V20! | {sym} Rp{price:.0f} | Vol 3J Naik {vol_ratio:.1f}x | Harga {naik:.1f}% Pos {pos:.0f}% | {global_txt} | OB {ob_low:.0f}-{ob_high:.0f} | UDAH JALAN, WATCHLIST!")
                seen.add(t['pair'])
            continue
        # === 3. BANDAR 6EX ===
        if gp>=3.0 and 0.3<=naik<=3.0 and pos<=45 and vol>=30_000_000:
            if t['pair'] not in seen:
                tier_global6.append(f"🌍 BANDAR 6EX! | {sym} Rp{price:.0f} | {global_txt} | Indo {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | ENTRY {entry_txt} | {ob_txt} | GLOBAL UDAH GAS, INDO BELUM!")
                seen.add(t['pair'])
            continue
        # === 4. BULLISH GLOBAL ===
        if gp>=5.0 and 3.0<naik<=15.0 and 15<=pos<=65 and vol>=30_000_000 and vol_ratio<2.5:
            if t['pair'] not in seen:
                tier_bullish.append(f"📈 BULLISH GLOBAL! | {sym} Rp{price:.0f} | {global_txt} | Indo {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn (Vol Indo biasa, bukan bandar lokal!) | ENTRY {entry_txt} | {ob_txt} | IKUT GLOBAL!")
                seen.add(t['pair'])
            continue
    save_vol(new_hist)
    msg=f"=== V28.3 + TIER 0 LONGGAR + 3JAM {now} - {len(tickers)} KOINS ===\n"
    msg+=f"🔥 TIER 0 [OI IGNITION] - MCAP <=50Mn + TURNOVER >=70% + OI >=10%!:\n"+("\n".join(tier_0[:8]) if tier_0 else "Belum ada Tier 0 - Mcap/OI masih kalem")+"\n\n"
    msg+=f"👑 BANDAR INDO 3JAM - BANDAR LOKAL BARU MASUK!:\n"+("\n".join(tier_bandar3[:8]) if tier_bandar3 else "Belum ada bandar Indo 3J - Vol masih sepi")+"\n\n"
    msg+=f"👀 BANDAR INDO V20 UDAH JALAN!:\n"+("\n".join(tier_bandar_v20[:8]) if tier_bandar_v20 else "Belum ada bandar V20")+"\n\n"
    msg+=f"🌍 BANDAR 6EX - GLOBAL GAS, INDO BELUM!:\n"+("\n".join(tier_global6[:8]) if tier_global6 else "Belum ada bandar 6EX")+"\n\n"
    msg+=f"📈 BULLISH GLOBAL - BULLISH TAPI BUKAN BANDAR LOKAL!:\n"+("\n".join(tier_bullish[:8]) if tier_bullish else "Belum ada bullish global")+"\n\n"
    return msg

if __name__=="__main__":
    send_tele(scan())
