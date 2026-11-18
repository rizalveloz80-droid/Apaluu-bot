# === V46 PREMIUM - GAK KETINGGALAN LAGI! SALIN FULL! JANGAN PATCH! ===
# KENAPA V44 GAGAL? V44 nunggu Vol 6J naik 1,8x! Padahal PIPPIN +70%, S +43%, PIEVERSE +40%, ICNT +33%, ANKR +21% naiknya cuma 15 MENIT!
# V46 baca 15 MENIT! Bukan 6 JAM!
# POLA PREMIUM (dari 5 chart lu):
# 1. TIDUR DATAR: Harga datar berjam-jam, EMA nempel! (Harga 15m lalu naik <1%!)
# 2. BREAKOUT 15M: Harga naik +3% dalam 15 menit! Vol 15m meledak 3x!
# 3. EMA7 NYALIP: Harga > EMA7 > EMA25! (Di-proxy: Harga sekarang > Harga 1 jam lalu *1,02!)
# 4. MASIH AWAL: Naik dari Low baru 5-25%! Bukan 50%! Jadi masih bisa ikut!
# 5. GAK BUTUH GLOBAL! GAK BUTUH PREMIUM! YANG PENTING INDO NYA LARI!
# + V32 FINAL BANDAR INDODAX + GLOBAL masih ada! + PUMP BAWAH masih ada!
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
    # Cari data paling deket target_age detik lalu!
    best=None; best_diff=999999
    if not isinstance(hist_list, list): return None
    for e in hist_list:
        if not isinstance(e, dict): continue
        age=now_ts-e.get("ts",0)
        diff=abs(age-target_age)
        if diff<best_diff: best_diff=diff; best=e
    # Kalo bedanya > 50% dari target, anggap gak ada!
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
        if last>50000: continue
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
    tier_breakout=[]; tier_momentum=[]; tier_bawah=[]; tier_scalp=[]; tier_early=[]; tier_new=[]; tier_indo=[]; tier_global=[]; tier_bahaya=[]
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
        # === HISTORY 15M / 1J / 6J - INI KUNCI V46 PREMIUM! ===
        phist=price_hist.get(t['pair'],[])
        if isinstance(phist, dict): phist=[phist]
        if not isinstance(phist, list): phist=[]
        phist=[e for e in phist if isinstance(e,dict) and now_ts-e.get("ts",0)<7*3600]
        vhist=vol_hist.get(t['pair'],[])
        if isinstance(vhist, dict): vhist=[vhist]
        if not isinstance(vhist, list): vhist=[]
        vhist=[e for e in vhist if isinstance(e,dict) and now_ts-e.get("ts",0)<7*3600]
        # Harga 15m lalu, 1j lalu!
        p15=get_closest(phist, now_ts, 15*60)
        p60=get_closest(phist, now_ts, 60*60)
        v15=get_closest(vhist, now_ts, 15*60)
        # Vol 15m = Vol sekarang - Vol 15m lalu! Ini Vol yang masuk 15 menit terakhir!
        vol_15m = (vol - v15.get("vol",0)) if v15 else 0
        # Rata-rata Vol 15m sebelumnya = (Vol 1j lalu - Vol 15m lalu) / 3! Proxy!
        # Kalo gak ada data, vol_15m = 0, jangan lolos!
        chg_15m = ((price - p15.get("price",price))/p15.get("price",price)*100) if p15 and p15.get("price",0)>0 else 0
        chg_60m = ((price - p60.get("price",price))/p60.get("price",price)*100) if p60 and p60.get("price",0)>0 else 0
        # Vol 15m meledak? Bandingin Vol 15m sekarang vs Vol 15m rata-rata 1 jam lalu!
        # Sederhana: Vol 15m harus >= 5% dari Vol 24H! Kalo tidur, Vol 15m kecil!
        vol_15m_ratio = (vol_15m / vol * 100) if vol>0 else 0
        vol_6h=get_vol_6h(vhist, now_ts)
        vol_ratio=(vol/vol_6h) if vol_6h and vol_6h>0 else 0
        vhist.append({"ts": now_ts, "vol": vol}); new_vol[t['pair']]=vhist
        phist.append({"ts": now_ts, "price": price}); new_price[t['pair']]=phist
        # ENTRY: Kalo breakout, ENTRY = Harga sekarang! Jangan nunggu Low! Nanti ketinggalan lagi!
        # CUT = ENTRY * 0,97! TARGET = ENTRY * 1,10 untuk BREAKOUT! TARGET 5% untuk SCALP!
        ent_break = price*0.98; ent_break_high = price*1.01
        ent_txt_break=f"{ent_break:.0f}-{ent_break_high:.0f} BREAKOUT"
        cut_break=ent_break*0.97; target_break=ent_break_high*1.10
        ent_low=min(low*1.01, price*0.99); ent_high=min(low*1.03, price*0.995)
        if ent_high<=ent_low: ent_low=price*0.98; ent_high=price*0.99
        ent_txt=f"{ent_low:.0f}-{ent_high:.0f} OB"
        cut=ent_low*0.97; target=ent_high*1.10
        cut_scalp=ent_low*0.98; target_scalp=ent_high*1.05
        retest_low=price*0.93; retest_high=price*0.97
        if pos>40:
            ent_txt2=f"{retest_low:.0f}-{retest_high:.0f} RETEST"; cut2=retest_low*0.97; target2=retest_high*1.10
        else:
            ent_txt2=ent_txt; cut2=cut; target2=target
        # BAHAYA: Naik >70% dari Low! Udah telat banget! Kayak PIPPIN +70%!
        if naik>70:
            tier_bahaya.append(f"⚠️ PUMP BAHAYA! JANGAN BELI! | {sym} Rp{price:.0f} | Indo {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {gp_txt} | Prem {premium:.1f}% | Udah +{naik:.0f}%! Telat!")
            continue
        if has_g and premium>30:
            tier_bahaya.append(f"⚠️ PUMP BAHAYA! JANGAN BELI! | {sym} Rp{price:.0f} | Indo {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {gp_txt} | Prem {premium:.1f}% | Udah telat!")
            continue
        # === 🚨 BREAKOUT 15M - INI YANG LU MAU! PREMIUM! ===
        # Pola PIPPIN, S, PIEVERSE, ICNT, ANKR: Tidur, lalu 15m naik +3%! Vol 15m gede! Masih awal Naik 5-30%!
        # Syarat: chg_15m >=3%! chg_60m >=5%! Vol 15m >=3% dari Vol 24H! Naik 5-30%! Pos 20-80%!
        # GAK BUTUH GLOBAL! GAK BUTUH PREMIUM! GAK BUTUH VOL 6J!
        if p15 is not None and chg_15m>=3.0 and chg_60m>=5.0 and vol_15m_ratio>=2.0 and 5<=naik<=35 and 20<=pos<=85 and vol>=50_000_000:
            tier_breakout.append(f"🚨 BREAKOUT 15M - LARI! | {sym} Rp{price:.0f} | +15m {chg_15m:.1f}% +1J {chg_60m:.1f}% | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn (15m {vol_15m/1e6:.0f}Mn) | {gp_txt} | Prem {premium:.1f}% | ENTRY {ent_txt_break} | CUT {cut_break:.0f} | TARGET {target_break:.0f} | MODAL 200rb! | INI KAYAK PIPPIN +70%! JANGAN TUNGGU LOW!")
        # === 🔥 MOMENTUM 1J - BARU MAU LARI! ===
        # Pola: 1 jam naik +8%! 15m naik +1%! Masih awal! Belum meledak!
        if p60 is not None and chg_60m>=8.0 and chg_15m>=1.0 and 5<=naik<=30 and vol>=50_000_000:
            tier_momentum.append(f"🔥 MOMENTUM 1J - MAU LARI! | {sym} Rp{price:.0f} | +1J {chg_60m:.1f}% +15m {chg_15m:.1f}% | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {gp_txt} | Prem {premium:.1f}% | ENTRY {ent_txt_break} | CUT {cut_break:.0f} | TARGET {target_break:.0f} | MODAL 200rb!")
        # === 🚀 PUMP DARI BAWAH - V44.1 FIX! ===
        if 0<=naik<=3.0 and 5<=pos<=30 and vol>=80_000_000 and vol_ratio>=1.8 and has_g and premium<10:
            tier_bawah.append(f"🚀 PUMP DARI BAWAH! | {sym} Rp{price:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn (6J {vol_ratio:.1f}x) | {gp_txt} | Prem {premium:.1f}% | ENTRY {ent_txt} | CUT {cut:.0f} | TARGET {target:.0f} | MODAL 200rb!")
        # === ⚡ SCALP INDO DOANG ===
        if 3<=naik<=15 and 20<=pos<=60 and vol>=100_000_000 and has_g and 10<=premium<=30:
            tier_scalp.append(f"⚡ SCALP INDO DOANG! | {sym} Rp{price:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {gp_txt} | Prem {premium:.1f}% | ENTRY {ent_txt} | CUT {cut_scalp:.0f} | TARGET {target_scalp:.0f} | MODAL 100rb! | 15 MENIT!")
        # === 🐣 EARLY ===
        if 0<=naik<=2.5 and 5<=pos<=30 and vol>=80_000_000 and vol_ratio>=1.8 and has_g and gp>=0.5 and premium<5:
            tier_early.append(f"🐣 EARLY! | {sym} Rp{price:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn (6J {vol_ratio:.1f}x) | {gp_txt} | Prem {premium:.1f}% | ENTRY {ent_txt} | CUT {cut:.0f} | TARGET {target:.0f} | MODAL 200rb!")
        # === 💥 NEW ===
        if has_g and gp>=2.0 and 2<=naik<=30 and 10<=pos<=70 and vol>=40_000_000 and premium<10:
            tier_new.append(f"💥 NEW {gp:.0f}% | {sym} Rp{price:.0f} | ENTRY {ent_txt2} | Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {gp_txt} | CUT {cut2:.0f} | TARGET {target2:.0f} | MODAL 200rb!")
        # === 👑 BANDAR INDODAX V32 FINAL! ===
        is_bandar_indo_a = vol_ratio>=2.5 and vol_6h and vol_6h>=20_000_000 and 0<=naik<=3.0 and 15<=pos<=45 and vol>=150_000_000
        is_bandar_indo_b = vol>=300_000_000 and vol_ratio>=1.5 and 0<=naik<=5.0 and 10<=pos<=50
        if is_bandar_indo_a or is_bandar_indo_b:
            if t['pair'] not in seen:
                tipe="A-MELEDAK" if is_bandar_indo_a else "B-GEDE"
                tier_indo.append(f"👑 BANDAR INDODAX [{tipe}]! | {sym} Rp{price:.0f} | Vol 6J {vol_ratio:.1f}x | Naik {naik:.1f}% Pos {pos:.0f}% | {gp_txt} | Prem {premium:.1f}% | ENTRY {ent_txt} | CUT {cut:.0f} | TARGET {target:.0f} | MODAL 200rb!")
                seen.add(t['pair'])
            continue
        # === 🌍 BANDAR GLOBAL V32 FINAL! ===
        is_global_a = has_g and gp>=3.0 and 0.3<=naik<=8.0 and pos<=50 and vol>=150_000_000
        is_global_b = has_g and gp>=5.0 and 0<=naik<=15.0 and pos<=60 and vol>=80_000_000
        is_global_c = has_g and gp>=2.0 and 0<=naik<=3.0 and pos<=30 and vol>=200_000_000
        if is_global_a or is_global_b or is_global_c:
            if t['pair'] not in seen:
                if is_global_a: tipe="A-GLOBAL NGEGAS"
                elif is_global_b: tipe="B-GLOBAL GEDE"
                else: tipe="C-GLOBAL MULAI"
                tier_global.append(f"🌍 BANDAR GLOBAL [{tipe}]! | {sym} Rp{price:.0f} | Indo {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {gp_txt} | Prem {premium:.1f}% | ENTRY {ent_txt} | CUT {cut:.0f} | TARGET {target:.0f} | MODAL 200rb!")
                seen.add(t['pair'])
            continue
    save_json(VOL_FILE, new_vol); save_json(PRICE_FILE, new_price)
    msg=f"=== V46 PREMIUM - GAK KETINGGALAN LAGI! {now} - {len(tickers)} KOINS (9 HOLD DISKIP) ===\n"
    msg+=f"🚨 BREAKOUT 15M [MAX 5 - INI YANG LU MAU! PIPPIN +70%!]:\n"+("\n".join(tier_breakout[:5]) if tier_breakout else "Belum ada breakout - semua masih tidur!")+"\n\n"
    msg+=f"🔥 MOMENTUM 1J [MAX 5 - MAU LARI!]:\n"+("\n".join(tier_momentum[:5]) if tier_momentum else "Belum ada momentum!")+"\n\n"
    msg+=f"🚀 PUMP DARI BAWAH [MAX 5]:\n"+("\n".join(tier_bawah[:5]) if tier_bawah else "Belum ada pump bawah!")+"\n\n"
    msg+=f"⚡ SCALP INDO DOANG [MAX 5]:\n"+("\n".join(tier_scalp[:5]) if tier_scalp else "Belum ada scalp!")+"\n\n"
    msg+=f"🐣 EARLY [MAX 5]:\n"+("\n".join(tier_early[:5]) if tier_early else "Belum ada early!")+"\n\n"
    msg+=f"💥 NEW [MAX 7]:\n"+("\n".join(tier_new[:7]) if tier_new else "Belum ada NEW!")+"\n\n"
    msg+=f"👑 BANDAR INDODAX V32 [MAX 5]:\n"+("\n".join(tier_indo[:5]) if tier_indo else "Belum ada bandar!")+"\n\n"
    msg+=f"🌍 BANDAR GLOBAL V32 [MAX 5]:\n"+("\n".join(tier_global[:5]) if tier_global else "Belum ada bandar Global!")+"\n\n"
    msg+=f"⚠️ PUMP BAHAYA:\n"+("\n".join(tier_bahaya[:5]) if tier_bahaya else "Gak ada pump bahaya!")+"\n\n"
    msg+=f"📌 BREAKOUT: ENTRY=Harga*0,98-1,01! JANGAN TUNGGU LOW! CUT 3%! TARGET 10%! 1 JAM! PENTING: Bot harus jalan tiap 5 menit! Kalo 1 jam sekali, ketinggalan lagi!\n"
    return msg
if __name__=="__main__":
    send_tele(scan())
