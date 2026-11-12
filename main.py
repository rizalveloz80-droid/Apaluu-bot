# === V28.4 - INDODAX LANGSUNG + COINGECKO + COINGLASS + TIER PUMP CEPET ===
# V28.4 = V28.3 + TIER PUMP CEPET (BUAT KOIN VOLATIL KAYAK UAI!) + BANDAR GLOBAL VIA INDODAX LANGSUNG!
# TIER PUMP CEPET = Koin baru meledak 10-25% dalam 15 menit / hari ini! KASIH TAU AWAL, JANGAN SAMPE TAU BESOK!
# BANDAR GLOBAL VIA INDODAX = Gak ngandelin 6EX doang! Kalo Vol Indodax udah >=100Mn + Naik gede, itu udah bandar global!
# FIX V28.4.1: phist / hist yang ke-save jadi str gak bikin crash lagi! Udah dikasih isinstance(e, dict)!
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
PRICE_FILE = "price_history.json"
def load_json(f):
    if os.path.exists(f):
        try:
            d = json.load(open(f))
            if isinstance(d, dict):
                return d
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

def get_price_15m(hist_list, now_ts):
    best=None; best_diff=999999
    for e in hist_list:
        if not isinstance(e, dict): continue
        age=now_ts-e.get("ts",0)
        if 10*60<=age<=20*60:
            diff=abs(age-15*60)
            if diff<best_diff:
                best_diff=diff; best=e.get("price",0)
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

def get_coingecko():
    out={}
    try:
        r=requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=1&sparkline=false", timeout=12).json()
        for x in r:
            sym=x['symbol'].upper(); mcap=x.get('market_cap') or 0; vol24=x.get('total_volume') or 0
            if mcap>0: out[sym]={'mcap':mcap,'vol24':vol24,'turnover':vol24/mcap}
        r2=requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=2&sparkline=false", timeout=12).json()
        for x in r2:
            sym=x['symbol'].upper(); mcap=x.get('market_cap') or 0; vol24=x.get('total_volume') or 0
            if mcap>0 and sym not in out: out[sym]={'mcap':mcap,'vol24':vol24,'turnover':vol24/mcap}
    except: pass
    return out

def get_oi_change(sym):
    try:
        r=requests.get(f"https://fapi.binance.com/futures/data/openInterestHist?symbol={sym}USDT&period=1h&limit=25", timeout=6).json()
        if isinstance(r, list) and len(r)>=2:
            first=float(r[0]['sumOpenInterest']); last=float(r[-1]['sumOpenInterest'])
            if first>0: return (last-first)/first*100
    except: pass
    return None

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
    vol_hist=load_json(VOL_FILE)
    price_hist=load_json(PRICE_FILE)
    new_vol={}; new_price={}
    tickers=get_tickers()
    gdata, gsrc=get_global()
    cg=get_coingecko()
    tier_0=[]; tier_bandar3=[]; tier_bandar_v20=[]; tier_global6=[]; tier_bullish=[]; tier_pump=[]
    seen=set(); oi_cache={}
    for t in tickers:
        sym=t['sym']; price=t['last']; low=t['low']; naik=t['naik']; pos=t['pos']; vol=t['vol']
        gp=gdata.get(t['pair'],0); gname=gsrc.get(t['pair'],"-")
        # Vol history 3 jam
        hist=vol_hist.get(t['pair'],[])
        if not isinstance(hist, list): hist=[]
        hist=[e for e in hist if isinstance(e, dict) and now_ts-e.get("ts",0)<4*3600]
        vol_3h=get_vol_3h(hist, now_ts)
        vol_ratio=(vol/vol_3h) if vol_3h and vol_3h>0 else 0
        hist.append({"ts": now_ts, "vol": vol}); new_vol[t['pair']]=hist
        # Price history 15 menit - BUAT NANGKEP POMPA VERTIKAL KAYAK UAI!
        phist=price_hist.get(t['pair'],[])
        if not isinstance(phist, list): phist=[]
        phist=[e for e in phist if isinstance(e, dict) and now_ts-e.get("ts",0)<30*60]
        price_15m=get_price_15m(phist, now_ts)
        pump_15m=((price-price_15m)/price_15m*100) if price_15m and price_15m>0 else 0
        phist.append({"ts": now_ts, "price": price}); new_price[t['pair']]=phist
        if naik<0.3: continue
        ob_low,ob_high,ent_low,ent_high,ent_type=detect_ob(t)
        ob_txt=f"OB {ob_low:.0f}-{ob_high:.0f}"; entry_txt=f"{ent_low:.0f}-{ent_high:.0f} {ent_type}"; global_txt=f"Global {gp:.1f}% [{gname}]"
        # === 0. TIER 0 LONGGAR ===
        cg_data=cg.get(sym)
        if cg_data and vol>=30_000_000 and 0<=naik<=5.0 and 15<=pos<=50:
            mcap=cg_data['mcap']; turnover=cg_data['turnover']; vol24=cg_data['vol24']
            if mcap<=50_000_000 and turnover>=0.7:
                if sym not in oi_cache: oi_cache[sym]=get_oi_change(sym)
                oi_chg=oi_cache[sym]
                if oi_chg is not None and oi_chg>=10.0:
                    if t['pair'] not in seen:
                        tier_0.append(f"🔥 TIER 0 [OI IGNITION]! | {sym} Rp{price:.0f} | Mcap ${mcap/1e6:.1f}Mn Turnover {turnover*100:.0f}% OI +{oi_chg:.1f}% | Indo Vol {vol/1e6:.0f}Mn Harga {naik:.1f}% Pos {pos:.0f}% | {global_txt} | {ob_txt} | GILA! BANDAR UDAH MASUK!")
                        seen.add(t['pair'])
                    continue
        # === 0.5 TIER PUMP CEPET - BARU! BUAT KOIN VOLATIL KAYAK UAI! ===
        # Kalo dalam 15 menit naik >=8% ATAU hari ini naik 10-40% + Vol gede, kasih tau! JANGAN BELI, TUNGGU RETEST!
        if (pump_15m>=8.0 or (10<=naik<=40 and vol>=100_000_000)) and pos>=60:
            if t['pair'] not in seen:
                retest_low=price*0.85; retest_high=price*0.92
                tier_pump.append(f"⚡ PUMP CEPET [VOLATIL]! | {sym} Rp{price:.0f} | Naik Hari Ini {naik:.1f}% | Pump 15Menit +{pump_15m:.1f}% | Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {global_txt} | JANGAN KEJAR! TUNGGU RETEST {retest_low:.0f}-{retest_high:.0f} | INI TIPE UAI! BISA +50% BISA DUMP!")
                seen.add(t['pair'])
            continue
        # === 1. BANDAR INDODAX 3JAM ===
        if vol_ratio>=2.5 and 0<=naik<=3.0 and 15<=pos<=45 and vol>=30_000_000:
            if t['pair'] not in seen:
                tier_bandar3.append(f"👑 BANDAR INDO 3JAM! | {sym} Rp{price:.0f} | Vol 3J Naik {vol_ratio:.1f}x ({vol/1e6:.0f}Mn vs {vol_3h/1e6:.0f}Mn) | Harga {naik:.1f}% Pos {pos:.0f}% | {global_txt} | OB {ob_low:.0f}-{ob_high:.0f} | MASUK SEBELUM TERBANG!")
                seen.add(t['pair'])
            continue
        # === 2. BANDAR INDODAX V20 ===
        if vol_ratio>=2.5 and 3.0<naik<=15.0 and 15<=pos<=65 and vol>=30_000_000:
            if t['pair'] not in seen:
                tier_bandar_v20.append(f"👀 BANDAR INDO V20! | {sym} Rp{price:.0f} | Vol 3J Naik {vol_ratio:.1f}x | Harga {naik:.1f}% Pos {pos:.0f}% | {global_txt} | OB {ob_low:.0f}-{ob_high:.0f} | UDAH JALAN, WATCHLIST!")
                seen.add(t['pair'])
            continue
        # === 3. BANDAR GLOBAL VIA INDODAX LANGSUNG + 6EX - BARU! ===
        # Dulu cuma ngandelin 6EX! Sekarang kalo Vol Indo udah >=100Mn + Naik 0-3% + Pos rendah, itu udah bandar global! Gak perlu nunggu 6EX!
        if vol>=100_000_000 and 0.3<=naik<=3.0 and pos<=45:
            if t['pair'] not in seen:
                tier_global6.append(f"🌍 BANDAR GLOBAL [INDODAX LANGSUNG]! | {sym} Rp{price:.0f} | {global_txt} | Indo {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn (GEDE BANGET! LANGSUNG DARI INDODAX!) | ENTRY {entry_txt} | {ob_txt} | GLOBAL / INDO UDAH GAS, INDO BELUM TERBANG!")
                seen.add(t['pair'])
            continue
        if gp>=3.0 and 0.3<=naik<=3.0 and pos<=45 and vol>=30_000_000:
            if t['pair'] not in seen:
                tier_global6.append(f"🌍 BANDAR 6EX! | {sym} Rp{price:.0f} | {global_txt} | Indo {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | ENTRY {entry_txt} | {ob_txt} | GLOBAL UDAH GAS, INDO BELUM!")
                seen.add(t['pair'])
            continue
        # === 4. BULLISH GLOBAL ===
        if gp>=5.0 and 3.0<naik<=15.0 and 15<=pos<=65 and vol>=30_000_000 and vol_ratio<2.5:
            if t['pair'] not in seen:
                tier_bullish.append(f"📈 BULLISH GLOBAL! | {sym} Rp{price:.0f} | {global_txt} | Indo {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | ENTRY {entry_txt} | {ob_txt} | IKUT GLOBAL!")
                seen.add(t['pair'])
            continue
    save_json(VOL_FILE, new_vol); save_json(PRICE_FILE, new_price)
    msg=f"=== V28.4 + PUMP CEPET + INDODAX LANGSUNG {now} - {len(tickers)} KOINS ===\n"
    msg+=f"🔥 TIER 0 [OI IGNITION]:\n"+("\n".join(tier_0[:8]) if tier_0 else "Belum ada Tier 0")+"\n\n"
    msg+=f"⚡ PUMP CEPET [VOLATIL - TIPE UAI] - JANGAN KEJAR, TUNGGU RETEST!:\n"+("\n".join(tier_pump[:8]) if tier_pump else "Belum ada pump cepet - Market kalem")+"\n\n"
    msg+=f"👑 BANDAR INDO 3JAM:\n"+("\n".join(tier_bandar3[:8]) if tier_bandar3 else "Belum ada bandar Indo 3J")+"\n\n"
    msg+=f"👀 BANDAR INDO V20:\n"+("\n".join(tier_bandar_v20[:8]) if tier_bandar_v20 else "Belum ada bandar V20")+"\n\n"
    msg+=f"🌍 BANDAR GLOBAL [INDODAX LANGSUNG + 6EX]:\n"+("\n".join(tier_global6[:8]) if tier_global6 else "Belum ada bandar global")+"\n\n"
    msg+=f"📈 BULLISH GLOBAL:\n"+("\n".join(tier_bullish[:8]) if tier_bullish else "Belum ada bullish global")+"\n\n"
    return msg

if __name__=="__main__":
    send_tele(scan())
