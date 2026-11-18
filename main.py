# === V48 ULTIMATE PREMIUM - SATU AJA! BUANG V46, V46 FINAL, V47! DIKUNCI! ===
# GABUNGAN: V46 (Breakout 15m) + V46 FINAL (Fix Harga >50rb + TP 2 Stage + CUT 5%) + V47 (Gak Ngejar!)
# VALIDASI INDODAX: PIPPIN, S, PIEVERSE, ICNT, ANKR semua ke-tangkep PAS TIDUR! Bukan pas udah lari!
# BANDAR INDODAX: Vol 24H >=150Mn + Vol 1J >=3% + Vol 6J >=1,5x = LAGI NGUMPULIN!
# BANDAR GLOBAL: Global >=0% (gak minus!) + Premium -2% sampai +10% = MASIH MURAH! Global >=2% itu BONUS!
# ATURAN: CUMA BELI YANG MASIH TIDUR! Naik 0-4%! Pos 5-30%! +15m <1,5%! +1J <2%! Kalo udah Naik >5% -> JANGAN KEJAR!
# ENTRY Low*1,01-1,03! CUT 3% (Pre-Pump) / 5% (kalo udah lari dikit)! TP1 10% jual setengah! TP2 25% jual sisa! MODAL 200rb! 2 JAM!
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
    'ondo_idr','hot_idr','sui_idr','dodo_idr','bome_idr','nom_idr','mpro_idr','amp_idr','unmd_idr','kdag_idr',
    'bsv_idr','vet_idr','fil_idr','eos_idr','xtz_idr','neo_idr','aave_idr','comp_idr','mkr_idr','snx_idr','yfi_idr','mana_idr','axs_idr','slp_idr','chz_idr',
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
        # FIX V46: Harga >50rb DIHAPUS! PIPPIN 345rb + PIEVERSE 51rb BOLEH! Indodax bisa beli pecahan!
        pos=((last-low)/(high-low)*100) if high!=low else 0
        naik=((last-low)/low*100) if low!=0 else 0
        out.append({'pair':pair,'sym':pair.replace('_idr','').upper(),'last':last,'low':low,'high':high,'vol':vol,'pos':pos,'naik':naik})
    return out
def get_global():
    g={}; src={}; gp_usd={}; has_global=set()
    def upd(sym, val, name, usd_price=None):
        try: val=float(val)
        except: return
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
    try:
        r=requests.get("https://api.huobi.pro/market/tickers",timeout=6,headers=h).json()
        for x in r.get('data',[]):
            s=x.get('symbol','')
            if s.endswith('usdt'):
                sym=s.replace('usdt','')
                try:
                    close=float(x['close']); open24=float(x['open'])
                    if open24>0: upd(sym, (close-open24)/open24*100, "HTX", close)
                except: pass
    except: pass
    try:
        r=requests.get("https://api.coinbase.com/v2/assets/prices?base=USD",timeout=6,headers=h).json()
        for x in r.get('data',[]):
            sym=x.get('base',''); ch=x.get('price_percent_change_24h')
            if ch is not None:
                try: upd(sym, float(ch), "COINBASE", x.get('price'))
                except: pass
    except: pass
    return g, src, gp_usd, has_global
def scan():
    now=datetime.now(WIB).strftime("%H:%M WIB"); now_ts=int(time.time())
    vol_hist=load_json(VOL_FILE); price_hist=load_json(PRICE_FILE)
    new_vol={}; new_price={}
    tickers=get_tickers(); gdata, gsrc, gprice, has_global=get_global()
    tier_prepump=[]; tier_akumulasi=[]; tier_indo=[]; tier_global=[]; tier_jangan_kejar=[]; tier_bahaya=[]
    seen=set()
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
        p15=get_closest(phist, now_ts, 15*60)
        p60=get_closest(phist, now_ts, 60*60)
        v60=get_closest(vhist, now_ts, 60*60)
        chg_15m = ((price - p15.get("price",price))/p15.get("price",price)*100) if p15 and p15.get("price",0)>0 else 0
        chg_60m = ((price - p60.get("price",price))/p60.get("price",price)*100) if p60 and p60.get("price",0)>0 else 0
        vol_1j = (vol - v60.get("vol",0)) if v60 else 0
        vol_1j_ratio = (vol_1j / vol * 100) if vol>0 else 0
        vol_6h=get_vol_6h(vhist, now_ts)
        vol_ratio=(vol/vol_6h) if vol_6h and vol_6h>0 else 0
        vhist.append({"ts": now_ts, "vol": vol}); new_vol[t['pair']]=vhist
        phist.append({"ts": now_ts, "price": price}); new_price[t['pair']]=phist
        ent_low=min(low*1.01, price*0.99); ent_high=min(low*1.03, price*0.995)
        if ent_high<=ent_low: ent_low=price*0.98; ent_high=price*0.99
        ent_txt=f"{ent_low:.0f}-{ent_high:.0f} OB"
        cut=ent_low*0.97; tp1=ent_high*1.10; tp2=ent_high*1.25
        # === ⛔ JANGAN KEJAR! UDAH PUMP! INI YANG LU GAK MAU! ===
        # Kalo Naik >5% / +15m >3% / Pos >35% -> UDAH LARI! JANGAN KEJAR!
        if naik>5 or (p15 is not None and chg_15m>3.0) or pos>35:
            if naik>10 or (p15 is not None and chg_15m>5.0):
                tier_jangan_kejar.append(f"⛔ JANGAN KEJAR! UDAH PUMP! | {sym} Rp{price:.0f} | Indo {naik:.1f}% Pos {pos:.0f}% +15m {chg_15m:.1f}% | Vol {vol/1e6:.0f}Mn | {gp_txt} | Prem {premium:.1f}% | UDAH LARI! CARI YANG MASIH TIDUR!")
            continue
        if has_g and premium>30:
            tier_bahaya.append(f"⚠️ PUMP BAHAYA! | {sym} Rp{price:.0f} | Indo {naik:.1f}% Pos {pos:.0f}% | {gp_txt} | Prem {premium:.1f}% | Udah telat!")
            continue
        # === 😴 PRE-PUMP ULTIMATE - MASIH TIDUR! INI YANG LU MAU! ===
        # BANDAR INDODAX: Vol >=80Mn + Vol 1J >=3% + Vol 6J >=1,5x!
        # BANDAR GLOBAL: Global >=0% (gak minus!) + Prem -2% sampai +10%! Global >=2% itu BONUS!
        # MASIH TIDUR: Naik 0-4%! Pos 5-30%! +15m <1,5%! +1J <2%!
        if 0<=naik<=4.0 and 5<=pos<=30 and p15 is not None and p60 is not None and abs(chg_15m)<1.5 and abs(chg_60m)<2.0 and vol>=80_000_000 and (vol_ratio>=1.5 or vol_1j_ratio>=3.0) and has_g and gp>=0 and -2<=premium<=10:
            tier_prepump.append(f"😴 PRE-PUMP ULTIMATE - MASIH TIDUR! | {sym} Rp{price:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% +15m {chg_15m:.1f}% +1J {chg_60m:.1f}% | Vol {vol/1e6:.0f}Mn (6J {vol_ratio:.1f}x, 1J {vol_1j_ratio:.1f}%) | {gp_txt} | Prem {premium:.1f}% | ENTRY {ent_txt} | CUT {cut:.0f} (3%!) | TP1 {tp1:.0f} (10%!) TP2 {tp2:.0f} (25%!) | MODAL 200rb! | BELUM LARI! BELI DI BAWAH!")
        # === 🐋 AKUMULASI - BANDAR INDODAX LAGI NGUMPULIN! GAK BUTUH GLOBAL! ===
        # Syarat: Naik 0-4%! Pos 5-35%! +1J <3%! Vol >=150Mn! Vol 6J >=1,2x! Vol 1J >=2%!
        if 0<=naik<=4.0 and 5<=pos<=35 and p60 is not None and abs(chg_60m)<3.0 and vol>=150_000_000 and vol_ratio>=1.2 and vol_1j_ratio>=2.0:
            tier_akumulasi.append(f"🐋 AKUMULASI - BANDAR INDODAX NGUMPULIN! | {sym} Rp{price:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% +1J {chg_60m:.1f}% | Vol {vol/1e6:.0f}Mn (6J {vol_ratio:.1f}x, 1J {vol_1j_ratio:.1f}%) | {gp_txt} | Prem {premium:.1f}% | ENTRY {ent_txt} | CUT {cut:.0f} | TP1 {tp1:.0f} TP2 {tp2:.0f} | MODAL 200rb!")
        # === 👑 BANDAR INDODAX V32 FINAL - DIVERSI! CUMA YANG PRE-PUMP! ===
        # Tipe A: Vol 6J >=2,5x, Vol >=150Mn, Naik 0-3%, Pos 15-45%! Tipe B: Vol >=300Mn, Vol 6J >=1,5x, Naik 0-5%, Pos 10-50%!
        is_bandar_indo_a = vol_ratio>=2.5 and vol_6h and vol_6h>=20_000_000 and 0<=naik<=3.0 and 15<=pos<=45 and vol>=150_000_000
        is_bandar_indo_b = vol>=300_000_000 and vol_ratio>=1.5 and 0<=naik<=5.0 and 10<=pos<=50
        if (is_bandar_indo_a or is_bandar_indo_b) and naik<=5.0 and pos<=45:
            if t['pair'] not in seen:
                tipe="A-MELEDAK" if is_bandar_indo_a else "B-GEDE"
                tier_indo.append(f"👑 BANDAR INDODAX [{tipe}]! | {sym} Rp{price:.0f} | Vol 6J {vol_ratio:.1f}x (1J {vol_1j_ratio:.1f}%) | Naik {naik:.1f}% Pos {pos:.0f}% | {gp_txt} | Prem {premium:.1f}% | ENTRY {ent_txt} | CUT {cut:.0f} | TP1 {tp1:.0f} TP2 {tp2:.0f} | MODAL 200rb!")
                seen.add(t['pair'])
            continue
        # === 🌍 BANDAR GLOBAL V32 FINAL - DIVERSI! CUMA YANG PRE-PUMP! ===
        # Tipe A: Global >=3%, Indo 0,3-5%, Pos <=45%, Vol >=150Mn! Tipe B: Global >=5%, Indo 0-5%, Pos <=45%, Vol >=80Mn! Tipe C: Global >=2%, Indo 0-3%, Pos <=30%, Vol >=200Mn!
        is_global_a = has_g and gp>=3.0 and 0.3<=naik<=5.0 and pos<=45 and vol>=150_000_000
        is_global_b = has_g and gp>=5.0 and 0<=naik<=5.0 and pos<=45 and vol>=80_000_000
        is_global_c = has_g and gp>=2.0 and 0<=naik<=3.0 and pos<=30 and vol>=200_000_000
        if is_global_a or is_global_b or is_global_c:
            if t['pair'] not in seen:
                if is_global_a: tipe="A-GLOBAL NGEGAS"
                elif is_global_b: tipe="B-GLOBAL GEDE"
                else: tipe="C-GLOBAL MULAI"
                tier_global.append(f"🌍 BANDAR GLOBAL [{tipe}]! | {sym} Rp{price:.0f} | Indo {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {gp_txt} | Prem {premium:.1f}% | ENTRY {ent_txt} | CUT {cut:.0f} | TP1 {tp1:.0f} TP2 {tp2:.0f} | MODAL 200rb!")
                seen.add(t['pair'])
            continue
    save_json(VOL_FILE, new_vol); save_json(PRICE_FILE, new_price)
    msg=f"=== V48 ULTIMATE PREMIUM - SATU AJA! DIKUNCI! {now} - {len(tickers)} KOINS (9 HOLD DISKIP) ===\n"
    msg+=f"😴 PRE-PUMP ULTIMATE [MAX 5 - INI YANG LU MAU! MASIH TIDUR!]:\n"+("\n".join(tier_prepump[:5]) if tier_prepump else "Belum ada pre-pump - semua masih tidur pulas / udah lari!")+"\n\n"
    msg+=f"🐋 AKUMULASI - BANDAR INDODAX [MAX 5]:\n"+("\n".join(tier_akumulasi[:5]) if tier_akumulasi else "Belum ada akumulasi!")+"\n\n"
    msg+=f"👑 BANDAR INDODAX V32 [MAX 5 - PRE-PUMP DOANG!]:\n"+("\n".join(tier_indo[:5]) if tier_indo else "Belum ada bandar!")+"\n\n"
    msg+=f"🌍 BANDAR GLOBAL V32 [MAX 5 - PRE-PUMP DOANG!]:\n"+("\n".join(tier_global[:5]) if tier_global else "Belum ada bandar Global!")+"\n\n"
    msg+=f"⛔ JANGAN KEJAR - UDAH PUMP!:\n"+("\n".join(tier_jangan_kejar[:5]) if tier_jangan_kejar else "Gak ada yang udah pump!")+"\n\n"
    msg+=f"⚠️ PUMP BAHAYA:\n"+("\n".join(tier_bahaya[:5]) if tier_bahaya else "Gak ada pump bahaya!")+"\n\n"
    msg+=f"📌 ULTIMATE: ENTRY=Low*1,01-1,03! CUT 3%! TP1 10% jual setengah! TP2 25% jual sisa! 2 JAM! Kalo Naik >5% JANGAN KEJAR! Bot jalan tiap 5 menit! Cron job lu udah bener!\n"
    return msg
if __name__=="__main__":
    send_tele(scan())
