# === V44 FULL - GENERIC - NANGKEP SEMUA KOIN MAU PUMP! SALIN FULL! ===
# GAK ADA LAGI NAMA SKYAI / BMT! ITU CUMA CONTOH! SEMUA KOIN BISA MASUK!
# POLA: Pos 5-30% + Vol naik 1,8x + Premium <10% + Harga masih di bawah = MAU PUMP!
# 1. PUMP BAWAH: Nangkep 100+ koin Indodax dari bawah! Gak butuh Global!
# 2. SCALP INDO: Indo udah naik dikit, Premium 10-30%, Target 5% doang!
# 3. PHA MODE / GLOBAL: Global + Indo naik bareng!
# 4. NEW + EARLY + BANDAR masih ada! NO COOLDOWN! HOLD 9 KOIN DISKIP!
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
    g={}; src={}; gp_usd={}
    def upd(sym, val, name, usd_price=None):
        try: val=float(val)
        except: return
        key=sym.lower()+'_idr'
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
    return g, src, gp_usd
def scan():
    now=datetime.now(WIB).strftime("%H:%M WIB"); now_ts=int(time.time())
    vol_hist=load_json(VOL_FILE); price_hist=load_json(PRICE_FILE)
    new_vol={}; new_price={}
    tickers=get_tickers(); gdata, gsrc, gprice=get_global()
    tier_bawah=[]; tier_scalp=[]; tier_early=[]; tier_new=[]; tier_indo=[]; tier_global=[]; tier_bahaya=[]
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
        if t['pair'] in gprice and gprice[t['pair']]>0:
            fair=gprice[t['pair']]*USD_IDR
            premium=(price-fair)/fair*100 if fair>0 else 0
        else:
            premium=0
        hist=vol_hist.get(t['pair'],[])
        if isinstance(hist, dict): hist=[hist]
        if not isinstance(hist, list): hist=[]
        hist=[e for e in hist if isinstance(e,dict) and now_ts-e.get("ts",0)<7*3600]
        vol_6h=get_vol_6h(hist, now_ts)
        vol_ratio=(vol/vol_6h) if vol_6h and vol_6h>0 else 1.0
        hist.append({"ts": now_ts, "vol": vol}); new_vol[t['pair']]=hist
        prev=price_hist.get(t['pair'],{})
        if isinstance(prev, list): prev=prev[-1] if prev else {}
        if not isinstance(prev, dict): prev={}
        new_price[t['pair']]={"ts": now_ts, "price": price}
        ent_low=low*1.01; ent_high=low*1.03; ent_txt=f"{ent_low:.0f}-{ent_high:.0f} OB"
        cut=ent_low*0.97; target=ent_high*1.10
        cut_scalp=ent_low*0.98; target_scalp=ent_high*1.05
        retest_low=price*0.93; retest_high=price*0.97
        if pos>40:
            ent_txt2=f"{retest_low:.0f}-{retest_high:.0f} RETEST"
            cut2=retest_low*0.97; target2=retest_high*1.10
        else:
            ent_txt2=ent_txt; cut2=cut; target2=target
        if premium>30 or naik>35:
            tier_bahaya.append(f"⚠️ PUMP BAHAYA! JANGAN BELI! | {sym} Rp{price:.0f} | Indo {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {gp_txt} | Prem {premium:.1f}% | Udah telat! Bandar mau buang!")
            continue
        # === 🚀 PUMP DARI BAWAH - GENERIC! BERLAKU BUAT 100+ KOIN! ===
        # GAK PEDULI NAMA KOIN! GAK BUTUH GLOBAL! Cukup: Naik 0-3%! Pos 5-30%! Vol >=80Mn! Vol 6J >=1,8x! Prem <10%!
        # Ini pola SKYAI, BMT, ENJ pas masih di bawah! Bisa +30% sampai +52%!
        if 0<=naik<=3.0 and 5<=pos<=30 and vol>=80_000_000 and (vol_ratio>=1.8 or (vol_ratio==1.0 and vol>=150_000_000)) and premium<10:
            tier_bawah.append(f"🚀 PUMP DARI BAWAH! | {sym} Rp{price:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn (6J {vol_ratio:.1f}x) | {gp_txt} | Prem {premium:.1f}% | ENTRY {ent_txt} | CUT {cut:.0f} | TARGET {target:.0f} | MODAL 200rb! | INI BARU MAU TERBANG!")
        # === ⚡ SCALP INDO DOANG - GENERIC! ===
        if 3<=naik<=15 and 20<=pos<=60 and vol>=100_000_000 and 10<=premium<=30:
            tier_scalp.append(f"⚡ SCALP INDO DOANG! | {sym} Rp{price:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {gp_txt} | Prem {premium:.1f}% | ENTRY {ent_txt} | CUT {cut_scalp:.0f} (2%!) | TARGET {target_scalp:.0f} (5%!) | MODAL 100rb! | 15 MENIT DOANG!")
        # === 🐣 EARLY - BELUM TERBANG (GLOBAL) ===
        if 0<=naik<=2.5 and 5<=pos<=30 and vol>=80_000_000 and (vol_ratio>=1.8 or (vol_ratio==1.0 and vol>=150_000_000)) and gp>=0.5 and premium<5:
            tier_early.append(f"🐣 EARLY BELUM TERBANG! | {sym} Rp{price:.0f} | Naik {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn (6J {vol_ratio:.1f}x) | {gp_txt} | Prem {premium:.1f}% | ENTRY {ent_txt} | CUT {cut:.0f} | TARGET {target:.0f} | MODAL 200rb!")
        # === 💥 NEW 5%+ ===
        if gp>=2.0 and 2<=naik<=30 and 10<=pos<=70 and vol>=40_000_000 and premium<10:
            tier_new.append(f"💥 NEW {gp:.0f}% | {sym} Rp{price:.0f} | ENTRY {ent_txt2} | Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {gp_txt} | OB {ent_txt} | CUT {cut2:.0f} | TARGET {target2:.0f} | MODAL 200rb!")
        # === 👑 BANDAR INDODAX ===
        if vol_ratio>=2.5 and vol_6h and vol_6h>=20_000_000 and 0<=naik<=3.0 and 15<=pos<=45 and vol>=150_000_000:
            if t['pair'] not in seen:
                tier_indo.append(f"👑 BANDAR INDODAX! | {sym} Rp{price:.0f} | Vol 6J {vol_ratio:.1f}x ({vol/1e6:.0f}Mn vs {vol_6h/1e6:.0f}Mn) | Naik {naik:.1f}% Pos {pos:.0f}% | {gp_txt} | Prem {premium:.1f}% | ENTRY {ent_txt} | CUT {cut:.0f} | TARGET {target:.0f} | MODAL 200rb!")
                seen.add(t['pair'])
            continue
        # === 🌍 BANDAR GLOBAL ===
        if gp>=3.0 and 0.3<=naik<=8.0 and pos<=50 and vol>=150_000_000:
            if t['pair'] not in seen:
                tier_global.append(f"🌍 BANDAR GLOBAL! | {sym} Rp{price:.0f} | Indo {naik:.1f}% Pos {pos:.0f}% Vol {vol/1e6:.0f}Mn | {gp_txt} | Prem {premium:.1f}% | ENTRY {ent_txt} | CUT {cut:.0f} | TARGET {target:.0f} | MODAL 200rb!")
                seen.add(t['pair'])
            continue
    save_json(VOL_FILE, new_vol); save_json(PRICE_FILE, new_price)
    msg=f"=== V44 - GENERIC PUMP DARI BAWAH {now} - {len(tickers)} KOINS (9 HOLD DISKIP) ===\n"
    msg+=f"🚀 PUMP DARI BAWAH [MAX 5 - INI YANG LU MAU! SEMUA KOIN BISA!]:\n"+("\n".join(tier_bawah[:5]) if tier_bawah else "Belum ada yang mau pump - bandar Indo belum masuk!")+"\n\n"
    msg+=f"⚡ SCALP INDO DOANG [MAX 5 - TARGET 5% DOANG!]:\n"+("\n".join(tier_scalp[:5]) if tier_scalp else "Belum ada scalp - market lagi tidur!")+"\n\n"
    msg+=f"🐣 EARLY - BELUM TERBANG [MAX 5]:\n"+("\n".join(tier_early[:5]) if tier_early else "Belum ada yang mau terbang!")+"\n\n"
    msg+=f"💥 NEW 5%+ [MAX 7]:\n"+("\n".join(tier_new[:7]) if tier_new else "Belum ada NEW!")+"\n\n"
    msg+=f"👑 BANDAR INDODAX [MAX 5]:\n"+("\n".join(tier_indo[:5]) if tier_indo else "Belum ada bandar!")+"\n\n"
    msg+=f"🌍 BANDAR GLOBAL [MAX 5]:\n"+("\n".join(tier_global[:5]) if tier_global else "Belum ada bandar Global!")+"\n\n"
    msg+=f"⚠️ PUMP BAHAYA - JANGAN BELI!:\n"+("\n".join(tier_bahaya[:5]) if tier_bahaya else "Gak ada pump bahaya!")+"\n\n"
    msg+=f"📌 PUMP BAWAH: ENTRY=Low*1.01-1.03! CUT 3%! TARGET 10%! 2 JAM! SCALP: CUT 2%! TARGET 5%! 15 MENIT! MODAL BAWAH 200rb, SCALP 100rb!\n"
    return msg
if __name__=="__main__":
    send_tele(scan())
