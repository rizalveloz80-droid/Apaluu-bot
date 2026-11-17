# === V39 FINAL - BANDAR INDODAX + BANDAR GLOBAL 6EX ===
# V39 = V38 + BANDAR GLOBAL 6EX! V38 cuma Bandar Indo, V39 ada 2 bandar!
# 9EX Global: BINANCE BYBIT GATE KUCOIN BITGET MEXC OKX HTX COINBASE
# FIX: Vol >=100Mn biar VELODROME/NBT gak muncul!
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
    'ondo_idr','hot_idr','sui_idr','dodo_idr','bome_idr','nom_idr','mpro_idr','amp_idr','unmd_idr','kdag_idr',
    'bsv_idr','vet_idr','fil_idr','eos_idr','xtz_idr','neo_idr','aave_idr','comp_idr','mkr_idr','snx_idr','yfi_idr','mana_idr','axs_idr','slp_idr','chz_idr','enj_idr',
    'flow_idr','icp_idr','near_idr','egld_idr','hbar_idr','algo_idr','ftm_idr','one_idr','klay_idr','celo_idr','rvn_idr',
    'ena_idr','hype_idr','pippin_idr','pengu_idr','fanc_idr','mog_idr','edena_idr',
}
VOL_FILE="vol_history.json"; PRICE_FILE="price_history.json"
def load_json(f):
    if os.path.exists(f):
        try:
            d=json.load(open(f)); return d if isinstance(d,dict) else {}
        except: return {}
    return {}
def save_json(f,d):
    try: json.dump(d, open(f,"w"))
    except: pass
def get_vol_6h(hist_list, now_ts):
    best=None; best_diff=999999
    if not isinstance(hist_list, list): return None
    for e in hist_list:
        if not isinstance(e, dict): continue
        age=now_ts-e.get("ts",0)
        if 5*3600<=age<=7*3600:
            diff=abs(age-6*3600)
            if diff<best_diff: best_diff=diff; best=e.get("vol",0)
    return best
def send_tele(msg):
    print(msg); msg=msg[:3800]
    try: requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", json={"chat_id": TELE_CHAT_ID, "text": msg}, timeout=20)
    except: pass
def get_tickers():
    try: r=requests.get("https://indodax.com/api/tickers", timeout=15).json()['tickers']
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
        naik=((last-low)/low*100) if low!=0 else 0
        out.append({'pair':pair,'sym':pair.replace('_idr','').upper(),'last':last,'low':low,'high':high,'vol':vol,'pos':pos,'naik':naik})
    return out
def get_global():
    g={}; src={}
    def upd(sym, val, name):
        try: val=float(val)
        except: return
        key=sym.lower()+'_idr'
        if val>g.get(key,-100): g[key]=val; src[key]=name
    h={"User-Agent":"Mozilla/5.0"}
    # === 6EX UTAMA BANDAR GLOBAL ===
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
    # === 3EX TAMBAHAN ===
    try:
        r=requests.get("https://www.okx.com/api/v5/market/tickers?instType=SPOT",timeout=6,headers=h).json()
        for x in r.get('data',[]):
            if x.get('instId','').endswith('-USDT'):
                sym=x['instId'].replace('-USDT','')
                try:
                    last=float(x['last']); open24=float(x.get('open24h',0))
                    if open24>0: upd(sym, (last-open24)/open24*100, "OKX")
                    else: upd(sym, float(x.get('chgUtc8',0))*100, "OKX")
                except: pass
    except: pass
    try:
        r=requests.get("https://api.huobi.pro/market/tickers",timeout=6,headers=h).json()
        for x in r.get('data',[]):
            s=x.get('symbol','')
            if s.endswith('usdt'):
                sym=s.replace('usdt','')
                try:
                    close=float(x['close']); open24=float(x['open'])
                    if open24>0: upd(sym, (close-open24)/open24*100, "HTX")
                except: pass
    except: pass
    try:
        r=requests.get("https://api.coinbase.com/v2/assets/prices?base=USD",timeout=6,headers=h).json()
        for x in r.get('data',[]):
            sym=x.get('base',''); ch=x.get('price_percent_change_24h')
            if ch is not None:
                try: upd(sym, float(ch), "COINBASE")
                except: pass
    except: pass
    return g, src
def scan():
    now=datetime.now(WIB).strftime("%H:%M WIB"); now_ts=int(time.time())
    vol_hist=load_json(VOL_FILE); price_hist=load_json(PRICE_FILE)
    new_vol={}; new_price={}
    tickers=get_tickers(); gdata, gsrc=get_global()
    tier_indo=[]; tier_global=[]; tier_early=[]; tier_spike=[]; tier_pantau=[]
    seen=set()
    for t in tickers:
        sym=t['sym']; price=t['last']; low=t['low']; naik=t['naik']; pos=t['pos']; vol=t['vol']
        gp=gdata.get(t['pair'],0); gname=gsrc.get(t['pair'],"-"); gp_txt=f"Global {gp:.1f}% [{gname}]"
        hist=vol_hist.get(t['pair'],[])
        if isinstance(hist, dict): hist=[hist]
        if not isinstance(hist, list): hist=[]
        hist=[e for e in hist if isinstance(e,dict) and now_ts-e.get("ts",0)<7*3600]
        vol_6h=get_vol_6h(hist, now_ts)
        vol_ratio=(vol/vol_6h) if vol_6h and vol_6h>0 else 0
        hist.append({"ts": now_ts, "vol": vol}); new_vol[t['pair']]=hist
        prev=price_hist.get(t['pair'],{})
        if isinstance(prev, list): prev=prev[-1] if prev else {}
        if not isinstance(prev, dict): prev={}
        prev_price=prev.get("price",0); prev_ts=prev.get("ts",0)
        spike_5m=0
        if prev_price and prev_price>0 and 240<=(now_ts-prev_ts)<=420:
            spike_5m=(price-prev_price)/prev_price*100
        new_price[t['pair']]={"ts": now_ts, "price": price}
        if pos>25:
            ent_low=price*0.93; ent_high=price*0.97; ent_txt=f"{ent_low:.0f}-{ent_high:.0f} RETEST"
        else:
            ent_low=low*1.01; ent_high=low*1.03; ent_txt=f"{ent_low:.0f}-{ent_high:.0f} OB REAL"
        cut=low*0.995; target=ent_high*1.10
        # === PANTAU ===
        if (gp>=40) or (naik>=10 and pos>=60):
            if t['pair'] not in seen:
                tier_pantau.append(f"👀 PANTAU! | {sym} Rp{price:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {gp_txt} | TUNGGU {price*0.70:.0f}-{price*0.80:.0f} | UDAH TERBANG!")
                seen.add(t['pair'])
            continue
        # === SPIKE 5M ===
        if spike_5m>=4.0 and vol>=100_000_000:
            if t['pair'] not in seen:
                tier_spike.append(f"⚡ SPIKE 5M! | {sym} Rp{price:.0f} | +{spike_5m:.1f}% 5mnt | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {gp_txt} | ENTRY {ent_txt} | CUT {cut:.0f} | TARGET {target:.0f} | JANGAN KEJAR PUCUK!")
                seen.add(t['pair'])
            continue
        # === BANDAR INDODAX - V33.8 ===
        if vol_ratio>=2.5 and 0<=naik<=3.0 and 15<=pos<=45 and vol>=100_000_000:
            if t['pair'] not in seen:
                tier_indo.append(f"👑 BANDAR INDODAX! | {sym} Rp{price:.0f} | Vol 6J {vol_ratio:.1f}x ({vol/1e6:.0f}Mn vs {vol_6h/1e6:.0f}Mn) | Naik {naik:.1f}% Pos {pos:.0f}% | {gp_txt} | ENTRY {ent_txt} | CUT {cut:.0f} | TARGET {target:.0f} | MASUK SEBELUM TERBANG!")
                seen.add(t['pair'])
            continue
        # === BANDAR GLOBAL 6EX - INI YANG BARU! ===
        if gp>=3.0 and 0.3<=naik<=8.0 and pos<=50 and vol>=100_000_000:
            if t['pair'] not in seen:
                tier_global.append(f"🌍 BANDAR GLOBAL 6EX! | {sym} Rp{price:.0f} | Indo {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {gp_txt} | ENTRY {ent_txt} | CUT {cut:.0f} | TARGET {target:.0f} | GLOBAL UDAH GAS, INDODAX BELUM!")
                seen.add(t['pair'])
            continue
        # === EARLY RUNNER ===
        if 5<=naik<=15 and 15<=pos<=45 and vol>=100_000_000:
            if t['pair'] not in seen:
                tier_early.append(f"🏃 EARLY RUNNER! | {sym} Rp{price:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {gp_txt} | ENTRY {ent_txt} | CUT {cut:.0f} | TARGET {target:.0f} | GAS!")
                seen.add(t['pair'])
            continue
    save_json(VOL_FILE, new_vol); save_json(PRICE_FILE, new_price)
    msg=f"=== V39 FINAL - INDO + GLOBAL 6EX {now} - {len(tickers)} KOINS ===\n"
    msg+=f"👑 BANDAR INDODAX [DIBELI]:\n"+("\n".join(tier_indo[:8]) if tier_indo else "Belum ada bandar Indo")+"\n\n"
    msg+=f"🌍 BANDAR GLOBAL 6EX [DIBELI]:\n"+("\n".join(tier_global[:8]) if tier_global else "Belum ada bandar Global")+"\n\n"
    msg+=f"🏃 EARLY RUNNER [CADANGAN]:\n"+("\n".join(tier_early[:8]) if tier_early else "Belum ada early runner")+"\n\n"
    msg+=f"⚡ SPIKE 5M [JANGAN KEJAR]:\n"+("\n".join(tier_spike[:8]) if tier_spike else "Belum ada spike")+"\n\n"
    msg+=f"👀 PANTAU [UDAH PUMP]:\n"+("\n".join(tier_pantau[:8]) if tier_pantau else "Belum ada yang pump")+"\n\n"
    return msg
if __name__=="__main__":
    send_tele(scan())
