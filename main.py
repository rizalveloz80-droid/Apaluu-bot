# === V49 FINAL - FULL 4 TIPE - HTX DIBUANG! SALIN FULL! BUKAN V50! ===
# TIPE 1: RETEST OB! GAS AWAL V29.9 | PUMP CEPET V29.9 | TOP 5 V30.10 | BULLISH GLOBAL V30.10 | BANDAR INDO V30.10 | PUMP BAHAYA V44 FIX | GAP V19.1b BEAM + OB REAL vs RETEST + NEW!
# TIPE 2: BREAKOUT RETEST! BUAT KOIN VOL GEDE! Naik 10-40% + Pos 50-75% + Vol >=1 Miliar + +15m >0,5%! Contoh: PIEVERSE!
# TIPE 3: OI + MARKET CAP! BUAT KOIN OI NAIK! OI 1J >3% + Market Cap Naik + Global Naik + Indo Naik! Contoh: ICNT!
# TIPE 4: GLOBAL LEAD - INDO LAG! BUAT KOIN KECIL GLOBAL GEDE! Global >=20% + GAP >5% + Prem <10% + Naik 10-40% + Vol 20Mn-500Mn! UMUM! BUKAN KHUSUS 1 KOIN!
# FIX: HTX DIBUANG! HTX NIPU VVV 904% + PIEVERSE 902%! FILTER Global >100% DIBUANG!
# LYFEL BALIK! NVDAX DIBUANG! ENTRY TIPE 1=Low*1,01-1,03! ENTRY TIPE 2,3,4=Harga Sekarang! CUT 3-5%! TP1 10% TP2 25%! MODAL 200rb! 2 JAM! Bot tiap 5 menit!
import requests, os, json, time
from datetime import datetime
import pytz
TELE_TOKEN = os.getenv('TELE_TOKEN')
TELE_CHAT_ID = os.getenv('TELE_CHAT_ID') or os.getenv('CHAT_ID')
WIB = pytz.timezone('Asia/Jakarta')
HOLD_LIST={'btc_idr','uai_idr','qnt_idr','myx_idr','birb_idr','aih_idr','mct_idr','onl_idr','home_idr'}
BLACKLIST={
    'usdt_idr','usdc_idr','dai_idr','busd_idr','usde_idr','paxg_idr','xaut_idr','xaus_idr','eurc_idr','usdp_idr','tusd_idr','gusd_idr','usdd_idr','wbtc_idr','weth_idr','weur_idr',
    'btc_idr','eth_idr','bnb_idr','sol_idr','xrp_idr','ada_idr','doge_idr','trx_idr','dot_idr','matic_idr','avax_idr','link_idr','ltc_idr','bch_idr','etc_idr','xlm_idr','uni_idr',
    'luna_idr','lunc_idr','ftt_idr','ustc_idr','luna2_idr','btt_idr','bttc_idr','dgb_idr','qtum_idr','waves_idr','zrx_idr','omg_idr','bat_idr','ont_idr','iost_idr','sc_idr','zcash_idr','dash_idr','xem_idr','bcd_idr','bcha_idr',
    'shib_idr','pepe_idr','floki_idr','bonk_idr','wif_idr','ern_idr',
    'ondo_idr','hot_idr','sui_idr','bome_idr','nom_idr','mpro_idr','amp_idr','unmd_idr','kdag_idr',
    'bsv_idr','vet_idr','fil_idr','eos_idr','xtz_idr','neo_idr','aave_idr','comp_idr','mkr_idr','snx_idr','yfi_idr','mana_idr','axs_idr','slp_idr','chz_idr',
    'flow_idr','icp_idr','near_idr','egld_idr','hbar_idr','algo_idr','ftm_idr','one_idr','klay_idr','celo_idr','rvn_idr',
    'ena_idr','hype_idr','pengu_idr','fanc_idr','mog_idr','edena_idr',
    'msftx_idr',
}
VOL_FILE="vol_history.json"; PRICE_FILE="price_history.json"; OI_FILE="oi_history.json"
def load_json(f):
    if os.path.exists(f):
        try:
            d=json.load(open(f)); return d if isinstance(d,dict) else {}
        except: return {}
    return {}
def save_json(f,d):
    try: json.dump(d, open(f,"w"))
    except: pass
def get_closest(hist_list, now_ts, target_age):
    best=None; best_diff=999999
    if not isinstance(hist_list, list): return None
    for e in hist_list:
        if not isinstance(e, dict): continue
        age=now_ts-e.get("ts",0)
        diff=abs(age-target_age)
        if diff<best_diff: best_diff=diff; best=e
    if best is None or best_diff>target_age*0.5: return None
    return best
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
        if pair in HOLD_LIST: continue
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
    g={}; src={}; gp_usd={}; has_global=set()
    def upd(sym, val, name, usd_price=None):
        try: val=float(val)
        except: return
        if val>100 or val<-50: return  # FIX HTX! Kalo Global >100% atau <-50%, itu PALSU! Buang! Kayak VVV 904% + PIEVERSE 902%!
        key=sym.lower()+'_idr'
        has_global.add(key)
        if val>g.get(key,-100): g[key]=val; src[key]=name
        if usd_price is not None:
            try: gp_usd[key]=float(usd_price)
            except: pass
    h={"User-Agent":"Mozilla/5.0"}
    try:
        r=requests.get("https://api.bybit.com/v5/market/tickers?category=spot",timeout=6).json()
        for x in r['result']['list']:
            if x['symbol'].endswith('USDT'): upd(x['symbol'].replace('USDT',''), float(x['price24hPcnt'])*100, "BYBIT", x.get('lastPrice'))
    except: pass
    try:
        r=requests.get("https://api.gateio.ws/api/v4/spot/tickers",timeout=6).json()
        for x in r:
            if x['currency_pair'].endswith('_USDT'): upd(x['currency_pair'].replace('_USDT',''), float(x['change_percentage']), "GATE", x.get('last'))
    except: pass
    try:
        r=requests.get("https://api.kucoin.com/api/v1/market/allTickers",timeout=6).json()
        for x in r['data']['ticker']:
            if x['symbol'].endswith('-USDT'): upd(x['symbol'].replace('-USDT',''), float(x['changeRate'])*100, "KUCOIN", x.get('last'))
    except: pass
    try:
        r=requests.get("https://api.bitget.com/api/v2/spot/market/tickers",timeout=6).json()
        for x in r['data']:
            if x['symbol'].endswith('USDT'): upd(x['symbol'].replace('USDT',''), float(x['change24h']), "BITGET", x.get('lastPr'))
    except: pass
    try:
        r=requests.get("https://api.mexc.com/api/v3/ticker/24hr",timeout=6,headers=h).json()
        for x in r:
            if x['symbol'].endswith('USDT'): upd(x['symbol'].replace('USDT',''), float(x['priceChangePercent']), "MEXC", x.get('lastPrice'))
    except: pass
    try:
        r=requests.get("https://data-api.binance.vision/api/v3/ticker/24hr",timeout=6,headers=h).json()
        for x in r:
            if x['symbol'].endswith('USDT'): upd(x['symbol'].replace('USDT',''), float(x['priceChangePercent']), "BINANCE", x.get('lastPrice'))
    except:
        try:
            r=requests.get("https://api.binance.com/api/v3/ticker/24hr",timeout=6,headers=h).json()
            for x in r:
                if x['symbol'].endswith('USDT'): upd(x['symbol'].replace('USDT',''), float(x['priceChangePercent']), "BINANCE", x.get('lastPrice'))
        except: pass
    try:
        r=requests.get("https://www.okx.com/api/v5/market/tickers?instType=SPOT",timeout=6,headers=h).json()
        for x in r.get('data',[]):
            if x.get('instId','').endswith('-USDT'):
                sym=x['instId'].replace('-USDT','')
                try:
                    last=float(x['last']); open24=float(x.get('open24h',0))
                    if open24>0: upd(sym, (last-open24)/open24*100, "OKX", last)
                    else: upd(sym, float(x.get('chgUtc8',0))*100, "OKX", last)
                except: pass
    except: pass
    # HTX DIBUANG! HTX NIPU VVV 904% + PIEVERSE 902%! Gak dipake lagi!
    try:
        r=requests.get("https://api.coinbase.com/v2/assets/prices?base=USD",timeout=6,headers=h).json()
        for x in r.get('data',[]):
            sym=x.get('base',''); ch=x.get('price_percent_change_24h')
            if ch is not None:
                try: upd(sym, float(ch), "COINBASE", x.get('price'))
                except: pass
    except: pass
    return g, src, gp_usd, has_global
def get_oi_mcap():
    oi={}; mcap={}; mcap_chg={}
    try:
        r=requests.get("https://api.bybit.com/v5/market/tickers?category=linear", timeout=8).json()
        for x in r.get('result',{}).get('list',[]):
            s=x.get('symbol','')
            if s.endswith('USDT'):
                try:
                    v=float(x.get('openInterest',0))
                    if v>0: oi[s.replace('USDT','').lower()+'_idr']=v
                except: pass
    except: pass
    try:
        r=requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=1&sparkline=false", timeout=10).json()
        for x in r:
            try:
                k=x.get('symbol','').lower()+'_idr'
                mcap[k]=float(x.get('market_cap',0) or 0)
                mcap_chg[k]=float(x.get('market_cap_change_percentage_24h',0) or 0)
            except: pass
    except: pass
    return oi, mcap, mcap_chg
def scan():
    now=datetime.now(WIB).strftime("%H:%M WIB"); now_ts=int(time.time())
    vol_hist=load_json(VOL_FILE); price_hist=load_json(PRICE_FILE); oi_hist=load_json(OI_FILE)
    new_vol={}; new_price={}; new_oi={}
    tickers=get_tickers(); gdata, gsrc, gprice, has_global=get_global()
    oi_data, mcap_data, mcap_chg_data = get_oi_mcap()
    tier_gas=[]; tier_pumpcepet=[]; tier_global=[]; tier_indo=[]; tier_bahaya=[]
    tier_gap0=[]; tier_gap1b=[]; tier_gap2=[]
    tier_breakout=[]; tier_oi=[]; tier_lead=[]
    top_priority=[]
    USD_IDR=16500
    try:
        r=requests.get("https://indodax.com/api/tickers", timeout=10).json()['tickers']
        btc_idr=float(r['btc_idr']['last'])
        if 'btc_idr' in gprice and gprice['btc_idr']>0:
            USD_IDR=btc_idr/float(gprice['btc_idr'])
    except: pass
    for t in tickers:
        sym=t['sym']; price=t['last']; low=t['low']; naik=t['naik']; pos=t['pos']; vol=t['vol']
        gp=gdata.get(t['pair'],0); gname=gsrc.get(t['pair'],"-"); gp_txt=f"Global {gp:.1f}% [{gname}]"
        has_g = t['pair'] in has_global
        if has_g and t['pair'] in gprice and gprice[t['pair']]>0:
            fair=gprice[t['pair']]*USD_IDR
            premium=(price-fair)/fair*100 if fair>0 else 0
        else:
            premium=0
            if not has_g: gp_txt="Global - [NO GLOBAL]"
        phist=price_hist.get(t['pair'],[])
        if isinstance(phist, dict): phist=[phist]
        if not isinstance(phist, list): phist=[]
        phist=[e for e in phist if isinstance(e,dict) and now_ts-e.get("ts",0)<7*3600]
        vhist=vol_hist.get(t['pair'],[])
        if isinstance(vhist, dict): vhist=[vhist]
        if not isinstance(vhist, list): vhist=[]
        vhist=[e for e in vhist if isinstance(e,dict) and now_ts-e.get("ts",0)<7*3600]
        ohist=oi_hist.get(t['pair'],[])
        if isinstance(ohist, dict): ohist=[ohist]
        if not isinstance(ohist, list): ohist=[]
        ohist=[e for e in ohist if isinstance(e,dict) and now_ts-e.get("ts",0)<7*3600]
        p15=get_closest(phist, now_ts, 15*60)
        p60=get_closest(phist, now_ts, 60*60)
        v60=get_closest(vhist, now_ts, 60*60)
        o60=get_closest(ohist, now_ts, 60*60)
        chg_15m = ((price - p15.get("price",price))/p15.get("price",price)*100) if p15 and p15.get("price",0)>0 else 0
        chg_60m = ((price - p60.get("price",price))/p60.get("price",price)*100) if p60 and p60.get("price",0)>0 else 0
        vol_1j = (vol - v60.get("vol",0)) if v60 else 0
        vol_1j_ratio = (vol_1j / vol * 100) if vol>0 else 0
        vol_6h=get_vol_6h(vhist, now_ts)
        vol_ratio=(vol/vol_6h) if vol_6h and vol_6h>0 else 0
        cur_oi = oi_data.get(t['pair'],0)
        oi_1j_chg = 0
        has_oi = cur_oi>0 and o60 is not None and o60.get("oi",0)>0
        if has_oi:
            oi_1j_chg = (cur_oi - o60.get("oi",0)) / o60.get("oi",1) * 100
        mcap = mcap_data.get(t['pair'],0)
        mcap_chg = mcap_chg_data.get(t['pair'],0)
        vhist.append({"ts": now_ts, "vol": vol}); new_vol[t['pair']]=vhist
        phist.append({"ts": now_ts, "price": price}); new_price[t['pair']]=phist
        if cur_oi>0:
            ohist.append({"ts": now_ts, "oi": cur_oi}); new_oi[t['pair']]=ohist
        else:
            if ohist: new_oi[t['pair']]=ohist
        ent_low=min(low*1.01, price*0.99); ent_high=min(low*1.03, price*0.995)
        if ent_high<=ent_low: ent_low=price*0.98; ent_high=price*0.99
        ent_txt=f"{ent_low:.0f}-{ent_high:.0f} OB"
        cut=ent_low*0.97; tp1=ent_high*1.10; tp2=ent_high*1.25
        # === TIPE 1: GAP V19.1b DALEMAN ASLI! ===
        gap = (gp - naik) if has_g else 0
        is_beam = pos < 5.0
        beam_txt = "BEAM!" if is_beam else ""
        if price <= ent_high*1.02:
            ob_type = "OB REAL"
        else:
            ob_type = "RETEST"
        is_new = has_g and gap>2.0 and chg_60m<2.0
        new_txt = "NEW " if is_new else ""
        if has_g and gap>2.0 and vol>=100_000_000 and naik<5.0 and pos<60:
            tier_gap0.append((gap, f"💥 TIER 0 - NEW LAUNCH! | {new_txt}{gap:.0f}% GAP {naik:.1f}% + OB {ent_low:.0f}-{ent_high:.0f} {beam_txt} | {sym} Rp{price:.0f} | ENTRY {ent_low:.0f}-{ent_high:.0f} {ob_type} | Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}% | Prem {premium:.1f}% | CUT {cut:.0f} | TP1 {tp1:.0f} TP2 {tp2:.0f} | MODAL 200rb!"))
        if has_g and gap>2.0 and gp>=3.0 and 2.0<=naik<=8.0 and vol>=150_000_000 and premium<10:
            tier_gap1b.append((gap, f"🚀 TIER 1B - BANDAR GLOBAL GAP RUNNING! | {sym} Rp{price:.0f} | GAP {gap:.1f}% {beam_txt} | Indo {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}% [{gname}] | Prem {premium:.1f}% | ENTRY {ent_txt} {ob_type} | CUT {cut:.0f} | TP1 {tp1:.0f} TP2 {tp2:.0f} | MODAL 200rb!"))
        if has_g and gap>2.0 and naik>=0.5 and chg_15m>0.5 and vol>=100_000_000 and vol_1j_ratio>=3.0 and pos<35 and premium<10:
            tier_gap2.append((gap, f"🔥 TIER 2 - IGNITION GAP! | {sym} Rp{price:.0f} | GAP {gap:.1f}% {beam_txt} | Indo {naik:.1f}% +15m {chg_15m:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn (1J {vol_1j_ratio:.1f}%) | Global {gp:.1f}% | Prem {premium:.1f}% | ENTRY {ent_txt} {ob_type} | CUT {cut:.0f} | TP1 {tp1:.0f} TP2 {tp2:.0f} | MODAL 200rb!"))
        # === TIPE 2: BREAKOUT RETEST! BUAT KOIN VOL GEDE! ===
        if 10.0<=naik<=40.0 and 50<=pos<=75 and vol>=1_000_000_000 and chg_15m>0.5:
            br_cut = price*0.95; br_tp1 = price*1.10; br_tp2 = price*1.25
            score_br = vol/1e9 + naik
            tier_breakout.append((score_br, f"🚀 BREAKOUT RETEST! | {sym} Rp{price:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% +15m {chg_15m:.1f}% +1J {chg_60m:.1f}% | Vol {vol/1e6:.0f}Mn GEDE! | {gp_txt} | Prem {premium:.1f}% | ENTRY {price:.0f} BREAKOUT | CUT {br_cut:.0f} | TP1 {br_tp1:.0f} TP2 {br_tp2:.0f} | MODAL 200rb!"))
            top_priority.append((score_br+25, f"🏆 TOP PRIORITY [BREAKOUT]! | {sym} Rp{price:.0f} | ENTRY {price:.0f} BREAKOUT | CUT {br_cut:.0f} | TP1 {br_tp1:.0f} TP2 {br_tp2:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {gp_txt} | Prem {premium:.1f}% | MODAL 200rb!"))
        # === TIPE 3: OI + MARKET CAP! ===
        oi_ok = False
        oi_txt = ""
        if has_oi and oi_1j_chg>3.0:
            oi_ok = True
            oi_txt = f"OI +{oi_1j_chg:.1f}% 1J!"
        elif not has_oi and vol>=1_000_000_000 and vol_1j_ratio>=5.0:
            oi_ok = True
            oi_txt = f"OI? Vol 1J {vol_1j_ratio:.1f}%!"
        mcap_ok = mcap_chg>0 or (has_g and gp>=2.0)
        if oi_ok and mcap_ok and 0<=naik<=30.0 and pos<=70 and vol>=500_000_000 and premium<15 and chg_15m>-1.0:
            oi_cut = price*0.95; oi_tp1 = price*1.10; oi_tp2 = price*1.25
            score_oi = (oi_1j_chg if has_oi else vol_1j_ratio) + (gp if has_g else 0) + naik
            tier_oi.append((score_oi, f"🔥 OI + MCAP! | {sym} Rp{price:.0f} | {oi_txt} MCAP {mcap_chg:.1f}% | Naik {naik:.1f}% Pos {pos:.0f}% +15m {chg_15m:.1f}% +1J {chg_60m:.1f}% | Vol {vol/1e6:.0f}Mn | Global {gp:.1f}% [{gname}] | Prem {premium:.1f}% | ENTRY {price:.0f} OI! | CUT {oi_cut:.0f} | TP1 {oi_tp1:.0f} TP2 {oi_tp2:.0f} | MODAL 200rb!"))
            top_priority.append((score_oi+30, f"🏆 TOP PRIORITY [OI+MCAP]! | {sym} Rp{price:.0f} | ENTRY {price:.0f} OI! | CUT {oi_cut:.0f} | TP1 {oi_tp1:.0f} TP2 {oi_tp2:.0f} | {oi_txt} Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | Global {gp:.1f}% | MODAL 200rb!"))
        # === TIPE 4: GLOBAL LEAD - INDO LAG! UMUM! BUKAN KHUSUS 1 KOIN! ===
        gap_lead = (gp - naik) if has_g else 0
        is_global_lead = has_g and gp>=20.0 and gap_lead>5.0 and premium<10 and 10.0<=naik<=40.0 and 20_000_000<=vol<=500_000_000
        if is_global_lead:
            lead_cut = price*0.95; lead_tp1 = price*1.10; lead_tp2 = price*1.25
            score_lead = gp + gap_lead
            tier_lead.append((score_lead, f"🌍 GLOBAL LEAD - INDO LAG! | {sym} Rp{price:.0f} | Global {gp:.1f}% [{gname}] GAP {gap_lead:.1f}% | Indo {naik:.1f}% Pos {pos:.0f}% | Vol {vol/1e6:.0f}Mn KECIL TAPI GLOBAL GEDE! | Prem {premium:.1f}% | ENTRY {price:.0f} GLOBAL LEAD! | CUT {lead_cut:.0f} | TP1 {lead_tp1:.0f} TP2 {lead_tp2:.0f} | MODAL 200rb!"))
            top_priority.append((score_lead+28, f"🏆 TOP PRIORITY [GLOBAL LEAD]! | {sym} Rp{price:.0f} | ENTRY {price:.0f} GLOBAL LEAD! | CUT {lead_cut:.0f} | TP1 {lead_tp1:.0f} TP2 {lead_tp2:.0f} | Global {gp:.1f}% GAP {gap_lead:.1f}% | MODAL 200rb!"))
        # === PUMP BAHAYA V44 FIX! ===
        is_global_lead_now = has_g and gp>=20.0 and (gp - naik)>5.0 and premium<10 and 10.0<=naik<=40.0
        is_oi_breakout = (10.0<=naik<=40.0 and 50<=pos<=75 and vol>=1_000_000_000) or (oi_ok and mcap_ok and vol>=500_000_000) or is_global_lead_now
        is_bahaya_pump = (naik>30 and vol<1_000_000_000 and not is_oi_breakout) or (naik>15 and pos>70 and vol<1_000_000_000 and not is_oi_breakout)
        is_bahaya_mahal = has_g and premium>30 and not is_oi_breakout
        if is_bahaya_pump or is_bahaya_mahal:
            if is_bahaya_mahal and not is_bahaya_pump:
                tier_bahaya.append(f"⛔ PUMP BAHAYA - MAHAL! JANGAN BELI! | {sym} Rp{price:.0f} | Indo {naik:.1f}% Pos {pos:.0f}% | Vol {vol/1e6:.0f}Mn | {gp_txt} | Prem {premium:.1f}% | INDO MAHAL {premium:.0f}% DARI GLOBAL! JANGAN BELI!")
            else:
                tier_bahaya.append(f"⛔ PUMP BAHAYA - UDAH PUMP! JANGAN BELI! | {sym} Rp{price:.0f} | Indo {naik:.1f}% Pos {pos:.0f}% +15m {chg_15m:.1f}% | Vol {vol/1e6:.0f}Mn | {gp_txt} | Prem {premium:.1f}% | UDAH PUMP! JANGAN KEJAR!")
            continue
        # === TIPE 1: GAS AWAL V29.9 FIX! ===
        score_gas = vol_1j_ratio + (vol_ratio*2 if vol_ratio else 0)
        if 0<=naik<=4.0 and 5<=pos<=35 and p15 is not None and p60 is not None and abs(chg_15m)<1.5 and abs(chg_60m)<2.0 and vol>=80_000_000 and vol_1j_ratio>=2.0:
            tier_gas.append((score_gas, f"⛽ GAS AWAL - V29.9! | {sym} Rp{price:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% +15m {chg_15m:.1f}% +1J {chg_60m:.1f}% | Vol {vol/1e6:.0f}Mn (6J {vol_ratio:.1f}x, 1J {vol_1j_ratio:.1f}%) | {gp_txt} | Prem {premium:.1f}% | ENTRY {ent_txt} | CUT {cut:.0f} | TP1 {tp1:.0f} TP2 {tp2:.0f} | MODAL 200rb!"))
            top_priority.append((score_gas+10, f"🏆 TOP PRIORITY [GAS AWAL]! | {sym} Rp{price:.0f} | ENTRY {ent_txt} | CUT {cut:.0f} | TP1 {tp1:.0f} TP2 {tp2:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn (1J {vol_1j_ratio:.1f}%) | {gp_txt} | Prem {premium:.1f}% | MODAL 200rb!"))
        # === TIPE 1: PUMP CEPET V29.9 FIX! ===
        if 0<=naik<=5.0 and 5<=pos<=45 and vol>=150_000_000 and vol_ratio>=1.5 and vol_1j_ratio>=3.0:
            score_pump = vol_1j_ratio + (vol_ratio*3 if vol_ratio else 0)
            tier_pumpcepet.append((score_pump, f"🚀 PUMP CEPET - V29.9! | {sym} Rp{price:.0f} | Vol 6J {vol_ratio:.1f}x (1J {vol_1j_ratio:.1f}%) | Naik {naik:.1f}% Pos {pos:.0f}% +1J {chg_60m:.1f}% | Vol {vol/1e6:.0f}Mn | {gp_txt} | Prem {premium:.1f}% | ENTRY {ent_txt} | CUT {cut:.0f} | TP1 {tp1:.0f} TP2 {tp2:.0f} | MODAL 200rb!"))
            top_priority.append((score_pump+20, f"🏆 TOP PRIORITY [PUMP CEPET]! | {sym} Rp{price:.0f} | ENTRY {ent_txt} | CUT {cut:.0f} | TP1 {tp1:.0f} TP2 {tp2:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn (6J {vol_ratio:.1f}x, 1J {vol_1j_ratio:.1f}%) | {gp_txt} | Prem {premium:.1f}% | MODAL 200rb!"))
        # === TIPE 1: BANDAR INDO V30.10 DIPISAH! ===
        is_indo_a = vol_ratio>=2.5 and vol_6h and vol_6h>=20_000_000 and 0<=naik<=3.0 and 15<=pos<=45 and vol>=150_000_000
        is_indo_b = vol>=300_000_000 and vol_ratio>=1.5 and 0<=naik<=5.0 and 10<=pos<=50
        if is_indo_a or is_indo_b:
            tipe="A-MELEDAK" if is_indo_a else "B-GEDE"
            score_indo = vol_1j_ratio + (vol_ratio*3 if vol_ratio else 0)
            tier_indo.append((score_indo, f"👑 BANDAR INDO - V30.10 [{tipe}]! | {sym} Rp{price:.0f} | Vol 6J {vol_ratio:.1f}x (1J {vol_1j_ratio:.1f}%) | Naik {naik:.1f}% Pos {pos:.0f}% | Vol {vol/1e6:.0f}Mn | {gp_txt} | Prem {premium:.1f}% | ENTRY {ent_txt} | CUT {cut:.0f} | TP1 {tp1:.0f} TP2 {tp2:.0f} | MODAL 200rb!"))
            top_priority.append((score_indo+18, f"🏆 TOP PRIORITY [BANDAR INDO]! | {sym} Rp{price:.0f} | ENTRY {ent_txt} | CUT {cut:.0f} | TP1 {tp1:.0f} TP2 {tp2:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn (6J {vol_ratio:.1f}x) | {gp_txt} | Prem {premium:.1f}% | MODAL 200rb!"))
        # === TIPE 1: BULLISH GLOBAL V30.10! ===
        is_global_a = has_g and gp>=3.0 and 0.3<=naik<=5.0 and pos<=45 and vol>=150_000_000 and premium<10
        is_global_b = has_g and gp>=5.0 and 0<=naik<=5.0 and pos<=45 and vol>=80_000_000 and premium<10
        is_global_c = has_g and gp>=2.0 and 0<=naik<=3.0 and pos<=30 and vol>=200_000_000 and premium<10
        if is_global_a or is_global_b or is_global_c:
            if is_global_a: tipe="A-GLOBAL NGEGAS"
            elif is_global_b: tipe="B-GLOBAL GEDE"
            else: tipe="C-GLOBAL MULAI"
            score_global = gp + (vol_1j_ratio)
            tier_global.append((score_global, f"🌍 BULLISH GLOBAL - V30.10 [{tipe}]! | {sym} Rp{price:.0f} | Indo {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {gp_txt} | Prem {premium:.1f}% | ENTRY {ent_txt} | CUT {cut:.0f} | TP1 {tp1:.0f} TP2 {tp2:.0f} | MODAL 200rb!"))
            top_priority.append((score_global+15, f"🏆 TOP PRIORITY [BULLISH GLOBAL]! | {sym} Rp{price:.0f} | ENTRY {ent_txt} | CUT {cut:.0f} | TP1 {tp1:.0f} TP2 {tp2:.0f} | Indo {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {gp_txt} | Prem {premium:.1f}% | MODAL 200rb!"))
    save_json(VOL_FILE, new_vol); save_json(PRICE_FILE, new_price); save_json(OI_FILE, new_oi)
    tier_gas_sorted = [x[1] for x in sorted(tier_gas, key=lambda y: y[0], reverse=True)]
    tier_pump_sorted = [x[1] for x in sorted(tier_pumpcepet, key=lambda y: y[0], reverse=True)]
    tier_indo_sorted = [x[1] for x in sorted(tier_indo, key=lambda y: y[0], reverse=True)]
    tier_global_sorted = [x[1] for x in sorted(tier_global, key=lambda y: y[0], reverse=True)]
    tier_gap0_sorted = [x[1] for x in sorted(tier_gap0, key=lambda y: y[0], reverse=True)]
    tier_gap1b_sorted = [x[1] for x in sorted(tier_gap1b, key=lambda y: y[0], reverse=True)]
    tier_gap2_sorted = [x[1] for x in sorted(tier_gap2, key=lambda y: y[0], reverse=True)]
    tier_breakout_sorted = [x[1] for x in sorted(tier_breakout, key=lambda y: y[0], reverse=True)]
    tier_oi_sorted = [x[1] for x in sorted(tier_oi, key=lambda y: y[0], reverse=True)]
    tier_lead_sorted = [x[1] for x in sorted(tier_lead, key=lambda y: y[0], reverse=True)]
    top_sorted = [x[1] for x in sorted(top_priority, key=lambda y: y[0], reverse=True)]
    seen_top=set(); top_5=[]
    for line in top_sorted:
        try: sym_part = line.split("|")[1].strip().split(" ")[0]
        except: sym_part=line
        if sym_part not in seen_top:
            seen_top.add(sym_part); top_5.append(line)
        if len(top_5)>=5: break
    msg=f"=== V49 FINAL - 4 TIPE - HTX DIBUANG! {now} - {len(tickers)} KOINS (9 HOLD DISKIP) ===\n"
    msg+=f"🏆 TOP 5 ENTRI - V30.10 + BREAKOUT + OI + GLOBAL LEAD [MAX 5 - LIAT INI DULU!]:\n"+("\n".join(top_5) if top_5 else "Belum ada TOP 5!")+"\n\n"
    msg+=f"⛽ TIPE 1 - GAS AWAL - V29.9 FIX [MAX 5]:\n"+("\n".join(tier_gas_sorted[:5]) if tier_gas_sorted else "Belum ada GAS AWAL!")+"\n\n"
    msg+=f"🚀 TIPE 1 - PUMP CEPET - V29.9 FIX [MAX 5 - DIPISAH!]:\n"+("\n".join(tier_pump_sorted[:5]) if tier_pump_sorted else "Belum ada PUMP CEPET!")+"\n\n"
    msg+=f"🌍 TIPE 1 - BULLISH GLOBAL - V30.10 [MAX 5]:\n"+("\n".join(tier_global_sorted[:5]) if tier_global_sorted else "Belum ada BULLISH GLOBAL!")+"\n\n"
    msg+=f"👑 TIPE 1 - BANDAR INDO - V30.10 [MAX 5 - DIPISAH!]:\n"+("\n".join(tier_indo_sorted[:5]) if tier_indo_sorted else "Belum ada BANDAR INDO!")+"\n\n"
    msg+=f"💥 TIPE 1 - TIER 0 - NEW LAUNCH GAP V19.1b [MAX 5 - GAP = Global - Indo!]:\n"+("\n".join(tier_gap0_sorted[:5]) if tier_gap0_sorted else "Belum ada GAP!")+"\n\n"
    msg+=f"🚀 TIPE 1 - TIER 1B - BANDAR GLOBAL GAP RUNNING V19.1b [MAX 5]:\n"+("\n".join(tier_gap1b_sorted[:5]) if tier_gap1b_sorted else "Tidak ada")+"\n\n"
    msg+=f"🔥 TIPE 1 - TIER 2 - IGNITION GAP V19.1b [MAX 5]:\n"+("\n".join(tier_gap2_sorted[:5]) if tier_gap2_sorted else "Tidak ada")+"\n\n"
    msg+=f"🚀 TIPE 2 - BREAKOUT RETEST - KOIN VOL GEDE! [MAX 5 - Naik 10-40% + Pos 50-75% + Vol >=1 Miliar!]:\n"+("\n".join(tier_breakout_sorted[:5]) if tier_breakout_sorted else "Belum ada BREAKOUT!")+"\n\n"
    msg+=f"🔥 TIPE 3 - OI + MARKET CAP - KOIN OI NAIK! [MAX 5 - OI 1J >3% + MCAP Naik + Global Naik!]:\n"+("\n".join(tier_oi_sorted[:5]) if tier_oi_sorted else "Belum ada OI!")+"\n\n"
    msg+=f"🌍 TIPE 4 - GLOBAL LEAD - INDO LAG - KOIN APA AJA! [MAX 5 - Global >=20% + GAP >5% + Prem <10% + Naik 10-40% + Vol 20Mn-500Mn!]:\n"+("\n".join(tier_lead_sorted[:5]) if tier_lead_sorted else "Belum ada GLOBAL LEAD!")+"\n\n"
    msg+=f"⛔ PUMP BAHAYA - JANGAN BELI - V44-GENERIC FIX [MAX 5 - TIPE 2/3/4 Bukan Bahaya! Naik >40% Baru Bahaya!]:\n"+("\n".join(tier_bahaya[:5]) if tier_bahaya else "Gak ada pump bahaya!")+"\n\n"
    msg+=f"📌 V49 FINAL 4 TIPE - HTX DIBUANG! TIPE 1 = RETEST OB! TIPE 2 = BREAKOUT! TIPE 3 = OI + MCAP! TIPE 4 = GLOBAL LEAD! LYFEL BALIK! NVDAX DIBUANG! BANDAR INDO DIPISAH! GAP V19.1b = Global - Indo + BEAM + OB REAL vs RETEST + NEW! ENTRY TIPE 1=Low*1,01-1,03! ENTRY TIPE 2,3,4=Harga Sekarang! CUT 3-5%! TP1 10% TP2 25%! 2 JAM! Bot jalan tiap 5 menit!\n"
    return msg
if __name__=="__main__":
    send_tele(scan())
